# AI Chat Assistant Backend

A clean, modular FastAPI backend for an AI chat assistant built with OpenAI.

## Project Structure

```
backend/
├── app/                    # Main application package
│   ├── api/               # API endpoints
│   │   ├── __init__.py
│   │   ├── chat.py        # Chat-related endpoints
│   │   └── health.py      # Health check endpoints
│   ├── core/              # Core configuration and utilities
│   │   ├── __init__.py
│   │   ├── config.py      # Application settings
│   │   ├── exceptions.py  # Custom exceptions
│   │   └── logging_config.py  # Logging configuration
│   ├── models/            # Pydantic models
│   │   ├── __init__.py
│   │   ├── api_models.py  # API request/response models
│   │   └── chat_models.py # Chat workflow models
│   ├── prompts/           # Prompt management
│   │   ├── __init__.py
│   │   ├── prompt_manager.py
│   │   ├── system_prompts.py
│   │   └── README.md
│   ├── services/          # Business logic services
│   │   ├── __init__.py
│   │   ├── llm_service.py       # LLM service
│   │   ├── openai_service.py    # OpenAI integration
│   │   └── streaming_service.py # Streaming functionality
│   └── utils/             # Utility functions
│       ├── __init__.py
│       └── exception_handlers.py
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── Dockerfile            # Docker configuration
```

## Features

- **Clean Architecture**: Modular design with separation of concerns
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **OpenAI Integration**: GPT-3.5-turbo for AI responses
- **Streaming**: Real-time response streaming
- **Error Handling**: Comprehensive exception handling
- **Logging**: Structured logging throughout the application
- **Type Safety**: Full type hints with Pydantic models
- **Configuration**: Environment-based configuration management

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and other settings
   ```

3. **Run the Application**:
   ```bash
   python main.py
   ```

4. **API Documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health
- `GET /` - Root endpoint
- `GET /health` - Health check

### Chat
- `GET /api/welcome` - Stream welcome message
- `POST /api/chat` - Process chat message
- `GET /api/prompts` - Get available prompt types

## Configuration

The application uses environment variables for configuration. See `.env.example` for all available options.

Key settings:
- `OPENAI_API_KEY`: Your OpenAI API key
- `DEBUG`: Enable debug mode (default: false)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

## Development

### Adding New Endpoints
1. Create endpoint functions in appropriate files in `app/api/`
2. Add models to `app/models/` if needed
3. Register the router in `app/api/__init__.py`

### Adding New Services
1. Create service classes in `app/services/`
2. Export from `app/services/__init__.py`
3. Use dependency injection pattern

### Error Handling
- Custom exceptions are defined in `app/core/exceptions.py`
- Exception handlers in `app/utils/exception_handlers.py`
- All exceptions are automatically converted to proper JSON responses

## Docker

Build and run with Docker:
```bash
docker build -t ai-chat-backend .
docker run -p 8000:8000 --env-file .env ai-chat-backend
```

## Testing

```bash
# Test the API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "prompt_type": "default"}'
```
