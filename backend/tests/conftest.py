"""
Test configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.middleware.auth import get_current_user, get_current_user_optional
from app.database import Base, get_db

# Use in-memory SQLite for tests (NOT production PostgreSQL!)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Mock user for tests
mock_user = {"sub": "test_user_123", "email": "test@example.com"}

# Override FastAPI dependencies
def override_get_current_user():
    return mock_user

def override_get_current_user_optional():
    return mock_user

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply overrides
app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_current_user_optional] = override_get_current_user_optional
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database tables before all tests."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    # Clean up test database file
    if os.path.exists("./test.db"):
        os.remove("./test.db")

# Create test client
client = TestClient(app)

@pytest.fixture
def client():
    """Provide test client with mocked auth and test database."""
    return TestClient(app)