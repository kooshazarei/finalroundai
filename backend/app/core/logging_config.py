"""
Logging configuration.
"""

import logging
import logging.config
import sys
import json
from datetime import datetime
from typing import Dict, Any


def setup_logging(level: str = "INFO") -> None:
    """Setup application logging."""

    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "agent": {
                "format": "%(asctime)s - [AGENT] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "default",
                "stream": sys.stdout,
            },
            "agent_console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "agent",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "app": {
                "level": level,
                "handlers": ["console"],
                "propagate": False,
            },
            "app.agents": {
                "level": "INFO",
                "handlers": ["agent_console"],
                "propagate": False,
            },
        },
        "root": {
            "level": level,
            "handlers": ["console"],
        },
    }

    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(f"app.{name}")


def get_agent_logger() -> logging.Logger:
    """Get a specialized logger for agent interactions."""
    return logging.getLogger("app.agents")


def log_agent_interaction(
    logger: logging.Logger,
    agent_name: str,
    thread_id: str,
    interaction_type: str,
    message: str,
    extra_data: Dict[str, Any] = None
) -> None:
    """Log agent interactions with structured format."""
    timestamp = datetime.now().isoformat()

    log_entry = {
        "timestamp": timestamp,
        "agent": agent_name,
        "thread_id": thread_id,
        "type": interaction_type,
        "message": message,
    }

    if extra_data:
        log_entry["data"] = extra_data

    # Log as structured JSON for agents (this goes to logs)
    logger.info(json.dumps(log_entry, indent=2))

    # Simplified console output - skip streaming chunks and other verbose types
    if interaction_type in ["STREAMING_CHUNK"]:
        return

    # Also print to console for visibility (simplified format)
    print(f"🤖 [{agent_name}] {interaction_type}: {message}")
    if extra_data and interaction_type not in ["PROCESSING_COMPLETE"]:
        for key, value in extra_data.items():
            if key in ["response_preview", "current_chunk"]:  # Skip verbose data
                continue
            if isinstance(value, str) and len(value) > 100:
                print(f"   {key}: {value[:100]}...")
            else:
                print(f"   {key}: {value}")
    print("-" * 50)
