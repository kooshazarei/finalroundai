"""
Health check endpoints - Simplified.
"""

from fastapi import APIRouter
from datetime import datetime

from ..core import settings

router = APIRouter(tags=["health"])


@router.get("/")
async def root():
    """Root endpoint."""
    return {"message": f"{settings.app_name} API is running"}


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
