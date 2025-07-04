"""
VaultPilot EvoAgentX Integration Package

Complete server-side integration package for connecting VaultPilot Obsidian plugin
with EvoAgentX AI backend services.
"""

from .api_models import *
from .obsidian_routes import obsidian_router
from .vault_analyzer import VaultAnalyzer
from .copilot_engine import CopilotEngine
from .workflow_processor import WorkflowProcessor
from .agent_manager import AgentManager
from .websocket_handler import websocket_manager
from .cors_config import setup_cors

__version__ = "1.0.0"
__author__ = "VaultPilot Integration Team"

# Export main components for easy integration
__all__ = [
    # FastAPI router
    "obsidian_router",
    
    # Service classes
    "VaultAnalyzer",
    "CopilotEngine", 
    "WorkflowProcessor",
    "AgentManager",
    
    # WebSocket manager
    "websocket_manager",
    
    # Configuration
    "setup_cors",
    
    # Models (re-exported from api_models)
    "ChatRequest",
    "ChatResponse", 
    "CopilotRequest",
    "CopilotResponse",
    "WorkflowRequest",
    "WorkflowResponse",
    "Agent",
    "AgentCreateRequest",
    "AgentExecuteRequest",
    "VaultAnalysisResponse",
    "VaultStats",
    "VaultContext",
    "APIResponse",
    "HealthResponse",
    "ErrorResponse"
]

def get_integration_info():
    """Get integration package information"""
    return {
        "name": "VaultPilot EvoAgentX Integration",
        "version": __version__,
        "description": "Complete integration package for VaultPilot Obsidian plugin",
        "components": {
            "api_routes": "FastAPI routes for all VaultPilot endpoints",
            "service_classes": "Business logic implementations for AI services",
            "data_models": "Pydantic models for request/response validation",
            "websocket_handler": "Real-time communication support",
            "copilot_prompt": "Specialized AI agent prompt for knowledge management",
            "cors_config": "Cross-origin resource sharing configuration"
        },
        "endpoints": [
            "POST /api/obsidian/chat",
            "POST /api/obsidian/copilot", 
            "POST /api/obsidian/workflow",
            "GET /api/obsidian/agents",
            "POST /api/obsidian/agents",
            "POST /api/obsidian/agents/{agent_id}/execute",
            "POST /api/obsidian/vault/context",
            "POST /api/obsidian/planning/tasks",
            "POST /api/obsidian/intelligence/parse",
            "POST /api/obsidian/memory/update",
            "WS /ws/obsidian"
        ],
        "features": [
            "AI-powered chat assistance",
            "Intelligent auto-completion",
            "Complex workflow execution", 
            "Specialized AI agents",
            "Vault analysis and insights",
            "Real-time WebSocket communication",
            "Task planning and management",
            "Content intelligence parsing"
        ]
    }

def quick_setup_guide():
    """Get quick setup instructions"""
    return """
    VaultPilot Integration Quick Setup:
    
    1. Copy integration files to your EvoAgentX project
    2. Install dependencies: pip install fastapi uvicorn websockets pydantic
    3. Add to your FastAPI app:
       
       from vaultpilot_integration import obsidian_router, websocket_manager, setup_cors
       
       setup_cors(app, development=True)
       app.include_router(obsidian_router, prefix="/api/obsidian")
       
       @app.websocket("/ws/obsidian")
       async def websocket_endpoint(websocket: WebSocket):
           await websocket_manager.connect(websocket)
    
    4. Implement business logic in service classes
    5. Configure VaultPilot plugin to point to your server
    6. Test endpoints and WebSocket connection
    
    See IMPLEMENTATION_GUIDE.md for detailed instructions.
    """
