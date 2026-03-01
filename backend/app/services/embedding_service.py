"""
Embedding service - Gemini primary via direct REST API, Cohere fallback.
"""
import os
import logging
from typing import List
import httpx
import cohere

logger = logging.getLogger(__name__)

GEMINI_EMBED_URL = "https://generativelanguage.googleapis.com/v1/models/text-embedding-004:batchEmbedContents"

class EmbeddingService:

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key:
            logger.info(f"Gemini REST client ready, key starts with: {self.gemini_api_key[:8]}")
        else:
            logger.warning("GEMINI_API_KEY missing")

        self.cohere_api_key = os.getenv("COHERE_API_KEY")
        if self.cohere_api_key:
            self.cohere_client = cohere.ClientV2(api_key=self.cohere_api_key)
            logger.info("Cohere fallback ready")
        else:
            self.cohere_client = None

    def _gemini_batch(self, texts: List[str], task_type: str) -> List[List[float]]:
        """Call Gemini v1 REST API directly - no SDK, no version issues."""
        body = {
            "requests": [
                {
                    "model": "models/text-embedding-004",
                    "content": {"parts": [{"text": t}]},
                    "taskType": task_type
                }
                for t in texts
            ]
        }
        response = httpx.post(
            GEMINI_EMBED_URL,
            json=body,
            params={"key": self.gemini_api_key},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return [item["embedding"]["values"] for item in data["embeddings"]]

    def generate_embedding(self, text: str) -> List[float]:
        if not text or not text.strip():
            return None
        text = text.strip()

        if self.gemini_api_key:
            try:
                embeddings = self._gemini_batch([text], "RETRIEVAL_QUERY")
                logger.info(f"Gemini embedding: {len(embeddings[0])} dims")
                return embeddings[0]
            except Exception as e:
                logger.warning(f"Gemini failed: {e}, trying Cohere...")

        if self.cohere_client:
            try:
                r = self.cohere_client.embed(
                    texts=[text], model="embed-english-v3.0",
                    input_type="search_query", embedding_types=["float"]
                )
                return r.embeddings.float_[0]
            except Exception as e:
                logger.error(f"Cohere failed: {e}")

        return None

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return None
        texts = [t.strip() for t in texts if t and t.strip()]
        if not texts:
            return None

        if self.gemini_api_key:
            try:
                embeddings = self._gemini_batch(texts, "RETRIEVAL_DOCUMENT")
                logger.info(f"Gemini batch: {len(embeddings)} texts, {len(embeddings[0])} dims")
                return embeddings
            except Exception as e:
                logger.warning(f"Gemini batch failed: {e}, trying Cohere...")

        if self.cohere_client:
            try:
                r = self.cohere_client.embed(
                    texts=texts, model="embed-english-v3.0",
                    input_type="search_document", embedding_types=["float"]
                )
                return r.embeddings.float_
            except Exception as e:
                logger.error(f"Cohere failed: {e}")

        return None

embedding_service = EmbeddingService()





























# """
# Embedding service with Gemini primary, Cohere fallback.
# """
# import os
# import logging
# from typing import List
# import cohere
# from google import genai
# from google.genai import types

# logger = logging.getLogger(__name__)

# class EmbeddingService:

#     def __init__(self):
#         # Gemini (Primary)
#         self.gemini_api_key = os.getenv("GEMINI_API_KEY")
#         if self.gemini_api_key:
#             self.gemini_client = genai.Client(api_key=self.gemini_api_key)
#             logger.info("Gemini embedding service initialized (google-genai SDK)")
#         else:
#             self.gemini_client = None
#             logger.warning("GEMINI_API_KEY not found")

#         # Cohere (Fallback)
#         self.cohere_api_key = os.getenv("COHERE_API_KEY")
#         if self.cohere_api_key:
#             self.cohere_client = cohere.ClientV2(api_key=self.cohere_api_key)
#             logger.info("Cohere embedding service initialized")
#         else:
#             self.cohere_client = None

#     def generate_embedding(self, text: str) -> List[float]:
#         if not text or not text.strip():
#             logger.error("Empty text provided")
#             return None

#         text = text.strip()

#         # Try Gemini first
#         if self.gemini_client:
#             try:
#                 response = self.gemini_client.models.embed_content(
#                     model="text-embedding-004",
#                     contents=text,
#                     config=types.EmbedContentConfig(
#                         task_type="RETRIEVAL_QUERY"
#                     )
#                 )
#                 embedding = response.embeddings[0].values
#                 logger.info(f"Gemini embedding generated: {len(embedding)} dims")
#                 return embedding
#             except Exception as e:
#                 logger.warning(f"Gemini embedding failed: {e}, trying Cohere...")

#         # Fallback to Cohere
#         if self.cohere_client:
#             try:
#                 response = self.cohere_client.embed(
#                     texts=[text],
#                     model="embed-english-v3.0",
#                     input_type="search_query",
#                     embedding_types=["float"]
#                 )
#                 embedding = response.embeddings.float_[0]
#                 logger.info("Cohere embedding generated (fallback)")
#                 return embedding
#             except Exception as e:
#                 logger.error(f"Cohere also failed: {e}")

#         logger.error("No embedding service available")
#         return None

#     def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
#         if not texts:
#             return None

#         texts = [t.strip() for t in texts if t and t.strip()]
#         if not texts:
#             return None

#         # Try Gemini first
#         if self.gemini_client:
#             try:
#                 response = self.gemini_client.models.embed_content(
#                     model="text-embedding-004",
#                     contents=texts,
#                     config=types.EmbedContentConfig(
#                         task_type="RETRIEVAL_DOCUMENT"
#                     )
#                 )
#                 embeddings = [e.values for e in response.embeddings]
#                 logger.info(f"Gemini batch embeddings: {len(embeddings)} texts, {len(embeddings[0])} dims")
#                 return embeddings
#             except Exception as e:
#                 logger.warning(f"Gemini batch failed: {e}, trying Cohere...")

#         # Fallback to Cohere
#         if self.cohere_client:
#             try:
#                 response = self.cohere_client.embed(
#                     texts=texts,
#                     model="embed-english-v3.0",
#                     input_type="search_document",
#                     embedding_types=["float"]
#                 )
#                 logger.info(f"Cohere batch embeddings: {len(texts)} texts")
#                 return response.embeddings.float_
#             except Exception as e:
#                 logger.error(f"Both failed: {e}")

#         return None

# # Global instance
# embedding_service = EmbeddingService()




























# # """
# # Embedding service using Gemini (768-dimension).
# # """

# # import os
# # import logging
# # from typing import List
# # from google import genai

# # logger = logging.getLogger(__name__)


# # class EmbeddingService:

# #     def __init__(self):
# #         self.gemini_api_key = os.getenv("GEMINI_API_KEY")

# #         if not self.gemini_api_key:
# #             logger.error("GEMINI_API_KEY not found")
# #             self.client = None
# #             return

# #         # Force correct Gemini API version
# #         self.client = genai.Client(
# #             api_key=self.gemini_api_key,
# #             http_options={"api_version": "v1"}
# #         )

# #         logger.info("Gemini embedding service initialized (text-embedding-004)")

# #     def generate_embedding(self, text: str) -> List[float]:
# #         if not text or not text.strip():
# #             logger.error("Empty text provided for embedding")
# #             return None

# #         try:
# #             response = self.client.models.embed_content(
# #                 model="models/embedding-001",
# #                 contents=text.strip()
# #             )

# #             embedding = response.embeddings[0].values
# #             logger.info("Gemini embedding generated successfully")
# #             return embedding

# #         except Exception as e:
# #             logger.error(f"Gemini embedding failed: {e}")
# #             return None

# #     def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
# #         if not texts:
# #             logger.error("Empty texts list provided")
# #             return None

# #         texts = [t.strip() for t in texts if t and t.strip()]
# #         if not texts:
# #             logger.error("All texts were empty after stripping")
# #             return None

# #         try:
# #             response = self.client.models.embed_content(
# #                 model="models/embedding-001",
# #                 contents=texts
# #             )

# #             embeddings = [e.values for e in response.embeddings]
# #             logger.info(f"Generated {len(embeddings)} Gemini embeddings")
# #             return embeddings

# #         except Exception as e:
# #             logger.error(f"Gemini batch embedding failed: {e}")
# #             return None


# # embedding_service = EmbeddingService()













































# # # """
# # # Embedding service with Gemini primary, Cohere fallback.
# # # """
# # # import os
# # # import logging
# # # from typing import List
# # # import cohere
# # # from google import genai


# # # logger = logging.getLogger(__name__)

# # # class EmbeddingService:
    
# # #     def __init__(self):
# # #         # Gemini (Primary - 15,000 free/month)
# # #         self.gemini_api_key = os.getenv("GEMINI_API_KEY")
# # #         logger.info(f"Gemini key present: {bool(self.gemini_api_key)}, starts with: {self.gemini_api_key[:8] if self.gemini_api_key else 'MISSING'}")
# # #         if self.gemini_api_key:
# # #             genai.configure(api_key=self.gemini_api_key)
# # #             logger.info("Gemini embedding service initialized")
        
# # #         # Cohere (Fallback - 100 free/month)
# # #         self.cohere_api_key = os.getenv("COHERE_API_KEY")
# # #         if self.cohere_api_key:
# # #             self.cohere_client = cohere.ClientV2(api_key=self.cohere_api_key)
# # #             logger.info("Cohere embedding service initialized")
    
# # #     def generate_embedding(self, text: str) -> List[float]:
# # #         """Generate embedding - Try Gemini first, fallback to Cohere."""
# # #         if not text or len(text.strip()) == 0:
# # #             logger.error("Empty text provided for embedding")
# # #             return None
        
# # #         text = text.strip()
        
# # #         # Try Gemini first
# # #         if self.gemini_api_key:
# # #             try:
# # #                 result = genai.embed_content(
# # #                     model="models/embedding-001",
# # #                     content=text,
# # #                     task_type="retrieval_query"
# # #                 )
# # #                 logger.info("Gemini embedding generated successfully")
# # #                 return result['embedding']
# # #             except Exception as e:
# # #                 logger.warning(f"Gemini embedding failed: {e}, trying Cohere fallback...")
        
# # #         # # Fallback to Cohere
# # #         # if self.cohere_api_key:
# # #         #     try:
# # #         #         response = self.cohere_client.embed(
# # #         #             texts=[text],
# # #         #             model="embed-english-v3.0",
# # #         #             input_type="search_query",
# # #         #             embedding_types=["float"]
# # #         #         )
# # #         #         embedding = response.embeddings.float_[0]
# # #         #         logger.info("Cohere embedding generated successfully (fallback)")
# # #         #         return embedding
# # #         #     except Exception as e:
# # #         #         logger.error(f"Cohere embedding also failed: {e}")
# # #         #         return None
        
# # #         logger.error("No embedding service available")
# # #         return None
    
# # #     def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
# # #         """Generate embeddings for multiple texts - Gemini first, Cohere fallback."""
# # #         if not texts:
# # #             logger.error("Empty texts list provided")
# # #             return None
        
# # #         texts = [t.strip() for t in texts if t and len(t.strip()) > 0]
        
# # #         if not texts:
# # #             logger.error("All texts were empty after stripping")
# # #             return None
        
# # #         # Try Gemini first
# # #         if self.gemini_api_key:
# # #             try:
# # #                 result = genai.embed_content(
# # #                     model="models/embedding-001",
# # #                     content=texts,
# # #                     task_type="retrieval_document"
# # #                 )
# # #                 logger.info(f"Gemini batch embeddings: {len(texts)} texts")
# # #                 return result['embedding']
# # #             except Exception as e:
# # #                 logger.warning(f"Gemini failed: {e}, trying Cohere...")
        
# # #         # Fallback to Cohere
# # #         # if self.cohere_api_key:
# # #         #     try:
# # #         #         response = self.cohere_client.embed(
# # #         #             texts=texts,
# # #         #             model="embed-english-v3.0",
# # #         #             input_type="search_document",
# # #         #             embedding_types=["float"]
# # #         #         )
# # #         #         logger.info(f"Cohere batch embeddings: {len(texts)} texts")
# # #         #         return response.embeddings.float_
# # #         #     except Exception as e:
# # #         #         logger.error(f"Both embedding services failed: {e}")
# # #         #         return None
        
# # #         logger.error("No embedding service available")
# # #         return None

# # # # Global instance
# # # embedding_service = EmbeddingService()