# EvoAgentX Obsidian Integration Documentation

## Overview

This document provides comprehensive integration documentation for the EvoAgentX backend API, specifically designed to enable seamless integration with the VaultPilot Obsidian plugin. The EvoAgentX backend offers 15+ specialized endpoints for Obsidian integration, WebSocket support for real-time communication, and advanced AI capabilities.

## 1. API Endpoint Documentation

### Base Configuration
- **Base URL**: `http://localhost:8000` (configurable)
- **API Prefix**: `/api/obsidian`
- **Content-Type**: `application/json`
- **CORS**: Configured for cross-origin requests

### Agent Chat Endpoints

#### POST `/api/obsidian/chat`
Chat with an AI agent in a conversational manner.

**Request Schema:**
```typescript
interface AgentChatRequest {
  message: string;
  conversation_id?: string;
  agent_name?: string;
  context?: Record<string, any>;
}
```

**Response Schema:**
```typescript
interface AgentChatResponse {
  response: string;
  conversation_id: string;
  agent_name: string;
  timestamp: string;
  metadata?: Record<string, any>;
}
```

**Example:**
```typescript
const response = await fetch(`${serverUrl}/api/obsidian/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "Help me organize my notes about machine learning",
    context: { current_file: "ML_Notes.md" }
  })
});
```

#### POST `/api/obsidian/conversation/history`
Retrieve conversation history.

**Request Schema:**
```typescript
interface ConversationHistoryRequest {
  conversation_id: string;
  limit?: number; // default: 50
}
```

**Response Schema:**
```typescript
interface ConversationHistoryResponse {
  conversation_id: string;
  messages: ChatMessage[];
  total_count: number;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}
