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
