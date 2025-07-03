from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union, Literal
from datetime import datetime


# Request/Response models for Obsidian integration

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    context_used: bool


class AgentChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    agent_name: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    mode: Literal["ask", "agent"] = Field(default="ask", description="Chat mode: 'ask' for simple Q&A, 'agent' for complex workflows")


class AgentChatResponse(BaseModel):
    response: str
    conversation_id: str
    agent_name: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class WorkflowRequest(BaseModel):
    goal: str
    context: Optional[str] = None


class WorkflowResponse(BaseModel):
    goal: str
    output: str
    graph: Optional[Dict[str, Any]] = None
    execution_id: str
    status: str


class CopilotCompletionRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The text content to complete")
    cursor_position: int = Field(..., ge=0, description="Position of cursor in the text")
    file_type: Optional[str] = Field(None, description="Type of file (markdown, text, etc.)")
    context: Optional[str] = Field(None, description="Additional context for completion")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello world, this is a sample text for",
                "cursor_position": 35,
                "file_type": "markdown",
                "context": "writing a technical document"
            }
        }


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


# Enhanced Vault Structure Management Schemas

class VaultStructureRequest(BaseModel):
    """Request vault structure information"""
    include_content: bool = Field(default=False, description="Include file content previews")
    max_depth: Optional[int] = Field(default=None, description="Maximum folder depth to scan")
    file_types: Optional[List[str]] = Field(default=None, description="Filter by file types (e.g., ['md', 'txt'])")


class VaultFileInfo(BaseModel):
    """Information about a single file in the vault"""
    path: str
    name: str
    size: int
    modified: datetime
    file_type: str
    content_preview: Optional[str] = None
    tags: Optional[List[str]] = None
    links: Optional[List[str]] = None


class VaultFolderInfo(BaseModel):
    """Information about a folder in the vault"""
    path: str
    name: str
    file_count: int
    subfolder_count: int
    files: List[VaultFileInfo]
    subfolders: List['VaultFolderInfo'] = []


VaultFolderInfo.model_rebuild()  # Enable forward references


class VaultStructureResponse(BaseModel):
    """Complete vault structure information"""
    vault_name: str
    total_files: int
    total_folders: int
    total_size: int
    structure: VaultFolderInfo
    recent_files: List[VaultFileInfo]
    orphaned_files: List[VaultFileInfo]


class FileOperationRequest(BaseModel):
    """Request to perform file operations"""
    operation: Literal["create", "update", "delete", "move", "copy"]
    file_path: str
    content: Optional[str] = None
    destination_path: Optional[str] = None
    create_missing_folders: bool = Field(default=True, description="Create missing parent folders")


class FileOperationResponse(BaseModel):
    """Response from file operation"""
    success: bool
    message: str
    file_path: str
    operation_performed: str


class BatchFileOperationRequest(BaseModel):
    """Request to perform multiple file operations"""
    operations: List[FileOperationRequest]
    continue_on_error: bool = Field(default=True, description="Continue processing if one operation fails")


class BatchFileOperationResponse(BaseModel):
    """Response from batch file operations"""
    success: bool
    completed_operations: int
    failed_operations: int
    results: List[FileOperationResponse]
    errors: List[str]


class VaultOrganizationRequest(BaseModel):
    """Request to reorganize vault structure"""
    organization_goal: str = Field(..., description="What you want to achieve with reorganization")
    current_structure: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User preferences for organization")
    dry_run: bool = Field(default=True, description="Preview changes without applying them")


class VaultOrganizationResponse(BaseModel):
    """Response from vault reorganization"""
    reorganization_plan: str
    suggested_changes: List[Dict[str, Any]]
    estimated_changes_count: int
    dry_run: bool
    execution_steps: Optional[List[str]] = None


class VaultSearchRequest(BaseModel):
    """Request to search vault content"""
    query: str
    search_type: Literal["content", "filename", "tags", "links"] = "content"
    file_types: Optional[List[str]] = None
    max_results: int = Field(default=50, le=200)
    include_context: bool = Field(default=True, description="Include surrounding context for matches")


class VaultSearchResult(BaseModel):
    """Individual search result"""
    file_path: str
    file_name: str
    match_type: str
    snippet: str
    line_number: Optional[int] = None
    relevance_score: float


class VaultSearchResponse(BaseModel):
    """Response from vault search"""
    query: str
    total_results: int
    results: List[VaultSearchResult]
    search_time: float


class VaultBackupRequest(BaseModel):
    """Request to create vault backup"""
    backup_name: Optional[str] = None
    include_settings: bool = Field(default=True, description="Include Obsidian settings in backup")
    compress: bool = Field(default=True, description="Create compressed backup")


class VaultBackupResponse(BaseModel):
    """Response from vault backup creation"""
    success: bool
    backup_path: str
    backup_size: int
    files_backed_up: int
    backup_time: datetime


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
