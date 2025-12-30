"""
Tests for document upload functionality.
"""
import io
import pytest
from fastapi import UploadFile

def test_upload_valid_pdf(client):
    """Test uploading a valid PDF file."""
    # Create fake PDF content
    pdf_content = b"%PDF-1.4\nTest PDF content"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    
    response = client.post("/api/documents/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert data["filename"] == "test.pdf"
    assert data["file_type"] == "pdf"

def test_upload_valid_txt(client):
    """Test uploading a valid TXT file."""
    txt_content = b"This is test text content for the RAG system."
    files = {"file": ("test.txt", io.BytesIO(txt_content), "text/plain")}
    
    response = client.post("/api/documents/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["file_type"] == "txt"
    assert data["character_count"] > 0

def test_upload_invalid_file_type(client):
    """Test uploading invalid file type."""
    exe_content = b"MZ\x90\x00"  # Fake EXE header
    files = {"file": ("virus.exe", io.BytesIO(exe_content), "application/x-msdownload")}
    
    response = client.post("/api/documents/upload", files=files)
    
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

def test_upload_file_too_large(client):
    """Test uploading file exceeding size limit."""
    # Create 11MB file (over 10MB limit)
    large_content = b"x" * (11 * 1024 * 1024)
    files = {"file": ("large.txt", io.BytesIO(large_content), "text/plain")}
    
    response = client.post("/api/documents/upload", files=files)
    
    assert response.status_code == 400
    assert "too large" in response.json()["detail"]

def test_upload_empty_file(client):
    """Test uploading empty file."""
    files = {"file": ("empty.txt", io.BytesIO(b""), "text/plain")}
    
    response = client.post("/api/documents/upload", files=files)
    
    # Should still succeed but with 0 characters
    assert response.status_code == 200