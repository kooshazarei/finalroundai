"""
Prompt management utilities for loading and managing prompts.
"""

import os
from typing import Dict, Optional
from .system_prompts import (
    DEFAULT_SYSTEM_PROMPT,
    CREATIVE_ASSISTANT_PROMPT,
    TECHNICAL_ASSISTANT_PROMPT,
    CLARIFICATION_PROMPT,
    ERROR_HANDLING_PROMPT,
    WELCOME_SYSTEM_PROMPT
)

class PromptManager:
    """Manages prompts for the AI Chat Assistant."""

    def __init__(self):
        self.prompts = {
            "default": DEFAULT_SYSTEM_PROMPT,
            "creative": CREATIVE_ASSISTANT_PROMPT,
            "technical": TECHNICAL_ASSISTANT_PROMPT,
            "clarification": CLARIFICATION_PROMPT,
            "error": ERROR_HANDLING_PROMPT,
            "welcome": WELCOME_SYSTEM_PROMPT
        }

    def get_prompt(self, prompt_type: str = "default") -> str:
        """
        Get a prompt by type.

        Args:
            prompt_type: The type of prompt to retrieve

        Returns:
            The prompt string
        """
        return self.prompts.get(prompt_type, self.prompts["default"])

    def get_available_prompts(self) -> Dict[str, str]:
        """Get all available prompts."""
        return self.prompts.copy()

    def add_custom_prompt(self, name: str, prompt: str) -> None:
        """Add a custom prompt."""
        self.prompts[name] = prompt

    def load_prompt_from_file(self, filepath: str) -> Optional[str]:
        """Load a prompt from a file."""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        except Exception as e:
            print(f"Error loading prompt from {filepath}: {e}")
        return None

# Global prompt manager instance
prompt_manager = PromptManager()
