#!/bin/bash

# EvoAgentX Server Startup Script
# This script starts the FastAPI server with the planner functionality
# It automatically kills any existing processes on the target port

# Default port, can be overridden with: ./start-server.sh 3000
PORT=${1:-8000}

echo "🚀 Starting EvoAgentX Server..."
echo "📍 Server will be available at: http://localhost:$PORT"
echo "📋 Planner API: http://localhost:$PORT/planner/planday"
echo "🔍 API Documentation: http://localhost:$PORT/docs"
echo ""

# Check if port is already in use and automatically kill processes
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port $PORT is already in use!"
    echo "🔄 Automatically stopping existing processes on port $PORT..."
    
    # Get all PIDs using the port
    PIDS=$(lsof -ti:$PORT 2>/dev/null)
    
    if [ -n "$PIDS" ]; then
        echo "📋 Found processes: $PIDS"
        
        # First try graceful termination
        echo "🛑 Attempting graceful shutdown..."
        echo "$PIDS" | xargs kill -TERM 2>/dev/null
        sleep 3
        
        # Check if processes are still running
        REMAINING_PIDS=$(lsof -ti:$PORT 2>/dev/null)
        if [ -n "$REMAINING_PIDS" ]; then
            echo "💥 Force killing remaining processes: $REMAINING_PIDS"
            echo "$REMAINING_PIDS" | xargs kill -9 2>/dev/null
            sleep 2
        fi
    fi
    
    # Final verification
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Failed to free port $PORT. Manual intervention required."
        echo "🔧 Try running: lsof -ti:$PORT | xargs kill -9"
        exit 1
    else
        echo "✅ Port $PORT is now free!"
    fi
else
    echo "✅ Port $PORT is available!"
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "🐍 Activating virtual environment..."
    source .venv/bin/activate
fi

# Start the server
echo "🎯 Starting server on port $PORT..."
python -m uvicorn server.main:sio_app --host 0.0.0.0 --port $PORT --reload
echo "✅ Server started!"