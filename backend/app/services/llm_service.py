"""
LLM service for answer generation using Google Gemini.
Handles RAG answer generation with retrieved context
"""

import os
import logging
from typing import List, Dict, Any
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

        logger.info(f"LLM service installed: {GEMINI_MODEL}")

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
                        "filename": chunk.get("source", {}).get("filename", "Unknown"),
                        "document_id": chunk.get("source", {}).get("document_id", 0),
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
