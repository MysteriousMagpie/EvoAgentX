from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import os
import socketio
import pkg_resources
import json
from datetime import datetime
from typing import Optional

from .api.run import router as run_router
from .api.calendar import calendar_router
from .api.obsidian import router as obsidian_router
from .api.planner import planner_router
from .core.websocket_manager import manager
from .core.obsidian_websocket import obsidian_ws_manager

# Build the list of allowed Socket.IO origins (can override via ALLOWED_ORIGINS env var)
sio_allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173, http://192.168.10.51:5173, http://192.168.10.51:5174"
)
sio_origins = [origin.strip() for origin in sio_allowed_origins.split(',') if origin.strip()]

# Configure CORS origins for FastAPI - include Obsidian plugin origins
cors_origins = [
    "*",  # Allow all origins for development - can be restricted in production
    "app://obsidian.md",
    "capacitor://localhost", 
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://192.168.10.51:5173",
    "http://192.168.10.51:5174"
]

app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=sio_origins)
sio_app = socketio.ASGIApp(sio, app)

# Add global validation error handler for better debugging
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed debugging information"""
    # Log the validation error details
    print(f"[VALIDATION ERROR] URL: {request.url}")
    print(f"[VALIDATION ERROR] Method: {request.method}")
    print(f"[VALIDATION ERROR] Headers: {dict(request.headers)}")
    
    # Try to get the request body for debugging
    try:
        body = await request.body()
        body_str = body.decode('utf-8')
        print(f"[VALIDATION ERROR] Raw Body: {body_str}")
        
        # Try to parse as JSON
        try:
            body_json = json.loads(body_str) if body_str else {}
            print(f"[VALIDATION ERROR] Parsed Body: {json.dumps(body_json, indent=2)}")
        except json.JSONDecodeError:
            print(f"[VALIDATION ERROR] Body is not valid JSON")
    except Exception as e:
        print(f"[VALIDATION ERROR] Could not read request body: {e}")
    
    print(f"[VALIDATION ERROR] Validation Details: {exc.errors()}")
    
    # Check for common misrouted requests
    error_details = exc.errors()
    is_conversation_history_endpoint = "/conversation/history" in str(request.url)
    has_message_field_error = any("conversation_id" in str(error.get("loc", [])) for error in error_details)
    
    if is_conversation_history_endpoint and has_message_field_error:
        return JSONResponse(
            status_code=422,
            content={
                "error": "Endpoint Mismatch",
                "message": "You're sending chat data to the conversation history endpoint. Use /api/obsidian/chat instead.",
                "correct_endpoint": "/api/obsidian/chat",
                "expected_payload_for_chat": {
                    "message": "your message here",
                    "conversation_id": "optional_conversation_id"
                },
                "expected_payload_for_history": {
                    "conversation_id": "required_conversation_id", 
                    "limit": "optional_number"
                },
                "validation_errors": error_details
            }
        )
    
    # Default validation error response
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "The request data doesn't match the expected format",
            "validation_errors": error_details,
            "url": str(request.url),
            "method": request.method
        }
    )

# Add CORS middleware with comprehensive configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(run_router)
app.include_router(calendar_router)
app.include_router(obsidian_router)
app.include_router(planner_router)

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
