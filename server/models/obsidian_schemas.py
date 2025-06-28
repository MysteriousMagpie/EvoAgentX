from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


# Request/Response models for Obsidian integration

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class AgentChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    agent_name: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class AgentChatResponse(BaseModel):
    response: str
    conversation_id: str
    agent_name: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class WorkflowRequest(BaseModel):
    goal: str
    context: Optional[Dict[str, Any]] = None


class WorkflowResponse(BaseModel):
    goal: str
    output: str
    graph: Optional[Dict[str, Any]] = None
    execution_id: str
    status: str


class CopilotCompletionRequest(BaseModel):
    text: str
    cursor_position: int
    file_type: Optional[str] = None
    context: Optional[str] = None


class CopilotCompletionResponse(BaseModel):
    completion: str
    confidence: float
    suggestions: List[str]


class AgentListResponse(BaseModel):
    agents: List[Dict[str, Any]]


class ConversationHistoryRequest(BaseModel):
    conversation_id: str
    limit: Optional[int] = 50


class ConversationHistoryResponse(BaseModel):
    conversation_id: str
    messages: List[ChatMessage]
    total_count: int


class MemoryUpdateRequest(BaseModel):
    user_id: str
    memory_updates: Dict[str, Any]


class MemoryUpdateResponse(BaseModel):
    success: bool
    updated_memory: Dict[str, Any]


class VaultContextRequest(BaseModel):
    file_paths: List[str]
    content_snippets: Optional[Dict[str, str]] = None


class VaultContextResponse(BaseModel):
    context_summary: str
    relevant_notes: List[Dict[str, Any]]


class TaskPlanningRequest(BaseModel):
    goal: str
    constraints: Optional[List[str]] = None
    deadline: Optional[datetime] = None


class TaskPlanningResponse(BaseModel):
    plan: Dict[str, Any]
    subtasks: List[Dict[str, Any]]
    estimated_duration: Optional[int] = None


class AgentExecutionRequest(BaseModel):
    agent_name: str
    action_name: str
    inputs: Dict[str, Any]
    conversation_id: Optional[str] = None


class AgentExecutionResponse(BaseModel):
    result: Any
    execution_time: float
    conversation_id: str
    metadata: Dict[str, Any]


class IntelligenceParseRequest(BaseModel):
    user_id: str
    history: List[Dict[str, str]]
    user_input: str


class IntelligenceParseResponse(BaseModel):
    response: str
    parsed_data: Optional[Dict[str, Any]] = None
    follow_up_needed: bool = False
