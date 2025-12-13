"""
Embedding service using Pinecone auto-embeddings.
No local model needed - Pinecone handles embedding generation.
"""

import os
import logging
from pinecone import Pinecone

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing embeddings via Pinecone."""
    
    def __init__(self):
        """Initialize Pinecone connection."""
        try:
            api_key = os.getenv("PINECONE_API_KEY")
            index_name = os.getenv("PINECONE_INDEX_NAME")
            
            if not api_key or not index_name:
                logger.warning("Pinecone credentials not configured")
                self.pc = None
                self.index = None
                return
            
            self.pc = Pinecone(api_key=api_key)
            self.index = self.pc.Index(index_name)
            logger.info(f"Pinecone embedding service initialized with index: {index_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            self.pc = None
            self.index = None
    
    def generate_embeddings(self, texts):
        """
        Generate embeddings for texts using Pinecone.
        Returns None - Pinecone handles embeddings during upsert.
        """
        if not texts:
            return None
        
        logger.info(f"Embedding generation delegated to Pinecone for {len(texts)} texts")
        return None  # Pinecone auto-embeds during upsert


# Global instance
embedding_service = EmbeddingService()




# """
# Embedding service using sentence-transformers.
# Provides local, free embedding generation for RAG system.
# """

# import logging
# from typing import List
# from sentence_transformers import SentenceTransformer

# # Configure logging
# logger = logging.getLogger(__name__)

# # Model configuration
# MODEL_NAME = "all-mpnet-base-v2"
# EMBEDDING_DIMENSION = 768


# class EmbeddingService:
#     """
#     Service for generating embeddings using sentence-transformers.

#     Loads model once and reuses for all embedding generation.
#     Supports single text or batch processing.
#     """

#     def __init__(self):
#         """
#         Initialize embedding service.
#         Loads the sentence-transformer model.
#         """
#         logger.info(f"Loading embedding model: {MODEL_NAME}")
#         self.model = SentenceTransformer(MODEL_NAME)
#         logger.info(f"Model loaded successfully. Dimension: {EMBEDDING_DIMENSION}")

#     def generate_embedding(self, text: str) -> List[float]:
#         """
#         Generate embedding for single text.

#         Args:
#             text: Text to embed

#         Returns:
#             List of floats representing the embedding (768 dimensiuons)

#         Example:
#         >>> service = EmbeddingService()
#         >>> embedding = service.generate_embedding("Hello world")
#         >>> len(embedding)
#         """

#         try:
#             # Generate embedding
#             embedding = self.model.encode(text, convert_to_numpy=True)

#             # Convert numpy array to list for JSON serialization
#             embedding_list = embedding.tolist()

#             logger.debug(f"Generated embedding for text (length: {len(text)} chars)")

#             return embedding_list

#         except Exception as e:
#             logger.error(f"Error generating embedding: {str(e)}")
#             raise

#     def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
#         """
#         Generate embeddings for multiple texts (batch processing).

#         More efficient than calling generate_embedding() multiple times.

#         Args:
#             texts: List of texts to embed

#         Returns:
#             List of embeddings (each embedding is a list of 768 floats)

#         Example:
#         >>> service = EmbeddingService()
#         >>> embeddings = service.generate_embeddings_batch(["Hello", "World"])
#         >>> len(embeddings)
#         2
#         >>> len(embeddings[0])
#         768
#         """

#         try:
#             # Generate embeddings in batch (more efficient)
#             embeddings = self.model.encode(
#                 texts,
#                 convert_to_numpy=True,
#                 show_progress_bar=len(texts) > 10 # Show progress for large batches
#                 )

#             # Convert numpy array to list of lists
#             embeddings_list = embeddings.tolist()

#             logger.info(f"Generated {len(texts)} embeddings in batch")

#             return embeddings_list

#         except Exception as e:
#             logger.error(f"Error generating batch embeddings: {str(e)}")
#             raise

#     def get_embedding_dimension(self) -> int:
#         """
#         Get the dimension of embeddings produced by this model.

#         Returns:
#             Embedding dimension (768 for all-mpnet-base-v2)
#         """
#         return EMBEDDING_DIMENSION


# # Global singleton instance
# # Loaded once when module is imported, shared across application
# embedding_service = EmbeddingService()
