"""
Tests for document management endpoints.
"""
import pytest

def test_list_documents_empty(client):
    """Test listing documents when none exist."""
    response = client.get("/api/documents/list")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_delete_nonexistent_document(client):
    """Test deleting document that doesn't exist."""
    response = client.delete("/api/documents/999")
    
    assert response.status_code == 404

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/documents/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"