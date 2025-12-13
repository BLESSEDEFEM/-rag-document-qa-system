"""
Basic API tests for RAG Document Q&A System.
Tests critical endpoints to ensure core functionality works.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test that health check endpoint returns 200 and expected fields."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "redis" in data


def test_document_list():
    """Test that document list endpoint returns successfully."""
    response = client.get("/api/documents/list")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should return a list (even if empty)
    assert isinstance(data, list)


def test_upload_invalid_file_type():
    """Test that uploading invalid file type is rejected."""
    # Create a fake file with invalid extension
    files = {
        "file": ("test.exe", b"fake content", "application/x-msdownload")
    }
    
    response = client.post("/api/documents/upload", files=files)
    
    # Should reject with 400 or 422 error
    assert response.status_code in [400, 422]


def test_answer_without_query():
    """Test that answer endpoint requires a query."""
    response = client.post(
        "/api/documents/answer",
        json={}
    )
    
    # Should return error for missing query
    assert response.status_code == 422


def test_answer_with_empty_query():
    """Test that answer endpoint rejects empty query."""
    response = client.post(
        "/api/documents/answer",
        json={"query": ""}
    )
    
    # Should return error
    assert response.status_code in [400, 422]