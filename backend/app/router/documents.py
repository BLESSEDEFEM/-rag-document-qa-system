import json
import logging
from datetime import datetime
from typing import List, Dict, Any

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

# Import database dependencies
from app.database import get_db
from app.models import Document

# Import services
from app.services import file_storage, text_extraction
from app.services.chunking_service import chunk_text
from app.services.embedding_service import embedding_service
from app.services.pinecone_service import pinecone_service
from app.services.llm_service import llm_service

# Configure logger for this module
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}}
)


@router.post("/upload", response_model=Dict[str, Any])
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document (PDF, DOCX, TXT) for processing.

    Process:
    1. Validate file type and size
    2. Save file to disk with unique UUID filename
    3. Extract text from document
    5. Return document details

    Security validations:
    File type checking (whitelist)
    File size limits
    Filename sanitization (UUID)
    """

    # Define allowed file types
    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB in bytes

    logger.info("Upload attempt: %s", file.filename)

    # SECURITY: Validate file extension
    file_extension = None
    if file.filename:
        file_extension = "." + file.filename.split(".")[-1].lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        logger.warning("Invalid file type attempted: %s", file.filename)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    # SECURITY: Check file size
    contents = await file.read()
    file_size = len(contents)

    if file_size > MAX_FILE_SIZE:
        logger.warning("File too large: %d bytes", file_size)
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)} MB")

    # Reset file pointer after reading (important!)
    await file.seek(0)

    # Save file to disk
    try:
        logger.info("Saving file to disk...")
        file_path, unique_filename = await file_storage.save_uploaded_file(file)
        logger.info("File saved: %s", file_path)
    except Exception as e:
        logger.error("Error saving file: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Error saving file: {str(e)}"
        ) from e

    # Extract text from document
    logger.info("Extracting text from document...")
    extraction_result = await text_extraction.extract_text(
        file_path,
        file_extension
    )

    # Initialize variables
    extracted_text = None
    page_count = None
    chunks = None
    embeddings = None
    chunk_count = None
    status = "failed"

    if extraction_result["success"]:
        logger.info(
            "Text extraction successful: %d characters", len(
                extraction_result['text']))
        extracted_text = extraction_result["text"]
        page_count = extraction_result["page_count"]
        status = "extracted"

        # Generate chunks
        try:
            logger.info("Chunking text...")
            chunks = chunk_text(extracted_text, chunk_size=500, overlap=50)
            chunk_count = len(chunks)
            logger.info("Created %d chunks", chunk_count)

            # Generate embeddings
            logger.info("Generate embeddings...")
            embeddings = embedding_service.generate_embeddings_batch(chunks)
            logger.info("Generated %d embeddings", len(embeddings))

            status = "ready"  # Fully processed

        except Exception as e:
            logger.error("Error during chunking/embedding: %s", e)
            status = "extracted"  # Text extracted but embedding failed
            # Continue without embeddings (graceful degradation)

    else:
        logger.warning(
            "Text extraction failed: %s",
            extraction_result['error'])

    # Create database record
    try:
        logger.info("Creating database record...")

        document = Document(
            filename=unique_filename,
            original_filename=file.filename or "unknown",
            file_path=file_path,
            file_size=file_size,
            file_type=file_extension.replace(".", ""),
            extracted_text=extracted_text,
            page_count=page_count,
            status=status,
            # Embedding fields
            chunks=json.dumps(chunks) if chunks else None,
            embeddings=None,  # Stored in Pinecone, not postgreSQL
            chunk_count=chunk_count,
            embedding_model="all-mpnet-base-v2" if embeddings else None,
            embedding_dimension=768 if embeddings else None,
            embedding_date=datetime.utcnow() if embeddings else None
            # upload_date is auto-set by datbase (server_default=func.now())
            # is_deleted dafaults to False
        )

        db.add(document)
        db.commit()
        db.refresh(document)  # Get the ID assigned by database

        logger.info("Database record created: Document ID %d", document.id)

        # Store embeddings in Pinecone
        if embeddings and chunks and document.id:
            try:
                logger.info(
                    "Storing %d embeddings in Pinecone...",
                    len(embeddings))

                pinecone_result = pinecone_service.upsert_embeddings(
                    document_id=document.id,
                    chunks=chunks,
                    embeddings=embeddings,
                    metadata={
                        "filename": document.original_filename,
                        "file_type": document.file_type
                    }
                )

                if pinecone_result["success"]:
                    logger.info(
                        "Pinecone storage successful: %d vectors",
                        pinecone_result['upserted_count'])
                else:
                    logger.error(
                        "Pinecone storage failed: %s",
                        pinecone_result.get('error'))

            except Exception as e:
                logger.error("Error storing in Pinecone: %s", e)
                # Don't fail the entire upload if Pinecone fails (graceful
                # degradation)

    except Exception as e:
        logger.error("Error creating database record: %s", e)
        db.rollback()

        # Delete uploaded file (cleanup)
        await file_storage.delete_file(file_path)

        raise HTTPException(
            status_code=500,
            detail=f"Error saving to database: {str(e)}"
        ) from e

    return {
        "message": "Document uploaded and processed succesfully",
        "document_id": document.id,
        "filename": document.original_filename,
        "unique_filename": document.filename,
        "size_bytes": document.file_size,
        "file_type": document.file_type,
        "status": document.status,
        "page_count": document.page_count,
        "character_count": len(extracted_text) if extracted_text else 0,
        "chunk_count": document.chunk_count,
        "embedding_dimension": document.embedding_dimension,
        "is_embedded": document.chunk_count is not None and document.chunk_count > 0,
        "upload_date": document.upload_date.isoformat(),
        "extracted_text_preview": extracted_text[:200] + "..." if extracted_text and len(extracted_text) > 200 else extracted_text
    }


@router.post("/query", response_model=Dict[str, Any])
async def query_documents(
    query: str,
    top_k: int = 5,
    min_score: float = 0.3,
    _db: Session = Depends(get_db)
):
    """
    Query documents using semantic search.

    Process:
    1. Generate embedding for user query
    2. Search Pinecone for similar vectors
    3. Retrieve relevant chunks with metadata
    4. Filter by minimum score threshold
    5. Return ranked results

    Args:
        query: User's question or search query
        top_k: Number of results to return (default: 5)
        min_score: Minimum similarity score (0.0-1.0, default: 0.3)
        db: Database session

    Returns:
        Dictionary with query and ranked results
    """

    logger.info("Query received: %s (top_k=%d)", query, top_k)

    # Validate query
    if not query or len(query.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )

    if len(query) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Query too long (max 1000 characters)"
        )

    try:
        # Step 1: Generate embedding for query
        logger.info("Generating query embedding...")
        query_embedding = embedding_service.generate_embedding(query.strip())
        logger.info(
            "Query embedding generated: %d dimensions",
            len(query_embedding))

        # Step 2: Search Pinecone for similar vectors
        logger.info("Searching Pinecone for top %d matches...", top_k)
        pinecone_results = pinecone_service.query_similar(
            query_embedding=query_embedding,
            top_k=top_k
        )

        logger.info("Pinecone returned %d results", len(pinecone_results))

        # Step 3: Format results
        results = []
        for match in pinecone_results:
            result = {
                "chunk_text": match["metadata"].get("chunk_text", ""),
                "score": match["score"],
                "source": {
                    "document_id": match["metadata"].get("document_id"),
                    "filename": match["metadata"].get("filename", "Unknown"),
                    "file_type": match["metadata"].get("file_type", "Unknown"),
                    "chunk_index": match["metadata"].get("chunk_index", 0),
                    "query_terms_found": ["AI", "medical", "diagnose"]
                }
            }
            results.append(result)

        # Step 3.5: Filter results by minimum score
        results = [r for r in results if r["score"] >= min_score]
        logger.info(
            "After filtering (min_score={min_score}): %d results remain",
            len(results))

        # Step 4: Return response
        response = {
            "query": query,
            "top_k": top_k,
            "min_score": min_score,
            "results_count": len(results),
            "results": results,
            "stats": {
                "unique_documents": len(set(r["source"]["document_id"] for r in results)),
                "avg_score": sum(r["score"] for r in results) / len(results) if results else 0,
                "best_score": max(r["score"] for r in results) if results else 0
            }
        }

        logger.info(
            "Query completed successfully: %d results returned",
            len(results))
        return response

    except Exception as e:
        logger.error("Error processing query: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        ) from e


@router.post("/answer", response_model=Dict[str, Any])
async def answer_question(
    query: str,
    top_k: int = 5,
    min_score: float = 0.3,
    _db: Session = Depends(get_db)
):
    """
    Answer user question using RAG (Retrieval-Augmented Generation).

    Complete RAG pipeline:
    1. Generate query embedding
    2. Retrieve relevant chunks from Pinecone
    3. Filter by minimum score
    4. Generate natural language answer using LLM
    5. Return answer with source citations

    Args:
        query: User's question
        top_k: Number of chunks to retrieve (default: 5)
        min_score: Minimum relevance score (default: 0.3)
        db: Database session

    Returns:
        Dictionary with generated answer and sources
    """

    logger.info(
        "Answer request: '{query}' (top_k={top_k}, min_score={min_score})")

    # Validate query
    if not query or len(query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if len(query) > 1000:
        raise HTTPException(status_code=400,
                            detail="Query too long (max 1000 characters)")

    try:
        # RETRIEVAL PHASE
        logger.info("Generating query embedding...")
        query_embedding = embedding_service.generate_embedding(query.strip())

        logger.info("Searching Pinecone for top %d matches...", top_k)
        pinecone_results = pinecone_service.query_similar(
            query_embedding=query_embedding,
            top_k=top_k
        )

        # Format and filter results
        context_chunks = []
        for match in pinecone_results:
            chunk = {
                "chunk_text": match["metadata"].get("chunk_text", ""),
                "score": match["score"],
                "source": {
                    "document": match["metadata"].get("document_id"),
                    "filename": match["metadata"].get("filename", "Unknown"),
                    "file_type": match["metadata"].get("file_type", "Unknown"),
                    "chunk_index": match["metadata"].get("chunk_index", 0)
                }
            }
            context_chunks.append(chunk)

        context_chunks = [c for c in context_chunks if c["score"] >= min_score]
        logger.info(
            "After filtering: %d chunks, min_score= %f",
            len(context_chunks),
            min_score)

        # Handle no results
        if len(context_chunks) == 0:
            return {
                "success": True,
                "answer": "I couldn't find any relevant information in the documents to answer your question. Please try rephrasing or upload related documents.",
                "query": query,
                "chunks_used": 0,
                "sources": []}

        # GENERATION PHASE
        logger.info("Generating answer with %d chunks...", len(context_chunks))
        llm_result = llm_service.generate_answer(
            query=query,
            context_chunks=context_chunks,
            max_chunks=5
        )

        if not llm_result["success"]:
            raise HTTPException(
                status_code=500,
                detail="Error generating answer: {llm_result.get('error')}"
            )

        logger.info("Answer generated successfully")

        return {
            "success": True,
            "answer": llm_result["answer"],
            "query": query,
            "chunks_used": llm_result["chunks_used"],
            "sources": llm_result["sources"],
            "retrieval_stats": {
                "chunks_retrieved": len(pinecone_results),
                "chunks_after_filter": len(context_chunks),
                "top_k": top_k,
                "min_score": min_score
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error processing answer request: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing answer request: {str(e)}"
        ) from e


@router.get("/list", response_model=List[Dict[str, Any]])
async def list_documents(db: Session = Depends(get_db)):
    """
    List all uploaded documents.
    """
    logger.info("Document list requested")

    # Query database for all non-deleted documents
    documents = db.query(Document).filter(Document.is_deleted is False).all()

    return [
        {
            "id": doc.id,
            "filename": doc.original_filename,
            "unique_filename": doc.filename,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "status": doc.status,
            "page_count": doc.page_count,
            "upload_date": doc.upload_date.isoformat(),
            "character_count": len(doc.extracted_text) if doc.extracted_text else 0
        }
        for doc in documents
    ]


@router.get("/health")
async def documents_health():
    """
    Health check for documents router
    """
    return {
        "status": "healthy",
        "router": "documents",
        "timestamps": datetime.utcnow().isoformat()
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    # Delete from PostgreSQL
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(404, "Document not found")

    db.delete(document)
    db.commit()

    # Delete from Pinecone
    pinecone_service.delete_document_vectors(document_id)

    # Delete file from disk
    await file_storage.delete_file(document.file_path)

    return {"message": "Document deleted", "document_id": document_id}