```

### Copilot Completion Endpoints

#### POST `/api/obsidian/copilot/complete`
Provide intelligent text completion while writing.

**Request Schema:**
```typescript
interface CopilotCompletionRequest {
  text: string;
  cursor_position: number;
  file_type?: string; // default: "markdown"
  context?: string;
}
```

**Response Schema:**
```typescript
interface CopilotCompletionResponse {
  completion: string;
  confidence: number; // 0.0 to 1.0
  suggestions: string[];
}
```

**Example:**
```typescript
const completion = await fetch(`${serverUrl}/api/obsidian/copilot/complete`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: "## Machine Learning Concepts\n\nNeural networks are",
    cursor_position: 45,
    file_type: "markdown",
    context: "academic notes"
  })
});
```

### Workflow Execution Endpoints

#### POST `/api/obsidian/workflow`
Execute a full EvoAgentX workflow.

**Request Schema:**
```typescript
interface WorkflowRequest {
  goal: string;
  context?: Record<string, any>;
}
```

**Response Schema:**
```typescript
interface WorkflowResponse {
  goal: string;
  output: string;
  graph?: Record<string, any>;
  execution_id: string;
  status: string;
}
```

**Example:**
```typescript
const workflow = await fetch(`${serverUrl}/api/obsidian/workflow`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    goal: "Create a comprehensive study plan for machine learning",
    context: { vault_size: 150, focus_area: "deep_learning" }
  })
});
```

### Vault Analysis Endpoints

#### POST `/api/obsidian/vault/context`
Analyze Obsidian vault content and provide insights.

**Request Schema:**
```typescript
interface VaultContextRequest {
  file_paths: string[];
  content_snippets?: Record<string, string>;
}
```

**Response Schema:**
```typescript
interface VaultContextResponse {
  context_summary: string;
  relevant_notes: Array<{
    path: string;
    relevance: number;
    snippet: string;
  }>;
}
```

### Task Planning Endpoints

#### POST `/api/obsidian/planning/tasks`
Plan tasks and create actionable steps.

**Request Schema:**
```typescript
interface TaskPlanningRequest {
  goal: string;
  constraints?: string[];
  deadline?: string; // ISO date string
}
```

**Response Schema:**
```typescript
interface TaskPlanningResponse {
  plan: Record<string, any>;
  subtasks: Array<{
    name: string;
    priority: "low" | "medium" | "high";
    estimated_time: number; // minutes
  }>;
  estimated_duration?: number; // minutes
}
```

### Agent Management Endpoints

#### GET `/api/obsidian/agents`
List all available agents.

**Response Schema:**
```typescript
interface AgentListResponse {
  agents: Array<{
    name: string;
    description: string;
    actions: string[];
    type: string;
  }>;
}
```

#### POST `/api/obsidian/agents/create`
Create a new custom agent.

**Request Parameters:**
```typescript
interface CreateAgentRequest {
  name: string;
  description: string;
  system_prompt: string;
  prompt: string;
}
```

#### POST `/api/obsidian/agent/execute`
Execute a specific action on an agent.

**Request Schema:**
```typescript
interface AgentExecutionRequest {
  agent_name: string;
  action_name: string;
  inputs: Record<string, any>;
  conversation_id?: string;
}
```

**Response Schema:**
```typescript
interface AgentExecutionResponse {
  result: any;
  execution_time: number;
  conversation_id: string;
  metadata: Record<string, any>;
}
```

### Intelligence Parsing Endpoints

#### POST `/api/obsidian/intelligence/parse`
Parse user input for intelligence and context extraction.

**Request Schema:**
```typescript
interface IntelligenceParseRequest {
  user_id: string;
  history: Array<{ role: string; content: string }>;
  user_input: string;
}
```

**Response Schema:**
```typescript
interface IntelligenceParseResponse {
  response: string;
  parsed_data?: Record<string, any>;
  follow_up_needed: boolean;
}
```

### Memory Management Endpoints

#### POST `/api/obsidian/memory/update`
Update user memory/context.

**Request Schema:**
```typescript
interface MemoryUpdateRequest {
  user_id: string;
  memory_updates: Record<string, any>;
}
```

**Response Schema:**
```typescript
interface MemoryUpdateResponse {
  success: boolean;
  updated_memory: Record<string, any>;
}
```

### Utility Endpoints

#### GET `/api/obsidian/health`
Health check endpoint.

**Response:**
```typescript
interface HealthResponse {
  status: "healthy";
  timestamp: string;
  active_agents: number;
  active_conversations: number;
}
```

#### DELETE `/api/obsidian/conversations/{conversation_id}`
Delete a conversation.

**Response:**
```typescript
interface DeleteResponse {
  success: boolean;
  message: string;
}
```

## 2. WebSocket Integration Details

### Connection URL and Protocols
```
ws://localhost:8000/ws/obsidian?vault_id={optional_vault_id}
```

### Authentication/Handshake Process
No authentication required for WebSocket connections. The connection automatically sends a welcome message upon successful connection.

### Message Formats

#### Connection Established
```typescript
{
  type: "connection_established",
  connection_id: string,
  vault_id?: string,
  timestamp: string
}
```

#### Ping/Pong
```typescript
// Client sends:
{
  type: "ping"
}

// Server responds:
{
  type: "pong",
  timestamp: string
}
```

#### Chat Messages
```typescript
// Client sends:
{
  type: "chat_message",
  content: string,
  conversation_id?: string
}

// Server responds:
{
  type: "chat_received",
  message: string,
  timestamp: string
}
```

#### Vault Updates
```typescript
// Client sends:
{
  type: "vault_update",
  vault_id: string,
  update: Record<string, any>
}

