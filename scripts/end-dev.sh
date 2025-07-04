#!/bin/bash
# Kill EvoAgentX dev servers (both backend and frontend)

# Find and kill backend (uvicorn or python)
BE_PID=$(lsof -i :8000 -t)
if [ -n "$BE_PID" ]; then
  echo "Killing backend server (PID $BE_PID)"
  kill $BE_PID
else
  echo "No backend server found on port 8000."
fi

# Find and kill frontend (vite)
FE_PID=$(lsof -i :5173 -t)
if [ -n "$FE_PID" ]; then
  echo "Killing frontend server (PID $FE_PID)"
  kill $FE_PID
else
  echo "No frontend server found on port 5173."
fi

# Optionally, kill any leftover node or python processes (uncomment if needed)
# pkill -f "vite"
# pkill -f "uvicorn"
# pkill -f "python.*run_evoagentx.py"

exit 0
