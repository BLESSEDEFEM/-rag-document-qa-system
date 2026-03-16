"""
LLM service for answer generation using Google Gemini.
"""
 
import os
import logging
from typing import List, Dict, Any, AsyncGenerator
from dotenv import load_dotenv
from google import genai
 
load_dotenv()
 
logger = logging.getLogger(__name__)
 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
 
 
class LLMService:
 
    def __init__(self):
        logger.info(f"Initializing LLM service (model: {GEMINI_MODEL})")
 
        if not GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not found - LLM service disabled")
            self.client = None
            return
 
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info(f"LLM service initialized: {GEMINI_MODEL}")
 
    def generate_answer(
            self,
            query: str,
            context_chunks: List[Dict[str, Any]],
            max_chunks: int = 5
    ) -> Dict[str, Any]:
 
        try:
            context_chunks = context_chunks[:max_chunks]
            prompt = self._build_prompt(query, context_chunks)
 
            logger.info(f"Generating answer for query: '{query[:50]}...'")
            logger.info(f"Using {len(context_chunks)} context chunks")
 
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
            answer = response.text
 
            logger.info(f"Answer generated successfully ({len(answer)} characters)")
 
            return {
                "success": True,
                "answer": answer,
                "query": query,
                "chunks_used": len(context_chunks),
                "sources": [
                    {
                        "filename": chunk.get("source", {}).get("filename", "Unknown"),
                        "document_id": chunk.get("source", {}).get("document", 0),
                        "chunk_index": chunk.get("source", {}).get("chunk_index", 0),
                        "relevance_score": chunk.get("score", 0.0)
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
 
    async def generate_answer_stream(
            self,
            query: str,
            context_chunks: List[Dict[str, Any]],
            max_chunks: int = 5
    ) -> AsyncGenerator[str, None]:
 
        try:
            context_chunks = context_chunks[:max_chunks]
            prompt = self._build_prompt(query, context_chunks)
 
            logger.info(f"Streaming answer for query: '{query[:50]}...'")
 
            for chunk in self.client.models.generate_content_stream(
                model=GEMINI_MODEL,
                contents=prompt
            ):
                if chunk.text:
                    yield chunk.text
 
            logger.info("Streaming completed successfully")
 
        except Exception as e:
            logger.error(f"Error streaming answer: {e}")
            yield f"\n\n[Error: {str(e)}]"
 
    def _build_prompt(
            self,
            query: str,
            context_chunks: List[Dict[str, Any]]
    ) -> str:
 
        context_text = ""
        for i, chunk in enumerate(context_chunks, 1):
            source = chunk["source"]
            filename = source.get("filename", "Unknown")
            context_text += f"\n[Source: {filename}]\n"
            context_text += f"{chunk['chunk_text']}\n"
            context_text += f"(Relevance: {chunk['score']:.2f})\n"
 
        prompt = f"""You are a helpful AI assistant answering questions based on provided documents.
 
CONTEXT FROM DOCUMENTS:
{context_text}
 
USER QUESTION: {query}
 
INSTRUCTIONS:
1. Answer the question based ONLY on the information provided in the documents above
2. If the documents don't contain enough information to answer, say so clearly
3. Always cite sources by their actual filename (e.g., "According to corporate_risk_and_data_policy.pdf..." or "Based on internal_ops_notes.txt...")
4. If multiple sources support a point, mention all relevant filenames
5. Be specific and factual
6. Keep the answer concise but complete
 
ANSWER:"""
 
        return prompt
 
 
# Global singleton instance
llm_service = LLMService()