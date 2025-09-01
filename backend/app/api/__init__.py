"""
API router configuration.
"""

from fastapi import APIRouter
from .health import router as health_router
from .chat import router as chat_router

# Main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health_router)
api_router.include_router(chat_router)

__all__ = ["api_router"]
