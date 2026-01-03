"""
Database configuration and session management
Uses SQLAlchemy for ORM and connection pooling.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variable
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Set it in .env file for local development or Railway/Vercel for production."
    )

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True, # Verify connections before using
    echo=False # Set to True to see SQL queries (debugging)
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create base class for models
Base = declarative_base()

# Dependency for getting database session
def get_db():
    """
    Dependency that provides database session
    Automatically closes session after request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
