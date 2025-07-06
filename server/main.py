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

from server.api.run import router as run_router
from server.api.calendar import calendar_router
from server.api.obsidian import router as obsidian_router
from server.api.vault_management_enhanced import router as vault_management_router
from server.api.enhanced_workflows import router as enhanced_workflows_router
from server.api.planner import planner_router
from server.api.workflow import router as workflow_router
from server.core.websocket_manager import manager
from server.core.obsidian_websocket import obsidian_ws_manager

# Import dev-pipe integration
from server.services.devpipe_integration import dev_pipe

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

# Enhanced CORS setup for VaultPilot integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "User-Agent",
        "Cache-Control",
        "Pragma"
    ],
    expose_headers=[
        "Content-Length",
        "Content-Type", 
        "Date",
        "Server"
    ],
    max_age=3600
)
print("CORS configured for VaultPilot integration (development=True)")

# Add debug middleware to see CORS headers
@app.middleware("http")
async def debug_cors_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # Debug: Print response headers for CORS debugging
    if any('access-control' in header.lower() for header, value in response.headers.items()):
        print(f"CORS Response headers for {request.method} {request.url.path}:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
    
    return response

# Handle OPTIONS preflight requests
@app.options("/{path:path}")
async def options_handler(request: Request, path: str):
    """Handle CORS preflight requests"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, Accept, Origin, User-Agent, Cache-Control, Pragma",
            "Access-Control-Max-Age": "3600"
        }
    )

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

# Add CORS middleware with comprehensive configuration (this is now handled by setup_cors)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=cors_origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
#     allow_headers=["*"],
#     expose_headers=["*"],
# )

app.include_router(run_router)
app.include_router(calendar_router)
app.include_router(obsidian_router)
app.include_router(vault_management_router)
app.include_router(enhanced_workflows_router)
app.include_router(planner_router)
app.include_router(workflow_router)

status_router = APIRouter()


@status_router.get("/status")
async def status() -> dict[str, str]:
    """Return basic service health information."""
    return {
        "status": "ok",
        "version": pkg_resources.get_distribution("evoagentx").version,
    }


@status_router.get("/health")
async def health_check():
    """Enhanced health check with dev-pipe integration status"""
    try:
        # Update dev-pipe system status
        await dev_pipe.update_system_status("server", {
            "status": "healthy",
            "services": {
                "obsidian_api": "active",
                "vault_management": "active", 
                "enhanced_workflows": "active",
                "websocket": "active"
            },
            "dev_pipe_integration": "active",
            "last_health_check": datetime.now().isoformat()
        })
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": pkg_resources.get_distribution("evoagentx").version,
            "services": {
                "obsidian_integration": "active",
                "vault_management": "active",
                "enhanced_workflows": "active",
                "dev_pipe_integration": "active",
                "websocket": "active"
            },
            "dev_pipe": {
                "status": "connected",
                "communication_active": True,
                "task_tracking": True,
                "error_handling": True
            }
        }
    except Exception as e:
        await dev_pipe.log_message("error", f"Health check failed: {str(e)}")
        return {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "dev_pipe_integration": "error"
        }

@status_router.get("/dev-pipe/status")
async def dev_pipe_status():
    """Get detailed dev-pipe system status"""
    try:
        # Get recent activity from dev-pipe logs
        logs_dir = dev_pipe.logs_dir
        tasks_dir = dev_pipe.tasks_dir
        
        # Count active tasks
        active_tasks = len(list((tasks_dir / "active").glob("*.json"))) if (tasks_dir / "active").exists() else 0
        pending_tasks = len(list((tasks_dir / "pending").glob("*.json"))) if (tasks_dir / "pending").exists() else 0
        completed_tasks = len(list((tasks_dir / "completed").glob("*.json"))) if (tasks_dir / "completed").exists() else 0
        failed_tasks = len(list((tasks_dir / "failed").glob("*.json"))) if (tasks_dir / "failed").exists() else 0
        
        return {
            "dev_pipe_status": "operational",
            "communication": {
                "protocol_version": "1.0.0",
                "message_queues": "active",
                "task_tracking": "active",
                "error_handling": "active"
            },
            "task_statistics": {
                "active_tasks": active_tasks,
                "pending_tasks": pending_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "total_tasks": active_tasks + pending_tasks + completed_tasks + failed_tasks
            },
            "system_integration": {
                "vault_management": "integrated",
                "enhanced_workflows": "integrated",
                "obsidian_api": "integrated",
                "websocket_support": "integrated"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        await dev_pipe.log_message("error", f"Dev-pipe status check failed: {str(e)}")
        return {
            "dev_pipe_status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
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
    """Enhanced WebSocket endpoint for Obsidian plugin connections with dev-pipe integration"""
    connection_id = await obsidian_ws_manager.connect(websocket, vault_id)
    
    # Log WebSocket connection via dev-pipe
    await dev_pipe.log_message("info", f"Obsidian WebSocket connected: {vault_id or 'default'}", {
        "connection_id": connection_id,
        "vault_id": vault_id
    })
    
    try:
        while True:
            # Receive messages from Obsidian
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                # Log message receipt via dev-pipe
                await dev_pipe.log_message("debug", f"WebSocket message received: {message_type}", {
                    "connection_id": connection_id,
                    "message_type": message_type
                })
                
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
                    msg_vault_id = message.get("vault_id")
                    if msg_vault_id:
                        await obsidian_ws_manager.send_to_vault(msg_vault_id, {
                            "type": "vault_sync",
                            "update": message.get("update", {}),
                            "timestamp": datetime.now().isoformat()
                        })
                elif message_type == "task_progress":
                    # Handle task progress updates
                    task_id = message.get("task_id")
                    if task_id:
                        await dev_pipe.notify_progress(
                            task_id, 
                            message.get("operation", "unknown"),
                            message.get("progress", 0),
                            details=message.get("details", {})
                        )
                        
                        # Broadcast progress to other connections
                        await obsidian_ws_manager.send_to_vault(vault_id or "default", {
                            "type": "task_progress",
                            "task_id": task_id,
                            "progress": message.get("progress", 0),
                            "timestamp": datetime.now().isoformat()
                        })
                        
            except json.JSONDecodeError:
                await obsidian_ws_manager.send_to_connection(connection_id, {
                    "type": "error",
                    "message": "Invalid JSON received",
                    "timestamp": datetime.now().isoformat()
                })
                
                await dev_pipe.log_message("error", "Invalid JSON received via WebSocket", {
                    "connection_id": connection_id,
                    "raw_data": data[:200]  # Log first 200 chars for debugging
                })
                
    except WebSocketDisconnect:
        await dev_pipe.log_message("info", f"Obsidian WebSocket disconnected: {vault_id or 'default'}", {
            "connection_id": connection_id
        })
        obsidian_ws_manager.disconnect(connection_id)
    except Exception as e:
        await dev_pipe.log_message("error", f"WebSocket error: {str(e)}", {
            "connection_id": connection_id,
            "error_type": type(e).__name__
        })
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
