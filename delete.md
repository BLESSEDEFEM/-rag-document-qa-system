import axios from 'axios';

// Base URL for backend API
const API_BASE_URL = 'http://localhost:8000/api/documents';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Upload document
export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

// Get all documents
export const getDocuments = async () => {
  const response = await api.get('/list');
  return response.data;
};

// Query documents (retrieval only)
export const queryDocuments = async (query, topK = 5, minScore = 0.3) => {
  const response = await api.post('/query', null, {
    params: { query, top_k: topK, min_score: minScore },
  });
  return response.data;
};

// Answer question (complete RAG)
export const answerQuestion = async (query, topK = 5, minScore = 0.3) => {
  const response = await api.post('/answer', null, {
    params: { query, top_k: topK, min_score: minScore },
  });
  return response.data;
};

export default api;





















"""
LLM service for answer generation using Google Gemini.
Handles RAG answer generation with retrieved context.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


class LLMService:
    """
    Service for generating answers using Google Gemini LLM.
    
    Handles:
    - Answer generation from retrieved context
    - Prompt construction
    - Response formatting
    """
    
    def __init__(self):
        """Initialize Gemini LLM."""
        logger.info(f"Initializing LLM service (model: {GEMINI_MODEL})")
        
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Initialize model
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        
        logger.info(f"LLM service initialized: {GEMINI_MODEL}")
    
    def generate_answer(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        max_chunks: int = 5
    ) -> Dict[str, Any]:
        """
        Generate answer using LLM with retrieved context.
        
        Args:
            query: User's question
            context_chunks: Retrieved chunks from vector search
            max_chunks: Maximum number of chunks to use (default: 5)
        
        Returns:
            Dictionary with answer and metadata
        
        Example:
            >>> context = [
            ...     {"chunk_text": "AI improves diagnostics...", "score": 0.95, "source": {...}},
            ...     {"chunk_text": "Machine learning helps...", "score": 0.87, "source": {...}}
            ... ]
            >>> result = llm_service.generate_answer(
            ...     query="How does AI help healthcare?",
            ...     context_chunks=context
            ... )
            >>> print(result['answer'])
            "AI improves healthcare through..."
        """
        try:
            # Limit context chunks
            context_chunks = context_chunks[:max_chunks]
            
            # Build prompt with context
            prompt = self._build_prompt(query, context_chunks)
            
            logger.info(f"Generating answer for query: '{query[:50]}...'")
            logger.info(f"Using {len(context_chunks)} context chunks")
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Extract answer text
            answer = response.text
            
            logger.info(f"Answer generated successfully ({len(answer)} characters)")
            
            return {
                "success": True,
                "answer": answer,
                "query": query,
                "chunks_used": len(context_chunks),
                "sources": [
                    {
                        "filename": chunk["source"]["filename"],
                        "document_id": chunk["source"]["document_id"],
                        "chunk_index": chunk["source"]["chunk_index"],
                        "relevance_score": chunk["score"]
                    }
                    for chunk in context_chunks
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def _build_prompt(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]]
    ) -> str:
        """
        Build prompt for LLM with retrieved context.
        
        Args:
            query: User's question
            context_chunks: Retrieved document chunks
        
        Returns:
            Formatted prompt string
        """
        # Build context section
        context_text = ""
        for i, chunk in enumerate(context_chunks, 1):
            source = chunk["source"]
            context_text += f"\n[Document {i}] {source['filename']}\n"
            context_text += f"{chunk['chunk_text']}\n"
            context_text += f"(Relevance: {chunk['score']:.2f})\n"
        
        # Build complete prompt
        prompt = f"""You are a helpful AI assistant answering questions based on provided documents.

CONTEXT FROM DOCUMENTS:
{context_text}

USER QUESTION: {query}

INSTRUCTIONS:
1. Answer the question based ONLY on the information provided in the documents above
2. If the documents don't contain enough information to answer, say so clearly
3. Cite which documents you're using (e.g., "According to Document 1...")
4. Be specific and factual
5. Keep the answer concise but complete

ANSWER:"""

        return prompt


# Global singleton instance
llm_service = LLMService()


















































sorry for the interruption. kindly ignore the attempt to switch back to zed. let's continue here from where we stopped

All the while, __init__.py file is created empty and separately from other files in the same folder and none(__init__ method) inside the files. But you put yours inside the file, why?

Secondly, "self" wasn't used all through while sonnet on zed created for me, as parameter to the functions but you now do, why?

Third, in the files created by you on Zed, the services functions were majorly async and also the logger was at the info lvel and upwards never at debug level. why the difference here?

# To cancel Claude pro plan
https://claude.ai/settings/billing




"""
Text chunking service for RAG.
Splits documents into optimal chunks for embedding and retrieval.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)

