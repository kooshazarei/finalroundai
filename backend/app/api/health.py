"""
Health check and general API endpoints.
"""

from fastapi import APIRouter
from datetime import datetime
import logging

from ..models import HealthResponse
from ..core import settings, get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["health"])


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"{settings.app_name} API is running with LangGraph",
        "version": settings.app_version
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow().isoformat(),
            version=settings.app_version
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow().isoformat(),
            version=settings.app_version
        )
