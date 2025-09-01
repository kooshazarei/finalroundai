"""
Exception handlers for FastAPI application.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

from ..core import ChatAssistantException, get_logger
from ..models import ErrorResponse

logger = get_logger(__name__)


async def chat_assistant_exception_handler(request: Request, exc: ChatAssistantException):
    """Handle custom chat assistant exceptions."""
    logger.error(f"ChatAssistantException: {exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.message,
            details=exc.details,
            status_code=exc.status_code
        ).dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.error(f"Validation error: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Validation error",
            details={"validation_errors": exc.errors()},
            status_code=422
        ).dict()
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP exception: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            status_code=exc.status_code
        ).dict()
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            details={"exception": str(exc)},
            status_code=500
        ).dict()
    )
