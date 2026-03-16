"""
Health check endpoints for monitoring.
Public endpoint (no auth required) for external uptime monitoring.
"""
 
import logging
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
 
from app.database import get_db
from app.services.embedding_service import embedding_service
from app.services.pinecone_service import pinecone_service
from app.services.cache_service import cache_service
 
logger = logging.getLogger(__name__)
 
router = APIRouter(tags=["health"])
 
 
@router.get("/health")
async def basic_health():
    """Basic health check - just confirms the server is running."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
 
 
@router.get("/health/detailed")
async def detailed_health(db: Session = Depends(get_db)):
    """
    Detailed health check - tests all critical services.
    No authentication required so external monitors can ping it.
    """
    checks = {
        "server": True,
        "database": False,
        "pinecone": False,
        "embedding_service": False,
        "redis": False
    }
    errors = {}
 
    # Database check
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        errors["database"] = str(e)
        logger.error(f"Health check - database failed: {e}")
 
    # Pinecone check
    try:
        stats = pinecone_service.index.describe_index_stats()
        checks["pinecone"] = True
    except Exception as e:
        errors["pinecone"] = str(e)
        logger.error(f"Health check - pinecone failed: {e}")
 
    # Embedding service check
    try:
        test_embedding = embedding_service.generate_embedding("health check test")
        if test_embedding and len(test_embedding) == 768:
            checks["embedding_service"] = True
        else:
            errors["embedding_service"] = f"Unexpected dimension: {len(test_embedding) if test_embedding else 'None'}"
    except Exception as e:
        errors["embedding_service"] = str(e)
        logger.error(f"Health check - embedding failed: {e}")
 
    # Redis check
    try:
        if cache_service.is_connected():
            checks["redis"] = True
        else:
            errors["redis"] = "Cache service not connected"
    except Exception as e:
        errors["redis"] = str(e)
 
    all_healthy = all(checks.values())
 
    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": checks,
        "errors": errors if errors else None,
        "all_healthy": all_healthy
    }