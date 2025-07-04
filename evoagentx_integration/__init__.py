"""
VaultPilot EvoAgentX Integration Package

Enhanced server-side integration package for connecting VaultPilot Obsidian plugin
with EvoAgentX AI backend services.

Features advanced capabilities including agent evolution, marketplace integration,
and multi-modal intelligence processing.
"""

# Core integration components
from .api_models import *
from .obsidian_routes import obsidian_router
from .websocket_handler import websocket_manager
from .cors_config import setup_cors

# Service implementations
from .vault_analyzer import VaultAnalyzer
from .copilot_engine import CopilotEngine
from .workflow_processor import WorkflowProcessor
from .agent_manager import AgentManager

# Enhanced features
from .agent_evolution_system import (
    AgentEvolutionEngine, 
    EvolutionStrategy, 
    AgentDNA, 
    InteractionFeedback
)
from .marketplace_integrator import (
    EvoAgentXMarketplace,
    MarketplaceAgent,
    AgentCategory,
    AgentComplexity
)
from .multimodal_intelligence import (
    MultiModalIntelligenceEngine,
    ModalityType,
    ProcessingCapability,
    MediaAsset
)
from .evoagentx_workflow_integrator import EvoAgentXWorkflowIntegrator
from .calendar_integration import CalendarIntegration
from .enhanced_intelligence_parser import EnhancedIntelligenceParser
from .performance_monitor import PerformanceMonitor

__version__ = "2.0.0"
__author__ = "VaultPilot Team"
__license__ = "MIT"

# Export main components for easy integration
__all__ = [
    # Core FastAPI components
    "obsidian_router",
    "websocket_manager", 
    "setup_cors",
    
    # Service classes
    "VaultAnalyzer",
    "CopilotEngine", 
    "WorkflowProcessor",
    "AgentManager",
    
    # Enhanced AI systems
    "AgentEvolutionEngine",
    "EvoAgentXMarketplace", 
    "MultiModalIntelligenceEngine",
    "EvoAgentXWorkflowIntegrator",
    "CalendarIntegration",
    "EnhancedIntelligenceParser",
    "PerformanceMonitor",
    
    # Data models and enums
    "ChatRequest",
    "ChatResponse", 
    "CopilotRequest",
    "CopilotResponse",
    "WorkflowRequest",
    "WorkflowResponse",
    "Agent",
    "AgentDNA",
    "InteractionFeedback",
    "MarketplaceAgent", 
    "MediaAsset",
    "EvolutionStrategy",
    "AgentCategory",
    "AgentComplexity",
    "ModalityType",
    "ProcessingCapability",
    
    # Utility functions
    "get_integration_info",
    "setup_vaultpilot_integration",
    "get_quick_start_guide"
]

def get_integration_info():
    """Get comprehensive integration package information"""
    return {
        "package": {
            "name": "VaultPilot EvoAgentX Integration",
            "version": __version__,
            "description": "Advanced AI integration for Obsidian knowledge management",
            "author": __author__,
            "license": __license__
        },
        "core_features": [
            "FastAPI endpoints for Obsidian communication",
            "WebSocket support for real-time features", 
            "CORS configuration for cross-origin requests",
            "Pydantic models for request/response validation",
            "AI-powered chat with vault context",
            "Intelligent auto-completion and copilot",
            "Complex workflow execution system"
        ],
        "advanced_features": [
            "Agent Evolution System - Self-improving AI agents",
            "Marketplace Integration - Discover and install specialized agents", 
            "Multi-Modal Intelligence - Process text, images, audio, data",
            "Enhanced Workflow Templates - Advanced automation patterns",
            "Calendar Integration - Smart scheduling and synchronization",
            "Performance Monitoring - Real-time analytics and optimization"
        ],
        "endpoints": {
            "core": [
                "POST /api/obsidian/chat",
                "POST /api/obsidian/copilot", 
                "POST /api/obsidian/workflow",
                "GET /api/obsidian/agents",
                "WS /ws/obsidian"
            ],
            "enhanced": [
                "POST /api/obsidian/agents/evolve",
                "GET /api/obsidian/marketplace",
                "POST /api/obsidian/multimodal/analyze", 
                "POST /api/obsidian/calendar/sync",
                "GET /api/obsidian/performance/stats"
            ]
        },
        "requirements": [
            "fastapi>=0.68.0",
            "uvicorn>=0.15.0", 
            "websockets>=10.0",
            "pydantic>=1.8.0",
            "python-multipart>=0.0.5"
        ]
    }

