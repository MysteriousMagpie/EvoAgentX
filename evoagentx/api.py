from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import time
import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from .tools.interpreter_docker import DockerInterpreter, DockerLimits, ALLOWED_RUNTIMES
# Import intelligent interpreter selector and OpenAI interpreter
from .tools.intelligent_interpreter_selector import (
    IntelligentInterpreterSelector, 
    ExecutionContext, 
    execute_smart
)
from .tools.openai_code_interpreter import OpenAICodeInterpreter

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


# Enhanced execution models
class SmartExecRequest(BaseModel):
    code: str
    language: str = "python"
    interpreter: Optional[str] = "auto"  # auto, python, docker, openai
    security_level: str = "medium"  # low, medium, high
    budget_limit: Optional[float] = None
    files: Optional[List[str]] = None
    visualization_needed: bool = False
    performance_priority: bool = False


class SmartExecResponse(BaseModel):
    output: str
    interpreter_used: str
    success: bool
    estimated_cost: float
    runtime_seconds: float
    analysis: Dict[str, Any]
    error: Optional[str] = None


class OpenAIExecRequest(BaseModel):
    code: str
    language: str = "python"
    files: Optional[List[str]] = None
    model: str = "gpt-4-1106-preview"


class OpenAIExecResponse(BaseModel):
    output: str
    generated_files: List[Dict[str, str]]
    uploaded_file_ids: List[str]
    success: bool
    error: Optional[str] = None


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

# Add DevPipe API endpoints for VaultPilot model selection
from fastapi import APIRouter

devpipe_router = APIRouter(prefix="/api/v1/devpipe", tags=["DevPipe"])

@devpipe_router.get("/health")
async def devpipe_health():
    """DevPipe health check endpoint for VaultPilot integration"""
    return {
        "status": "healthy",
        "service": "devpipe",
        "timestamp": time.time(),
        "model_selection_available": True,
        "integration_status": "active"
    }

@devpipe_router.get("/status")
async def devpipe_status():
    """DevPipe status endpoint"""
    return {
        "status": "running",
        "service": "devpipe-model-selection",
        "version": "1.0.0",
        "timestamp": time.time(),
        "features": {
            "model_selection": True,
            "health_monitoring": True,
            "performance_tracking": True
        }
    }

@devpipe_router.post("/message")
async def devpipe_message(message: dict):
    """Handle DevPipe messages from VaultPilot"""
    # Process devpipe message
    message_type = message.get("header", {}).get("message_type", "unknown")
    
    if message_type == "model_selection_request":
        # Handle model selection request
        return {
            "header": {
                "message_id": str(time.time()),
                "timestamp": time.time(),
                "message_type": "model_selection_response",
                "correlation_id": message.get("header", {}).get("message_id")
            },
            "payload": {
                "success": True,
                "selected_model": {
                    "name": "gpt-4o-mini",
                    "provider": "openai",
                    "capabilities": ["chat", "text_analysis"]
                },
                "reasoning": "Default model selection"
            }
        }
    
    return {
        "status": "received",
        "message_type": message_type,
        "timestamp": time.time()
    }

# Include DevPipe router
app.include_router(devpipe_router)


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


@app.websocket("/api/obsidian/ws/enhanced")
async def enhanced_websocket_endpoint(websocket: WebSocket, vault_id: str = "default"):
    """
    Enhanced WebSocket endpoint for VaultPilot real-time communication
    
    This enables enhanced features:
    - Real-time chat updates
    - Vault synchronization 
    - Agent status updates
    - Workflow progress notifications
    - Enhanced features support
    """
    if not VAULTPILOT_AVAILABLE or not websocket_manager:
        await websocket.close(code=1000, reason="VaultPilot integration not available")
        return
    
    # Accept connection manually
    await websocket.accept()
    
    # Add to websocket manager without sending default welcome message
    if vault_id not in websocket_manager.connections:
        websocket_manager.connections[vault_id] = set()
    websocket_manager.connections[vault_id].add(websocket)
    
    # Send enhanced welcome message
    welcome_message = {
        "type": "connection",
        "data": {
            "status": "connected",
            "enhanced": True,
            "features": ["real-time-updates", "vault-sync", "agent-status"],
            "timestamp": datetime.now().isoformat()
        }
    }
    await websocket_manager.send_to_connection(websocket, welcome_message)
    
    try:
        while True:
            # Listen for incoming messages
            data = await websocket.receive_text()
            
            # Process the message
            try:
                message = json.loads(data)
                
                # Handle different message types for enhanced features
                if message.get("type") == "ping":
                    await websocket_manager.send_to_connection(websocket, {
                        "type": "pong",
                        "data": {"status": "alive", "enhanced": True}
                    })
                    
                elif message.get("type") == "vault_sync":
                    # Handle vault synchronization
                    await websocket_manager.send_to_connection(websocket, {
                        "type": "vault_sync_response",
                        "data": {"status": "synced", "timestamp": datetime.now().isoformat()}
                    })
                    
                elif message.get("type") == "agent_status":
                    # Handle agent status requests
                    await websocket_manager.send_to_connection(websocket, {
                        "type": "agent_status_response", 
                        "data": {"status": "active", "enhanced_features": True}
                    })
                    
                elif message.get("type") == "broadcast":
                    # Broadcast to all connections in vault
                    await websocket_manager.broadcast_to_vault(vault_id, message)
                    
                else:
                    # Echo back with enhanced flag
                    await websocket_manager.send_to_connection(websocket, {
                        "type": "echo",
                        "data": message,
                        "enhanced": True
                    })
                    
            except json.JSONDecodeError:
                await websocket_manager.send_to_connection(websocket, {
                    "type": "error",
                    "data": {"message": "Invalid JSON format"},
                    "enhanced": True
                })
                
    except WebSocketDisconnect:
        # Clean up connection manually  
        if vault_id in websocket_manager.connections:
            websocket_manager.connections[vault_id].discard(websocket)
            if not websocket_manager.connections[vault_id]:
                del websocket_manager.connections[vault_id]


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
            "vaultpilot_websocket": "/ws/obsidian" if VAULTPILOT_AVAILABLE else "Not available",
            "vaultpilot_websocket_enhanced": "/api/obsidian/ws/enhanced" if VAULTPILOT_AVAILABLE else "Not available"
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


