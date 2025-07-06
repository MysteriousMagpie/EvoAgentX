"""
Enhanced API Routes for VaultPilot Experience Improvements

These routes provide improved performance, progress tracking, and UX enhancements
for all VaultPilot operations.
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from typing import Dict, Any, Optional, List
import asyncio
import json
import uuid
from datetime import datetime

from .api_models import (
    APIResponse, ChatRequest, ChatResponse, CopilotRequest, CopilotResponse,
    WorkflowRequest, WorkflowResponse, VaultContextRequest, VaultContextResponse
)
from .experience_enhancements import (
    ExperienceEnhancementEngine, OperationType, ProgressIndicatorManager, 
    KeyboardShortcutManager, ResponseOptimizer
)
from .websocket_handler import WebSocketManager

# Create enhanced router
enhanced_router = APIRouter(prefix="/api/obsidian", tags=["Enhanced VaultPilot"])

# Global instances (would be dependency injected in production)
websocket_manager = WebSocketManager()
enhancement_engine = ExperienceEnhancementEngine(websocket_manager)


@enhanced_router.websocket("/ws/enhanced")
async def enhanced_websocket_endpoint(websocket: WebSocket, vault_id: str = "default"):
    """Enhanced WebSocket endpoint with progress tracking"""
    await websocket_manager.connect(websocket, vault_id)
    
    try:
        while True:
            # Listen for client messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            message_type = message.get("type", "unknown")
            
            if message_type == "ping":
                await websocket_manager.send_to_connection(websocket, {
                    "type": "pong",
                    "data": {"timestamp": datetime.now().isoformat()}
                })
                
            elif message_type == "shortcut_request":
                shortcuts = enhancement_engine.get_keyboard_shortcuts()
                await websocket_manager.send_to_connection(websocket, {
                    "type": "shortcuts",
                    "data": shortcuts
                })
                
            elif message_type == "performance_stats":
                stats = enhancement_engine.get_performance_stats()
                await websocket_manager.send_to_connection(websocket, {
                    "type": "performance_stats", 
                    "data": stats
                })
                
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket, vault_id)


@enhanced_router.post("/enhanced/chat", response_model=APIResponse)
async def enhanced_chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """Enhanced chat endpoint with response optimization and progress tracking"""
    
    try:
        # Apply enhancements
        optimized_request, metrics = await enhancement_engine.enhanced_execute(
            operation="chat",
            data=request.dict(),
            vault_id=getattr(request, 'vault_id', 'default'),
            operation_type=OperationType.AI_PROCESSING,
            context={'content_required': True}
        )
        
        # TODO: Integrate with your actual chat processing
        # For now, simulate response
        await asyncio.sleep(0.1)  # Simulate AI processing
        
        response_data = {
            "message": f"Enhanced response to: {request.message}",
            "conversation_id": request.conversation_id or str(uuid.uuid4()),
            "response_time": metrics.response_time,
            "optimizations_applied": metrics.optimizations_applied,
            "suggestions": [
                "Try using the Smart Search (Ctrl+Shift+S)",
                "Use Workflow Modal (Ctrl+Shift+W) for complex tasks",
                "Access AI Copilot with Ctrl+Space"
            ]
        }
        
        return APIResponse(
            success=True,
            data=response_data,
            message="Chat response with enhancements"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced chat failed: {str(e)}")


@enhanced_router.post("/enhanced/copilot", response_model=APIResponse)
async def enhanced_copilot(request: CopilotRequest):
    """Enhanced copilot with faster response times and better suggestions"""
    
    try:
        # Apply response optimizations
        optimized_request, metrics = await enhancement_engine.enhanced_execute(
            operation="copilot",
            data=request.dict(),
            vault_id=getattr(request, 'vault_id', 'default'),
            operation_type=OperationType.AI_PROCESSING,
            context={'fast_response': True}
        )
        
        # Enhanced copilot logic
        suggestions = await _generate_enhanced_suggestions(request, metrics)
        
        response_data = {
            "suggestions": suggestions,
            "response_time": metrics.response_time,
            "cache_hit": metrics.cache_hit,
            "keyboard_shortcuts": {
                "accept": "Alt+Enter",
                "next": "Tab",
                "dismiss": "Esc"
            }
        }
        
        return APIResponse(
            success=True,
            data=response_data,
            message="Enhanced copilot suggestions"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced copilot failed: {str(e)}")


@enhanced_router.post("/enhanced/workflow", response_model=APIResponse)
async def enhanced_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """Enhanced workflow execution with detailed progress tracking"""
    
    operation_id = str(uuid.uuid4())
    
    try:
        # Start progress tracking
        await enhancement_engine.progress_manager.start_operation(
            operation_id=operation_id,
            operation_type=OperationType.WORKFLOW_EXECUTION,
            vault_id=getattr(request, 'vault_id', 'default'),
            total_steps=6,
            description=f"Executing workflow: {request.goal}"
        )
        
        # Execute workflow with enhancements
        result, metrics = await enhancement_engine.enhanced_execute(
            operation="workflow",
            data=request.dict(),
            vault_id=getattr(request, 'vault_id', 'default'),
            operation_type=OperationType.WORKFLOW_EXECUTION,
            context={'track_progress': True},
            progress_callback=lambda op_id, data: _update_workflow_progress(op_id, data)
        )
        
        # Simulate workflow steps with progress updates
        await _execute_enhanced_workflow_steps(operation_id, request)
        
        response_data = {
            "goal": request.goal,
            "operation_id": operation_id,
            "status": "completed",
            "execution_time": metrics.response_time,
            "optimizations_applied": metrics.optimizations_applied,
            "keyboard_shortcuts": {
                "cancel": "Ctrl+C",
                "pause": "Ctrl+P",
                "details": "Ctrl+D"
            }
        }
        
        return APIResponse(
            success=True,
            data=response_data,
            message="Enhanced workflow execution completed"
        )
        
    except Exception as e:
        await enhancement_engine.progress_manager.fail_operation(
            operation_id, str(e)
        )
        raise HTTPException(status_code=500, detail=f"Enhanced workflow failed: {str(e)}")


@enhanced_router.post("/enhanced/vault/analyze", response_model=APIResponse)
async def enhanced_vault_analysis(request: VaultContextRequest, background_tasks: BackgroundTasks):
    """Enhanced vault analysis with progress indicators and optimization"""
    
    operation_id = str(uuid.uuid4())
    
    try:
        # Start operation tracking
        await enhancement_engine.progress_manager.start_operation(
            operation_id=operation_id,
            operation_type=OperationType.VAULT_ANALYSIS,
            vault_id=getattr(request, 'vault_id', 'default'),
            total_steps=5,
            description="Analyzing vault structure and content"
        )
        
        # Step 1: Optimize request
        await enhancement_engine.progress_manager.update_progress(
            operation_id, 1, "Optimizing analysis parameters..."
        )
        
        optimized_request, metrics = await enhancement_engine.enhanced_execute(
            operation="vault_analyze",
            data=request.dict(),
            vault_id=getattr(request, 'vault_id', 'default'),
            operation_type=OperationType.VAULT_ANALYSIS
        )
        
        # Step 2: Analyze structure
        await enhancement_engine.progress_manager.update_progress(
            operation_id, 2, "Analyzing vault structure..."
        )
        await asyncio.sleep(0.2)  # Simulate analysis
        
        # Step 3: Process content
        await enhancement_engine.progress_manager.update_progress(
            operation_id, 3, "Processing vault content..."
        )
        await asyncio.sleep(0.3)  # Simulate processing
        
        # Step 4: Generate insights
        await enhancement_engine.progress_manager.update_progress(
            operation_id, 4, "Generating insights..."
        )
        await asyncio.sleep(0.2)  # Simulate insights
        
        # Complete operation
        await enhancement_engine.progress_manager.complete_operation(
            operation_id, "Vault analysis completed successfully"
        )
        
        response_data = {
            "vault_path": request.vault_path,
            "analysis": {
                "total_files": 150,  # Mock data
                "total_folders": 25,
                "insights": [
                    "Your vault is well-organized",
                    "Consider linking more notes together",
                    "Some files could benefit from tags"
                ],
                "optimization_suggestions": [
                    "Use Smart Search (Ctrl+Shift+S) to find connections",
                    "Try Vault Organizer (Ctrl+Shift+O) for better structure"
                ]
            },
            "operation_id": operation_id,
            "performance": {
                "response_time": metrics.response_time,
                "optimizations_applied": metrics.optimizations_applied,
                "cache_hit": metrics.cache_hit
            }
        }
        
        return APIResponse(
            success=True,
            data=response_data,
            message="Enhanced vault analysis completed"
        )
        
    except Exception as e:
        await enhancement_engine.progress_manager.fail_operation(
            operation_id, str(e)
        )
        raise HTTPException(status_code=500, detail=f"Enhanced vault analysis failed: {str(e)}")


@enhanced_router.get("/enhanced/shortcuts", response_model=APIResponse)
async def get_keyboard_shortcuts():
    """Get all available keyboard shortcuts and commands"""
    
    try:
        shortcuts_data = enhancement_engine.get_keyboard_shortcuts()
        
        return APIResponse(
            success=True,
            data=shortcuts_data,
            message="Keyboard shortcuts retrieved"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get shortcuts: {str(e)}")


@enhanced_router.get("/enhanced/performance", response_model=APIResponse)  
async def get_performance_stats():
    """Get performance statistics and optimization info"""
    
    try:
        stats = enhancement_engine.get_performance_stats()
        
        return APIResponse(
            success=True,
            data=stats,
            message="Performance statistics retrieved"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance stats: {str(e)}")


@enhanced_router.post("/enhanced/shortcuts/custom", response_model=APIResponse)
async def add_custom_shortcut(request: Dict[str, Any]):
    """Add custom keyboard shortcut"""
    
    try:
        shortcut = request.get("shortcut")
        command = request.get("command") 
        description = request.get("description", "")
        category = request.get("category", "custom")
        
        if not shortcut or not command:
            raise HTTPException(status_code=400, detail="Shortcut and command are required")
        
        enhancement_engine.shortcut_manager.add_custom_shortcut(
            shortcut, command, description, category
        )
        
        return APIResponse(
            success=True,
            data={"shortcut": shortcut, "command": command},
            message="Custom shortcut added successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add custom shortcut: {str(e)}")


# Helper functions

async def _generate_enhanced_suggestions(request: CopilotRequest, metrics) -> List[str]:
    """Generate enhanced copilot suggestions with context awareness"""
    
    # Basic suggestions with context
    base_suggestions = [
        f"Continue with: {request.text[-20:]}...",
        "Consider linking to related notes",
        "Add relevant tags for better organization"
    ]
    
    # Add performance-aware suggestions
    if metrics.cache_hit:
        base_suggestions.append("💡 Suggestion from cache (fast response)")
    else:
        base_suggestions.append("✨ Fresh AI-generated suggestion")
    
    return base_suggestions


async def _update_workflow_progress(operation_id: str, data: Any):
    """Update workflow progress during execution"""
    # This would be called during actual workflow execution
    pass


async def _execute_enhanced_workflow_steps(operation_id: str, request: WorkflowRequest):
    """Execute workflow steps with detailed progress tracking"""
    
    steps = [
        "Analyzing goal requirements...",
        "Breaking down into actionable steps...", 
        "Executing step 1 of workflow...",
        "Executing step 2 of workflow...",
        "Generating final output..."
    ]
    
    for i, step_description in enumerate(steps, 1):
        await enhancement_engine.progress_manager.update_progress(
            operation_id, i, step_description
        )
        await asyncio.sleep(0.2)  # Simulate work
    
    # Complete the workflow
    await enhancement_engine.progress_manager.complete_operation(
        operation_id, 
        "Workflow completed successfully",
        result_data={
            "artifacts_created": 2,
            "tasks_completed": 5,
            "time_saved": "15 minutes"
        }
    )
