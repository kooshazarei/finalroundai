"""
Prompts package for AI Chat Assistant.
"""

from .prompt_manager import prompt_manager, PromptManager
from .system_prompts import (
    DEFAULT_SYSTEM_PROMPT,
    CREATIVE_ASSISTANT_PROMPT,
    TECHNICAL_ASSISTANT_PROMPT,
    CLARIFICATION_PROMPT,
    ERROR_HANDLING_PROMPT
)

__all__ = [
    "prompt_manager",
    "PromptManager",
    "DEFAULT_SYSTEM_PROMPT",
    "CREATIVE_ASSISTANT_PROMPT",
    "TECHNICAL_ASSISTANT_PROMPT",
    "CLARIFICATION_PROMPT",
    "ERROR_HANDLING_PROMPT"
]
