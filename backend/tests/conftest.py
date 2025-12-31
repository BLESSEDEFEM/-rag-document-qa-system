"""
Test configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock Clerk auth BEFORE importing app
mock_user = {"sub": "test_user_123", "email": "test@example.com"}

# Patch the auth dependency
with patch('app.middleware.auth.get_current_user', return_value=mock_user):
    with patch('app.middleware.auth.get_current_user_optional', return_value=mock_user):
        from app.main import app

@pytest.fixture
def client():
    """Create test client with mocked auth."""
    with patch('app.middleware.auth.get_current_user', return_value=mock_user):
        with patch('app.middleware.auth.get_current_user_optional', return_value=mock_user):
            with TestClient(app) as test_client:
                yield test_client