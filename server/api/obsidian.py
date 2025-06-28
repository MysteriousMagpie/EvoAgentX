from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional
import uuid
import json
import asyncio
from datetime import datetime

from ..models.obsidian_schemas import (
    AgentChatRequest, AgentChatResponse,
    WorkflowRequest, WorkflowResponse,
    CopilotCompletionRequest, CopilotCompletionResponse,
    AgentListResponse, ConversationHistoryRequest, ConversationHistoryResponse,
    MemoryUpdateRequest, MemoryUpdateResponse,
    VaultContextRequest, VaultContextResponse,
    TaskPlanningRequest, TaskPlanningResponse,
    AgentExecutionRequest, AgentExecutionResponse,
    IntelligenceParseRequest, IntelligenceParseResponse,
    ChatMessage
)
from evoagentx.core.runner import run_workflow_async
from evoagentx.agents import CustomizeAgent, Agent
from evoagentx.models import OpenAILLMConfig
from evoagentx.agents.task_planner import TaskPlanner
from evoagentx.prompts.agent_generator import AGENT_GENERATOR
import os

router = APIRouter(prefix="/api/obsidian", tags=["obsidian"])

# In-memory storage for conversations and agents (consider using Redis/DB for production)
conversations: Dict[str, List[ChatMessage]] = {}
active_agents: Dict[str, Agent] = {}
user_memory: Dict[str, Dict] = {}

def get_llm_config():
    """Get the default LLM configuration"""
    return OpenAILLMConfig(
        model="gpt-4o-mini",
        openai_key=os.getenv("OPENAI_API_KEY"),
        stream=False,
        output_response=True,
        max_tokens=4000,
    )

def get_or_create_conversation(conversation_id: Optional[str] = None) -> str:
    """Get existing conversation or create new one"""
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
    if conversation_id not in conversations:
        conversations[conversation_id] = []
    return conversation_id

def get_default_agent() -> Agent:
    """Get or create the default assistant agent"""
    agent_name = "ObsidianAssistant"
    if agent_name not in active_agents:
        active_agents[agent_name] = CustomizeAgent(
            name=agent_name,
            description="A helpful assistant for Obsidian vault management and general queries",
            llm_config=get_llm_config(),
            system_prompt="You are a helpful assistant integrated with Obsidian. You help users manage their knowledge, take notes, organize thoughts, and answer questions. Provide concise, actionable responses.",
            prompt="Answer the user's question helpfully and concisely:\n\n{query}"
        )
    return active_agents[agent_name]

@router.post("/chat", response_model=AgentChatResponse)
async def chat_with_agent(request: AgentChatRequest):
    """Chat with an agent in a conversational manner"""
    try:
        conversation_id = get_or_create_conversation(request.conversation_id)
        
        # Get or create agent
        if request.agent_name and request.agent_name in active_agents:
            agent = active_agents[request.agent_name]
        else:
            agent = get_default_agent()
        
        # Add user message to conversation
        user_message = ChatMessage(
            role="user",
            content=request.message,
            timestamp=datetime.now()
        )
        conversations[conversation_id].append(user_message)
        
        # Get agent response
        try:
            # Use the agent's default action (if CustomizeAgent, it has one action)
            if hasattr(agent, 'actions') and agent.actions:
                action_name = agent.actions[0].name
                result = await agent.async_execute(
                    action_name=action_name,
                    action_input_data={"query": request.message}
                )
                response_text = str(result.content) if hasattr(result, 'content') else str(result)
            else:
                # Fallback for other agent types
                response_text = f"Agent {agent.name} processed: {request.message}"
        except Exception as e:
            response_text = f"Error processing request: {str(e)}"
        
        # Add assistant response to conversation
        assistant_message = ChatMessage(
            role="assistant",
            content=response_text,
            timestamp=datetime.now()
        )
        conversations[conversation_id].append(assistant_message)
        
        return AgentChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            agent_name=agent.name,
            timestamp=datetime.now(),
            metadata={"context": request.context}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.post("/workflow", response_model=WorkflowResponse)