# Chunking configuration
CHUNK_SIZE = 500  # Characters per chunk
CHUNK_OVERLAP = 50  # Overlap between chunks (for context continuity)


def chunk_text(
    text: str, 
    chunk_size: int = CHUNK_SIZE, 
    overlap: int = CHUNK_OVERLAP
) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Uses character-based chunking with sentence boundary detection.
    Ensures context continuity through overlap between chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Target size of each chunk (characters)
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    
    Example:
        >>> text = "This is a long document with multiple sentences. " * 20
        >>> chunks = chunk_text(text, chunk_size=100, overlap=20)
        >>> len(chunks)
        10
        >>> chunks[0][:20]
        'This is a long docum'
    
    Algorithm:
        1. Validate input (empty text returns empty list)
        2. If text smaller than chunk_size, return as single chunk
        3. Otherwise, split into chunks:
           - Move forward by chunk_size each time
           - Try to break at sentence boundaries (. ! ? or newline)
           - Apply overlap for context continuity
           - Continue until end of text
    """
    # Validate input
    if not text or len(text) == 0:
        logger.warning("Empty text provided for chunking")
        return []
    
    # Clean text
    text = text.strip()
    
    # If text is smaller than chunk size, return as single chunk
    if len(text) <= chunk_size:
        logger.debug(f"Text ({len(text)} chars) smaller than chunk size ({chunk_size}), returning single chunk")
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Calculate end position
        end = start + chunk_size
        
        # If this is not the last chunk, try to break at sentence boundary
        if end < len(text):
            # Look for sentence ending (. ! ? newline) within next 100 chars
            search_end = min(end + 100, len(text))
            
            # Find all possible sentence boundaries
            sentence_ends = [
                text.rfind('. ', end, search_end),
                text.rfind('! ', end, search_end),
                text.rfind('? ', end, search_end),
                text.rfind('\n', end, search_end)
            ]
            
            # Use the nearest sentence boundary if found
            best_break = max(sentence_ends)
            if best_break > end:
                end = best_break + 1  # Include the punctuation
        
        # Extract chunk
        chunk = text[start:end].strip()
        
        # Only add non-empty chunks
        if chunk:
            chunks.append(chunk)
        
        # Move start position (with overlap)
        start = end - overlap
        
        # Prevent infinite loop on very small overlaps
        if start <= 0 or start >= len(text):
            break
    
    logger.info(f"Chunked text ({len(text)} chars) into {len(chunks)} chunks (size={chunk_size}, overlap={overlap})")
    
    return chunks
```

**3. Save the file** (Ctrl + S)

---

## ⏸️ PAUSE - FILE CREATED?

**Before I explain every line with TFET, confirm:**
```
Status: [File created / Need help]

File location: backend/app/services/chunking_service.py

Ready for: [Line-by-line TFET explanation]




"""
Pinecone vector database service.
Handles storing and querying embeddings in Pinecone.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Pinecone configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "rag-documents")