@app.post("/execute/smart", response_model=SmartExecResponse)
def execute_smart_endpoint(req: SmartExecRequest):
    """
    Execute code using intelligent interpreter selection.
    Automatically chooses the best interpreter based on code analysis and context.
    """
    start = time.monotonic()
    
    try:
        context = ExecutionContext(
            security_level=req.security_level,
            budget_limit=req.budget_limit,
            files_required=req.files or [],
            visualization_needed=req.visualization_needed,
            performance_priority=req.performance_priority
        )
        
        if req.interpreter == "auto":
            # Use intelligent selection
            result = execute_smart(
                code=req.code,
                language=req.language,
                security_level=req.security_level,
                budget_limit=req.budget_limit,
                files=req.files
            )
        else:
            # Use specified interpreter
            selector = IntelligentInterpreterSelector()
            if req.interpreter == "python":
                from .tools.interpreter_python import PythonInterpreter
                interpreter = PythonInterpreter()
            elif req.interpreter == "docker":
                interpreter = DockerInterpreter(print_stdout=False, print_stderr=False)
            elif req.interpreter == "openai":
                interpreter = OpenAICodeInterpreter()
            else:
                raise HTTPException(status_code=400, detail=f"Invalid interpreter: {req.interpreter}")
            
            output = interpreter.execute(req.code, req.language)
            result = {
                'output': output,
                'interpreter_used': req.interpreter,
                'analysis': selector.analyze_code(req.code),
                'estimated_cost': selector.estimate_openai_cost(req.code) if req.interpreter == "openai" else 0,
                'success': True
            }
        
        runtime = time.monotonic() - start
        
        return SmartExecResponse(
            output=result['output'],
            interpreter_used=result['interpreter_used'],
            success=result['success'],
            estimated_cost=result['estimated_cost'],
            runtime_seconds=runtime,
            analysis=result['analysis'],
            error=result.get('error')
        )
        
    except Exception as e:
        runtime = time.monotonic() - start
        return SmartExecResponse(
            output="",
            interpreter_used="error",
            success=False,
            estimated_cost=0,
            runtime_seconds=runtime,
            analysis={},
            error=str(e)
        )


@app.post("/execute/openai", response_model=OpenAIExecResponse)
def execute_openai_endpoint(req: OpenAIExecRequest):
    """
    Execute code using OpenAI's Code Interpreter with optional file uploads.
    """
    try:
        interpreter = OpenAICodeInterpreter(model=req.model)
        
        if req.files:
            # Execute with files
            result = interpreter.execute_with_files(req.code, req.files, req.language)
            return OpenAIExecResponse(
                output=result.get('output', ''),
                generated_files=result.get('generated_files', []),
                uploaded_file_ids=result.get('uploaded_file_ids', []),
                success='error' not in result,
                error=result.get('error')
            )
        else:
            # Simple execution
            output = interpreter.execute(req.code, req.language)
            return OpenAIExecResponse(
                output=output,
                generated_files=[],
                uploaded_file_ids=[],
                success=not output.startswith('Error:'),
                error=output if output.startswith('Error:') else None
            )
            
    except Exception as e:
        return OpenAIExecResponse(
            output="",
            generated_files=[],
            uploaded_file_ids=[],
            success=False,
            error=str(e)
        )


@app.post("/analyze-code")
def analyze_code_endpoint(request: dict):
    """
    Analyze code and provide interpreter recommendations
    """
    try:
        code = request.get('code', '')
        selector = IntelligentInterpreterSelector()
        
        # Analyze the code
        analysis = selector.analyze_code(code)
        
        # Get recommendation
        context = ExecutionContext()
        recommended_interpreter = selector.select_interpreter(code, context)
        
        # Estimate cost
        estimated_cost = selector.estimate_openai_cost(code)
        
        return {
            "analysis": analysis,
            "recommended_interpreter": recommended_interpreter.value,
            "estimated_cost": estimated_cost,
            "suggestions": _get_interpreter_suggestions(analysis)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def _get_interpreter_suggestions(analysis):
    """Generate human-readable suggestions based on analysis"""
    suggestions = []
    
    if analysis['has_visualization']:
        suggestions.append("Consider OpenAI interpreter for automatic chart generation")
    
    if analysis['security_risk_score'] > 2:
        suggestions.append("Use Docker interpreter for security isolation")
    
    if analysis['complexity_score'] < 5:
        suggestions.append("Local Python interpreter sufficient for simple code")
    
    if analysis['has_data_processing']:
        suggestions.append("OpenAI interpreter provides extensive data science libraries")
    
    return suggestions
