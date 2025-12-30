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

# Local application imports
from app.router import documents


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
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://rag-document-qa-system.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "message": "You're not Welcome to RAG Document Q&A API",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check endpoint (standard for production)
@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Health check endpoint with Redis and Auth status.
    """
    from app.services.cache_service import cache_service
    from app.middleware.auth import clerk_auth
    
    logger.info("Health check requested")
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "redis": "connected" if cache_service.is_connected() else "disconnected",
        "auth": "enabled" if clerk_auth.enabled else "disabled",
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
    
    # Log authentication status
    from app.middleware.auth import clerk_auth
    if clerk_auth.enabled:
        logger.info("Clerk authentication is ENABLED")
    else:
        logger.warning("Clerk authentication is DISABLED - check environment variables")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup when API shuts down.
    Close connections, save state, etc.
    """
    logger.info("RAG Document Q&A API Shutting down...")