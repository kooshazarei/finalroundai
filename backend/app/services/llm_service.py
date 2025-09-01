"""
LLM service for interfacing with language models.
"""

import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from ..core import get_logger

logger = get_logger(__name__)


class LLMService:
    """Service for generating responses using language models."""

    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Initialize the LLM service.

        Args:
            model_name: Name of the model to use
            temperature: Temperature for response generation
        """
        self.model_name = model_name
        self.temperature = temperature
        self._model = None

    def _get_api_key_for_model(self, model_name: str) -> str:
        """Get API key for the specified model."""
        if "openai" in model_name.lower() or "gpt" in model_name.lower():
            return os.getenv("OPENAI_API_KEY", "")
        elif "claude" in model_name.lower() or "anthropic" in model_name.lower():
            return os.getenv("ANTHROPIC_API_KEY", "")
        else:
            # Default to OpenAI for unknown models
            return os.getenv("OPENAI_API_KEY", "")

    def _get_model(self):
        """Get or create the model instance."""
        if self._model is None:
            api_key = self._get_api_key_for_model(self.model_name)
            if not api_key:
                raise ValueError(f"No API key found for model: {self.model_name}")

            self._model = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                api_key=api_key
            )
        return self._model

    async def generate_response(self, user_message: str, system_prompt: str = None) -> str:
        """
        Generate a response for the given user message.

        Args:
            user_message: The user's input message
            system_prompt: Optional system prompt to guide the response

        Returns:
            Generated response string
        """
        try:
            model = self._get_model()

            # Create messages
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            else:
                messages.append(SystemMessage(content="You are a helpful AI assistant."))

            messages.append(HumanMessage(content=user_message))

            # Generate response
            response = await model.ainvoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def generate_response(self, user_message: str, system_prompt: str = None) -> str:
        """
        Synchronous version of generate_response.

        Args:
            user_message: The user's input message
            system_prompt: Optional system prompt to guide the response

        Returns:
            Generated response string
        """
        try:
            model = self._get_model()

            # Create messages
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            else:
                messages.append(SystemMessage(content="You are a helpful AI assistant."))

            messages.append(HumanMessage(content=user_message))

            # Generate response
            response = model.invoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise


def create_llm_service(model_name: str = "gpt-3.5-turbo", temperature: float = 0.7) -> LLMService:
    """
    Factory function to create an LLM service instance.

    Args:
        model_name: Name of the model to use
        temperature: Temperature for response generation

    Returns:
        Configured LLMService instance
    """
    return LLMService(model_name, temperature)
