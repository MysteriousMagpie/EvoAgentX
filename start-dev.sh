#!/bin/bash
# Start both backend (Socket.IO + FastAPI) and frontend (Vite) servers with improvements

set -e

# Kill previous backend process if running (uvicorn on port 8000)
if lsof -i:8000 -t >/dev/null; then
  echo "Killing previous backend process on port 8000..."
  kill -9 $(lsof -i:8000 -t)
fi

# Start backend
(uvicorn server.main:sio_app --reload &)
BACKEND_PID=$!
echo "Started backend (PID $BACKEND_PID) on http://localhost:8000"

# Start frontend
cd client

# Auto-install dependencies if missing or node_modules is corrupt
if [ ! -d "node_modules" ] || [ ! -f "package-lock.json" ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

# Print status
echo "Starting frontend (Vite dev server)..."
npm run dev
