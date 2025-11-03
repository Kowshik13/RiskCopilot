"""
Risk Copilot API - Main FastAPI Application
Multi-agent LLM system for risk management and compliance
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
from pathlib import Path

from app.config import settings
from app.api import chat, traces, health
from core.faiss_index import FAISSIndex

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global instances
faiss_index = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting Risk Copilot API...")
    
    # Initialize FAISS index
    global faiss_index
    try:
        index_path = Path("data/index")
        index_path.mkdir(parents=True, exist_ok=True)
        
        faiss_index = FAISSIndex(index_path=str(index_path))
        
        # Load existing index or create new one
        if faiss_index.exists():
            faiss_index.load()
            logger.info("✅ Loaded existing FAISS index")
        else:
            logger.info("📝 Creating new FAISS index...")
            # This will be populated in Phase 2
            
        app.state.faiss_index = faiss_index
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize FAISS index: {e}")
    
    logger.info("✅ Risk Copilot API started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Risk Copilot API...")
    # Cleanup resources if needed
    logger.info("👋 Risk Copilot API shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Risk Copilot API",
    description="Multi-agent LLM system for automated risk assessment and compliance",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(traces.router, prefix="/api/v1", tags=["Traces"])

@app.get("/")
async def root():
    """
    Root endpoint - API information
    """
    return {
        "name": "Risk Copilot API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "health": "/api/v1/health",
        "features": [
            "Multi-agent orchestration",
            "RAG-based document retrieval",
            "Guardrails for compliance",
            "Full audit trails",
            "Risk assessment",
            "Citation extraction"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
