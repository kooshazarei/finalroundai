"""
OpenAI service for LLM interactions.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from typing import List, AsyncGenerator
import logging
import json

from ..core import settings, OpenAIConfigurationError, get_logger

logger = get_logger(__name__)


class OpenAIService:
    """Service for OpenAI LLM interactions."""

    def __init__(self):
        self._chat_model = None

    @property
    def chat_model(self) -> ChatOpenAI:
        """Get or create ChatOpenAI instance."""
        if self._chat_model is None:
            if not settings.openai_api_key:
                raise OpenAIConfigurationError()

            self._chat_model = ChatOpenAI(
                model=settings.openai_model,
                openai_api_key=settings.openai_api_key,
                temperature=settings.openai_temperature,
                streaming=True
            )
            logger.info(f"Initialized OpenAI model: {settings.openai_model}")

        return self._chat_model

    def generate_response(self, messages: List[BaseMessage]) -> str:
        """Generate response from OpenAI."""
        try:
            logger.debug(f"Generating response for {len(messages)} messages")
            response = self.chat_model.invoke(messages)
            logger.debug("Response generated successfully")
            return response.content
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            raise

    async def stream_response(self, messages: List[BaseMessage]) -> AsyncGenerator[str, None]:
        """Stream response from OpenAI in SSE format."""
        try:
            logger.debug(f"Starting stream for {len(messages)} messages")

            async for chunk in self.chat_model.astream(messages):
                if hasattr(chunk, 'content') and chunk.content:
                    data = {"content": chunk.content, "done": False}
                    yield f"data: {json.dumps(data)}\n\n"

            # Send completion signal
            data = {"content": "", "done": True}
            yield f"data: {json.dumps(data)}\n\n"

            logger.debug("Stream completed successfully")

        except Exception as e:
            logger.error(f"Error streaming OpenAI response: {e}")
            # Send error completion
            error_data = {"content": "", "done": True, "error": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"


# Global service instance
openai_service = OpenAIService()