def setup_vaultpilot_integration(app, 
                                evolution_engine=None,
                                marketplace=None, 
                                multimodal_engine=None,
                                enable_cors=True,
                                development_mode=False):
    """
    Setup complete VaultPilot integration with enhanced features
    
    Args:
        app: FastAPI application instance
        evolution_engine: Optional AgentEvolutionEngine instance
        marketplace: Optional EvoAgentXMarketplace instance
        multimodal_engine: Optional MultiModalIntelligenceEngine instance
        enable_cors: Whether to enable CORS
        development_mode: Enable development features
    
    Returns:
        Dictionary with integration status and component references
    """
    # Setup CORS
    if enable_cors:
        setup_cors(app, development=development_mode)
    
    # Add core routes
    app.include_router(obsidian_router, prefix="/api/obsidian")
    
    # Initialize enhanced features if not provided
    if evolution_engine is None:
        evolution_engine = AgentEvolutionEngine()
    
    if marketplace is None:
        marketplace = EvoAgentXMarketplace(evolution_engine)
    
    if multimodal_engine is None:
        multimodal_engine = MultiModalIntelligenceEngine()
    
    # Store components in app state for access in routes
    app.state.evolution_engine = evolution_engine
    app.state.marketplace = marketplace  
    app.state.multimodal_engine = multimodal_engine
    
    # Initialize additional components
    app.state.workflow_integrator = EvoAgentXWorkflowIntegrator()
    app.state.calendar_integration = CalendarIntegration()
    app.state.intelligence_parser = EnhancedIntelligenceParser()
    app.state.performance_monitor = PerformanceMonitor()
    
    return {
        "status": "success",
        "message": "VaultPilot integration configured with enhanced features",
        "components": {
            "evolution_engine": evolution_engine,
            "marketplace": marketplace,
            "multimodal_engine": multimodal_engine,
            "workflow_integrator": app.state.workflow_integrator,
            "calendar_integration": app.state.calendar_integration,
            "intelligence_parser": app.state.intelligence_parser,
            "performance_monitor": app.state.performance_monitor
        },
        "endpoints_configured": len(obsidian_router.routes),
        "advanced_features_enabled": True,
        "version": __version__
    }

def get_quick_start_guide():
    """Get quick start integration guide"""
    return """
    VaultPilot EvoAgentX Integration - Enhanced Quick Start
    =====================================================
    
    1. COPY INTEGRATION FILES:
       cp -r evoagentx_integration/ /path/to/your/evoagentx/project/
    
    2. INSTALL DEPENDENCIES:
       pip install fastapi uvicorn websockets pydantic python-multipart
    
    3. BASIC INTEGRATION:
       from fastapi import FastAPI
       from evoagentx_integration import setup_vaultpilot_integration
       
       app = FastAPI()
       result = setup_vaultpilot_integration(app, development_mode=True)
       print(f"Integration status: {result['status']}")
    
    4. MANUAL SETUP (for more control):
       from fastapi import FastAPI
       from evoagentx_integration import (
           obsidian_router, setup_cors,
           AgentEvolutionEngine, EvoAgentXMarketplace, 
           MultiModalIntelligenceEngine
       )
       
       app = FastAPI()
       setup_cors(app, development=True)
       app.include_router(obsidian_router, prefix="/api/obsidian")
       
       # Initialize enhanced features
       evolution_engine = AgentEvolutionEngine()
       marketplace = EvoAgentXMarketplace(evolution_engine)
       multimodal = MultiModalIntelligenceEngine()
       
       # Store in app state
       app.state.evolution_engine = evolution_engine
       app.state.marketplace = marketplace
       app.state.multimodal_engine = multimodal
    
    5. START SERVER:
       uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    
    6. TEST INTEGRATION:
       curl http://localhost:8000/status
       # Should return EvoAgentX status
    
    ENHANCED FEATURES:
    - Agent Evolution: Agents improve based on user feedback
    - Marketplace: Discover and install specialized agents
    - Multi-Modal: Process images, audio, documents automatically
    - Advanced Workflows: Template-based automation
    - Calendar Sync: Integrate with system calendar
    - Performance Monitoring: Real-time usage analytics
    
    For detailed setup, see IMPLEMENTATION_GUIDE.md and INTEGRATION_SUMMARY.md
    """

def get_architecture_overview():
    """Get system architecture overview"""
    return {
        "core_layer": {
            "description": "Basic VaultPilot-EvoAgentX communication",
            "components": ["FastAPI routes", "WebSocket handler", "CORS config", "API models"]
        },
        "service_layer": {
            "description": "AI service implementations", 
            "components": ["Vault analyzer", "Copilot engine", "Workflow processor", "Agent manager"]
        },
        "intelligence_layer": {
            "description": "Advanced AI capabilities",
            "components": ["Agent evolution", "Marketplace", "Multi-modal processing", "Enhanced parsing"]
        },
        "integration_layer": {
            "description": "External system integrations",
            "components": ["Calendar sync", "Performance monitoring", "Workflow templates"]
        },
        "data_flow": [
            "1. Obsidian Plugin → FastAPI Endpoints",
            "2. API Validation → Service Layer", 
            "3. AI Processing → Intelligence Layer",
            "4. External Integrations → Response",
            "5. WebSocket Updates → Real-time UI"
        ]
    }

# Package initialization message
def _package_info():
    """Display package initialization info"""
    return f"""
    🚀 VaultPilot EvoAgentX Integration v{__version__}
    
    Enhanced AI integration package loaded with:
    ✅ Core API endpoints and WebSocket support
    ✅ Agent evolution and learning system  
    ✅ AI agent marketplace integration
    ✅ Multi-modal intelligence processing
    ✅ Advanced workflow automation
    ✅ Calendar and external integrations
    ✅ Performance monitoring and analytics
    
    Ready for integration with EvoAgentX backend!
    Use get_quick_start_guide() for setup instructions.
    """

# Print info when package is imported (optional)
# print(_package_info())
