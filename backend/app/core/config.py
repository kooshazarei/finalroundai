"""
Application configuration settings.
"""

import os
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    """Application settings."""

    # API Settings
    app_name: str = "AI Chat Assistant"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS Settings
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://frontend:3000"
    ]

    # OpenAI Error Handling Settings
    openai_max_retries: int = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
    openai_initial_delay: float = float(os.getenv("OPENAI_INITIAL_DELAY", "1.0"))
    openai_max_delay: float = float(os.getenv("OPENAI_MAX_DELAY", "60.0"))
    openai_timeout: float = float(os.getenv("OPENAI_TIMEOUT", "30.0"))

    # Circuit Breaker Settings
    circuit_breaker_failure_threshold: int = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5"))
    circuit_breaker_recovery_timeout: float = float(os.getenv("CIRCUIT_BREAKER_RECOVERY_TIMEOUT", "60.0"))

    # Latency Optimization Settings
    stream_timeout: float = float(os.getenv("STREAM_TIMEOUT", "5.0"))
    max_response_time: float = float(os.getenv("MAX_RESPONSE_TIME", "45.0"))

    # Langfuse Settings (from environment variables)
    langfuse_public_key: str = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    langfuse_secret_key: str = os.getenv("LANGFUSE_SECRET_KEY", "")
    langfuse_host: str = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()