async def execute_workflow(request: WorkflowRequest):
    """Execute a full EvoAgentX workflow"""
    try:
        execution_id = str(uuid.uuid4())
        
        # Execute the workflow
        result, graph = await run_workflow_async(
            goal=request.goal,
            return_graph=True
        )
        
        return WorkflowResponse(
            goal=request.goal,
            output=result,
            graph=graph,
            execution_id=execution_id,
            status="completed"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution error: {str(e)}")

@router.post("/copilot/complete", response_model=CopilotCompletionResponse)
async def copilot_completion(request: CopilotCompletionRequest):
    """Provide copilot-style text completion"""
    try:
        # Create a specialized completion agent
        completion_agent = CustomizeAgent(
            name="CopilotAgent",
            description="Provides intelligent text completion for writing",
            llm_config=get_llm_config(),
            system_prompt="You are a writing assistant. Provide natural, helpful text completions that continue the user's text in a meaningful way. Be concise and contextually appropriate.",
            prompt="Continue this text naturally and helpfully:\n\nText: {text}\nCursor position: {position}\nFile type: {file_type}\nContext: {context}\n\nCompletion:"
        )
        
        result = await completion_agent.async_execute(
            action_name=completion_agent.actions[0].name,
            action_input_data={
                "text": request.text,
                "position": str(request.cursor_position),
                "file_type": request.file_type or "markdown",
                "context": request.context or "general writing"
            }
        )
        
        completion_text = str(result.content) if hasattr(result, 'content') else str(result)
        
        return CopilotCompletionResponse(
            completion=completion_text,
            confidence=0.85,  # Could be calculated based on model certainty
            suggestions=[completion_text]  # Could generate multiple alternatives
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Completion error: {str(e)}")

@router.get("/agents", response_model=AgentListResponse)
async def list_agents():
    """List all available agents"""
    try:
        agents_info = []
        for name, agent in active_agents.items():
            agent_info = {
                "name": agent.name,
                "description": agent.description,
                "actions": [action.name for action in agent.actions] if agent.actions else [],
                "type": type(agent).__name__
            }
            agents_info.append(agent_info)
        
        return AgentListResponse(agents=agents_info)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing agents: {str(e)}")

@router.post("/conversation/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(request: ConversationHistoryRequest):
    """Get conversation history"""
    try:
        if request.conversation_id not in conversations:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = conversations[request.conversation_id]
        limited_messages = messages[-request.limit:] if request.limit else messages
        
        return ConversationHistoryResponse(
            conversation_id=request.conversation_id,
            messages=limited_messages,
            total_count=len(messages)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")

@router.post("/memory/update", response_model=MemoryUpdateResponse)
async def update_user_memory(request: MemoryUpdateRequest):
    """Update user memory/context"""
    try:
        if request.user_id not in user_memory:
            user_memory[request.user_id] = {}
        
        # Update memory
        user_memory[request.user_id].update(request.memory_updates)
        
        return MemoryUpdateResponse(
            success=True,
            updated_memory=user_memory[request.user_id]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory update error: {str(e)}")

@router.post("/vault/context", response_model=VaultContextResponse)
async def analyze_vault_context(request: VaultContextRequest):
    """Analyze Obsidian vault context and provide insights"""
    try:
        # Create a context analysis agent
        context_agent = CustomizeAgent(
            name="VaultAnalyzer",
            description="Analyzes Obsidian vault content and provides insights",
            llm_config=get_llm_config(),
            system_prompt="You are an expert at analyzing knowledge bases and note collections. Provide insightful summaries and identify connections between ideas.",
            prompt="Analyze these vault files and content:\n\nFiles: {files}\nContent: {content}\n\nProvide a helpful summary and insights:"
        )
        
        result = await context_agent.async_execute(
            action_name=context_agent.actions[0].name,
            action_input_data={
                "files": ", ".join(request.file_paths),
                "content": json.dumps(request.content_snippets or {})
            }
        )
        
        summary = str(result.content) if hasattr(result, 'content') else str(result)
        
        # Create mock relevant notes (in real implementation, this would use vector search)
        relevant_notes = [
            {"path": path, "relevance": 0.8, "snippet": "..."}
            for path in request.file_paths[:3]
        ]
        
        return VaultContextResponse(
            context_summary=summary,
            relevant_notes=relevant_notes
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context analysis error: {str(e)}")

@router.post("/planning/tasks", response_model=TaskPlanningResponse)
async def plan_tasks(request: TaskPlanningRequest):
    """Plan tasks and create actionable steps"""
    try:
        # Create task planner
        planner = TaskPlanner(llm_config=get_llm_config())
        
        # Build planning context
        planning_context = {
            "goal": request.goal,
            "constraints": request.constraints or [],
            "deadline": request.deadline.isoformat() if request.deadline else None
        }
        
        result = await planner.async_execute(
            action_name="TaskPlanning",
            action_input_data=planning_context
        )
        
        # Parse the result (assuming it's a structured plan)
        plan_content = str(result.content) if hasattr(result, 'content') else str(result)
        
        # Create mock subtasks (in real implementation, parse from LLM output)
        subtasks = [
            {"name": f"Subtask for: {request.goal}", "priority": "high", "estimated_time": 30}
        ]
        
        return TaskPlanningResponse(
            plan={"description": plan_content, "context": planning_context},
            subtasks=subtasks,
            estimated_duration=60
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task planning error: {str(e)}")

@router.post("/agent/execute", response_model=AgentExecutionResponse)
async def execute_agent_action(request: AgentExecutionRequest):
    """Execute a specific action on an agent"""
    try:
        if request.agent_name not in active_agents:
            raise HTTPException(status_code=404, detail=f"Agent {request.agent_name} not found")
        
        agent = active_agents[request.agent_name]
        conversation_id = get_or_create_conversation(request.conversation_id)
        
        start_time = datetime.now()
        
        result = await agent.async_execute(
            action_name=request.action_name,
            action_input_data=request.inputs
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return AgentExecutionResponse(
            result=result.content if hasattr(result, 'content') else result,
            execution_time=execution_time,
            conversation_id=conversation_id,
            metadata={
                "agent": request.agent_name,
                "action": request.action_name,
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(e)}")

@router.post("/intelligence/parse", response_model=IntelligenceParseResponse)
async def parse_intelligence(request: IntelligenceParseRequest):
    """Parse user input for intelligence and context extraction"""
    try:
        # Try to import the intelligence parser function
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from intelligenceParser import handleMessage
            
            # Convert history to the expected format
            history = [{"role": msg["role"], "content": msg["content"]} for msg in request.history]
            
            # Call the intelligence parser
            result = await handleMessage(
                userId=request.user_id,
                history=history,
                userInput=request.user_input
            )
            
            # Check if it's a follow-up question
            follow_up_needed = result.startswith("FollowUp:")
            
            # Try to parse as JSON for structured data
            parsed_data = None
            if not follow_up_needed:
                try:
                    parsed_data = json.loads(result)
                except json.JSONDecodeError:
                    pass
            
            return IntelligenceParseResponse(
                response=result,
                parsed_data=parsed_data,
                follow_up_needed=follow_up_needed
            )
        except ImportError:
            # Fallback if intelligence parser is not available
            return IntelligenceParseResponse(
                response=f"Processed: {request.user_input}",
                parsed_data={"intent": "general", "context": request.user_input},
                follow_up_needed=False
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intelligence parsing error: {str(e)}")

@router.post("/agents/create")
async def create_custom_agent(
    name: str,
    description: str,
    system_prompt: str,
    prompt: str
):
    """Create a new custom agent"""
    try:
        if name in active_agents:
            raise HTTPException(status_code=400, detail=f"Agent {name} already exists")
        
        agent = CustomizeAgent(
            name=name,
            description=description,
            llm_config=get_llm_config(),
            system_prompt=system_prompt,
            prompt=prompt
        )
        
        active_agents[name] = agent
        
        return {
            "success": True,
            "agent_name": name,
            "message": f"Agent {name} created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent creation error: {str(e)}")

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    try:
        if conversation_id in conversations:
            del conversations[conversation_id]
            return {"success": True, "message": "Conversation deleted"}
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_agents": len(active_agents),
        "active_conversations": len(conversations)
    }
