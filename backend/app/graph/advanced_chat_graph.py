"""
Advanced LangGraph implementation for future use.
This version uses actual LangGraph features but is more carefully implemented.
"""

from typing import Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict


class AdvancedGraphState(TypedDict):
    """State definition for the advanced chat graph."""
    messages: Annotated[list[BaseMessage], add_messages]
    user_input: str
    response: str
    conversation_context: str


class AdvancedChatGraph:
    """Advanced chat graph using actual LangGraph features."""

    def __init__(self, llm_model):
        """
        Initialize the advanced chat graph with an LLM model.

        Args:
            llm_model: LangChain LLM model for generating responses
        """
        self.llm_model = llm_model
        self.graph = self._create_graph()

    def _create_graph(self):
        """Create and configure the advanced chat graph."""
        try:
            workflow = StateGraph(AdvancedGraphState)

            # Add nodes
            workflow.add_node("analyze_input", self._analyze_input)
            workflow.add_node("generate_response", self._generate_response)
            workflow.add_node("format_output", self._format_output)

            # Define the flow
            workflow.set_entry_point("analyze_input")
            workflow.add_edge("analyze_input", "generate_response")
            workflow.add_edge("generate_response", "format_output")
            workflow.add_edge("format_output", END)

            # Compile the graph with error handling
            return workflow.compile()

        except Exception as e:
            print(f"Error creating advanced graph: {e}")
            # Fallback to None, will use simple implementation
            return None

    def _analyze_input(self, state: AdvancedGraphState) -> AdvancedGraphState:
        """Analyze the user input and extract context."""
        user_input = state.get("user_input", "")
        messages = state.get("messages", [])

        # Add system message if this is the first message
        if not messages:
            messages.append(SystemMessage(content="You are a helpful AI assistant."))

        # Add user message
        if user_input:
            messages.append(HumanMessage(content=user_input))

        # Simple context analysis (can be enhanced later)
        context = f"User asked: {user_input}"

        return {
            **state,
            "messages": messages,
            "conversation_context": context,
        }

    def _generate_response(self, state: AdvancedGraphState) -> AdvancedGraphState:
        """Generate a response using the LLM model."""
        messages = state.get("messages", [])
        context = state.get("conversation_context", "")

        # Generate response using the LLM model
        try:
            response = self.llm_model.invoke(messages)
            response_text = response.content
        except Exception as e:
            response_text = f"Error generating response: {str(e)}"

        # Add AI message to the conversation
        messages.append(AIMessage(content=response_text))

        return {
            **state,
            "messages": messages,
            "response": response_text,
        }

    def _format_output(self, state: AdvancedGraphState) -> AdvancedGraphState:
        """Format the final output."""
        # Could add additional formatting, logging, etc.
        return state

    async def ainvoke(self, user_input: str, session_id: str = None) -> Dict[str, Any]:
        """
        Asynchronously invoke the advanced graph with user input.

        Args:
            user_input: The user's message
            session_id: Optional session identifier for conversation tracking

        Returns:
            Dict containing the response and conversation state
        """
        # If graph creation failed, use simple implementation
        if self.graph is None:
            return await self._simple_invoke(user_input, session_id)

        try:
            initial_state = {
                "messages": [],
                "user_input": user_input,
                "response": "",
                "conversation_context": "",
            }

            # Run the graph
            result = await self.graph.ainvoke(initial_state)

            return {
                "response": result.get("response", ""),
                "messages": result.get("messages", []),
                "session_id": session_id,
                "context": result.get("conversation_context", ""),
            }

        except Exception as e:
            print(f"Error in advanced graph: {e}")
            # Fallback to simple implementation
            return await self._simple_invoke(user_input, session_id)

    async def _simple_invoke(self, user_input: str, session_id: str = None) -> Dict[str, Any]:
        """Fallback simple implementation."""
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
                "context": f"Simple mode - User asked: {user_input}",
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
                "context": "Error mode",
            }


def create_advanced_chat_graph(llm_model) -> AdvancedChatGraph:
    """
    Factory function to create an advanced chat graph instance.

    Args:
        llm_model: LangChain LLM model for generating responses

    Returns:
        Configured AdvancedChatGraph instance
    """
    return AdvancedChatGraph(llm_model)
