#!/bin/bash

# AI Chat Assistant - Build and Run Script
# This script builds and runs the entire application using Docker
# Usage: ./deploy.sh [--detached] [--rebuild] [--logs] [--stop]

echo "🚀 Building and running AI Chat Assistant..."

# Parse command line arguments
DETACHED=false
REBUILD=false
SHOW_LOGS=false
STOP_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--detached)
            DETACHED=true
            shift
            ;;
        -r|--rebuild)
            REBUILD=true
            shift
            ;;
        -l|--logs)
            SHOW_LOGS=true
            shift
            ;;
        -s|--stop)
            STOP_ONLY=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -d, --detached    Run in detached mode (background)"
            echo "  -r, --rebuild     Force rebuild of Docker images"
            echo "  -l, --logs        Show logs after starting"
            echo "  -s, --stop        Stop running containers"
            echo "  -h, --help        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# If stop only, just stop containers and exit
if [ "$STOP_ONLY" = true ]; then
    echo "🛑 Stopping containers..."
    docker-compose down
    echo "✅ Containers stopped"
    exit 0
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    echo "# AI Chat Assistant Environment Variables" > .env
    echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env
    echo "📝 Please edit .env file and add your OpenAI API key before running again."
    echo "   Example: OPENAI_API_KEY=sk-your-key-here"
    exit 1
fi

# Check if OPENAI_API_KEY is set
source .env
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ OPENAI_API_KEY is not set in .env file."
    echo "   Please add your OpenAI API key to the .env file."
    exit 1
fi

echo "✅ Environment validation passed"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start the application
BUILD_ARGS=""
RUN_ARGS=""

if [ "$REBUILD" = true ]; then
    BUILD_ARGS="--build --no-cache"
    echo "🔨 Force rebuilding and starting containers..."
else
    BUILD_ARGS="--build"
    echo "🔨 Building and starting containers..."
fi

if [ "$DETACHED" = true ]; then
    RUN_ARGS="-d"
    docker-compose up $BUILD_ARGS $RUN_ARGS
else
    RUN_ARGS=""
    echo "💡 Tip: Use Ctrl+C to stop, or run with --detached to run in background"
    docker-compose up $BUILD_ARGS $RUN_ARGS
fi

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    echo ""
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "📊 View logs with: docker-compose logs -f"
    echo "🛑 Stop with: docker-compose down"
else
    echo "❌ Failed to start services. Check logs with: docker-compose logs"
    exit 1
fi
