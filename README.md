# AI Chat Assistant

A modern, responsive chat application with AI Assistant powered by OpenAI and LangChain. The application consists of a Python FastAPI backend and a React TypeScript frontend, all containerized with Docker. Includes comprehensive observability with LangSmith tracing.

## Features

- 🤖 AI-powered chat using OpenAI GPT-3.5-turbo
- 🌐 Modern, responsive web interface
- 🔄 Real-time conversation with conversation history
- � LangSmith observability and tracing
- �🐳 Fully containerized with Docker
- 🚀 Easy deployment and development setup
- 💬 Clean, intuitive chat interface with Material-UI

## Architecture

- **Backend**: Python FastAPI with LangChain and OpenAI integration
- **Frontend**: React TypeScript with Material-UI components
- **Observability**: LangSmith tracing for conversation flows
- **Containerization**: Docker and Docker Compose
- **API**: RESTful API for chat interactions

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- LangSmith API key (optional, for observability)

## Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd finalroundai
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file and add your API keys:
   ```
   OPENAI_API_KEY=your_actual_openai_api_key_here
   LANGSMITH_PROJECT=FinalRoundAI
   LANGSMITH_API_KEY=your_langsmith_api_key_here
   ```

3. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Tracing Status: http://localhost:8000/tracing-status

## LangSmith Observability

This application includes comprehensive LangSmith integration for observability:

### Features
- **Automatic Tracing**: All LangGraph workflows and OpenAI calls are automatically traced
- **Rich Metadata**: Each trace includes prompt type, message length, and custom tags
- **Project Organization**: All traces are organized under the configured project name
- **Error Tracking**: Failed operations are captured with detailed error information

### Configuration
```bash
# Required environment variables for LangSmith
LANGSMITH_PROJECT=FinalRoundAI
LANGSMITH_API_KEY=your_langsmith_api_key_here
```

### What's Traced
- LangGraph chat workflows with full state transitions
- OpenAI API calls (both streaming and non-streaming)
- Prompt management and system message preparation
- Error conditions and recovery

### Viewing Traces
1. Visit [LangSmith](https://smith.langchain.com/)
2. Navigate to your project: "FinalRoundAI"
3. View detailed traces of all chat interactions

## Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAI API key and LangSmith settings

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at http://localhost:3000

### API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /tracing-status` - LangSmith tracing status
- `POST /api/chat` - Send message to AI assistant
- `POST /api/chat/stream` - Stream AI assistant response
- `GET /api/welcome` - Stream welcome message
- `GET /api/prompts` - Get available prompt types

### API Usage Example

```bash
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Hello, how are you?",
       "prompt_type": "default"
     }'
```

## Docker Commands

### Build and run all services:
```bash
docker-compose up --build
```

### Run in detached mode:
```bash
docker-compose up -d
```

### Stop all services:
```bash
docker-compose down
```

### View logs:
```bash
docker-compose logs -f
```

### Rebuild specific service:
```bash
docker-compose build backend
# or
docker-compose build frontend
```

## Project Structure

```
finalroundai/
├── backend/
│   ├── main.py              # FastAPI application with LangSmith setup
│   ├── requirements.txt     # Python dependencies (includes langsmith)
│   ├── Dockerfile          # Backend container configuration
│   └── .env.example        # Backend environment variables template
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Main React component
│   │   └── index.tsx       # Application entry point
│   ├── public/
│   │   └── index.html      # HTML template
│   ├── package.json        # Node.js dependencies
│   └── Dockerfile         # Frontend container configuration
├── docker-compose.yml      # Multi-container configuration with LangSmith env vars
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Environment Variables

### Required
- `OPENAI_API_KEY` - Your OpenAI API key

### Optional (but recommended)
- `LANGSMITH_PROJECT` - LangSmith project name (default: "FinalRoundAI")
- `LANGSMITH_API_KEY` - Your LangSmith API key for tracing
- `REACT_APP_API_URL` - Backend API URL (default: http://localhost:8000)

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error:**
   - Ensure you've set the `OPENAI_API_KEY` in your `.env` file
   - Verify the API key is valid and has sufficient credits

2. **LangSmith Tracing Not Working:**
   - Check that `LANGSMITH_API_KEY` is set correctly
   - Visit `/tracing-status` endpoint to verify configuration
   - Ensure your LangSmith account has access to the project

3. **Port Conflicts:**
   - If ports 3000 or 8000 are in use, modify the ports in `docker-compose.yml`

4. **Docker Build Issues:**
   - Try clearing Docker cache: `docker system prune -a`
   - Ensure Docker daemon is running

5. **CORS Issues in Development:**
   - The backend is configured to allow requests from localhost:3000
   - For different origins, update the CORS settings in `backend/main.py`

## Monitoring and Observability

### LangSmith Dashboard
- Monitor conversation flows and performance
- Track token usage and costs
- Debug failed interactions
- Analyze user interaction patterns

### Application Logs
- Structured logging throughout the application
- Error tracking and debugging information
- Performance metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly (including trace verification in LangSmith)
5. Submit a pull request

## License

This project is open source and available under the MIT License.
