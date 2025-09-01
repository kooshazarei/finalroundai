"""
Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class ChatMessage(BaseModel):
    """Chat message request model."""

    message: str = Field(..., min_length=1, max_length=10000, description="The user's message")
    prompt_type: str = Field(default="default", description="Type of prompt to use")


class ChatResponse(BaseModel):
    """Chat response model."""

    response: str = Field(..., description="The AI's response")
    status: Literal["success", "error"] = Field(default="success", description="Response status")
    prompt_type: str = Field(default="default", description="Prompt type used")


class HealthResponse(BaseModel):
    """Health check response model."""

    status: Literal["healthy", "unhealthy"] = Field(..., description="Service health status")
    timestamp: str = Field(..., description="Response timestamp")
    version: str = Field(..., description="Application version")


class PromptsResponse(BaseModel):
    """Available prompts response model."""

    prompts: List[str] = Field(..., description="List of available prompt types")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    status_code: int = Field(..., description="HTTP status code")
