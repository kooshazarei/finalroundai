"""
Simple test for the LangGraph implementation.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from app.graph.chat_graph import ChatGraph, create_chat_graph
from langchain_core.messages import AIMessage


def test_create_chat_graph():
    """Test creating a chat graph."""
    # Mock LLM model
    mock_model = Mock()

    # Create graph
    graph = create_chat_graph(mock_model)

    assert isinstance(graph, ChatGraph)
    assert graph.llm_model == mock_model


@pytest.mark.asyncio
async def test_chat_graph_ainvoke():
    """Test the chat graph ainvoke method."""
    # Mock LLM model
    mock_model = Mock()
    mock_model.invoke.return_value = AIMessage(content="Hello! How can I help you?")

    # Create graph
    graph = create_chat_graph(mock_model)

    # Test ainvoke
    result = await graph.ainvoke("Hello", session_id="test123")

    assert "response" in result
    assert "messages" in result
    assert "session_id" in result
    assert result["session_id"] == "test123"
    assert result["response"] == "Hello! How can I help you?"


def test_graph_nodes():
    """Test individual graph nodes."""
    mock_model = Mock()
    graph = ChatGraph(mock_model)

    # Test process_input
    state = {"user_input": "Hello", "messages": []}
    result = graph._process_input(state)

    assert len(result["messages"]) == 2  # System + user message
    assert result["messages"][-1].content == "Hello"

    # Test generate_response
    mock_model.invoke.return_value = AIMessage(content="Hi there!")
    state = result.copy()
    result = graph._generate_response(state)

    assert result["response"] == "Hi there!"
    assert len(result["messages"]) == 3  # System + user + AI message


if __name__ == "__main__":
    # Run a simple test
    print("🧪 Running simple graph test...")

    # Test graph creation
    mock_model = Mock()
    graph = create_chat_graph(mock_model)
    print("✅ Graph creation test passed")

    # Test process input
    state = {"user_input": "Test message", "messages": []}
    result = graph._process_input(state)
    print(f"✅ Process input test passed: {len(result['messages'])} messages")

    print("🎉 All basic tests passed!")
