"""
Custom exceptions for the application.
"""

from typing import Any, Dict, Optional


class ChatAssistantException(Exception):
    """Base exception for chat assistant errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class OpenAIConfigurationError(ChatAssistantException):
    """Raised when OpenAI configuration is invalid."""

    def __init__(self, message: str = "OpenAI API key not configured"):
        super().__init__(message, status_code=500)


class ChatProcessingError(ChatAssistantException):
    """Raised when chat processing fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Chat processing error: {message}", status_code=500, details=details)


class StreamingError(ChatAssistantException):
    """Raised when streaming fails."""

    def __init__(self, message: str):
        super().__init__(f"Streaming error: {message}", status_code=500)
