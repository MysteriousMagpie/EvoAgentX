from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import os
import socketio
import pkg_resources
import json
from datetime import datetime
from typing import Optional

from .api.run import router as run_router
from .api.calendar import calendar_router
from .api.obsidian import router as obsidian_router
from .core.websocket_manager import manager
from .core.obsidian_websocket import obsidian_ws_manager

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
app.include_router(obsidian_router)

status_router = APIRouter()


@status_router.get("/status")
async def status() -> dict[str, str]:
    """Return basic service health information."""
    return {
        "status": "ok",
        "version": pkg_resources.get_distribution("evoagentx").version,
    }


app.include_router(status_router)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/obsidian")
async def obsidian_websocket_endpoint(websocket: WebSocket, vault_id: Optional[str] = None):
    """WebSocket endpoint specifically for Obsidian plugin connections"""
    connection_id = await obsidian_ws_manager.connect(websocket, vault_id)
    try:
        while True:
            # Receive messages from Obsidian
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                # Handle different message types
                if message_type == "ping":
                    await obsidian_ws_manager.send_to_connection(connection_id, {
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                elif message_type == "chat_message":
                    # Handle real-time chat messages
                    await obsidian_ws_manager.send_to_connection(connection_id, {
                        "type": "chat_received",
                        "message": message.get("content", ""),
                        "timestamp": datetime.now().isoformat()
                    })
                elif message_type == "vault_update":
                    # Handle vault content updates
                    vault_id = message.get("vault_id")
                    if vault_id:
                        await obsidian_ws_manager.send_to_vault(vault_id, {
                            "type": "vault_sync",
                            "update": message.get("update", {}),
                            "timestamp": datetime.now().isoformat()
                        })
                        
            except json.JSONDecodeError:
                await obsidian_ws_manager.send_to_connection(connection_id, {
                    "type": "error",
                    "message": "Invalid JSON received",
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        obsidian_ws_manager.disconnect(connection_id)

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
