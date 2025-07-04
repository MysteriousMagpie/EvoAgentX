#!/bin/bash

# Start EvoAgentX server with Obsidian integration
# This script starts the FastAPI server with all the Obsidian endpoints

set -e

echo "🚀 Starting EvoAgentX Server for Obsidian Integration"
echo "===================================================="

# Check if we're in the right directory
if [ ! -f "server/main.py" ]; then
    echo "❌ Error: Please run this script from the EvoAgentX root directory"
    exit 1
fi

# Check if dependencies are installed
python -c "import fastapi, uvicorn" 2>/dev/null || {
    echo "❌ Error: Missing dependencies. Please run ./setup-obsidian.sh first"
    exit 1
}

# Load environment variables
if [ -f ".env" ]; then
    echo "📝 Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set. Some features may not work."
    echo "   Please set it in .env file or environment variables"
    echo ""
fi

# Start the server
echo "🌐 Starting server on http://localhost:8000"
echo "📚 API documentation will be available at:"
echo "   - Swagger UI: http://localhost:8000/docs"
echo "   - ReDoc: http://localhost:8000/redoc"
echo ""
echo "🔗 Obsidian API endpoints available at /api/obsidian/*"
echo "🔌 WebSocket endpoint: ws://localhost:8000/ws/obsidian"
echo ""
echo "💡 Tip: Use Ctrl+C to stop the server"
echo ""

cd server
python -m uvicorn main:sio_app --host 0.0.0.0 --port 8000 --reload
