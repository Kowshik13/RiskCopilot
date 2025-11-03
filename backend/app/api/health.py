"""
Health check endpoint for Risk Copilot API
"""

from fastapi import APIRouter, Depends
from datetime import datetime
import time
import os
from app.models import HealthStatus
from app.config import settings

router = APIRouter()

# Track startup time
STARTUP_TIME = time.time()

@router.get("/health", response_model=HealthStatus)
async def health_check():
    """
    Health check endpoint - returns system status
    """
    uptime = int(time.time() - STARTUP_TIME)
    
    # Check component health
    components = {
        "api": "healthy",
        "faiss_index": "healthy" if os.path.exists(settings.FAISS_INDEX_PATH) else "not_initialized",
        "llm_adapter": "healthy" if settings.USE_MOCK_LLM or settings.OPENAI_API_KEY else "degraded",
        "guardrails": "healthy" if settings.ENABLE_GUARDRAILS else "disabled",
    }
    
    # Determine overall status
    if all(status in ["healthy", "disabled"] for status in components.values()):
        overall_status = "healthy"
    elif any(status == "unhealthy" for status in components.values()):
        overall_status = "unhealthy"
    else:
        overall_status = "degraded"
    
    return HealthStatus(
        status=overall_status,
        version=settings.APP_VERSION,
        uptime_seconds=uptime,
        components=components
    )

@router.get("/ready")
async def readiness_check():
    """
    Readiness check - returns 200 if service is ready to accept requests
    """
    return {"ready": True}

@router.get("/live")
async def liveness_check():
    """
    Liveness check - returns 200 if service is alive
    """
    return {"alive": True}