// Server broadcasts to vault:
{
  type: "vault_sync",
  update: Record<string, any>,
  timestamp: string
}
```

#### Workflow Progress
```typescript
{
  type: "workflow_progress",
  workflow_id: string,
  progress: {
    step: string,
    percentage: number,
    message: string
  },
  timestamp: string
}
```

#### Agent Responses
```typescript
{
  type: "agent_response",
  conversation_id: string,
  response: Record<string, any>,
  timestamp: string
}
```

#### Copilot Suggestions
```typescript
{
  type: "copilot_suggestion",
  suggestion: {
    completion: string,
    confidence: number,
    context: string
  },
  timestamp: string
}
```

#### Error Messages
```typescript
{
  type: "error",
  message: string,
  timestamp: string
}
```

### Connection Management Best Practices

1. **Reconnection Handling**: Implement exponential backoff for reconnections
2. **Heartbeat**: Send ping messages every 30 seconds
3. **Error Handling**: Listen for error events and log appropriately
4. **Per-vault Connections**: Use vault_id parameter for vault-specific features

## 3. TypeScript Type Definitions

### Core Interfaces
```typescript
// Chat and Communication
interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface ConversationContext {
  vault_id?: string;
  current_file?: string;
  selection?: string;
  context_files?: string[];
}

// Agent Types
interface AgentInfo {
  name: string;
  description: string;
  actions: string[];
  type: string;
  status: "active" | "inactive";
}

// Workflow Types
interface WorkflowGraph {
  nodes: Array<{
    id: string;
    type: string;
    agent: string;
    description: string;
  }>;
  edges: Array<{
    from: string;
    to: string;
    condition?: string;
  }>;
}

// Memory and Context
interface UserMemory {
  energyLevel?: "low" | "medium" | "high";
  mood?: string;
  goals?: string[];
  avoidances?: string[];
  intent?: string;
  priority?: "low" | "med" | "high";
  deadline?: string | null;
  durationMinutes?: number | null;
  nextAction?: string;
}

// WebSocket Message Types
type WebSocketMessage = 
  | ConnectionEstablished
  | PingMessage
  | PongMessage
  | ChatMessageWS
  | ChatReceived
  | VaultUpdate
  | VaultSync
  | WorkflowProgress
  | AgentResponse
  | CopilotSuggestion
  | ErrorMessage;

interface WebSocketEvent<T = any> {
  type: string;
  timestamp: string;
  data?: T;
}

// Error Response Format
interface ErrorResponse {
  status: "error";
  message: string;
  errors?: Array<{
    field: string;
    message: string;
  }>;
}

// Configuration Objects
interface EvoAgentXConfig {
  serverUrl: string;
  enableWebSocket: boolean;
  enableCopilot: boolean;
  reconnectInterval: number;
  heartbeatInterval: number;
  defaultAgent?: string;
  vaultId?: string;
}
```

## 4. Example Integration Code

### Basic API Client Setup
```typescript
class EvoAgentXClient {
  private serverUrl: string;
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private heartbeatInterval: NodeJS.Timeout | null = null;

  constructor(config: EvoAgentXConfig) {
    this.serverUrl = config.serverUrl;
    
    if (config.enableWebSocket) {
      this.connectWebSocket(config.vaultId);
    }
  }

