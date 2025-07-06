"""
Enhanced Workflow Processor with Dev-Pipe Integration

This module implements enhanced workflow execution capabilities with proper
dev-pipe protocol integration for streaming progress, error handling, and
comprehensive monitoring.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Dict, List, Optional, Any, AsyncGenerator
import asyncio
import json
import time
from datetime import datetime
import uuid

from ..services.devpipe_integration import dev_pipe
from evoagentx.agents.vault_manager import VaultManagerAgent
from evoagentx.models import OpenAILLMConfig
import os

router = APIRouter(prefix="/api/obsidian/workflow", tags=["enhanced-workflows"])

class WorkflowStatus:
    """Track workflow execution status"""
    def __init__(self):
        self.workflows: Dict[str, Dict[str, Any]] = {}
    
    def create_workflow(self, workflow_id: str, template_id: str, goal: str) -> Dict[str, Any]:
        workflow = {
            "workflow_id": workflow_id,
            "template_id": template_id,
            "goal": goal,
            "status": "initializing",
            "progress": 0,
            "current_step": "Starting workflow",
            "created_at": datetime.now().isoformat(),
            "estimated_completion": None,
            "steps": [],
            "results": {},
            "errors": []
        }
        self.workflows[workflow_id] = workflow
        return workflow
    
    def update_workflow(self, workflow_id: str, **updates):
        if workflow_id in self.workflows:
            self.workflows[workflow_id].update(updates)
            self.workflows[workflow_id]["updated_at"] = datetime.now().isoformat()
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        return self.workflows.get(workflow_id)

workflow_status = WorkflowStatus()

def get_llm_config():
    """Get the default LLM configuration"""
    return OpenAILLMConfig(
        model="gpt-4o-mini",
        openai_key=os.getenv("OPENAI_API_KEY"),
        stream=False,
        output_response=True,
        max_tokens=4000,
    )

def get_vault_manager(vault_root: Optional[str] = None) -> VaultManagerAgent:
    """Get or create the global vault manager instance"""
    return VaultManagerAgent(llm_config=get_llm_config(), vault_root=vault_root)

async def execute_workflow_step(workflow_id: str, step_name: str, step_function, 
                               progress_start: int, progress_end: int, **kwargs):
    """Execute a single workflow step with progress tracking"""
    
    workflow_status.update_workflow(workflow_id, 
                                   current_step=step_name,
                                   progress=progress_start)
    
    await dev_pipe.notify_progress(workflow_id, "workflow_execution", progress_start,
                                 details={"current_step": step_name})
    
    try:
        result = await step_function(**kwargs)
        
        workflow_status.update_workflow(workflow_id, progress=progress_end)
        await dev_pipe.notify_progress(workflow_id, "workflow_execution", progress_end,
                                     details={"step_completed": step_name})
        
        return result
        
    except Exception as e:
        await dev_pipe.handle_error(workflow_id, e, {"step": step_name})
        raise

@router.post("/execute")
async def execute_enhanced_workflow(request: Dict[str, Any], background_tasks: BackgroundTasks):
    """Execute workflow with advanced features and dev-pipe integration"""
    
    workflow_id = str(uuid.uuid4())
    template_id = request.get("template_id") or "default"  # Provide default template_id
    goal = request.get("goal", "")
    context = request.get("context", {})
    streaming = request.get("streaming", False)
    workspace_integration = request.get("workspace_integration", True)
    
    # Create dev-pipe task
    task_id = await dev_pipe.create_task(
        task_type="enhanced_workflow",
        operation="execute_workflow",
        parameters={
            "workflow_id": workflow_id,
            "template_id": template_id,
            "goal": goal,
            "streaming": streaming,
            "workspace_integration": workspace_integration
        }
    )
    
    # Create workflow status
    workflow = workflow_status.create_workflow(workflow_id, template_id, goal)
    
    if streaming:
        return StreamingResponse(
            stream_workflow_execution(workflow_id, template_id, goal, context, task_id),
            media_type="application/json"
        )
    else:
        background_tasks.add_task(
            execute_workflow_background, workflow_id, template_id, goal, context, task_id
        )
        
        return {
            "workflow_id": workflow_id,
            "status": "running",
            "progress": 0,
            "current_step": "Initializing workflow",
            "estimated_completion": datetime.now().isoformat(),
            "streaming": streaming
        }

async def stream_workflow_execution(workflow_id: str, template_id: str, goal: str, 
                                  context: Dict[str, Any], task_id: str) -> AsyncGenerator[str, None]:
    """Stream workflow execution progress"""
    
    try:
        async for update in execute_workflow_generator(workflow_id, template_id, goal, context, task_id):
            yield f"data: {json.dumps(update)}\n\n"
            
    except Exception as e:
        error_update = {
            "workflow_id": workflow_id,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        yield f"data: {json.dumps(error_update)}\n\n"

async def execute_workflow_background(workflow_id: str, template_id: str, goal: str,
                                    context: Dict[str, Any], task_id: str):
    """Execute workflow in background"""
    
    async for update in execute_workflow_generator(workflow_id, template_id, goal, context, task_id):
        # Updates are handled internally by the generator
        pass

async def execute_workflow_generator(workflow_id: str, template_id: str, goal: str,
                                   context: Dict[str, Any], task_id: str) -> AsyncGenerator[Dict[str, Any], None]:
    """Generator for workflow execution with progress updates"""
    
    try:
        manager = get_vault_manager()
        
        # Workflow execution based on template
        if template_id == "research_synthesis":
            async for update in execute_research_synthesis(workflow_id, goal, context, manager, task_id):
                yield update
                
        elif template_id == "content_optimization":
            async for update in execute_content_optimization(workflow_id, goal, context, manager, task_id):
                yield update
                
        elif template_id == "vault_organization":
            async for update in execute_vault_organization(workflow_id, goal, context, manager, task_id):
                yield update
                
        elif template_id == "knowledge_mapping":
            async for update in execute_knowledge_mapping(workflow_id, goal, context, manager, task_id):
                yield update
                
        else:
            async for update in execute_custom_workflow(workflow_id, goal, context, manager, task_id):
                yield update
                
    except Exception as e:
        await dev_pipe.handle_error(task_id, e, {"workflow_id": workflow_id})
        workflow_status.update_workflow(workflow_id, status="failed", error=str(e))
        
        yield {
            "workflow_id": workflow_id,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def execute_research_synthesis(workflow_id: str, goal: str, context: Dict[str, Any],
                                   manager: VaultManagerAgent, task_id: str) -> AsyncGenerator[Dict[str, Any], None]:
    """Execute research synthesis workflow"""
    
    yield {"workflow_id": workflow_id, "status": "running", "progress": 10, 
           "current_step": "Analyzing research materials"}
    
    # Step 1: Analyze source materials
    await execute_workflow_step(
        workflow_id, "Analyzing source materials",
        analyze_research_materials, 10, 30,
        context=context, manager=manager
    )
    
    yield {"workflow_id": workflow_id, "progress": 30, 
           "current_step": "Extracting key concepts"}
    
    # Step 2: Extract key concepts
    concepts = await execute_workflow_step(
        workflow_id, "Extracting key concepts",
        extract_key_concepts, 30, 50,
        context=context, manager=manager
    )
    
    yield {"workflow_id": workflow_id, "progress": 50,
           "current_step": "Synthesizing research", 
           "partial_results": {"concepts_found": len(concepts)}}
    
    # Step 3: Synthesize research
    synthesis = await execute_workflow_step(
        workflow_id, "Synthesizing research",
        synthesize_research, 50, 80,
        concepts=concepts, goal=goal, manager=manager
    )
    
    yield {"workflow_id": workflow_id, "progress": 80,
           "current_step": "Generating final document"}
    
    # Step 4: Generate final document
    final_document = await execute_workflow_step(
        workflow_id, "Generating final document",
        generate_synthesis_document, 80, 100,
        synthesis=synthesis, goal=goal, manager=manager
    )
    
    workflow_status.update_workflow(workflow_id, status="completed", progress=100,
                                   results={"document": final_document})
    
    await dev_pipe.send_completion_notification(
        task_id, "research_synthesis",
        {"workflow_id": workflow_id, "concepts_synthesized": len(concepts),
         "document_generated": bool(final_document)}
    )
    
    yield {"workflow_id": workflow_id, "status": "completed", "progress": 100,
           "results": {"synthesis_document": final_document}}

async def execute_content_optimization(workflow_id: str, goal: str, context: Dict[str, Any],
                                     manager: VaultManagerAgent, task_id: str) -> AsyncGenerator[Dict[str, Any], None]:
    """Execute content optimization workflow"""
    
    file_paths = context.get("target_files", [])
    optimization_type = context.get("parameters", {}).get("optimization_type", "general")
    
    yield {"workflow_id": workflow_id, "status": "running", "progress": 15,
           "current_step": "Analyzing content structure"}
    
    # Step 1: Analyze content
    analysis = await execute_workflow_step(
        workflow_id, "Analyzing content structure",
        analyze_content_structure, 15, 40,
        file_paths=file_paths, manager=manager
    )
    
    yield {"workflow_id": workflow_id, "progress": 40,
           "current_step": "Identifying optimization opportunities"}
    
    # Step 2: Identify optimizations
    optimizations = await execute_workflow_step(
        workflow_id, "Identifying optimization opportunities", 
        identify_optimizations, 40, 70,
        analysis=analysis, optimization_type=optimization_type, manager=manager
    )
    
    yield {"workflow_id": workflow_id, "progress": 70,
           "current_step": "Applying optimizations",
           "partial_results": {"optimizations_found": len(optimizations)}}
    
    # Step 3: Apply optimizations
    results = await execute_workflow_step(
        workflow_id, "Applying optimizations",
        apply_optimizations, 70, 100,
        optimizations=optimizations, file_paths=file_paths, manager=manager
    )
    
    workflow_status.update_workflow(workflow_id, status="completed", progress=100, results=results)
    
    await dev_pipe.send_completion_notification(
        task_id, "content_optimization",
        {"workflow_id": workflow_id, "files_optimized": len(file_paths),
         "optimizations_applied": len(optimizations)}
    )
    
    yield {"workflow_id": workflow_id, "status": "completed", "progress": 100, "results": results}

async def execute_vault_organization(workflow_id: str, goal: str, context: Dict[str, Any],
                                   manager: VaultManagerAgent, task_id: str) -> AsyncGenerator[Dict[str, Any], None]:
    """Execute vault organization workflow"""
    
    yield {"workflow_id": workflow_id, "status": "running", "progress": 10,
           "current_step": "Analyzing vault structure"}
    
    # Step 1: Analyze current structure
    structure_analysis = await execute_workflow_step(
        workflow_id, "Analyzing vault structure",
        analyze_vault_structure, 10, 30,
        manager=manager
    )
    
    yield {"workflow_id": workflow_id, "progress": 30,
           "current_step": "Generating organization plan"}
    
    # Step 2: Generate organization plan
    organization_plan = await execute_workflow_step(
        workflow_id, "Generating organization plan",
        generate_organization_plan, 30, 60,
        structure_analysis=structure_analysis, goal=goal, manager=manager
    )
    
    yield {"workflow_id": workflow_id, "progress": 60,
           "current_step": "Validating organization plan",
           "partial_results": {"plan_steps": len(organization_plan.get("steps", []))}}
    
    # Step 3: Validate plan
    validated_plan = await execute_workflow_step(
        workflow_id, "Validating organization plan",
        validate_organization_plan, 60, 80,
        plan=organization_plan, manager=manager
    )
    
    yield {"workflow_id": workflow_id, "progress": 80,
           "current_step": "Generating implementation guide"}
    
    # Step 4: Generate implementation guide
    implementation_guide = await execute_workflow_step(
        workflow_id, "Generating implementation guide",
        generate_implementation_guide, 80, 100,
        plan=validated_plan, manager=manager
    )
    
    results = {
        "organization_plan": validated_plan,
        "implementation_guide": implementation_guide
    }
    
    workflow_status.update_workflow(workflow_id, status="completed", progress=100, results=results)
    
    await dev_pipe.send_completion_notification(
        task_id, "vault_organization",
        {"workflow_id": workflow_id, "plan_generated": bool(validated_plan),
         "implementation_steps": len(implementation_guide.get("steps", []))}
    )
    
    yield {"workflow_id": workflow_id, "status": "completed", "progress": 100, "results": results}

async def execute_knowledge_mapping(workflow_id: str, goal: str, context: Dict[str, Any],
                                  manager: VaultManagerAgent, task_id: str) -> AsyncGenerator[Dict[str, Any], None]:
    """Execute knowledge mapping workflow"""
    
    focus_area = context.get("parameters", {}).get("focus_area", "general")
    depth = context.get("parameters", {}).get("depth", "medium")
    
    yield {"workflow_id": workflow_id, "status": "running", "progress": 15,
           "current_step": "Discovering knowledge nodes"}
    
    # Step 1: Discover knowledge nodes
    knowledge_nodes = await execute_workflow_step(
        workflow_id, "Discovering knowledge nodes",
        discover_knowledge_nodes, 15, 35,
        focus_area=focus_area, manager=manager
    )
    
    yield {"workflow_id": workflow_id, "progress": 35,
           "current_step": "Mapping relationships"}
    
    # Step 2: Map relationships
    relationships = await execute_workflow_step(
        workflow_id, "Mapping relationships",
        map_knowledge_relationships, 35, 65,
        nodes=knowledge_nodes, manager=manager
    )
    
    yield {"workflow_id": workflow_id, "progress": 65,
           "current_step": "Creating knowledge map",
           "partial_results": {"nodes_found": len(knowledge_nodes),
                              "relationships_mapped": len(relationships)}}
    
    # Step 3: Create knowledge map
    knowledge_map = await execute_workflow_step(
        workflow_id, "Creating knowledge map",
        create_knowledge_map, 65, 90,
        nodes=knowledge_nodes, relationships=relationships, depth=depth, manager=manager
    )
    
    yield {"workflow_id": workflow_id, "progress": 90,
           "current_step": "Generating insights"}
    
    # Step 4: Generate insights
    insights = await execute_workflow_step(
        workflow_id, "Generating insights",
        generate_knowledge_insights, 90, 100,
        knowledge_map=knowledge_map, focus_area=focus_area, manager=manager
    )
    
    results = {
        "knowledge_map": knowledge_map,
        "insights": insights,
        "nodes_count": len(knowledge_nodes),
        "relationships_count": len(relationships)
    }
    
    workflow_status.update_workflow(workflow_id, status="completed", progress=100, results=results)
    
    await dev_pipe.send_completion_notification(
        task_id, "knowledge_mapping",
        {"workflow_id": workflow_id, "nodes_mapped": len(knowledge_nodes),
         "insights_generated": len(insights)}
    )
    
    yield {"workflow_id": workflow_id, "status": "completed", "progress": 100, "results": results}

async def execute_custom_workflow(workflow_id: str, goal: str, context: Dict[str, Any],
                                manager: VaultManagerAgent, task_id: str) -> AsyncGenerator[Dict[str, Any], None]:
    """Execute custom workflow based on goal analysis"""
    
    yield {"workflow_id": workflow_id, "status": "running", "progress": 20,
           "current_step": "Analyzing workflow requirements"}
    
    # Step 1: Analyze requirements
    requirements = await execute_workflow_step(
        workflow_id, "Analyzing workflow requirements",
        analyze_workflow_requirements, 20, 50,
        goal=goal, context=context, manager=manager
    )
    
    yield {"workflow_id": workflow_id, "progress": 50,
           "current_step": "Executing custom workflow"}
    
    # Step 2: Execute based on requirements
    results = await execute_workflow_step(
        workflow_id, "Executing custom workflow",
        execute_custom_logic, 50, 100,
        requirements=requirements, goal=goal, context=context, manager=manager
    )
    
    workflow_status.update_workflow(workflow_id, status="completed", progress=100, results=results)
    
    await dev_pipe.send_completion_notification(
        task_id, "custom_workflow",
        {"workflow_id": workflow_id, "goal": goal, "results_generated": bool(results)}
    )
    
    yield {"workflow_id": workflow_id, "status": "completed", "progress": 100, "results": results}

# Workflow step implementations (placeholder functions that would be implemented based on specific needs)

async def analyze_research_materials(context: Dict[str, Any], manager: VaultManagerAgent):
    """Analyze research materials"""
    # Implementation would analyze provided materials
    return {"materials_analyzed": True}

async def extract_key_concepts(context: Dict[str, Any], manager: VaultManagerAgent):
    """Extract key concepts from research materials"""
    # Implementation would extract and return key concepts
    return ["concept1", "concept2", "concept3"]

async def synthesize_research(concepts: List[str], goal: str, manager: VaultManagerAgent):
    """Synthesize research findings"""
    # Implementation would synthesize research
    return {"synthesis": "Research synthesis content"}

async def generate_synthesis_document(synthesis: Dict[str, Any], goal: str, manager: VaultManagerAgent):
    """Generate final synthesis document"""
    # Implementation would generate final document
    return "Final synthesis document content"

async def analyze_content_structure(file_paths: List[str], manager: VaultManagerAgent):
    """Analyze content structure"""
    # Implementation would analyze content structure
    return {"structure_analysis": "Content structure analysis"}

async def identify_optimizations(analysis: Dict[str, Any], optimization_type: str, manager: VaultManagerAgent):
    """Identify optimization opportunities"""
    # Implementation would identify optimizations
    return ["optimization1", "optimization2"]

async def apply_optimizations(optimizations: List[str], file_paths: List[str], manager: VaultManagerAgent):
    """Apply identified optimizations"""
    # Implementation would apply optimizations
    return {"optimizations_applied": len(optimizations)}

async def analyze_vault_structure(manager: VaultManagerAgent):
    """Analyze vault structure"""
    # Implementation would analyze vault structure
    return {"structure_analysis": "Vault structure analysis"}

async def generate_organization_plan(structure_analysis: Dict[str, Any], goal: str, manager: VaultManagerAgent):
    """Generate organization plan"""
    # Implementation would generate organization plan
    return {"plan": "Organization plan", "steps": ["step1", "step2"]}

async def validate_organization_plan(plan: Dict[str, Any], manager: VaultManagerAgent):
    """Validate organization plan"""
    # Implementation would validate the plan
    return plan

async def generate_implementation_guide(plan: Dict[str, Any], manager: VaultManagerAgent):
    """Generate implementation guide"""
    # Implementation would generate implementation guide
    return {"guide": "Implementation guide", "steps": ["impl_step1", "impl_step2"]}

async def discover_knowledge_nodes(focus_area: str, manager: VaultManagerAgent):
    """Discover knowledge nodes"""
    # Implementation would discover knowledge nodes
    return ["node1", "node2", "node3"]

async def map_knowledge_relationships(nodes: List[str], manager: VaultManagerAgent):
    """Map knowledge relationships"""
    # Implementation would map relationships
    return [{"from": "node1", "to": "node2", "type": "related"}]

async def create_knowledge_map(nodes: List[str], relationships: List[Dict], depth: str, manager: VaultManagerAgent):
    """Create knowledge map"""
    # Implementation would create knowledge map
    return {"map": "Knowledge map visualization", "format": "graph"}

async def generate_knowledge_insights(knowledge_map: Dict[str, Any], focus_area: str, manager: VaultManagerAgent):
    """Generate knowledge insights"""
    # Implementation would generate insights
    return ["insight1", "insight2"]

async def analyze_workflow_requirements(goal: str, context: Dict[str, Any], manager: VaultManagerAgent):
    """Analyze workflow requirements"""
    # Implementation would analyze requirements
    return {"requirements": "Workflow requirements"}

async def execute_custom_logic(requirements: Dict[str, Any], goal: str, context: Dict[str, Any], manager: VaultManagerAgent):
    """Execute custom workflow logic"""
    # Implementation would execute custom logic
    return {"custom_results": "Custom workflow results"}

# Status and control endpoints

@router.get("/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get workflow execution status and progress"""
    
    workflow = workflow_status.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return workflow

@router.post("/cancel/{workflow_id}")
async def cancel_workflow(workflow_id: str):
    """Cancel running workflow"""
    
    workflow = workflow_status.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow["status"] in ["completed", "failed", "cancelled"]:
        return {"message": "Workflow already finished", "status": workflow["status"]}
    
    workflow_status.update_workflow(workflow_id, status="cancelled")
    
    # Notify via dev-pipe
    await dev_pipe.log_message("info", f"Workflow cancelled: {workflow_id}")
    
    return {"message": "Workflow cancelled successfully", "workflow_id": workflow_id}

@router.get("/list")
async def list_workflows():
    """List all workflows with their current status"""
    
    workflows = list(workflow_status.workflows.values())
    return {
        "workflows": workflows,
        "total_count": len(workflows),
        "active_count": len([w for w in workflows if w["status"] == "running"]),
        "completed_count": len([w for w in workflows if w["status"] == "completed"])
    }
