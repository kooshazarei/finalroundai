"""
Graph service for managing LangGraph instances.
"""

import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from ..graph import create_chat_graph
from ..core import get_logger

logger = get_logger(__name__)


class GraphService:
    """Service for managing and executing LangGraph instances."""

    def __init__(self):
        """Initialize the graph service."""
        self._graphs = {}

    def _get_api_key_for_model(self, model_name: str) -> str:
        """Get API key for the specified model."""
        if "openai" in model_name.lower() or "gpt" in model_name.lower():
            return os.getenv("OPENAI_API_KEY", "")
        elif "claude" in model_name.lower() or "anthropic" in model_name.lower():
            return os.getenv("ANTHROPIC_API_KEY", "")
        else:
            # Default to OpenAI for unknown models
            return os.getenv("OPENAI_API_KEY", "")

    def _create_llm_model(self, model_name: str, temperature: float = 0.7):
        """Create an LLM model instance."""
        api_key = self._get_api_key_for_model(model_name)
        if not api_key:
            raise ValueError(f"No API key found for model: {model_name}")

        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )

    def get_chat_graph(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Get or create a chat graph for the specified model.

        Args:
            model_name: Name of the model to use
            temperature: Temperature for response generation

        Returns:
            ChatGraph instance
        """
        graph_key = f"{model_name}_{temperature}"

        if graph_key not in self._graphs:
            logger.info(f"Creating new chat graph for {model_name}")
            llm_model = self._create_llm_model(model_name, temperature)
            self._graphs[graph_key] = create_chat_graph(llm_model)

        return self._graphs[graph_key]

    async def process_chat_message(
        self,
        message: str,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Process a chat message using the appropriate graph.

        Args:
            message: User's message
            model_name: Name of the model to use
            temperature: Temperature for response generation
            session_id: Optional session identifier

        Returns:
            Dict containing the response and metadata
        """
        try:
            graph = self.get_chat_graph(model_name, temperature)
            result = await graph.ainvoke(message, session_id)

            logger.info(f"Processed message using {model_name} graph")
            return result

        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            raise


# Global service instance
_graph_service = None


def get_graph_service() -> GraphService:
    """Get the global graph service instance."""
    global _graph_service
    if _graph_service is None:
        _graph_service = GraphService()
    return _graph_service
