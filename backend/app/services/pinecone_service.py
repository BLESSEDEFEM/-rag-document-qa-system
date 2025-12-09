"""
Pinecone vector database service
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
            document_id: str,
            chunks: List[str],
            embeddings: List[List[float]],
            metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Stores embeddings in Pinecone with metadata.

        Args:
            document_id: Database document ID
            chunks: List of text chunks
            embeddings: List of embedding vectors
            metadata: Additional metadata for all vectors

        Returns:
            Result dictionary with upser count

        Example:
            >>> result = pinecone_service.upsert_embeddings(
            ...     document_id=5,
            ...     chunks=["chunk1", "chunk2"],
            ...     embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
            ...     metadata={"filename": "report.pdf"}
            ...)
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
                    "chunk_text": chunk[:1000], # Limit text length (Pinecone metadata limits)
                }

                # Add any additional metadata
                if metadata:
                    vector_metadata.update(metadata)

                # Create vector tuple: (id, embedding, metadata)
                vectors.append((vector_id, embedding, vector_metadata))

            # Upsert to Pinecone
            logger.info(f"Upserting {len(vectors)} vectors for document {document_id}")
            upsert_response = self.index.upsert(vectors=vectors)

            logger.info(f"Succesfully upserted {upsert_response.upserted_count} vectors")

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
