#!/bin/bash
# Start both backend (Socket.IO + FastAPI) and frontend (Vite) servers with full automation

set -e

# 1. Check for Python virtual environment activation
if [ -z "$VIRTUAL_ENV" ]; then
  echo "[WARNING] Python virtual environment is not active. Activate your venv for best results."
fi

# 2. Install backend Python dependencies if needed
if [ -f "requirements.txt" ]; then
  echo "Checking Python dependencies..."
  pip install -r requirements.txt
fi

# 3. Kill previous backend process if running (uvicorn on port 8000)
if lsof -i:8000 -t >/dev/null; then
  echo "Killing previous backend process on port 8000..."
  kill -9 $(lsof -i:8000 -t)
fi

# 4. Start backend
(uvicorn server.main:sio_app --reload &)
BACKEND_PID=$!
echo "Started backend (PID $BACKEND_PID) on http://localhost:8000"

# 5. Start frontend
cd client

# Auto-install dependencies if missing or node_modules is corrupt
if [ ! -d "node_modules" ] || [ ! -f "package-lock.json" ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

# Ensure required CSS build tools are installed
REQUIRED_PKGS=(tailwindcss autoprefixer postcss)
for pkg in "${REQUIRED_PKGS[@]}"; do
  if ! npm list "$pkg" >/dev/null 2>&1; then
    echo "Installing missing package: $pkg"
    npm install "$pkg"
  fi
 done

# Print status
echo "Starting frontend (Vite dev server)..."
npm run dev &
FRONTEND_PID=$!

# 6. Open dashboard in default browser (macOS only)
if [[ "$OSTYPE" == "darwin" ]]; then
  sleep 2 # Give Vite a moment to start
  open http://localhost:5173
fi

# 7. Print summary
cd ..
echo "\n[INFO] Backend running at http://localhost:8000"
echo "[INFO] Frontend running at http://localhost:5173 (opened in browser)"
echo "[INFO] Press CTRL+C to stop both servers."

# Wait for background jobs
wait $BACKEND_PID $FRONTEND_PID
