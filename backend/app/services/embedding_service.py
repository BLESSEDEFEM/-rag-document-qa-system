"""
Embedding service with Gemini primary, Cohere fallback.
"""
import os
import logging
from typing import List
import cohere
import google.generativeai as genai

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        # Gemini (Primary - 15,000 free/month)
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            logger.info("Gemini embedding service initialized")
        
        # Cohere (Fallback - 100 free/month)
        self.cohere_api_key = os.getenv("COHERE_API_KEY")
        if self.cohere_api_key:
            self.cohere_client = cohere.ClientV2(api_key=self.cohere_api_key)
            logger.info("Cohere embedding service initialized")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding - Try Gemini first, fallback to Cohere."""
        if not text or len(text.strip()) == 0:
            logger.error("Empty text provided for embedding")
            return None
        
        text = text.strip()
        
        # Try Gemini first
        if self.gemini_api_key:
            try:
                result = genai.embed_content(
                    model="text-embedding-004",
                    content=text,
                    task_type="retrieval_query"
                )
                logger.info("Gemini embedding generated successfully")
                return result['embedding']
            except Exception as e:
                logger.warning(f"Gemini embedding failed: {e}, trying Cohere fallback...")
        
        # Fallback to Cohere
        if self.cohere_api_key:
            try:
                response = self.cohere_client.embed(
                    texts=[text],
                    model="embed-english-v3.0",
                    input_type="search_query",
                    embedding_types=["float"]
                )
                embedding = response.embeddings.float_[0]
                logger.info("Cohere embedding generated successfully (fallback)")
                return embedding
            except Exception as e:
                logger.error(f"Cohere embedding also failed: {e}")
                return None
        
        logger.error("No embedding service available")
        return None
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts - Gemini first, Cohere fallback."""
        if not texts:
            logger.error("Empty texts list provided")
            return None
        
        texts = [t.strip() for t in texts if t and len(t.strip()) > 0]
        
        if not texts:
            logger.error("All texts were empty after stripping")
            return None
        
        # Try Gemini first
        if self.gemini_api_key:
            try:
                result = genai.embed_content(
                    model="text-embedding-004",
                    content=texts,
                    task_type="retrieval_document"
                )
                logger.info(f"Gemini batch embeddings: {len(texts)} texts")
                return result['embedding']
            except Exception as e:
                logger.warning(f"Gemini failed: {e}, trying Cohere...")
        
        # Fallback to Cohere
        if self.cohere_api_key:
            try:
                response = self.cohere_client.embed(
                    texts=texts,
                    model="embed-english-v3.0",
                    input_type="search_document",
                    embedding_types=["float"]
                )
                logger.info(f"Cohere batch embeddings: {len(texts)} texts")
                return response.embeddings.float_
            except Exception as e:
                logger.error(f"Both embedding services failed: {e}")
                return None
        
        logger.error("No embedding service available")
        return None

# Global instance
embedding_service = EmbeddingService()