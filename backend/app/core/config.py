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

    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()
