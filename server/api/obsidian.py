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
    ChatRequest, ChatResponse,
    WorkflowRequest, WorkflowResponse,
    CopilotCompletionRequest, CopilotCompletionResponse,
    AgentListResponse, ConversationHistoryRequest, ConversationHistoryResponse,
    MemoryUpdateRequest, MemoryUpdateResponse,
    VaultContextRequest, VaultContextResponse,
    TaskPlanningRequest, TaskPlanningResponse,
    AgentExecutionRequest, AgentExecutionResponse,
    IntelligenceParseRequest, IntelligenceParseResponse,
    ChatMessage,
    # Vault management schemas
    VaultStructureRequest, VaultStructureResponse,
    FileOperationRequest, FileOperationResponse,
    BatchFileOperationRequest, BatchFileOperationResponse,
    VaultSearchRequest, VaultSearchResponse,
    VaultOrganizationRequest, VaultOrganizationResponse,
    VaultBackupRequest, VaultBackupResponse
)
from evoagentx.core.runner import run_workflow_async
from evoagentx.agents import CustomizeAgent, Agent
from evoagentx.agents.vault_manager import VaultManagerAgent
from evoagentx.models import OpenAILLMConfig
from evoagentx.agents.task_planner import TaskPlanner
from evoagentx.prompts.agent_generator import AGENT_GENERATOR
from evoagentx.intents.embed_classifier import classify_intent, Intent
from evoagentx.embeds import get_embedding
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

# Global vault manager instance
vault_manager: Optional[VaultManagerAgent] = None

def get_vault_manager(vault_root: Optional[str] = None) -> VaultManagerAgent:
    """Get or create the global vault manager instance"""
    global vault_manager
    if vault_manager is None:
        vault_manager = VaultManagerAgent(llm_config=get_llm_config(), vault_root=vault_root)
    return vault_manager

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

# ===== NEW VAULT MANAGEMENT ENDPOINTS =====