class PineconeService:
    """
    Service for interacting with Pinecone vector database.
    
    Handles:
    - Storing embeddings with metadata
    - Querying similar vectors
    - Deleting vectors
    """
    
    def __init__(self):
        """Initialize Pinecone client and connect to index."""
        logger.info(f"Initializing Pinecone service (index: {PINECONE_INDEX_NAME})")
        
        if not PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Connect to index
        self.index = self.pc.Index(PINECONE_INDEX_NAME)
        
        logger.info(f"Connected to Pinecone index: {PINECONE_INDEX_NAME}")
    
    def upsert_embeddings(
        self,
        document_id: int,
        chunks: List[str],
        embeddings: List[List[float]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store embeddings in Pinecone with metadata.
        
        Args:
            document_id: Database document ID
            chunks: List of text chunks
            embeddings: List of embedding vectors
            metadata: Additional metadata for all vectors
        
        Returns:
            Result dictionary with upsert count
        
        Example:
            >>> result = pinecone_service.upsert_embeddings(
            ...     document_id=5,
            ...     chunks=["chunk1", "chunk2"],
            ...     embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
            ...     metadata={"filename": "report.pdf"}
            ... )
            >>> result['upserted_count']
            2
        """
        try:
            # Prepare vectors for upsert
            vectors = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                # Create unique ID for this vector
                vector_id = f"doc_{document_id}_chunk_{i}"
                
                # Prepare metadata
                vector_metadata = {
                    "document_id": document_id,
                    "chunk_index": i,
                    "chunk_text": chunk[:1000],  # Limit text length (Pinecone metadata limits)
                }
                
                # Add any additional metadata
                if metadata:
                    vector_metadata.update(metadata)
                
                # Create vector tuple: (id, embedding, metadata)
                vectors.append((vector_id, embedding, vector_metadata))
            
            # Upsert to Pinecone
            logger.info(f"Upserting {len(vectors)} vectors for document {document_id}")
            upsert_response = self.index.upsert(vectors=vectors)
            
            logger.info(f"Successfully upserted {upsert_response.upserted_count} vectors")
            
            return {
                "success": True,
                "upserted_count": upsert_response.upserted_count,
                "document_id": document_id
            }
            
        except Exception as e:
            logger.error(f"Error upserting embeddings: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_id": document_id
            }
    
    def query_similar(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query Pinecone for similar vectors.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filter_dict: Optional metadata filter
        
        Returns:
            List of matching results with scores and metadata
        
        Example:
            >>> results = pinecone_service.query_similar(
            ...     query_embedding=[0.1, 0.2, ...],
            ...     top_k=3
            ... )
            >>> results[0]['score']
            0.95
        """
        try:
            # Query Pinecone
            query_response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Format results
            results = []
            for match in query_response.matches:
                results.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                })
            
            logger.info(f"Query returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error querying Pinecone: {e}")
            return []
    
    def delete_document_vectors(self, document_id: int) -> Dict[str, Any]:
        """
        Delete all vectors for a specific document.
        
        Args:
            document_id: Database document ID
        
        Returns:
            Result dictionary
        """
        try:
            # Delete by filter (all vectors with this document_id)
            self.index.delete(filter={"document_id": document_id})
            
            logger.info(f"Deleted all vectors for document {document_id}")
            
            return {
                "success": True,
                "document_id": document_id
            }
            
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_id": document_id
            }
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the Pinecone index.
        
        Returns:
            Index statistics dictionary
        """
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {}


# Global singleton instance
pinecone_service = PineconeService()
```

**3. Save the file** (Ctrl + S)

---

## ⏸️ FILE CREATED?

**Before continuing with integration, confirm:**
```
Status: [File created / Need help]

File location: backend/app/services/pinecone_service.py

Ready for: [Integration explanation / Have questions]



# Store embeddings in Pinecone (Day 3)
        if embeddings and chunks and document.id:
            try:
                logger.info(f"Storing {len(embeddings)} embeddings in Pinecone...")
                
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
                    logger.info(f"✅ Pinecone storage successful: {pinecone_result['upserted_count']} vectors")
                else:
                    logger.error(f"❌ Pinecone storage failed: {pinecone_result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error storing in Pinecone: {e}")
                # Don't fail the entire upload if Pinecone fails (graceful degradation)



@router.post("/query", response_model=Dict[str, Any])
async def query_documents(
    query: str,
    top_k: int = 5,
    db: Session = Depends(get_db)
):
    """
    Query documents using semantic search.
    
    Process:
    1. Generate embedding for user query
    2. Search Pinecone for similar vectors
    3. Retrieve relevant chunks with metadata
    4. Return ranked results
    
    Args:
        query: User's question or search query
        top_k: Number of results to return (default: 5)
        db: Database session
    
    Returns:
        Dictionary with query and ranked results
    """
    
    logger.info(f"Query received: '{query}' (top_k={top_k})")
    
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
        logger.info(f"Query embedding generated: {len(query_embedding)} dimensions")
        
        # Step 2: Search Pinecone for similar vectors
        logger.info(f"Searching Pinecone for top {top_k} matches...")
        pinecone_results = pinecone_service.query_similar(
            query_embedding=query_embedding,
            top_k=top_k
        )
        
        logger.info(f"Pinecone returned {len(pinecone_results)} results")
        
        # Step 3: Format results
        results = []
        for match in pinecone_results:
            result = {
                "chunk_text": match["metadata"].get("chunk_text", ""),
                "score": match["score"],
                "source": {
                    "document_id": match["metadata"].get("document_id"),
                    "filename": match["metadata"].get("filename", "Unknown"),
                    "file_type": match["metadata"].get("file_type", "unknown"),
                    "chunk_index": match["metadata"].get("chunk_index", 0)
                }
            }
            results.append(result)
        
        # Step 4: Return response
        response = {
            "query": query,
            "top_k": top_k,
            "results_count": len(results),
            "results": results
        }
        
        logger.info(f"Query completed successfully: {len(results)} results returned")
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )