"""
Tests for query and answer functionality.
"""
import pytest

def test_query_without_documents(client):
    """Test querying when no documents exist."""
    response = client.post(
        "/api/documents/answer",
        json={"query": "What is machine learning?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    # Should return "no relevant information" message

def test_query_empty_string(client):
    """Test query with empty string."""
    response = client.post(
        "/api/documents/answer",
        json={"query": ""}
    )
    
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

def test_query_too_long(client):
    """Test query exceeding length limit."""
    long_query = "x" * 1001  # Over 1000 char limit
    response = client.post(
        "/api/documents/answer",
        json={"query": long_query}
    )
    
    assert response.status_code == 400
    assert "too long" in response.json()["detail"].lower()

def test_query_with_parameters(client):
    """Test query with custom parameters."""
    response = client.post(
        "/api/documents/answer",
        json={
            "query": "Test question",
            "top_k": 3,
            "min_score": 0.5
        }
    )
    
    assert response.status_code == 200

def test_query_with_document_filter(client):
    """Test query filtered by document ID."""
    response = client.post(
        "/api/documents/answer",
        json={
            "query": "Test question",
            "document_id": 999  # Non-existent ID
        }
    )
    
    # Should still work, just return no results
    assert response.status_code == 200