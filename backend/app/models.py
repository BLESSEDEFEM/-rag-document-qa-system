"""
Database models for RAG Document Q&A System.
Defines table schemas using SQLAlchemy ORM.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.database import Base


class Document(Base):
    """
    Document metadata table.
    Stores information about uploaded documents.
    """
    __tablename__ = "documents"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # File information
    user_id = Column(String, index=True, nullable=False)  # Clerk user ID
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False, unique=True)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)

    # Content
    extracted_text = Column(Text, nullable=True)
    page_count = Column(Integer, nullable=True)
    chunks = Column(JSON, nullable=True, comment="Text chunks for embedding")
    embeddings = Column(JSON, nullable=True, comment="Vector embeddings (temporary storage)")
    chunk_count = Column(Integer, nullable=True, comment="Number of chunks generated")
    embedding_model = Column(String(100), nullable=True, default="all-mpnet-base-v2")
    embedding_dimension = Column(Integer, nullable=True, default=768)
    embedding_date = Column(DateTime(timezone=True), nullable=True)

    # Processing status
    # Possible values:
    # - "pending_processing": Uploaded, awaiting text extraction
    # - "extracting": Text extraction in progress
    # - "extracted": Text extracted successfully
    # - "embedding": Generating embeddings
    # - "ready": Fully processed and searchable
    # - "failed": Processing failed (check logs)
    status = Column(
        String(50),
        nullable=False,
        default="pending_processing",
        index=True
    )

    # Metadata
    upload_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_date = Column(DateTime(timezone=True), nullable=True)

    # Flags
    is_deleted = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        """String representation for debugging."""
        return f"<Document(id={self.id}, filename='{self.filename}', status='{self.status}')>"
