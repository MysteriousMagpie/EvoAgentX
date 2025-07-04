"""
VaultPilot API Models for EvoAgentX Integration

This file contains all Pydantic models for VaultPilot API endpoints.
These models ensure type safety and automatic API documentation.
"""

from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


# Base Response Models
class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool = True
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


# Health & Status Models
class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "ok"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)


# Chat Models
class ChatMessage(BaseModel):
    """Individual chat message"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat request from VaultPilot"""
    message: str = Field(..., min_length=1, description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for continuation")
    vault_context: Optional[str] = Field(None, description="Current vault content context")
    agent_id: Optional[str] = Field(None, description="Specific agent to use")
    mode: Literal["ask", "agent"] = Field(default="ask", description="Chat mode")


class ChatResponse(BaseModel):
    """Chat response to VaultPilot"""
    response: str = Field(..., description="AI agent response")
    conversation_id: str = Field(..., description="Conversation ID")
    agent_used: str = Field(..., description="Agent that handled the request")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional response metadata")


class ConversationHistoryRequest(BaseModel):
    """Request for conversation history"""
    conversation_id: str = Field(..., description="Conversation ID")
    limit: int = Field(default=50, ge=1, le=200, description="Maximum messages to return")
    include_messages: bool = Field(default=True, description="Include message content")


class ConversationHistory(BaseModel):
    """Conversation history response"""
    conversation_id: str
    messages: List[ChatMessage]
    total_count: int
    

# Copilot Models
class CopilotRequest(BaseModel):
    """Text completion request"""
    text: str = Field(..., min_length=1, description="Text to complete")
    cursor_position: int = Field(..., ge=0, description="Cursor position in text")
    file_type: str = Field(default="markdown", description="File type context")
    context: Optional[str] = Field(None, description="Additional context")


class CopilotResponse(BaseModel):
    """Text completion response"""
    completion: str = Field(..., description="Suggested completion")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    suggestions: List[str] = Field(default_factory=list, description="Alternative suggestions")


# Workflow Models
class WorkflowRequest(BaseModel):
    """Workflow execution request"""
    goal: str = Field(..., min_length=10, description="Workflow goal description")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    vault_content: Optional[str] = Field(None, description="Relevant vault content")
    constraints: Optional[List[str]] = Field(None, description="Execution constraints")


class WorkflowArtifact(BaseModel):
    """Workflow output artifact"""
    type: Literal["note", "plan", "analysis", "summary", "code"]
    title: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class WorkflowResponse(BaseModel):
    """Workflow execution response"""
    goal: str = Field(..., description="Original goal")
    output: str = Field(..., description="Main workflow output")
    result: Optional[str] = Field(None, description="Formatted result")
    steps_taken: List[str] = Field(default_factory=list, description="Execution steps")
    artifacts: List[WorkflowArtifact] = Field(default_factory=list, description="Generated artifacts")
    execution_time: float = Field(default=0.0, description="Execution time in seconds")
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique execution ID")
    status: Literal["completed", "failed", "partial"] = Field(default="completed")
    graph: Optional[Dict[str, Any]] = Field(None, description="Execution graph")


# Agent Models
class Agent(BaseModel):
    """AI Agent definition"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    capabilities: List[str] = Field(default_factory=list)
    active: bool = Field(default=True)
    system_prompt: Optional[str] = Field(None, description="Agent system prompt")


class AgentCreateRequest(BaseModel):
    """Create new agent request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    system_prompt: str = Field(..., min_length=1)
    capabilities: Optional[List[str]] = Field(default_factory=list)


class AgentExecuteRequest(BaseModel):
    """Execute specific agent request"""
    agent_id: str = Field(..., description="Agent ID to execute")
    task: str = Field(..., min_length=1, description="Task for agent")
    context: Optional[str] = Field(None, description="Task context")


# Vault Analysis Models
class Connection(BaseModel):
    """Vault content connection"""
    from_file: str = Field(..., alias="from")
    to_file: str = Field(..., alias="to")
    type: str = Field(..., description="Connection type (link, reference, etc.)")
    strength: float = Field(..., ge=0.0, le=1.0, description="Connection strength")


class VaultContextRequest(BaseModel):
    """Vault analysis request"""
    content: Optional[str] = Field(None, description="Vault content to analyze")
    file_paths: Optional[List[str]] = Field(None, description="Specific files to analyze")
    analysis_type: Literal["summary", "connections", "insights", "gaps", "all"] = Field(
        default="all", description="Type of analysis to perform"
    )


class VaultContextResponse(BaseModel):
    """Vault analysis response"""
    analysis: str = Field(..., description="Main analysis result")
    insights: List[str] = Field(default_factory=list, description="Key insights")
    connections: List[Connection] = Field(default_factory=list, description="Content connections")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Analysis metadata")


# Vault Statistics and Analysis Models
class VaultStats(BaseModel):
    """Vault statistics"""
    total_files: int = Field(default=0, description="Total files in vault")
    markdown_files: int = Field(default=0, description="Number of markdown files")
    daily_notes: int = Field(default=0, description="Number of daily notes")
    attachments: int = Field(default=0, description="Number of attachments")
    folders: int = Field(default=0, description="Number of folders")
    total_words: int = Field(default=0, description="Total word count")
    total_links: int = Field(default=0, description="Total internal links")
    orphaned_notes: int = Field(default=0, description="Notes without links")
    tags_count: int = Field(default=0, description="Number of unique tags")
    average_note_length: float = Field(default=0.0, description="Average note length in words")


class VaultContext(BaseModel):
    """Vault context information"""
    file_tree: Dict[str, Any] = Field(default_factory=dict, description="Hierarchical file structure")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Vault metadata")
    content: Optional[Dict[str, str]] = Field(None, description="File contents if requested")
    total_files: int = Field(default=0, description="Total file count")
    last_updated: str = Field(..., description="Last update timestamp")


class VaultAnalysisResponse(BaseModel):
    """Comprehensive vault analysis response"""
    success: bool = Field(default=True, description="Analysis success status")
    stats: VaultStats = Field(..., description="Vault statistics")
    insights: List[str] = Field(default_factory=list, description="Generated insights")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")
    analysis_date: str = Field(..., description="Analysis timestamp")
    error: Optional[str] = Field(None, description="Error message if analysis failed")


# Task Planning Models
class Task(BaseModel):
    """Individual task"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    priority: Literal["low", "medium", "high"] = Field(default="medium")
    estimated_time: str = Field(..., description="Estimated completion time")
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")
    status: Literal["pending", "in_progress", "completed"] = Field(default="pending")


class Milestone(BaseModel):
    """Project milestone"""
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    target_date: str = Field(..., description="Target completion date")
    tasks: List[str] = Field(default_factory=list, description="Associated task IDs")


class TaskPlan(BaseModel):
    """Complete task plan"""
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    tasks: List[Task] = Field(default_factory=list)
    estimated_duration: str = Field(..., description="Total estimated duration")


class TaskPlanningRequest(BaseModel):
    """Task planning request"""
    goal: str = Field(..., min_length=10, description="Planning goal")
    timeframe: Optional[str] = Field(None, description="Desired timeframe")
    context: Optional[str] = Field(None, description="Planning context")
    constraints: Optional[List[str]] = Field(None, description="Planning constraints")


class TaskPlanningResponse(BaseModel):
    """Task planning response"""
    plan: TaskPlan = Field(..., description="Generated task plan")
    timeline: str = Field(..., description="Execution timeline")
    milestones: List[Milestone] = Field(default_factory=list, description="Key milestones")


# Intelligence Parsing Models
class Entity(BaseModel):
    """Extracted entity"""
    type: str = Field(..., description="Entity type")
    value: str = Field(..., description="Entity value")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence")
    start: int = Field(..., ge=0, description="Start position in text")
    end: int = Field(..., ge=0, description="End position in text")


class ContextInfo(BaseModel):
    """Context information"""
    domain: str = Field(..., description="Content domain")
    sentiment: str = Field(..., description="Sentiment analysis")
    topics: List[str] = Field(default_factory=list, description="Identified topics")
    keywords: List[str] = Field(default_factory=list, description="Key terms")


class IntelligenceParseRequest(BaseModel):
    """Intelligence parsing request"""
    text: str = Field(..., min_length=1, description="Text to parse")
    parse_type: Literal["intent", "entities", "context", "all"] = Field(
        default="all", description="Type of parsing to perform"
    )


class IntelligenceParseResponse(BaseModel):
    """Intelligence parsing response"""
    intent: str = Field(..., description="Detected intent")
    entities: List[Entity] = Field(default_factory=list, description="Extracted entities")
    context: ContextInfo = Field(..., description="Context information")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")


# Intent Classification Models
class IntentResult(BaseModel):
    """Intent classification result"""
    intent: Literal["ask", "agent"] = Field(..., description="Classified intent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")


class IntentDebug(BaseModel):
    """Intent classification debug info"""
    intent: Literal["ask", "agent"] = Field(..., description="Classified intent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")
    matched_example: Optional[str] = Field(None, description="Matched training example")
    reasoning: Optional[str] = Field(None, description="Classification reasoning")
    features: Optional[Dict[str, float]] = Field(None, description="Feature weights")


# Memory Models
class MemoryUpdateRequest(BaseModel):
    """Memory update request"""
    user_id: Optional[str] = Field(None, description="User identifier")
    information: str = Field(..., min_length=1, description="Information to store")
    context: Optional[str] = Field(None, description="Memory context")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Memory importance")


# WebSocket Models
class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: Literal["chat", "workflow_progress", "copilot", "vault_sync", "intent_debug", "error"]
    data: Any = Field(..., description="Message payload")
    timestamp: datetime = Field(default_factory=datetime.now)


class WorkflowProgress(BaseModel):
    """Workflow progress update"""
    step: str = Field(..., description="Current step description")
    progress: float = Field(..., ge=0.0, le=1.0, description="Progress percentage")
    status: Literal["running", "completed", "error"] = Field(..., description="Step status")
    details: Optional[str] = Field(None, description="Additional details")


# Error Models
class ErrorResponse(BaseModel):
    """Standardized error response"""
    error: str = Field(..., description="Error message")
    code: Optional[int] = Field(None, description="Error code")
    details: Optional[str] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.now)
    url: Optional[str] = Field(None, description="Request URL")
    method: Optional[str] = Field(None, description="HTTP method")


# Validation Error Models (for 422 responses)
class ValidationError(BaseModel):
    """Individual validation error"""
    type: str = Field(..., description="Error type")
    loc: List[Union[str, int]] = Field(..., description="Error location")
    msg: str = Field(..., description="Error message")
    input: Optional[Any] = Field(None, description="Invalid input")


class ValidationErrorResponse(BaseModel):
    """422 Validation error response"""
    error: str = "Validation Error"
    message: str = "The request data doesn't match the expected format"
    validation_errors: List[ValidationError] = Field(..., description="Detailed validation errors")
    url: str = Field(..., description="Request URL")
    method: str = Field(..., description="HTTP method")
