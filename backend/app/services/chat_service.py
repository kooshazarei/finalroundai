"""
Chat workflow service using LangGraph.
"""

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import List, AsyncGenerator
import logging

from ..models import ChatState
from ..core import ChatProcessingError, get_logger
from .openai_service import openai_service

# Import prompt manager from the moved location
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from prompts import prompt_manager

logger = get_logger(__name__)


class ChatWorkflowService:
    """Service for managing chat workflows using LangGraph."""

    def __init__(self):
        self._workflow = None

    @property
    def workflow(self):
        """Get or create the chat workflow."""
        if self._workflow is None:
            self._workflow = self._create_workflow()
            logger.info("Chat workflow initialized")
        return self._workflow

    def _create_workflow(self):
        """Create the LangGraph workflow."""
        workflow = StateGraph(ChatState)

        # Add nodes
        workflow.add_node("prepare_conversation", self._prepare_conversation)
        workflow.add_node("generate_response", self._generate_response)

        # Add edges
        workflow.set_entry_point("prepare_conversation")
        workflow.add_edge("prepare_conversation", "generate_response")
        workflow.add_edge("generate_response", END)

        return workflow.compile()

    def _prepare_conversation(self, state: ChatState) -> ChatState:
        """Prepare the conversation with system prompt."""
        try:
            prompt_type = state.get("current_prompt_type", "default")
            system_prompt = prompt_manager.get_prompt(prompt_type)

            messages = state["messages"]

            # Add system message if not already present
            if not messages or not isinstance(messages[0], SystemMessage):
                messages = [SystemMessage(content=system_prompt)] + messages

            logger.debug(f"Prepared conversation with prompt type: {prompt_type}")
            return {
                "messages": messages,
                "current_prompt_type": prompt_type,
                "response": state.get("response", "")
            }

        except Exception as e:
            logger.error(f"Error preparing conversation: {e}")
            raise ChatProcessingError(f"Failed to prepare conversation: {str(e)}")

    def _generate_response(self, state: ChatState) -> ChatState:
        """Generate AI response using OpenAI."""
        try:
            messages = state["messages"]
            response_content = openai_service.generate_response(messages)

            # Create AI message
            ai_message = AIMessage(content=response_content)
            updated_messages = messages + [ai_message]

            logger.debug("Response generated successfully")
            return {
                "messages": updated_messages,
                "response": response_content,
                "current_prompt_type": state.get("current_prompt_type", "default")
            }

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            error_msg = f"Error generating response: {str(e)}"
            return {
                "messages": state["messages"],
                "response": error_msg,
                "current_prompt_type": state.get("current_prompt_type", "default")
            }

    def process_chat(self, message: str, prompt_type: str = "default") -> ChatState:
        """Process a chat message through the workflow."""
        try:
            initial_state = {
                "messages": [HumanMessage(content=message)],
                "current_prompt_type": prompt_type,
                "response": ""
            }

            logger.info(f"Processing chat message with prompt type: {prompt_type}")
            result = self.workflow.invoke(initial_state)
            logger.info("Chat processing completed successfully")

            return result

        except Exception as e:
            logger.error(f"Error processing chat: {e}")
            raise ChatProcessingError(str(e))

    async def stream_chat_response(self, message: str, prompt_type: str = "default") -> AsyncGenerator[str, None]:
        """Stream a chat response directly from LLM."""
        try:
            # Prepare messages with system prompt
            system_prompt = prompt_manager.get_prompt(prompt_type)
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message)
            ]

            logger.info(f"Starting streaming chat with prompt type: {prompt_type}")

            # Stream directly from OpenAI service
            async for chunk in openai_service.stream_response(messages):
                yield chunk

            logger.info("Streaming chat completed successfully")

        except Exception as e:
            logger.error(f"Error streaming chat: {e}")
            # Send error in SSE format
            import json
            error_data = {"content": "", "done": True, "error": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"


# Global service instance
chat_workflow_service = ChatWorkflowService()
