import json
import logging
from datetime import datetime
from typing import List, Dict, Any

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request, BackgroundTasks
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
from app.services.cache_service import cache_service
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from app.middleware.auth import get_current_user, get_current_user_optional
from app.services.virus_scanner import scan_file

# Request models
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    min_score: float = 0.3
    document_id: int | None = None

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["documents"],
    responses={404: {"description": "Not found"}}
)


async def process_document_background(
    document_id: int,
    file_path: str,
    file_extension: str,
    db_session=None
):
    """Process document in background: extract text, chunk, embed."""
    from app.database import SessionLocal
    
    # Use provided session (for tests) or create new one (for production)
    if db_session:
        db = db_session
        should_close = False
    else:
        db = SessionLocal()
        should_close = True
    try:
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error(f"Document {document_id} not found for background processing")
            return
        
        logger.info(f"Background processing document {document_id}")
        
        # Extract text
        extraction_result = await text_extraction.extract_text(file_path, file_extension)
        
        if extraction_result["success"]:
            extracted_text = extraction_result["text"]
            page_count = extraction_result["page_count"]
            
            try:
                # Chunk text
                chunks = chunk_text(extracted_text, chunk_size=1000, overlap=100)
                chunks = [chunk.replace('\x00', '') for chunk in chunks] if chunks else None
                
                if chunks:
                    chunk_count = len(chunks)
                    
                    # Truncate if too many chunks
                    MAX_CHUNKS = 200
                    if chunk_count > MAX_CHUNKS:
                        logger.warning(f"Document has {chunk_count} chunks, truncating to {MAX_CHUNKS}")
                        chunks = chunks[:MAX_CHUNKS]
                        chunk_count = MAX_CHUNKS
                    
                    # Generate embeddings
                    logger.info(f"Generating embeddings for {chunk_count} chunks...")
                    embeddings = embedding_service.generate_embeddings(chunks)
                    
                    if embeddings and all(embeddings):
                        # Store in Pinecone
                        logger.info("Storing chunks in Pinecone...")
                        result = pinecone_service.upsert_embeddings(
                            document_id=document_id,
                            chunks=chunks,
                            embeddings=embeddings,
                            metadata={
                                "filename": document.original_filename,
                                "file_type": document.file_type
                            }
                        )
                        
                        if result["success"]:
                            logger.info(f"Pinecone storage successful: {result['upserted_count']} vectors")
                            
                            # Update document status
                            document.extracted_text = extracted_text.replace('\x00', '')
                            document.page_count = page_count
                            document.chunks = json.dumps(chunks)
                            document.chunk_count = chunk_count
                            document.embedding_model = "cohere-embed-v3"
                            document.embedding_dimension = 1024
                            document.embedding_date = datetime.utcnow()
                            document.status = "ready"
                            document.processed_date = datetime.utcnow()
                        else:
                            logger.error(f"Pinecone storage failed: {result.get('error')}")
                            document.status = "failed"
                    else:
                        logger.error("Failed to generate embeddings")
                        document.status = "failed"
                else:
                    document.status = "failed"
                    
            except Exception as e:
                logger.error(f"Error during chunking/embedding: {e}")
                document.status = "failed"
        else:
            logger.warning(f"Text extraction failed: {extraction_result['error']}")
            document.status = "failed"
        
        db.commit()
        logger.info(f"Background processing complete for document {document_id}: {document.status}")
        
    except Exception as e:
        logger.error(f"Background processing error for document {document_id}: {e}")
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = "failed"
                db.commit()
        except:
            pass
    finally:
        if should_close:
            db.close()


