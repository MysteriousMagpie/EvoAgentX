from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.exceptions import RequestValidationError
from typing import Dict, List, Optional
import uuid
import json
import asyncio
from datetime import datetime
from pydantic import ValidationError

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

# Custom middleware to log validation errors
async def log_request_validation_error(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except RequestValidationError as e:
        # Log the validation error details
        print(f"[VALIDATION ERROR] URL: {request.url}")
        print(f"[VALIDATION ERROR] Method: {request.method}")
        print(f"[VALIDATION ERROR] Headers: {dict(request.headers)}")
        try:
            body = await request.body()
            print(f"[VALIDATION ERROR] Body: {body.decode()}")
        except:
            print(f"[VALIDATION ERROR] Could not read body")
        print(f"[VALIDATION ERROR] Details: {e.errors()}")
        raise e

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
            prompt="Answer the user's question helpfully and concisely:\n\n{query}",
            inputs=[
                {
                    "name": "query",
                    "type": "str", 
                    "description": "The user's question or message to respond to",
                    "required": True
                }
            ],
            outputs=[
                {
                    "name": "response",
                    "type": "str",
                    "description": "The assistant's helpful response to the user's question",
                    "required": True
                }
            ],
            parse_mode="str"  # Use simple string parsing instead of structured parsing
        )
    return active_agents[agent_name]

