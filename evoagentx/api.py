from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import time
import os
import json

from .tools.interpreter_docker import DockerInterpreter, DockerLimits, ALLOWED_RUNTIMES

# Import VaultPilot integration
VAULTPILOT_AVAILABLE = False
websocket_manager = None

try:
    from evoagentx_integration.obsidian_routes import obsidian_router
    from evoagentx_integration.cors_config import setup_cors
    from evoagentx_integration.websocket_handler import WebSocketManager
    VAULTPILOT_AVAILABLE = True
    
    # Initialize WebSocket manager for VaultPilot
    websocket_manager = WebSocketManager()
except ImportError:
    print("VaultPilot integration not available. Install dependencies or check integration files.")
    obsidian_router = None
    setup_cors = None
    WebSocketManager = None

app = FastAPI(
    title="EvoAgentX API",
    description="EvoAgentX API with VaultPilot Integration",
    version="1.0.0"
)

# Setup CORS for VaultPilot integration
if VAULTPILOT_AVAILABLE and setup_cors:
    setup_cors(app, development=True)


class ExecRequest(BaseModel):
    code: str
    runtime: str = "python:3.11"
    limits: DockerLimits = DockerLimits()


class ExecResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    runtime_seconds: float


@app.post("/execute", response_model=ExecResponse)
def execute(req: ExecRequest):
    if req.runtime not in ALLOWED_RUNTIMES:
        raise HTTPException(status_code=400, detail="Invalid runtime")

    interpreter = DockerInterpreter(runtime=req.runtime, limits=req.limits, print_stdout=False, print_stderr=False)
    language = "node" if req.runtime.startswith("node") else "python"
    start = time.monotonic()
    try:
        output = interpreter.execute(req.code, language)
        runtime = time.monotonic() - start
        return ExecResponse(stdout=output, stderr="", exit_code=0, runtime_seconds=runtime)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Include VaultPilot routes if available
if VAULTPILOT_AVAILABLE and obsidian_router:
    app.include_router(obsidian_router, prefix="/api/obsidian", tags=["VaultPilot"])
    print("✅ VaultPilot integration loaded successfully")
    print("📍 Available endpoints:")
    print("   - /api/obsidian/chat")
    print("   - /api/obsidian/vault/analyze") 
    print("   - /api/obsidian/workflow")
    print("   - /api/obsidian/copilot/complete")
    print("   - /ws/obsidian (WebSocket)")


@app.websocket("/ws/obsidian")
async def websocket_endpoint(websocket: WebSocket, vault_id: str = "default"):
    """
    WebSocket endpoint for VaultPilot real-time communication
    
    This enables:
    - Real-time chat updates
    - Workflow progress notifications  
    - Live copilot suggestions
    - Vault synchronization events
    """
    if not VAULTPILOT_AVAILABLE or not websocket_manager:
        await websocket.close(code=1000, reason="VaultPilot integration not available")
        return
        
    await websocket_manager.connect(websocket, vault_id)
    
    try:
        while True:
            # Listen for incoming messages
            data = await websocket.receive_text()
            
            # Process the message (you can customize this)
            try:
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket_manager.send_to_connection(websocket, {
                        "type": "pong",
                        "data": {"status": "alive"}
                    })
                    
                elif message.get("type") == "broadcast":
                    # Broadcast to all connections in vault
                    await websocket_manager.broadcast_to_vault(vault_id, message)
                    
                else:
                    # Echo back for now
                    await websocket_manager.send_to_connection(websocket, {
                        "type": "echo",
                        "data": message
                    })
                    
            except json.JSONDecodeError:
                await websocket_manager.send_to_connection(websocket, {
                    "type": "error",
                    "data": {"message": "Invalid JSON format"}
                })
                
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket, vault_id)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "EvoAgentX API Server",
        "version": "1.0.0",
        "vaultpilot_integration": VAULTPILOT_AVAILABLE,
        "endpoints": {
            "code_execution": "/execute",
            "vaultpilot_chat": "/api/obsidian/chat" if VAULTPILOT_AVAILABLE else "Not available",
            "vaultpilot_websocket": "/ws/obsidian" if VAULTPILOT_AVAILABLE else "Not available"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "vaultpilot_integration": VAULTPILOT_AVAILABLE
    }


@app.get("/status")
async def status_check():
    """Status endpoint for server monitoring"""
    return {
        "status": "running",
        "server": "EvoAgentX",
        "version": "1.0.0",
        "timestamp": time.time(),
        "vaultpilot_integration": VAULTPILOT_AVAILABLE,
        "uptime": "active"
    }


@app.get("/ws/status")
async def websocket_status():
    """WebSocket connection status and diagnostics"""
    if not VAULTPILOT_AVAILABLE or not websocket_manager:
        return {
            "websocket_available": False,
            "error": "VaultPilot integration not available"
        }
    
    return {
        "websocket_available": True,
        "active_connections": websocket_manager.get_connection_count(),
        "active_vaults": websocket_manager.get_active_vaults(),
        "connection_details": {
            vault_id: websocket_manager.get_connection_count(vault_id) 
            for vault_id in websocket_manager.get_active_vaults()
        },
        "endpoint": "ws://127.0.0.1:8000/ws/obsidian",
        "timestamp": time.time()
    }