@router.post("/upload", response_model=Dict[str, Any])
async def upload_document(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Upload a document (PDF, DOCX, TXT) for processing."""

    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
    MAX_FILE_SIZE = 10 * 1024 * 1024

    logger.info("Upload attempt: %s", file.filename)

    file_extension = None
    if file.filename:
        file_extension = "." + file.filename.split(".")[-1].lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        logger.warning("Invalid file type attempted: %s", file.filename)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    contents = await file.read()
    file_size = len(contents)

    if file_size > MAX_FILE_SIZE:
        logger.warning("File too large: %d bytes", file_size)
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)} MB")

    await file.seek(0)

    try:
        logger.info("Saving file to disk...")
        file_path, unique_filename = await file_storage.save_uploaded_file(file)
        logger.info("File saved: %s", file_path)
        
        # Virus scan
        logger.info("Scanning file for viruses...")
        scan_result = await scan_file(file_path)
        
        if not scan_result["is_safe"]:
            logger.error(f"Malicious file detected: {scan_result}")
            await file_storage.delete_file(file_path)
            raise HTTPException(
                status_code=400,
                detail="File failed security scan. Malicious content detected."
            )

        logger.info(f"Virus scan result: {scan_result['scan_result']}")
    except Exception as e:
        logger.error("Error saving file: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Error saving file: {str(e)}"
        ) from e

    try:
        logger.info("Creating database record...")

        # Create document record with "processing" status
        document = Document(
            user_id=user["sub"],
            filename=unique_filename,
            original_filename=file.filename or "unknown",
            file_path=file_path,
            file_size=file_size,
            file_type=file_extension.replace(".", ""),
            extracted_text=None,
            page_count=None,
            status="processing",
            chunks=None,
            embeddings=None,
            chunk_count=None,
            embedding_model=None,
            embedding_dimension=None,
            embedding_date=None
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        logger.info("Database record created: Document ID %d", document.id)

        # Queue background processing
        background_tasks.add_task(
            process_document_background,
            document.id,
            file_path,
            file_extension,
            db
        )

    except Exception as e:
        logger.error("Error creating database record: %s", e)
        db.rollback()
        await file_storage.delete_file(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Error saving to database: {str(e)}"
        ) from e
        
    cache_service.delete("documents:list")

    return {
        "message": "Document uploaded successfully. Processing in background...",
        "document_id": document.id,
        "filename": document.original_filename,
        "unique_filename": document.filename,
        "size_bytes": document.file_size,
        "file_type": document.file_type,
        "status": "processing",
        "upload_date": document.upload_date.isoformat()
    }


@router.post("/answer", response_model=Dict[str, Any])
async def answer_question(
    request: QueryRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    query = request.query
    top_k = request.top_k
    min_score = request.min_score
    document_id = request.document_id

    logger.info(f"Answer request: '{query}' (document_id={document_id})")

    if not query or len(query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if len(query) > 1000:
        raise HTTPException(status_code=400,
                            detail="Query too long (max 1000 characters)")
        
    # NEW: Validate document_id if provided
    if document_id is not None and not isinstance(document_id, int):
        raise HTTPException(status_code=400, detail="Invalid document_id format")
    
    if document_id is not None and document_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid document_id value")

    try:
        logger.info("Generating query embedding...")
        query_embedding = embedding_service.generate_embedding(query.strip())
        
        if not query_embedding:
            raise HTTPException(500, "Failed to generate query embedding")

        logger.info("Searching Pinecone for top %d matches...", top_k)
        
        # Build filter
        if document_id:
            doc = db.query(Document).filter(
                Document.id == document_id,
                Document.user_id == user["sub"]
            ).first()
            
            if not doc:
                return {
                    "success": True,
                    "answer": "Document not found or you don't have access to it.",
                    "query": query,
                    "chunks_used": 0,
                    "sources": []
                }
            
            pinecone_filter = {"document_id": document_id}
        else:
            user_docs = db.query(Document.id).filter(
                Document.user_id == user["sub"],
                Document.is_deleted == False
            ).all()
            user_doc_ids = [doc.id for doc in user_docs]
            
            if not user_doc_ids:
                return {
                    "success": True,
                    "answer": "You haven't uploaded any documents yet. Please upload documents first.",
                    "query": query,
                    "chunks_used": 0,
                    "sources": []
                }
            
            pinecone_filter = {"document_id": {"$in": user_doc_ids}}
        
        pinecone_results = pinecone_service.query_similar(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_dict=pinecone_filter
        )

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
        logger.info("After filtering: %d chunks", len(context_chunks))

        if len(context_chunks) == 0:
            return {
                "success": True,
                "answer": "I couldn't find any relevant information in your documents to answer your question. Please try rephrasing or upload related documents.",
                "query": query,
                "chunks_used": 0,
                "sources": []}

        logger.info("Generating answer with %d chunks...", len(context_chunks))
        llm_result = llm_service.generate_answer(
            query=query,
            context_chunks=context_chunks,
            max_chunks=5
        )

        if not llm_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating answer: {llm_result.get('error')}"
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
async def list_documents(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """List all uploaded documents."""
    logger.info(f"Document list requested by user: {user['sub']}")
    
    cache_key = f"documents:list:{user['sub']}"
    cached = cache_service.get(cache_key)
    if cached:
        logger.info("Returning cached document list")
        return cached
    
    documents = db.query(Document).filter(
        Document.is_deleted == False,
        Document.user_id == user["sub"]
    ).all()
    
    result = [
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
    
    cache_service.set(cache_key, result, ttl=300)
    
    return result


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Delete a document."""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user["sub"]
    ).first()
    
    if not document:
        raise HTTPException(404, "Document not found")

    db.delete(document)
    db.commit()

    pinecone_service.delete_document_vectors(document_id)
    await file_storage.delete_file(document.file_path)
    
    cache_service.delete(f"documents:list:{user['sub']}")

    return {"message": "Document deleted", "document_id": document_id}


@router.get("/health")
async def documents_health():
    """Health check for documents router."""
    return {
        "status": "healthy",
        "router": "documents",
        "timestamps": datetime.utcnow().isoformat()
    }