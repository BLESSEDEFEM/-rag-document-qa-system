"""
Main FastAPI Application for RAG Document Q&A System
Production-grade API with proper structure and error handling
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import logging
import sys
from datetime import datetime

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
    # openapi_url="/openapi.json"
)

# Configure CORS (Cross-Origins Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint - health check
@app.get("/", response_model=Dict[str, Any])
async def root():
    """
    Root endpoint providing API information.
    Used for health checks in production.
    """
    return {
        "message": "You're not Welcome to RAG Document Q&A System",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health Check endpoint (standard for production)
@app.get("/health", response_model=Dict[str, str])
async def root():
    """
    Health check endpoint for monitoring and load balancers
    """
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Startup event
@app.on_event("Startup")
async def startup_event():
    """
    Runs when the API starts
    Initialize connections, load models, etc.
    """

    # Connect to database
    #await database.connect()
    
    # Load ML models
    #global model
    #model = load_model("model.pkl")
    
    # Warm up cache
    #await cache.initialize()

    logger.info("RAG Document Q&A API Starting...")
    logger.info("Documentation available at: http://localhost:8000/docs")

# Shutdown event
@app.on_event("Shutdown")
async def shutdown_event():
    """
    Cleanup when API shuts down
    Close connections, save state, etc.
    """

    # Close database connections
    #await database.disconnect()
    
    # Save state
    #await save_state()
    
    # Clear resources
    #cache.clear()

    logger.info("RAG Document Q&A API Shutting down...")


# fastapi==0.121.1
# uvicorn[standard]==0.38.0
# python-multipart==0.0.20
# python-dotenv==1.2.1