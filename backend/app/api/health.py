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
    """
Health check endpoints with performance monitoring.
"""

from typing import Dict, Any
from fastapi import APIRouter
from ..core.config import settings
from ..services.circuit_breaker import openai_circuit_breaker
from ..services.latency_optimizer import default_latency_optimizer

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version
    }


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with performance metrics."""
    circuit_breaker_state = openai_circuit_breaker.get_state()
    performance_stats = default_latency_optimizer.get_performance_stats()

    # Determine overall health
    is_healthy = (
        circuit_breaker_state["state"] != "open" and
        performance_stats.get("performance_grade", "D") in ["A", "B", "C"]
    )

    return {
        "status": "healthy" if is_healthy else "degraded",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "timestamp": import_time.time(),
        "circuit_breaker": circuit_breaker_state,
        "performance": performance_stats,
        "configuration": {
            "max_retries": settings.openai_max_retries,
            "timeout": settings.openai_timeout,
            "max_response_time": settings.max_response_time,
            "circuit_breaker_threshold": settings.circuit_breaker_failure_threshold
        }
    }


# Add import for time
import time as import_time
