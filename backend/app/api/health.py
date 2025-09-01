"""
Health check and general API endpoints.
"""

from fastapi import APIRouter
from datetime import datetime
import logging
import os

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


@router.get("/tracing-status")
async def tracing_status():
    """Get LangSmith tracing status."""
    langsmith_enabled = os.getenv("LANGCHAIN_TRACING_V2") == "true"
    langsmith_project = os.getenv("LANGCHAIN_PROJECT", "Not set")

    return {
        "langsmith_tracing_enabled": langsmith_enabled,
        "langsmith_project": langsmith_project,
        "langsmith_configured": settings.langsmith_tracing_enabled and bool(settings.langsmith_api_key),
        "project_name": settings.langsmith_project
    }
