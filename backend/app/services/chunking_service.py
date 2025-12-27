"""
Text chunking service for RAG
Splits documents into optimal chunks for embedding and retrieval
"""

import logging
from typing import List

logger = logging.getLogger(__name__)

# Chunking configuartion
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100


def chunk_text(
        text: str,
        chunk_size: int = CHUNK_SIZE,
        overlap: int = CHUNK_OVERLAP
) -> List[str]:
    """
    Split text into overlapping chunks.

    Uses character-based chunking with sentence boundary detection.
    Ensures context continuity through overlap between chunks.

    Args:
        text: Text to chunk
        chunk_size: Target size of each chunk (characters)
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks

    Example:
        >>> text = "This is a long document with multiple sentences. " * 20
        >>> chunks = chunk_text(text, chunk_size=100, overlap=20)
        >>> len(chunks)
        10
        >>> chunks[0][:20]
        'This is a long docum'

    Algorithm:
        1. Validate input (empty text returns empty list)
        2. If text smaller than chunk_size, return as single chunk
        3. Otherwise, split into chunks:
           - Move forward by chunk_size each time
           - Try to break at sentence boundaries (. ! ? or newline)
           - Apply overlap for context continuity
           - Continue until end of text
    """
    # Validate input
    if not text or len(text) == 0:
        logger.warning("Empty text provided for chunking")
        return []

    # Clean text
    text = text.strip()

    # if text is smaller than chunk size, return as single chunk
    if len(text) <= chunk_size:
        logger.debug(f"Text ({len(text)} chars) smaller than chunk size ({chunk_size}), returning single chunk")
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        # Calculate end position
        end = start + chunk_size

        # if this is not the last chunk, try to break at sentence boundary
        if end < len(text):
            # Look for sentence ending (. ! ? newline) within next 100 chars
            search_end = min(end + 100, len(text))

            # Find all possible sentence boundaries
            sentence_ends = [
                text.rfind('.', end, search_end),
                text.rfind('! ', end, search_end),
                text.rfind('? ', end, search_end),
                text.rfind('\n', end, search_end)
            ]

            # Use the nearest sentence boundary if found
            best_break = max(sentence_ends)
            if best_break > end:
                end = best_break + 1  # Include the punctuation

        # Extract chunk
        chunk = text[start:end].strip()

        # Only add non-empty chunks
        if chunk:
            chunks.append(chunk)

        # Move start position (with overlap)
        start = end - overlap

        # Prevent infinite loop on very small overlaps
        if start <= 0 or start >= len(text):
            break

    logger.info(f"Chunked text ({len(text)} chars) into {len(chunks)} chunks (size={chunk_size}, overlap={overlap})")

    return chunks
