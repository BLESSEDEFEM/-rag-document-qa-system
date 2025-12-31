"""Tests for query/answer endpoints."""
import pytest
from unittest.mock import patch


def test_query_without_documents(client):
    """Test querying when no documents exist."""
    # Mock Cohere embeddings to avoid API rate limits
    with patch('app.services.embedding_service.embedding_service.generate_embeddings') as mock_embed:
        mock_embed.return_value = [[0.1] * 1024]  # Fake 1024-dim embedding
        
        response = client.post(
            "/api/documents/answer",
            json={"query": "What is machine learning?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        # Should return "no relevant information" when no documents exist
        assert "no relevant information" in data["answer"].lower() or data["answer"] == ""


def test_query_empty_string(client):
    """Test query with empty string."""
    response = client.post(
        "/api/documents/answer",
        json={"query": ""}
    )
    
    assert response.status_code == 400


def test_query_too_long(client):
    """Test query exceeding length limit."""
    long_query = "x" * 1001  # Over 1000 char limit
    response = client.post(
        "/api/documents/answer",
        json={"query": long_query}
    )
    
    assert response.status_code == 400


def test_query_with_parameters(client):
    """Test query with custom parameters."""
    # Mock Cohere embeddings
    with patch('app.services.embedding_service.embedding_service.generate_embeddings') as mock_embed:
        mock_embed.return_value = [[0.1] * 1024]
        
        response = client.post(
            "/api/documents/answer",
            json={
                "query": "Test question",
                "top_k": 3,
                "min_score": 0.5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data


def test_query_with_document_filter(client):
    """Test query filtered by document ID."""
    # Mock Cohere embeddings
    with patch('app.services.embedding_service.embedding_service.generate_embeddings') as mock_embed:
        mock_embed.return_value = [[0.1] * 1024]
        
        response = client.post(
            "/api/documents/answer",
            json={
                "query": "Test question",
                "document_id": 999  # Non-existent ID
            }
        )
        
        # Should still work, just return no results
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data