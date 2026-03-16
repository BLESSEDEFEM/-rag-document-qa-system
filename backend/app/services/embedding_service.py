"""
Embedding service - Gemini primary via direct REST API, Cohere fallback.
"""
import os
import logging
from typing import List
import httpx
import cohere
 
logger = logging.getLogger(__name__)
 
 
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
        """Call Gemini embedContent for each text using gemini-embedding-001."""
        embeddings = []
        for text in texts:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
            body = {
                "model": "models/gemini-embedding-001",
                "content": {"parts": [{"text": text}]},
                "taskType": task_type,
                "outputDimensionality": 768
            }
            response = httpx.post(
                url,
                json=body,
                params={"key": self.gemini_api_key},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            embeddings.append(data["embedding"]["values"])
        return embeddings
 
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
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
        """Generate embeddings for multiple texts."""
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