@router.post("/vault/structure", response_model=VaultStructureResponse)
async def get_vault_structure(request: VaultStructureRequest):
    """Get comprehensive vault structure with AI analysis"""
    try:
        manager = get_vault_manager()
        
        structure_data = manager.get_vault_structure(
            include_content=request.include_content,
            max_depth=request.max_depth,
            file_types=request.file_types
        )
        
        # Convert the response to match the expected schema format
        vault_structure = structure_data["raw_structure"]
        ai_analysis = structure_data.get("ai_analysis", {})
        
        # Build response according to schema
        return VaultStructureResponse(
            vault_name=str(manager.vault_tools.vault_root.name),
            total_files=vault_structure.get("total_files", 0),
            total_folders=vault_structure.get("total_folders", 0),
            total_size=vault_structure.get("total_size", 0),
            structure=vault_structure.get("structure", {}),
            recent_files=vault_structure.get("recent_files", []),
            orphaned_files=vault_structure.get("orphaned_files", []),
            analysis=ai_analysis.get("analysis"),
            recommendations=ai_analysis.get("recommendations"),
            organization_score=ai_analysis.get("organization_score")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vault structure error: {str(e)}")

@router.post("/vault/file/operation", response_model=FileOperationResponse)
async def perform_file_operation(request: FileOperationRequest):
    """Perform individual file operations (create, update, delete, move, copy)"""
    try:
        manager = get_vault_manager()
        
        if request.operation == "create":
            result = manager.create_file(
                request.file_path, 
                request.content or "", 
                request.create_missing_folders
            )
        elif request.operation == "update":
            result = manager.update_file(request.file_path, request.content or "")
        elif request.operation == "delete":
            result = manager.delete_file(request.file_path)
        elif request.operation == "move":
            if not request.destination_path:
                raise HTTPException(status_code=400, detail="Destination path required for move operation")
            result = manager.move_file(
                request.file_path, 
                request.destination_path, 
                request.create_missing_folders
            )
        elif request.operation == "copy":
            if not request.destination_path:
                raise HTTPException(status_code=400, detail="Destination path required for copy operation")
            result = manager.copy_file(
                request.file_path, 
                request.destination_path, 
                request.create_missing_folders
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation: {request.operation}")
        
        return FileOperationResponse(
            success=result.get("success", False),
            message=result.get("message", ""),
            file_path=request.file_path,
            operation_performed=request.operation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File operation error: {str(e)}")

@router.post("/vault/file/batch", response_model=BatchFileOperationResponse)
async def perform_batch_file_operations(request: BatchFileOperationRequest):
    """Perform multiple file operations in batch"""
    try:
        manager = get_vault_manager()
        
        # Convert request operations to the format expected by the manager
        operations = []
        for op in request.operations:
            operation_dict = {
                "operation": op.operation,
                "file_path": op.file_path,
                "create_missing_folders": op.create_missing_folders
            }
            if op.content is not None:
                operation_dict["content"] = op.content
            if op.destination_path is not None:
                operation_dict["destination_path"] = op.destination_path
            operations.append(operation_dict)
        
        result = manager.batch_file_operations(operations, request.continue_on_error)
        
        # Convert results to response format
        operation_results = []
        for i, op_result in enumerate(result["results"]):
            operation_results.append(FileOperationResponse(
                success=op_result.get("success", False),
                message=op_result.get("message", ""),
                file_path=request.operations[i].file_path,
                operation_performed=request.operations[i].operation
            ))
        
        return BatchFileOperationResponse(
            success=result["success"],
            completed_operations=result["completed_operations"],
            failed_operations=result["failed_operations"],
            results=operation_results,
            errors=result["errors"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch operation error: {str(e)}")

@router.post("/vault/search", response_model=VaultSearchResponse)
async def search_vault(request: VaultSearchRequest):
    """Perform intelligent search across the vault with AI analysis"""
    try:
        manager = get_vault_manager()
        
        search_results = manager.intelligent_search(
            query=request.query,
            search_type=request.search_type,
            file_types=request.file_types,
            max_results=request.max_results
        )
        
        # Convert results to response format
        results = []
        for result_item in search_results["raw_results"].get("results", []):
            results.append({
                "file_path": result_item.get("file_path", ""),
                "file_name": result_item.get("file_name", ""),
                "match_type": result_item.get("match_type", request.search_type),
                "snippet": result_item.get("snippet", ""),
                "line_number": result_item.get("line_number"),
                "relevance_score": result_item.get("relevance_score", 0.0)
            })
        
        return VaultSearchResponse(
            query=request.query,
            total_results=len(results),
            results=results,
            search_time=search_results["raw_results"].get("search_time", 0.0)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.post("/vault/organize", response_model=VaultOrganizationResponse)
async def organize_vault(request: VaultOrganizationRequest):
    """Plan vault reorganization with AI assistance"""
    try:
        manager = get_vault_manager()
        
        reorganization_plan = manager.plan_vault_reorganization(
            organization_goal=request.organization_goal,
            user_preferences=request.preferences
        )
        
        return VaultOrganizationResponse(
            reorganization_plan=reorganization_plan["reorganization_plan"],
            suggested_changes=[],  # TODO: Parse from plan
            estimated_changes_count=0,  # TODO: Calculate from plan
            dry_run=request.dry_run,
            execution_steps=reorganization_plan["implementation_steps"].split("\n") if reorganization_plan.get("implementation_steps") else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Organization error: {str(e)}")

@router.post("/vault/backup", response_model=VaultBackupResponse)
async def create_vault_backup(request: VaultBackupRequest):
    """Create a backup of the vault"""
    try:
        # For now, return a placeholder response since backup functionality
        # is not yet implemented in the VaultManagerAgent
        return VaultBackupResponse(
            success=False,
            backup_path="",
            backup_size=0,
            files_backed_up=0,
            backup_time=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup error: {str(e)}")

# ===== END NEW VAULT MANAGEMENT ENDPOINTS =====
