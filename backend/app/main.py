"""
Main FastAPI application for RAG Document Q&A System.
Production-grade API with proper structure and error handling.
"""

# Standard library imports
import logging
import sys
from datetime import datetime
from typing import Dict, Any
import os

# Third-party imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

# Local application imports
from app.router import documents

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.middleware.logging_middleware import log_requests


# Configure logging (essential for production)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI with metadata (appears in docs)
app = FastAPI(
    title="RAG Document Q&A API",
    description="Production-grade RAG system for intelligent document analysis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add logging middleware
app.middleware("http")(log_requests)

# CORS Configuration - Specific origins only for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # Production frontend - exact URL only
        "https://rag-document-qa-system.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trust proxy headers (for Railway/production behind reverse proxy)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Rate limiting - protect against abuse
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register routers
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])

# Root endpoint - health check
@app.get("/", response_model=Dict[str, Any])
async def root():
    """
    Root endpoint providing API information.
    Used for health checks in production.
    """
    return {
        "message": "Welcome to RAG Document Q&A API",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check endpoint (standard for production)
@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Health check endpoint with service status.
    """
    from app.services.cache_service import cache_service
    
    logger.info("Health check requested")
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "redis": "connected" if cache_service.is_connected() else "disconnected",
        "environment": "production" if os.getenv("RAILWAY_ENVIRONMENT") else "development"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Runs when the API starts.
    Initialize connections, load models, etc.
    """
    logger.info("RAG Document Q&A API Starting...")
    logger.info("Documentation available at: http://localhost:8000/docs")
    logger.info("Clerk authentication: ENABLED (JWT verification)")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup when API shuts down.
    Close connections, save state, etc.
    """
    logger.info("RAG Document Q&A API Shutting down...")