@router.post("/chat", response_model=AgentChatResponse)
async def chat_with_agent(request: AgentChatRequest):
    """Chat with an agent in a conversational manner or execute workflows based on mode"""
    try:
        conversation_id = get_or_create_conversation(request.conversation_id)
        
        # Add user message to conversation
        user_message = ChatMessage(
            role="user",
            content=request.message,
            timestamp=datetime.now()
        )
        conversations[conversation_id].append(user_message)
        
        # Handle different modes
        if request.mode == "agent":
            # Agent mode: Execute workflow for complex tasks
            try:
                from evoagentx.core.runner import run_workflow_async
                result, graph = await run_workflow_async(
                    goal=request.message,
                    return_graph=True
                )
                response_text = str(result)
                agent_name = "WorkflowAgent"
            except Exception as e:
                print(f"[WORKFLOW ERROR] Exception during workflow execution: {str(e)}")
                response_text = f"Workflow execution error: {str(e)}"
                agent_name = "WorkflowAgent"
        else:
            # Ask mode: Simple chat with agent
            try:
                # Get or create agent
                if request.agent_name and request.agent_name in active_agents:
                    agent = active_agents[request.agent_name]
                else:
                    agent = get_default_agent()
                
                agent_name = agent.name
                
                # Use the agent's default action (if CustomizeAgent, it has one action)
                if hasattr(agent, 'actions') and agent.actions:
                    action_name = agent.actions[0].name
                    result = await agent.async_execute(
                        action_name=action_name,
                        action_input_data={"query": request.message}
                    )
                    
                    # Extract response from result - handle different result types
                    response_text = None
                    
                    # Handle Message objects with content that has response attribute
                    if hasattr(result, 'content'):
                        content = getattr(result, 'content')
                        if hasattr(content, 'response'):
                            response_text = str(getattr(content, 'response'))
                        elif isinstance(content, str):
                            response_text = content
                        else:
                            response_text = str(content)
                    # Try accessing 'response' attribute directly
                    elif hasattr(result, 'response'):
                        response_text = str(getattr(result, 'response'))
                    # Handle tuple results
                    elif isinstance(result, tuple) and len(result) > 0:
                        first_result = result[0]
                        if hasattr(first_result, 'content'):
                            content = getattr(first_result, 'content')
                            if hasattr(content, 'response'):
                                response_text = str(getattr(content, 'response'))
                            else:
                                response_text = str(content)
                        elif hasattr(first_result, 'response'):
                            response_text = str(getattr(first_result, 'response'))
                        else:
                            response_text = str(first_result)
                    
                    # Fallback to string conversion
                    if response_text is None:
                        response_text = str(result)
                else:
                    # Fallback for other agent types
                    response_text = f"Agent {agent.name} processed: {request.message}"
            except Exception as e:
                print(f"[CHAT ERROR] Exception during agent execution: {str(e)}")
                response_text = f"Error processing request: {str(e)}"
                agent_name = "ChatAgent"
        
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
            agent_name=agent_name,
            timestamp=datetime.now(),
            metadata={"context": request.context, "mode": request.mode}
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
            graph=graph if isinstance(graph, dict) else None,
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
    
    # Log the incoming request for debugging
    print(f"[DEBUG] Copilot completion request received:")
    print(f"[DEBUG] - Text length: {len(request.text)} characters")
    print(f"[DEBUG] - Text preview: {repr(request.text[:100])}{'...' if len(request.text) > 100 else ''}")
    print(f"[DEBUG] - Cursor position: {request.cursor_position}")
    print(f"[DEBUG] - File type: {request.file_type}")
    print(f"[DEBUG] - Context: {request.context}")
    
    try:
        # Validate that text is not empty
        if not request.text or request.text.strip() == "":
            print("[DEBUG] ERROR: Empty text provided")
            raise HTTPException(
                status_code=400, 
                detail="Text cannot be empty. Please provide the text content to complete."
            )
        
        # Validate cursor position
        if request.cursor_position > len(request.text):
            print(f"[DEBUG] ERROR: Cursor position {request.cursor_position} exceeds text length {len(request.text)}")
            raise HTTPException(
                status_code=400,
                detail=f"Cursor position ({request.cursor_position}) cannot exceed text length ({len(request.text)})"
            )
        
        print("[DEBUG] Request validation passed, proceeding with completion...")
        
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
        
        completion_text = str(result[0].content) if isinstance(result, tuple) and hasattr(result[0], 'content') else str(result)
        
        print(f"[DEBUG] Generated completion: {repr(completion_text[:100])}{'...' if len(completion_text) > 100 else ''}")
        
        return CopilotCompletionResponse(
            completion=completion_text,
            confidence=0.85,  # Could be calculated based on model certainty
            suggestions=[completion_text]  # Could generate multiple alternatives
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        print(f"[DEBUG] ERROR: Completion failed with exception: {str(e)}")
        print(f"[DEBUG] Exception type: {type(e).__name__}")
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
        print(f"[DEBUG] Conversation history request received:")
        print(f"[DEBUG] - conversation_id: {request.conversation_id}")
        print(f"[DEBUG] - limit: {request.limit}")
        print(f"[DEBUG] Available conversations: {list(conversations.keys())}")
        
        if request.conversation_id not in conversations:
            print(f"[DEBUG] Conversation {request.conversation_id} not found in {list(conversations.keys())}")
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = conversations[request.conversation_id]
        limited_messages = messages[-request.limit:] if request.limit else messages
        
        print(f"[DEBUG] Returning {len(limited_messages)} messages from conversation {request.conversation_id}")
        
        return ConversationHistoryResponse(
            conversation_id=request.conversation_id,
            messages=limited_messages,
            total_count=len(messages)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Error retrieving history: {str(e)}")
        print(f"[ERROR] Request data: conversation_id={getattr(request, 'conversation_id', 'MISSING')}, limit={getattr(request, 'limit', 'MISSING')}")
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")

# Add a better error handler for common 422 errors on this endpoint
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

@router.post("/conversation/history/validate")
async def validate_conversation_history_request(request_body: dict):
    """Helper endpoint to validate conversation history requests and provide helpful error messages"""
    print(f"[DEBUG] Raw conversation history validation request: {request_body}")
    
    # Check if this looks like a chat request sent to the wrong endpoint
    if "message" in request_body:
        return JSONResponse(
            status_code=422,
            content={
                "error": "Wrong endpoint", 
                "message": "It looks like you're trying to send a chat message. Use POST /api/obsidian/chat instead.",
                "correct_endpoint": "/api/obsidian/chat",
                "expected_payload": {
                    "message": "your message here",
                    "conversation_id": "optional_conversation_id",
                    "context": {}
                },
                "received_payload": request_body
            }
        )
    
    # Try to validate as ConversationHistoryRequest
    try:
        validated = ConversationHistoryRequest(**request_body)
        return {"status": "valid", "validated_data": validated.dict()}
    except ValidationError as e:
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation failed",
                "message": "Conversation history endpoint expects 'conversation_id' (required) and optional 'limit'",
                "expected_payload": {
                    "conversation_id": "some-conversation-id",
                    "limit": 50
                },
                "validation_errors": e.errors(),
                "received_payload": request_body
            }
        )

