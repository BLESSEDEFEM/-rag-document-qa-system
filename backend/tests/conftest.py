"""
Test configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.middleware.auth import get_current_user, get_current_user_optional

# Mock user for tests
mock_user = {"sub": "test_user_123", "email": "test@example.com"}

# Override FastAPI dependencies
def override_get_current_user():
    return mock_user

def override_get_current_user_optional():
    return mock_user

# Apply overrides
app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_current_user_optional] = override_get_current_user_optional

# Create test client
client = TestClient(app)

@pytest.fixture
def client():
    """Provide test client with mocked auth."""
    return TestClient(app)