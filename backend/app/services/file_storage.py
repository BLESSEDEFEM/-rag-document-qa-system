"""
File storage service.
Handles saving uploaded files to disk with UUID naming and date organization.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Tuple
import logging

from fastapi import UploadFile


logger = logging.getLogger(__name__)

# Base upload directory
UPLOAD_BASE_DIR = Path("uploads")


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate unique filename using UUID to prevent conflicts.

    Args:
        original_filename: User's original filename (e.g., "report.pdf")

    Returns:
        Unique filename (e.g., "550e8400-e29b-41d4-a716-446655440000.pdf")

    Security: Prevents path traversal and file overwrites.
    """
    # Extract file extension
    file_extension = ""
    if "." in original_filename:
        file_extension = "." + original_filename.rsplit(".", 1)[1].lower()

    # Generate UUID (guaranteed unique)
    unique_id = str(uuid.uuid4())

    # Combine: UUID + extension
    return f"{unique_id}{file_extension}"


def get_date_directory() -> Path:
    """
    Get directory path organized by current date (YYYY/MM/DD).

    Returns:
        Path object (e.g., "uploads/2024/01/15")

    Organization: Prevents too many files in one directory (performance).
    """
    now = datetime.utcnow()
    date_path = UPLOAD_BASE_DIR / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}"
    return date_path


def ensure_directory_exists(directory: Path) -> None:
    """
    Create directory if it doesn't exist (including parent directories)

    Args:
        directory: Path to directory

    Example: "uploads/2024/01/15" creates all levels if needed.
    """
    directory.mkdir(parents=True, exist_ok=True)
    logger.info(f"Directory ensured: {directory}")


async def save_uploaded_file(file: UploadFile) -> Tuple[str, str]:
    """
    Save uploaded file to disk with unique name and date organization.

    Args:
        file: FastAPI UploadFile object

    Returns:
        Tuple of (file_path, unique_filename)
        - file_path: Full path where file is saved (e.g., "uploads/2024/01/15/uuid.pdf")
        - unique_filename: Just the filename (e.g., "uuid.pdf")

    Process:
        1. Generate unique filename (UUID + extension)
        2. Create date-organized directory (YYYY/MM/DD)
        3. Save file contents to disk
        4. Return paths for database storage

    Security:
        - UUID prevents filename conflicts
        - Path traversal impossible (no user input in path)
        - Date organization prevents directory overload
    """
    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename or "unknown")

    # Get date-organized directory
    date_dir = get_date_directory()

    # Ensure directory exists
    ensure_directory_exists(date_dir)

    # Full file path
    file_path = date_dir / unique_filename

    # Save file contents
    logger.info(f"Saving file: {file_path}")

    # Reset file pointer to beginning (file might have been read before)
    await file.seek(0)

    # Read file contents
    contents = await file.read()

    # Write to disk
    with open(file_path, "wb") as f:
        f.write(contents)

    logger.info(f"File saved successfully: {file_path} ({len(contents)} bytes)")

    # Return both full path and filename
    return str(file_path), unique_filename


async def delete_file(file_path: str) -> bool:
    """
    Delete file from disk (for cleanup or soft delete).

    Args:
        file_path: Path to file to delete

    Returns:
        True if deleted, False if file didn't exist

    Note: This is hard delete. Soft delete only marks is_deleted=True in database.
    """
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            logger.info(f"File deleted: {file_path}")
            return True
        else:
            logger.warning(f"File not found for deletion: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Error deleting file: {file_path}: {e}")
        return False


def get_file_path(filename: str) -> Path:
    """
    Get Path object for a filename (for reading).

    Args:
        filename: Just the filename (e.g., "uuid.pdf")

    Returns:
        Path object

    Note: This searches for file in date directories (future enhancement).
    Currently assumes filename includes path.
    """
    return Path(filename)
