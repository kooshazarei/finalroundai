# Simplified LangGraph AI Chat Assistant

This is a drastically simplified version of the AI Chat Assistant that removes all complex memory, chat models, and OpenAI service dependencies. Instead, it provides a simple LangGraph implementation with configurable models.

## What Was Removed

1. **Memory Services**: All conversation memory and thread management
2. **Chat Models**: Complex chat state management
3. **OpenAI Service**: Dedicated OpenAI service layer
4. **Prompts System**: Complex prompt management system
5. **LangSmith Integration**: Observability and tracing
6. **Streaming**: Real-time response streaming
7. **Thread Management**: Conversation threading
8. **Complex Exception Handling**: Multiple custom exceptions

## What Remains

- **Simple LangGraph Workflow**: A basic graph with one LLM node
- **Configurable Models**: Ability to specify different LLM models via API
- **Static User ID**: Uses a hardcoded user ID (`user123`)
- **Basic FastAPI Endpoints**: Health check and simple chat endpoint
- **Minimal Dependencies**: Only essential packages

## Core Implementation

### LangGraph Workflow

The simplified workflow consists of:

```python
# Simple state for LangGraph
class GraphState(TypedDict):
    messages: list
    response: str

# Single LLM node that processes messages
async def llm_node(state: GraphState, config: Dict[str, Any] = None):
    # Configure model based on request
    model_config = {
        "model": config.get("competitor_model", "gpt-3.5-turbo"),
        "api_key": get_api_key_for_model(...),
        "temperature": config.get("competitor_temperature", 0.7),
    }

    # Use configurable model
    model = configurable_model.with_config(model_config)

    # Add system message and process
    system_messages = [SystemMessage(content="You are a helpful AI assistant.")]
    final_messages = system_messages + list(state["messages"])

    # Generate response
    response = await model.ainvoke(final_messages, config=config)

    return {
        "messages": messages + [response],
        "response": response.content
    }
```

### API Usage

**Chat Endpoint:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "prompt_type": "gpt-3.5-turbo"
  }'
```

**Response:**
```json
{
  "response": "Hello! I'm doing well, thank you for asking...",
  "status": "success",
  "prompt_type": "gpt-3.5-turbo",
  "thread_id": null,
  "user_id": "user123"
}
```

## Configuration

The model is configured dynamically based on the request:

```python
# In the API request, you can specify:
{
    "message": "Your question here",
    "prompt_type": "gpt-4"  # This becomes the model name
}

# This gets translated to:
config = {
    "configurable": {
        "competitor_model": "gpt-4",
        "competitor_temperature": 0.7
    }
}
```

## File Structure (After Simplification)

```
backend/
├── main.py                          # FastAPI entry point
├── requirements.txt                 # Minimal dependencies
└── app/
    ├── __init__.py
    ├── api/
    │   ├── __init__.py
    │   ├── chat.py                  # Simplified chat endpoint with LangGraph
    │   └── health.py                # Health check endpoint
    ├── core/
    │   ├── __init__.py
    │   ├── config.py                # Minimal configuration
    │   ├── exceptions.py            # Basic exception handling
    │   └── logging_config.py        # Logging setup
    ├── models/
    │   ├── __init__.py
    │   └── api_models.py            # Request/response models
    └── utils/
        ├── __init__.py
        └── exception_handlers.py    # Basic exception handlers
```

## Running the Application

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

3. **Start the application:**
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. **Test the API:**
   ```bash
   curl -X GET "http://localhost:8000/api/health"
   curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello!", "prompt_type": "gpt-3.5-turbo"}'
   ```

## Key Features

- **✅ LangGraph Integration**: Uses LangGraph for workflow management
- **✅ Configurable Models**: Can specify different LLM models per request
- **✅ Static User ID**: Uses hardcoded "user123" as requested
- **✅ Simple API**: Just one chat endpoint with minimal complexity
- **✅ No Memory**: Stateless requests with no conversation history
- **✅ Clean Dependencies**: Only essential packages needed

## Model Configuration Example

You can now pass different models in your requests:

```python
# Use GPT-3.5 Turbo
{
    "message": "Hello!",
    "prompt_type": "gpt-3.5-turbo"
}

# Use GPT-4 (if available)
{
    "message": "Complex question",
    "prompt_type": "gpt-4"
}
```

The system will automatically:
1. Get the appropriate API key for the model
2. Configure the LangGraph workflow with the specified model
3. Process the request using `ainvoke`
4. Return the response with the model name used

This is exactly what you requested: a very simple LangGraph LLM call using `ainvoke` with a static user ID, configurable models, and no complex memory or service layers.
