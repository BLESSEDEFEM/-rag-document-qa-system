"""
LLM service using Gemini (google-genai SDK).
"""

import os
import logging
from typing import List, Dict, Any, AsyncGenerator
from google import genai

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


class LLMService:

    def __init__(self):
        logger.info(f"Initializing LLM service (model: {GEMINI_MODEL})")

        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY missing")
            self.client = None
            return

        self.client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options={"api_version": "v1"}
        )

        logger.info("LLM service initialized successfully")

    def generate_answer(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        max_chunks: int = 5
    ) -> Dict[str, Any]:

        try:
            context_chunks = context_chunks[:max_chunks]

            prompt = self._build_prompt(query, context_chunks)

            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )

            answer = response.text

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

            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                stream=True
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"\n\n[Error: {str(e)}]"

    def _build_prompt(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]]
    ) -> str:

        context_text = ""
        for i, chunk in enumerate(context_chunks, 1):
            source = chunk["source"]
            context_text += f"\n[Document {i}] {source['filename']}\n"
            context_text += f"{chunk['chunk_text']}\n"
            context_text += f"(Relevance: {chunk['score']:.2f})\n"

        return f"""You are a helpful AI assistant answering questions based on provided documents.

CONTEXT FROM DOCUMENTS:
{context_text}

USER QUESTION: {query}

INSTRUCTIONS:
1. Answer ONLY using the documents
2. If insufficient info, say so clearly
3. Cite document numbers
4. Be concise and factual

ANSWER:"""


llm_service = LLMService()
