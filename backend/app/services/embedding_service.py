import os
import logging
from typing import List, Optional
from pinecone import Pinecone
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class EmbeddingService:
    """
    Service for generating embeddings using Google Gemini's embedding-001 model
    and storing/retrieving them from Pinecone vector database.
    """
    
    def __init__(self):
        """Initialize Pinecone connection"""
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
    
    def generate_embedding(self, text: str, task_type: str = "retrieval_document") -> List[float]:
        """
        Generate embedding vector using Gemini embedding-001 model (FREE tier).
        
        Args:
            text: The text to embed
            task_type: Type of embedding task. Options:
                - "retrieval_document": For documents being indexed
                - "retrieval_query": For search queries
                - "semantic_similarity": For similarity comparisons
                - "classification": For classification tasks
        
        Returns:
            List of floats representing the embedding vector (768 dimensions)
        """
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided for embedding")
                return [0.0] * 768
            
            # Gemini has a token limit - truncate if needed
            max_chars = 20000  # Conservative limit
            if len(text) > max_chars:
                logger.warning(f"Text too long ({len(text)} chars), truncating to {max_chars}")
                text = text[:max_chars]
            
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type=task_type,
                title=None  # Optional title for document embeddings
            )
            
            embedding = result['embedding']
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            # Return zero vector as fallback (will not match well in queries)
            return [0.0] * 768
    
    def generate_embeddings(self, texts: List[str], task_type: str = "retrieval_document") -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            task_type: Type of embedding task
        
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for i, text in enumerate(texts):
            logger.debug(f"Generating embedding {i+1}/{len(texts)}")
            embedding = self.generate_embedding(text, task_type)
            embeddings.append(embedding)
        return embeddings
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding specifically optimized for query/search.
        Uses the retrieval_query task type for better query-document matching.
        
        Args:
            query: The search query
        
        Returns:
            Query embedding vector
        """
        return self.generate_embedding(query, task_type="retrieval_query")
    
    def store_embeddings(self, vectors: List[tuple]) -> bool:
        """
        Store embeddings in Pinecone.
        
        Args:
            vectors: List of tuples (id, embedding, metadata)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            logger.error("Pinecone index not initialized")
            return False
        
        try:
            self.index.upsert(vectors=vectors)
            logger.info(f"Successfully stored {len(vectors)} vectors in Pinecone")
            return True
        except Exception as e:
            logger.error(f"Failed to store embeddings in Pinecone: {e}")
            return False
    
    def query_embeddings(self, query_vector: List[float], top_k: int = 5, filter_dict: Optional[dict] = None):
        """
        Query Pinecone for similar vectors.
        
        Args:
            query_vector: The query embedding vector
            top_k: Number of results to return
            filter_dict: Optional metadata filters
        
        Returns:
            Query results from Pinecone
        """
        if not self.index:
            logger.error("Pinecone index not initialized")
            return None
        
        try:
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            logger.info(f"Query returned {len(results.matches)} matches")
            return results
        except Exception as e:
            logger.error(f"Failed to query Pinecone: {e}")
            return None


# Singleton instance
embedding_service = EmbeddingService()








# import os
# import logging
# from pinecone import Pinecone
# import google.generativeai as genai

# logger = logging.getLogger(__name__)

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# class EmbeddingService:
#     def __init__(self):
#         try:
#             api_key = os.getenv("PINECONE_API_KEY")
#             index_name = os.getenv("PINECONE_INDEX_NAME")
            
#             if not api_key or not index_name:
#                 logger.warning("Pinecone credentials not configured")
#                 self.pc = None
#                 self.index = None
#                 return
            
#             self.pc = Pinecone(api_key=api_key)
#             self.index = self.pc.Index(index_name)
#             logger.info(f"Pinecone embedding service initialized")
#         except Exception as e:
#             logger.error(f"Failed to initialize Pinecone: {e}")
#             self.pc = None
#             self.index = None
    
#     def generate_embedding(self, text):
#         """Generate embedding using Gemini (FREE)"""
#         try:
#             result = genai.embed_content(
#                 model="models/embedding-001",
#                 content=text,
#                 task_type="retrieval_document"
#             )
#             return result['embedding']
#         except Exception as e:
#             logger.error(f"Embedding error: {e}")
#             return [0.0] * 768
    
#     def generate_embeddings(self, texts):
#         """Generate embeddings for multiple texts"""
#         return [self.generate_embedding(text) for text in texts]


# embedding_service = EmbeddingService()




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
