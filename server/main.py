from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
import socketio

from .api.run import router as run_router
from .api.calendar import calendar_router
from .api.meta import router as meta_router
from .core.websocket_manager import manager

# Build the list of allowed Socket.IO origins (can override via ALLOWED_ORIGINS env var)
sio_allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173, http://192.168.10.51:5173, http://192.168.10.51:5174"
)
allowed_origins = [origin.strip() for origin in sio_allowed_origins.split(',') if origin.strip()]

app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=allowed_origins)
sio_app = socketio.ASGIApp(sio, app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(run_router)
app.include_router(calendar_router)
app.include_router(meta_router)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Example: emit progress event from backend to all clients
def emit_progress(message: str):
    import asyncio
    asyncio.create_task(sio.emit('progress', message))

# Example event handler (optional, can be expanded)
@sio.event
def connect(sid, environ):
    print(f"Socket.IO client connected: {sid}")

@sio.event
def disconnect(sid):
    print(f"Socket.IO client disconnected: {sid}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:sio_app", host="0.0.0.0", port=8000, reload=True)