# Add a raw payload capture endpoint for debugging
@router.post("/conversation/history/debug")
async def debug_conversation_history(request_data: dict):
    """Debug endpoint to see raw payload"""
    print(f"[DEBUG] Raw conversation history payload: {json.dumps(request_data, indent=2)}")
    return {"received_payload": request_data}

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
        
        summary = str(result[0].content) if isinstance(result, tuple) and hasattr(result[0], 'content') else str(result)
        
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
        plan_content = str(result[0].content) if isinstance(result, tuple) and hasattr(result[0], 'content') else str(result)
        
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
            result=result[0].content if isinstance(result, tuple) and hasattr(result[0], 'content') else result,
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
        # Intelligence parser is implemented in TypeScript, so we provide a Python fallback
        # In a production environment, you might want to call the TypeScript module via subprocess
        # or implement the intelligence parsing logic in Python
        
        # Fallback implementation - process the user input
        try:
            # Mock intelligence parsing logic
            user_input = request.user_input.lower().strip()
            
            # Simple intent detection
            intent = "general"
            if any(word in user_input for word in ["schedule", "calendar", "appointment"]):
                intent = "scheduling"
            elif any(word in user_input for word in ["task", "todo", "reminder"]):
                intent = "task_management"
            elif any(word in user_input for word in ["note", "write", "document"]):
                intent = "note_taking"
            
            # Simple follow-up detection
            follow_up_needed = any(word in user_input for word in ["?", "how", "what", "when", "where", "why"])
            
            parsed_data = {
                "intent": intent,
                "context": request.user_input,
                "confidence": 0.7,
                "entities": []
            }
            
            response = f"Processed input with intent: {intent}"
            if follow_up_needed:
                response = f"FollowUp: {response}"
            
            return IntelligenceParseResponse(
                response=response,
                parsed_data=parsed_data,
                follow_up_needed=follow_up_needed
            )
        except Exception as e:
            # Final fallback
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
    return {"status": "ok"}

@router.options("/health")
async def health_check_options():
    """Handle OPTIONS request for health endpoint"""
    return {"status": "ok"}

@router.post("/copilot/debug")
async def copilot_debug(request: Request):
    """Debug endpoint to see what payload is being sent"""
    try:
        body = await request.body()
        headers = dict(request.headers)
        
        print(f"[DEBUG] === COPILOT DEBUG ENDPOINT ===")
        print(f"[DEBUG] Method: {request.method}")
        print(f"[DEBUG] URL: {request.url}")
        print(f"[DEBUG] Headers: {headers}")
        print(f"[DEBUG] Raw body: {body}")
        
        if body:
            try:
                body_str = body.decode('utf-8')
                print(f"[DEBUG] Decoded body: {body_str}")
                body_json = json.loads(body_str)
                print(f"[DEBUG] Parsed JSON: {json.dumps(body_json, indent=2)}")
                return {
                    "received_payload": body_json,
                    "headers": headers,
                    "content_length": len(body),
                    "validation_status": "Would validate against CopilotCompletionRequest"
                }
            except json.JSONDecodeError as e:
                return {
                    "error": f"JSON decode failed: {e}",
                    "raw_body": body.decode('utf-8', errors='replace'),
                    "headers": headers
                }
        else:
            return {
                "error": "Empty request body",
                "headers": headers
            }
            
    except Exception as e:
        return {"error": f"Debug failed: {e}"}
