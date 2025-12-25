import os
import logging
import cohere
from pinecone import Pinecone

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        try:
            cohere_key = os.getenv("COHERE_API_KEY")
            if cohere_key:
                self.cohere_client = cohere.ClientV2(cohere_key)
                logger.info("Embedding service initialized with Cohere")
            else:
                logger.warning("COHERE_API_KEY not found")
                self.cohere_client = None
            
            api_key = os.getenv("PINECONE_API_KEY")
            index_name = os.getenv("PINECONE_INDEX_NAME")
            
            if api_key and index_name:
                self.pc = Pinecone(api_key=api_key)
                self.index = self.pc.Index(index_name)
        except Exception as e:
            logger.error(f"Init error: {e}")
            self.cohere_client = None
    
    def generate_embedding(self, text):
        try:
            response = self.cohere_client.embed(
                texts=[text],
                model='embed-english-v3.0',
                input_type='search_document',
                embedding_types=['float']
            )
            return response.embeddings.float[0]
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return None
    
    def generate_embeddings(self, texts):
        """Generate embeddings in batches of 96"""
        try:
            all_embeddings = []
            batch_size = 96
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = self.cohere_client.embed(
                    texts=batch,
                    model='embed-english-v3.0',
                    input_type='search_document',
                    embedding_types=['float']
                )
                all_embeddings.extend(response.embeddings.float)
                logger.info(f"Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
                
            return all_embeddings
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return None

embedding_service = EmbeddingService()










# import os
# import logging
# from pinecone import Pinecone
# import google.generativeai as genai

# logger = logging.getLogger(__name__)

# class EmbeddingService:
#     def __init__(self):
#         try:
#             # Configure Gemini
#             genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            
#             # Configure Pinecone
#             api_key = os.getenv("PINECONE_API_KEY")
#             index_name = os.getenv("PINECONE_INDEX_NAME")
            
#             if not api_key or not index_name:
#                 logger.warning("Pinecone credentials not configured")
#                 self.pc = None
#                 self.index = None
#                 return
            
#             self.pc = Pinecone(api_key=api_key)
#             self.index = self.pc.Index(index_name)
#             logger.info("Embedding service initialized with Gemini")
#         except Exception as e:
#             logger.error(f"Failed to initialize: {e}")
#             self.pc = None
#             self.index = None
    
#     def generate_embedding(self, text):
#         """Generate embedding using Gemini"""
#         try:
#             result = genai.embed_content(
#                 model="models/embedding-001",
#                 content=text,
#                 task_type="retrieval_document"
#             )
#             return result['embedding']
#         except Exception as e:
#             logger.error(f"Embedding error: {e}")
#             return None
    
#     def generate_embeddings(self, texts):
#         """Generate embeddings for multiple texts"""
#         return [self.generate_embedding(text) for text in texts]

# embedding_service = EmbeddingService()








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
