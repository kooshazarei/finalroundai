"""
Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional


class ChatMessage(BaseModel):
    """Chat message request model."""

    message: str = Field(..., min_length=1, max_length=10000, description="The user's message")
    prompt_type: str = Field(default="gpt-3.5-turbo", description="Model name to use (e.g., gpt-3.5-turbo, gpt-4)")
    thread_id: Optional[str] = Field(None, description="Thread ID for conversation context")
    user_id: Optional[str] = Field(None, description="User ID for personalization")


class ChatResponse(BaseModel):
    """Chat response model."""

    response: str = Field(..., description="The AI's response")
    status: Literal["success", "error"] = Field(default="success", description="Response status")
    prompt_type: str = Field(default="gpt-3.5-turbo", description="Model name used")
    thread_id: Optional[str] = Field(None, description="Thread ID used for conversation")
    user_id: Optional[str] = Field(None, description="User ID used for personalization")


class HealthResponse(BaseModel):
    """Health check response model."""

    status: Literal["healthy", "unhealthy"] = Field(..., description="Service health status")
    timestamp: str = Field(..., description="Response timestamp")
    version: str = Field(..., description="Application version")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    status_code: int = Field(..., description="HTTP status code")
