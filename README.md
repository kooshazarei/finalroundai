# AI Chat Assistant

A modern, responsive chat application with AI Assistant powered by OpenAI. The application consists of a Python FastAPI backend and a React TypeScript frontend, all containerized with Docker.

## Features

- 🤖 AI-powered chat using OpenAI GPT-3.5-turbo
- 🌐 Modern, responsive web interface
- 🔄 Real-time conversation with conversation history
- 🐳 Fully containerized with Docker
- 🚀 Easy deployment and development setup
- 💬 Clean, intuitive chat interface with Material-UI
- 📊 AI conversation tracing and monitoring with Langfuse

## Architecture

- **Backend**: Python FastAPI with OpenAI integration
- **Frontend**: React TypeScript with Material-UI components
- **Containerization**: Docker and Docker Compose
- **API**: RESTful API for chat interactions
- **Monitoring**: Langfuse integration for AI conversation tracking and analytics

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key

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
   LANGFUSE_PUBLIC_KEY=pk-lf-your_public_key_here
   LANGFUSE_SECRET_KEY=sk-lf-your_secret_key_here
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```

3. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - API Status: http://localhost:8000/status

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
# Edit .env with your OpenAI API key

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
- `GET /status` - API status
- `POST /api/chat/stream` - Stream AI assistant response
- `POST /api/chat/thread/new` - Create new chat thread

### API Usage Example

```bash
curl -X POST "http://localhost:8000/api/chat/stream" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Hello, how are you?",
       "thread_id": "test-thread"
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
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
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
├── docker-compose.yml      # Multi-container configuration
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Environment Variables

### Required
- `OPENAI_API_KEY` - Your OpenAI API key
- `LANGFUSE_PUBLIC_KEY` - Your Langfuse public key (for AI tracing)
- `LANGFUSE_SECRET_KEY` - Your Langfuse secret key (for AI tracing)

### Optional
- `LANGFUSE_HOST` - Langfuse host URL (default: https://cloud.langfuse.com)
- `REACT_APP_API_URL` - Backend API URL (default: http://localhost:8000)

## AI Monitoring with Langfuse

This application includes comprehensive AI monitoring and tracing using [Langfuse](https://langfuse.com/), an open-source observability platform for AI agents.

### What's Tracked

- **Agent Conversations**: All interactions between the user and the interview agents
- **Multi-Agent Handoffs**: When the orchestrator delegates to interviewer, evaluator, or topic manager agents
- **Token Usage**: Track costs and usage across all LLM calls
- **Response Times**: Monitor latency for each agent interaction
- **Error Tracking**: Capture and analyze any errors in the agent workflow

### Setting Up Langfuse

1. **Sign up for Langfuse Cloud** (free): https://cloud.langfuse.com/
   - Or self-host Langfuse: https://langfuse.com/self-hosting

2. **Get your API keys** from the project settings page

3. **Add to your environment variables**:
   ```bash
   LANGFUSE_PUBLIC_KEY=pk-lf-your_public_key_here
   LANGFUSE_SECRET_KEY=sk-lf-your_secret_key_here
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```

### Viewing Traces

Once configured, every conversation will automatically create traces in your Langfuse dashboard:

- **Interview Sessions**: Grouped by thread ID for easy tracking
- **Agent Details**: See which specific agent (orchestrator, interviewer, etc.) handled each interaction
- **Performance Metrics**: Response times, token counts, and costs
- **Debug Information**: Full conversation context and agent reasoning

Visit your Langfuse dashboard to explore detailed traces of all AI interactions.

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error:**
   - Ensure you've set the `OPENAI_API_KEY` in your `.env` file
   - Verify the API key is valid and has sufficient credits

2. **Docker Build Issues:**
   - Try clearing Docker cache: `docker system prune -a`
   - Ensure Docker daemon is running

3. **CORS Issues in Development:**
   - The backend is configured to allow requests from localhost:3000
   - For different origins, update the CORS settings in `backend/main.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
