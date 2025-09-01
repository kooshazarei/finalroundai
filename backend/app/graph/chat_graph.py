"""
Simple LangGraph implementation for chat functionality.
"""

from typing import Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage


class SimpleChatGraph:
    """Simple chat graph that processes messages and generates responses."""

    def __init__(self, llm_model):
        """
        Initialize the chat graph with an LLM model.

        Args:
            llm_model: LangChain LLM model for generating responses
        """
        self.llm_model = llm_model

    async def ainvoke(self, user_input: str, session_id: str = None) -> Dict[str, Any]:
        """
        Asynchronously invoke the graph with user input.

        Args:
            user_input: The user's message
            session_id: Optional session identifier for conversation tracking

        Returns:
            Dict containing the response and conversation state
        """
        try:
            # Create messages
            messages = [
                SystemMessage(content="You are a helpful AI assistant."),
                HumanMessage(content=user_input)
            ]

            # Generate response using the LLM model
            response = await self.llm_model.ainvoke(messages)
            response_text = response.content

            # Add AI message to the conversation
            messages.append(AIMessage(content=response_text))

            return {
                "response": response_text,
                "messages": messages,
                "session_id": session_id,
            }

        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            return {
                "response": error_msg,
                "messages": [
                    SystemMessage(content="You are a helpful AI assistant."),
                    HumanMessage(content=user_input),
                    AIMessage(content=error_msg)
                ],
                "session_id": session_id,
            }


# For backward compatibility, create aliases
ChatGraph = SimpleChatGraph


def create_chat_graph(llm_model) -> SimpleChatGraph:
    """
    Factory function to create a chat graph instance.

    Args:
        llm_model: LangChain LLM model for generating responses

    Returns:
        Configured SimpleChatGraph instance
    """
    return SimpleChatGraph(llm_model)
