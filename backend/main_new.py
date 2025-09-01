"""
FastAPI application entry point.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import logging.config

from app import api_router, settings, setup_logging
from app.core import ChatAssistantException
from app.utils import (
    chat_assistant_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Setup logging
    setup_logging(level="INFO" if not settings.debug else "DEBUG")
    logger = logging.getLogger("app.main")

    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add exception handlers
    app.add_exception_handler(ChatAssistantException, chat_assistant_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Include API routes
    app.include_router(api_router)

    logger.info(f"{settings.app_name} v{settings.app_version} initialized")
    return app


# Create app instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
