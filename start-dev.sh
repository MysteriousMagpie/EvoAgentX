#!/bin/bash
# Start both backend (Socket.IO + FastAPI) and frontend (Vite) servers

# Start backend
(uvicorn server.main:sio_app --reload &)

# Start frontend
cd client && npm run dev
