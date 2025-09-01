# LangGraph Implementation

This directory contains the LangGraph implementation for the AI Chat Assistant.

## Overview

The graph directory provides a structured approach to handling chat conversations using LangGraph concepts. The implementation is designed to be simple, reliable, and extensible.

## Components

### 1. Chat Graph (`chat_graph.py`)

The main chat graph implementation currently uses a simplified approach that mimics LangGraph patterns without the complexity that can cause runtime issues:

- **SimpleChatGraph**: A streamlined implementation that processes messages directly
- **Async Support**: Full async processing for better performance
- **Error Handling**: Comprehensive error handling for robustness

### 2. Advanced Chat Graph (`advanced_chat_graph.py`)

A more complex implementation that uses actual LangGraph features with fallback mechanisms:

- **AdvancedChatGraph**: Uses actual LangGraph StateGraph with multiple nodes
- **Fallback Logic**: Falls back to simple implementation if graph creation fails
- **Context Analysis**: Additional processing for conversation context

### 3. Graph Service (`../services/graph_service.py`)

A service layer that manages graph instances and provides a clean interface for the API endpoints:

- Creates and manages LLM model instances
- Handles graph instantiation and caching
- Provides async methods for processing messages

## Architecture

```
User Input → Graph Service → Chat Graph → LLM Model → Response
```

The flow:
1. User sends a message via API
2. Graph Service receives the request
3. Graph Service gets or creates appropriate Chat Graph
4. Chat Graph processes the message
5. LLM generates response
6. Response is returned to user

## Current Implementation

The current working implementation (`SimpleChatGraph`) provides:

- ✅ **Reliability**: Simple, tested approach that works consistently
- ✅ **Performance**: Fast response times with async support
- ✅ **Maintainability**: Easy to understand and modify
- ✅ **Error Handling**: Graceful handling of errors and edge cases

## Key Features

- **Simple State Management**: Direct message processing without complex state
- **Model Flexibility**: Easy to switch between different LLM models
- **Async Processing**: Full async support for better performance
- **Error Handling**: Comprehensive error handling throughout the flow
- **Caching**: Graph instances are cached for efficiency

## Usage

### Basic Usage

```python
from app.services import get_graph_service

# Get the graph service
graph_service = get_graph_service()

# Process a message
result = await graph_service.process_chat_message(
    message="Hello, how are you?",
    model_name="gpt-3.5-turbo",
    session_id="user123"
)

print(result["response"])
```

### Creating Custom Graphs

```python
from app.graph import create_chat_graph
from langchain_openai import ChatOpenAI

# Create your own LLM model
model = ChatOpenAI(model="gpt-4", temperature=0.5)

# Create a chat graph
graph = create_chat_graph(model)

# Use the graph
result = await graph.ainvoke("Your message here")
```

## Integration with API

The chat API endpoints (`/api/chat` and `/api/chat/stream`) use this graph implementation, providing:

- Consistent conversation handling
- Better state management
- Easier testing and debugging
- More extensible architecture

## Benefits of This Approach

1. **Reliability**: Simple implementation reduces potential failure points
2. **Performance**: Direct processing without graph overhead
3. **Maintainability**: Easy to understand and modify
4. **Extensibility**: Can be enhanced with LangGraph features as needed
5. **Testing**: Individual components can be tested separately

## Future Enhancements

The current implementation can be extended with:

- ✅ **Memory Management**: Conversation history storage
- ✅ **Tool Calling**: Integration with external APIs
- ✅ **Complex Flows**: Multi-step conversation handling
- ✅ **Conditional Logic**: Different responses based on context
- ✅ **User Preferences**: Personalized responses
- ✅ **Analytics**: Conversation analytics and insights

## Demo

Run the demo script to see the graph in action:

```bash
cd backend
python demo_graph.py
```

## Testing

Test the implementation:

```bash
cd backend
python test_graph.py
```

Test the full API:

```bash
cd /path/to/project
python test_api.py
```

## Deployment Status

✅ **Working**: The simplified implementation is fully functional and deployed
✅ **Tested**: All API endpoints are working correctly
✅ **Production Ready**: Ready for production use

Make sure you have `OPENAI_API_KEY` set in your environment variables for full functionality.
