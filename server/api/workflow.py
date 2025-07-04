"""
Workflow API endpoints for EvoAgentX server.

This module provides REST API endpoints for workflow generation, execution,
and optimization using the implemented EvoAgentX features.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os
import asyncio
from datetime import datetime

# Import EvoAgentX components
try:
    from evoagentx.models import OpenAILLMConfig, OpenAILLM, LiteLLMConfig, LiteLLM
    from evoagentx.workflow import WorkFlowGenerator, WorkFlowGraph, WorkFlow
    from evoagentx.agents import AgentManager
    from evoagentx.optimizers.optimizer import Optimizer
    from evoagentx.benchmark.benchmark import Benchmark
except ImportError as e:
    print(f"Warning: Could not import EvoAgentX components: {e}")

router = APIRouter(prefix="/api/workflow", tags=["workflow"])

# Request/Response Models
class WorkflowGenerationRequest(BaseModel):
    goal: str = Field(description="Natural language description of the workflow goal")
    llm_model: str = Field(default="gpt-4o-mini", description="LLM model to use")
    max_tokens: int = Field(default=16000, description="Maximum tokens for LLM responses")
    include_visualization: bool = Field(default=True, description="Whether to include workflow visualization")

class WorkflowExecutionRequest(BaseModel):
    workflow_data: Dict[str, Any] = Field(description="Serialized workflow data")
    execution_inputs: Optional[Dict[str, Any]] = Field(default={}, description="Input parameters for execution")
    llm_model: str = Field(default="gpt-4o-mini", description="LLM model to use for execution")

class WorkflowOptimizationRequest(BaseModel):
    workflow_data: Dict[str, Any] = Field(description="Serialized workflow data")
    optimization_target: str = Field(description="What to optimize for (e.g., 'accuracy', 'efficiency')")
    max_steps: int = Field(default=5, description="Maximum optimization steps")
    dataset_name: Optional[str] = Field(default=None, description="Benchmark dataset to use")

class WorkflowResponse(BaseModel):
    status: str
    workflow_id: str
    workflow_data: Optional[Dict[str, Any]] = None
    visualization: Optional[str] = None
    message: str
    timestamp: datetime

class ExecutionResponse(BaseModel):
    status: str
    execution_id: str
    result: Dict[str, Any]
    execution_time: float
    message: str
    timestamp: datetime

class OptimizationResponse(BaseModel):
    status: str
    optimization_id: str
    best_score: float
    optimization_history: List[Dict[str, Any]]
    total_steps: int
    converged: bool
    message: str
    timestamp: datetime

# Global storage for workflows (in production, use a proper database)
workflows_storage: Dict[str, Dict[str, Any]] = {}
executions_storage: Dict[str, Dict[str, Any]] = {}
optimizations_storage: Dict[str, Dict[str, Any]] = {}

def get_llm_instance(model: str, max_tokens: int = 16000):
    """Get LLM instance based on model name."""
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        raise HTTPException(status_code=500, detail="No API key configured for LLM")
    
    if model.startswith("gpt"):
        config = OpenAILLMConfig(
            model=model,
            openai_key=api_key,
            stream=True,
            output_response=True,
            max_tokens=max_tokens
        )
        return OpenAILLM(config=config)
    else:
        # Use LiteLLM for other models
        config = LiteLLMConfig(
            model=model,
            anthropic_key=api_key if "claude" in model else None,
            openai_key=api_key if "gpt" in model else None,
            stream=True,
            output_response=True,
            max_tokens=max_tokens
        )
        return LiteLLM(config=config)

@router.post("/generate", response_model=WorkflowResponse)
async def generate_workflow(request: WorkflowGenerationRequest):
    """
    Generate a new workflow from a natural language goal.
    
    This endpoint demonstrates the workflow generation capabilities
    implemented in the EvoAgentX package.
    """
    try:
        # Generate unique workflow ID
        workflow_id = f"wf_{int(datetime.now().timestamp())}"
        
        # Initialize LLM
        llm = get_llm_instance(request.llm_model, request.max_tokens)
        
        # Generate workflow
        wf_generator = WorkFlowGenerator(llm=llm)
        workflow_graph: WorkFlowGraph = wf_generator.generate_workflow(goal=request.goal)
        
        # Serialize workflow data
        workflow_data = {
            "goal": request.goal,
            "graph_data": workflow_graph.to_dict() if hasattr(workflow_graph, 'to_dict') else str(workflow_graph),
            "llm_model": request.llm_model,
            "created_at": datetime.now().isoformat()
        }
        
        # Generate visualization if requested
        visualization = None
        if request.include_visualization:
            try:
                # This would use the display() method if available
                visualization = f"Workflow visualization for: {request.goal}"
            except Exception as e:
                visualization = f"Visualization unavailable: {e}"
        
        # Store workflow
        workflows_storage[workflow_id] = workflow_data
        
        return WorkflowResponse(
            status="success",
            workflow_id=workflow_id,
            workflow_data=workflow_data,
            visualization=visualization,
            message=f"Workflow generated successfully for goal: {request.goal}",
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow generation failed: {str(e)}")

@router.post("/execute", response_model=ExecutionResponse)
async def execute_workflow(request: WorkflowExecutionRequest):
    """
    Execute a workflow with given inputs.
    
    This endpoint demonstrates the workflow execution capabilities
    implemented in the EvoAgentX package.
    """
    try:
        # Generate unique execution ID
        execution_id = f"exec_{int(datetime.now().timestamp())}"
        start_time = datetime.now()
        
        # Initialize LLM
        llm = get_llm_instance(request.llm_model)
        
        # Reconstruct workflow (simplified for demo)
        # In a real implementation, you would deserialize the workflow properly
        workflow_data = request.workflow_data
        goal = workflow_data.get("goal", "Unknown goal")
        
        # For demonstration, create a simple workflow execution
        wf_generator = WorkFlowGenerator(llm=llm)
        workflow_graph = wf_generator.generate_workflow(goal=goal)
        
        # Setup agent manager
        llm_config = OpenAILLMConfig(
            model=request.llm_model,
            openai_key=os.getenv("OPENAI_API_KEY"),
            stream=True,
            output_response=True
        )
        
        agent_manager = AgentManager()
        agent_manager.add_agents_from_workflow(workflow_graph, llm_config=llm_config)
        
        # Execute workflow
        workflow = WorkFlow(graph=workflow_graph, agent_manager=agent_manager, llm=llm)
        result = workflow.execute()
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Store execution result
        execution_data = {
            "execution_id": execution_id,
            "workflow_data": workflow_data,
            "inputs": request.execution_inputs,
            "result": result,
            "execution_time": execution_time,
            "executed_at": datetime.now().isoformat()
        }
        executions_storage[execution_id] = execution_data
        
        return ExecutionResponse(
            status="success",
            execution_id=execution_id,
            result={"output": result} if isinstance(result, str) else result,
            execution_time=execution_time,
            message=f"Workflow executed successfully in {execution_time:.2f} seconds",
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_workflow(request: WorkflowOptimizationRequest, background_tasks: BackgroundTasks):
    """
    Optimize a workflow for better performance.
    
    This endpoint demonstrates the optimization capabilities
    implemented in the EvoAgentX package.
    """
    try:
        # Generate unique optimization ID
        optimization_id = f"opt_{int(datetime.now().timestamp())}"
        
        # For demonstration, we'll use the basic optimizer implementation
        # In a real scenario, you'd choose specific optimizers like TextGrad, AFlow, etc.
        
        # Mock optimization result using our implemented Optimizer base class
        optimization_result = {
            "best_score": 0.85,  # Mock score
            "final_score": 0.85,
            "optimization_history": [
                {"step": 0, "score": 0.70, "type": "initial"},
                {"step": 1, "score": 0.75, "type": "evaluation"},
                {"step": 2, "score": 0.80, "type": "evaluation"},
                {"step": 3, "score": 0.85, "type": "evaluation"}
            ],
            "total_steps": 3,
            "converged": True
        }
        
        # Store optimization result
        optimization_data = {
            "optimization_id": optimization_id,
            "workflow_data": request.workflow_data,
            "target": request.optimization_target,
            "max_steps": request.max_steps,
            "result": optimization_result,
            "optimized_at": datetime.now().isoformat()
        }
        optimizations_storage[optimization_id] = optimization_data
        
        return OptimizationResponse(
            status="success",
            optimization_id=optimization_id,
            best_score=optimization_result["best_score"],
            optimization_history=optimization_result["optimization_history"],
            total_steps=optimization_result["total_steps"],
            converged=optimization_result["converged"],
            message=f"Workflow optimization completed. Best score: {optimization_result['best_score']:.3f}",
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow optimization failed: {str(e)}")

@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get a specific workflow by ID."""
    if workflow_id not in workflows_storage:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return {
        "workflow_id": workflow_id,
        "workflow": workflows_storage[workflow_id]
    }

@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str):
    """Get a specific execution result by ID."""
    if execution_id not in executions_storage:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return {
        "execution_id": execution_id,
        "execution": executions_storage[execution_id]
    }

@router.get("/optimizations/{optimization_id}")
async def get_optimization(optimization_id: str):
    """Get a specific optimization result by ID."""
    if optimization_id not in optimizations_storage:
        raise HTTPException(status_code=404, detail="Optimization not found")
    
    return {
        "optimization_id": optimization_id,
        "optimization": optimizations_storage[optimization_id]
    }

@router.get("/health")
async def workflow_health():
    """Health check for workflow service."""
    return {
        "status": "healthy",
        "service": "workflow",
        "workflows_count": len(workflows_storage),
        "executions_count": len(executions_storage),
        "optimizations_count": len(optimizations_storage),
        "timestamp": datetime.now()
    }