  // REST API methods
  async chat(message: string, conversationId?: string, context?: ConversationContext): Promise<AgentChatResponse> {
    const response = await fetch(`${this.serverUrl}/api/obsidian/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        context
      })
    });

    if (!response.ok) {
      throw new Error(`Chat failed: ${response.statusText}`);
    }

    return response.json();
  }

  async getCompletion(text: string, cursorPosition: number, fileType?: string): Promise<CopilotCompletionResponse> {
    const response = await fetch(`${this.serverUrl}/api/obsidian/copilot/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        cursor_position: cursorPosition,
        file_type: fileType || 'markdown'
      })
    });

    if (!response.ok) {
      throw new Error(`Completion failed: ${response.statusText}`);
    }

    return response.json();
  }

  async executeWorkflow(goal: string, context?: Record<string, any>): Promise<WorkflowResponse> {
    const response = await fetch(`${this.serverUrl}/api/obsidian/workflow`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ goal, context })
    });

    if (!response.ok) {
      throw new Error(`Workflow execution failed: ${response.statusText}`);
    }

    return response.json();
  }

  async analyzeVault(filePaths: string[], contentSnippets?: Record<string, string>): Promise<VaultContextResponse> {
    const response = await fetch(`${this.serverUrl}/api/obsidian/vault/context`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        file_paths: filePaths,
        content_snippets: contentSnippets
      })
    });

    if (!response.ok) {
      throw new Error(`Vault analysis failed: ${response.statusText}`);
    }

    return response.json();
  }

  async planTasks(goal: string, constraints?: string[], deadline?: Date): Promise<TaskPlanningResponse> {
    const response = await fetch(`${this.serverUrl}/api/obsidian/planning/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        goal,
        constraints,
        deadline: deadline?.toISOString()
      })
    });

    if (!response.ok) {
      throw new Error(`Task planning failed: ${response.statusText}`);
    }

    return response.json();
  }

  // WebSocket methods
  private connectWebSocket(vaultId?: string) {
    const wsUrl = `${this.serverUrl.replace('http', 'ws')}/ws/obsidian${vaultId ? `?vault_id=${vaultId}` : ''}`;
    
    try {
      this.ws = new WebSocket(wsUrl);
      this.setupWebSocketHandlers();
    } catch (error) {
      console.error('WebSocket connection failed:', error);
      this.scheduleReconnect();
    }
  }

  private setupWebSocketHandlers() {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('Connected to EvoAgentX WebSocket');
      this.reconnectAttempts = 0;
      this.startHeartbeat();
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.handleWebSocketMessage(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket connection closed');
      this.stopHeartbeat();
      this.scheduleReconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  private handleWebSocketMessage(message: WebSocketMessage) {
    switch (message.type) {
      case 'connection_established':
        console.log('Connection established:', message);
        break;
      
      case 'agent_response':
        this.onAgentResponse?.(message as AgentResponse);
        break;
      
      case 'copilot_suggestion':
        this.onCopilotSuggestion?.(message as CopilotSuggestion);
        break;
      
      case 'workflow_progress':
        this.onWorkflowProgress?.(message as WorkflowProgress);
        break;
      
      case 'error':
        console.error('Server error:', message.message);
        break;
      
      default:
        console.log('Unknown message type:', message.type);
    }
  }

  private startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // 30 seconds
  }

  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    const delay = Math.pow(2, this.reconnectAttempts) * 1000; // Exponential backoff
    this.reconnectAttempts++;

    setTimeout(() => {
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      this.connectWebSocket();
    }, delay);
  }

  // Event handlers (override these)
  onAgentResponse?: (response: AgentResponse) => void;
  onCopilotSuggestion?: (suggestion: CopilotSuggestion) => void;
  onWorkflowProgress?: (progress: WorkflowProgress) => void;

  // Cleanup
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.stopHeartbeat();
  }
}
```

### Obsidian Plugin Integration Example
```typescript
export default class VaultPilotPlugin extends Plugin {
  private evoClient: EvoAgentXClient;
  private currentConversationId: string | null = null;

  async onload() {
    await this.loadSettings();

    // Initialize EvoAgentX client
    this.evoClient = new EvoAgentXClient({
      serverUrl: this.settings.serverUrl,
      enableWebSocket: this.settings.enableRealtime,
      enableCopilot: this.settings.enableCopilot,
      reconnectInterval: 5000,
      heartbeatInterval: 30000,
      vaultId: this.getVaultId()
    });

    // Set up event handlers
    this.evoClient.onAgentResponse = this.handleAgentResponse.bind(this);
    this.evoClient.onCopilotSuggestion = this.handleCopilotSuggestion.bind(this);
    this.evoClient.onWorkflowProgress = this.handleWorkflowProgress.bind(this);

    // Add commands
    this.addCommand({
      id: 'vaultpilot-chat',
      name: 'Open AI Chat',
      callback: () => this.openChatModal()
    });

    this.addCommand({
      id: 'vaultpilot-complete',
      name: 'Get AI Completion',
      editorCallback: (editor: Editor) => this.handleCompletion(editor)
    });

    this.addCommand({
      id: 'vaultpilot-workflow',
      name: 'Execute Workflow',
      callback: () => this.executeWorkflowModal()
    });

    this.addCommand({
      id: 'vaultpilot-analyze',
      name: 'Analyze Vault',
      callback: () => this.analyzeVault()
    });
  }

  private async handleCompletion(editor: Editor) {
    const cursor = editor.getCursor();
    const text = editor.getValue();
    const cursorPosition = editor.posToOffset(cursor);
    
    try {
      const completion = await this.evoClient.getCompletion(text, cursorPosition);
      
      if (completion.completion) {
        const completionModal = new CompletionModal(this.app, completion);
        completionModal.onAccept = (selectedCompletion: string) => {
          editor.replaceRange(selectedCompletion, cursor);
        };
        completionModal.open();
      }
    } catch (error) {
      new Notice(`Completion failed: ${error.message}`);
    }
  }

  private async executeWorkflowModal() {
    const modal = new WorkflowGoalModal(this.app);
    modal.onSubmit = async (goal: string) => {
      try {
        const context = await this.buildVaultContext();
        const workflow = await this.evoClient.executeWorkflow(goal, context);
        
        new WorkflowResultModal(this.app, workflow).open();
      } catch (error) {
        new Notice(`Workflow failed: ${error.message}`);
      }
    };
    modal.open();
  }

  private async analyzeVault() {
    try {
      const files = this.app.vault.getMarkdownFiles();
      const filePaths = files.map(f => f.path).slice(0, 20); // Limit for performance
      
      const analysis = await this.evoClient.analyzeVault(filePaths);
      new VaultAnalysisModal(this.app, analysis).open();
    } catch (error) {
      new Notice(`Analysis failed: ${error.message}`);
    }
  }

  private async buildVaultContext(): Promise<Record<string, any>> {
    const files = this.app.vault.getMarkdownFiles();
    const activeFile = this.app.workspace.getActiveFile();
    
    return {
      vault_size: files.length,
      active_file: activeFile?.path,
      total_words: files.reduce((sum, file) => sum + (this.app.vault.cachedRead(file).then(content => content.split(' ').length) || 0), 0)
    };
  }

  private getVaultId(): string {
    // Generate or retrieve unique vault identifier
    return this.app.vault.adapter.getName() || 'default-vault';
  }

  private handleAgentResponse(response: AgentResponse) {
    // Handle real-time agent responses
    console.log('Agent response received:', response);
  }

  private handleCopilotSuggestion(suggestion: CopilotSuggestion) {
    // Handle real-time copilot suggestions
    if (this.settings.enableCopilot) {
      this.showInlineCompletion(suggestion.suggestion);
    }
  }

  private handleWorkflowProgress(progress: WorkflowProgress) {
    // Show workflow progress
    new Notice(`Workflow Progress: ${progress.progress.message}`);
  }

  onunload() {
    this.evoClient?.disconnect();
  }
}
```

## 5. Configuration and Setup

### Default Server Configuration
```typescript
const DEFAULT_CONFIG = {
  host: "0.0.0.0",
  port: 8000,
  cors_origins: ["http://localhost:5173", "*"],
  log_level: "INFO",
  mongodb_url: process.env.MONGODB_URL || "mongodb://localhost:27017",
  mongodb_db_name: "evoagentx"
};
```

### Required Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=evoagentx
ALLOWED_ORIGINS=http://localhost:5173,https://your-domain.com
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

### CORS Settings
The server is configured to accept requests from:
- `http://localhost:5173` (Vite development server)
- Any Obsidian plugin origin
- Custom origins via `ALLOWED_ORIGINS` environment variable

### Server Startup
```bash
# Development
uvicorn server.main:sio_app --host 0.0.0.0 --port 8000 --reload

# Production
python -m evoagentx.app.main
```

### Health Check Endpoints
- `GET /`: Basic health check
- `GET /api/obsidian/health`: Detailed health status
- `GET /metrics`: System metrics

## 6. Integration Architecture

### Data Flow Patterns

1. **Request-Response Pattern**: For immediate operations (chat, completion, analysis)
2. **WebSocket Events**: For real-time updates (workflow progress, live suggestions)
3. **Background Processing**: For long-running workflows with progress updates

### Recommended Architecture
```
Obsidian Plugin (VaultPilot)
    ↓ (HTTP/WebSocket)
EvoAgentX Backend Server
    ↓ (MongoDB)
Database Layer
    ↓ (LLM APIs)
AI Model Providers (OpenAI, etc.)
```

### Caching Strategies
- **Conversation History**: In-memory caching with MongoDB persistence
- **Agent Instances**: Singleton pattern for active agents
- **Vault Context**: Debounced updates with incremental analysis

### Offline Handling
- Queue API requests when offline
- Show cached conversation history
- Disable real-time features gracefully
- Provide offline indicators in UI

## 7. Error Handling and Edge Cases

### Common Error Scenarios

#### HTTP Status Codes
- `400`: Bad Request (invalid parameters, goal too short)
- `401`: Unauthorized (if authentication is enabled)
- `404`: Not Found (agent, conversation, or resource not found)
- `422`: Validation Error (malformed request body)
- `500`: Internal Server Error (LLM failures, system errors)

#### Network Failure Handling
```typescript
class NetworkErrorHandler {
  static async handleAPIError(error: any): Promise<void> {
    if (error.name === 'NetworkError') {
      new Notice('Network connection failed. Please check your connection.');
    } else if (error.status === 500) {
      new Notice('Server error. Please try again later.');
    } else if (error.status === 400) {
      new Notice(`Request error: ${error.message}`);
    } else {
      new Notice('An unexpected error occurred.');
    }
  }
}
```

#### WebSocket Error Handling
```typescript
// Implement exponential backoff for reconnections
private calculateBackoffDelay(attempt: number): number {
  return Math.min(30000, Math.pow(2, attempt) * 1000);
}

// Handle connection drops gracefully
private onWebSocketError(error: Event) {
  console.error('WebSocket error:', error);
  this.showOfflineIndicator();
  this.scheduleReconnect();
}
```

### Rate Limiting and Retry Strategies
```typescript
class RateLimitHandler {
  private requestQueue: Array<() => Promise<any>> = [];
  private isProcessing = false;
  private lastRequestTime = 0;
  private minRequestInterval = 100; // ms

  async executeRequest<T>(request: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      this.requestQueue.push(async () => {
        try {
          const now = Date.now();
          const timeSinceLastRequest = now - this.lastRequestTime;
          
          if (timeSinceLastRequest < this.minRequestInterval) {
            await this.delay(this.minRequestInterval - timeSinceLastRequest);
          }
          
          this.lastRequestTime = Date.now();
          const result = await request();
          resolve(result);
        } catch (error) {
          reject(error);
        }
      });
      
      this.processQueue();
    });
  }

  private async processQueue() {
    if (this.isProcessing || this.requestQueue.length === 0) return;
    
    this.isProcessing = true;
    
    while (this.requestQueue.length > 0) {
      const request = this.requestQueue.shift();
      if (request) {
        await request();
      }
    }
    
    this.isProcessing = false;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

### Large File/Vault Handling
- **File Size Limits**: 10MB per file for content analysis
- **Vault Size Limits**: Process up to 1000 files at once
- **Pagination**: Use pagination for large vault analysis
- **Streaming**: Support streaming responses for large completions

### Timeout Configurations
```typescript
const TIMEOUT_CONFIG = {
  chat: 30000,        // 30 seconds
  completion: 15000,  // 15 seconds
  workflow: 300000,   // 5 minutes
  analysis: 60000,    // 1 minute
  websocket: 5000     // 5 seconds for connection
};
```

## 8. Performance Considerations

### Optimal Request Batching
```typescript
class BatchRequestManager {
  private batchSize = 5;
  private batchTimeout = 1000; // ms
  private pendingRequests: Array<{
    request: any;
    resolve: Function;
    reject: Function;
  }> = [];

  async batchRequest(request: any): Promise<any> {
    return new Promise((resolve, reject) => {
      this.pendingRequests.push({ request, resolve, reject });
      
      if (this.pendingRequests.length >= this.batchSize) {
        this.processBatch();
      } else {
        setTimeout(() => this.processBatch(), this.batchTimeout);
      }
    });
  }

  private async processBatch() {
    if (this.pendingRequests.length === 0) return;
    
    const batch = this.pendingRequests.splice(0, this.batchSize);
    
    try {
      const batchRequest = {
        requests: batch.map(item => item.request)
      };
      
      const response = await fetch('/api/obsidian/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(batchRequest)
      });
      
      const results = await response.json();
      
      batch.forEach((item, index) => {
        item.resolve(results[index]);
      });
    } catch (error) {
      batch.forEach(item => item.reject(error));
    }
  }
}
```

### Recommended Polling Intervals
- **Workflow Status**: 2-5 seconds
- **Agent Status**: 10-30 seconds
- **Vault Sync**: 30-60 seconds
- **Health Check**: 5 minutes

### Memory Usage Considerations
- **Conversation Limits**: 50 messages per conversation
- **Agent Caching**: Maximum 10 active agents
- **WebSocket Connections**: Limit 100 concurrent connections
- **File Caching**: 100MB maximum cache size

### Concurrent Request Limitations
- **Per Client**: 10 concurrent requests
- **Per Vault**: 5 concurrent analysis requests
- **Global**: 1000 concurrent requests

## 9. Migration Guide

### From Basic VaultPilot to Full Integration

1. **Replace Simple /run Endpoint**:
```typescript
// Old approach
const result = await fetch('/run', {
  method: 'POST',
  body: JSON.stringify({ goal: 'my goal' })
});

// New approach
const client = new EvoAgentXClient(config);
const result = await client.executeWorkflow('my goal', context);
```

2. **Add WebSocket Integration**:
```typescript
// Initialize with WebSocket support
const client = new EvoAgentXClient({
  serverUrl: 'http://localhost:8000',
  enableWebSocket: true,
  vaultId: this.getVaultId()
});

// Handle real-time events
client.onWorkflowProgress = (progress) => {
  this.updateProgressBar(progress);
};
```

3. **Implement Chat Interface**:
```typescript
class ChatView extends ItemView {
  private conversationId: string | null = null;
  
  async sendMessage(message: string) {
    const response = await this.client.chat(
      message, 
      this.conversationId,
      this.buildContext()
    );
    
    this.conversationId = response.conversation_id;
    this.displayMessage(response);
  }
}
```

4. **Add Copilot Functionality**:
```typescript
// Hook into editor events
this.registerEvent(
  this.app.workspace.on('editor-change', (editor) => {
    this.debouncedCompletion(editor);
  })
);

private debouncedCompletion = debounce(async (editor: Editor) => {
  const text = editor.getValue();
  const cursor = editor.getCursor();
  const position = editor.posToOffset(cursor);
  
  const completion = await this.client.getCompletion(text, position);
  this.showInlineCompletion(completion);
}, 500);
```

This comprehensive documentation provides all the necessary information to integrate the VaultPilot Obsidian plugin with the EvoAgentX backend. The implementation includes proper error handling, real-time communication, and performance optimizations for a seamless user experience.
