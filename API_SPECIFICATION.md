# EvoAgentX API Specification for Frontend Developers

## 🎯 Quick Reference

**Base URL**: `http://localhost:8000`  
**WebSocket**: `ws://localhost:8000/ws/obsidian`  
**Content-Type**: `application/json`  
**CORS**: ✅ Configured for cross-origin requests

## 📡 Core API Endpoints

### 1. Health & Status
```http
GET /status
Response: {"status": "OK", "timestamp": "2025-01-05T..."}
```

### 2. Agent Chat
```http
POST /api/obsidian/chat
Content-Type: application/json

{
  "message": "string",
  "conversation_id": "string | null",
  "vault_context": "string | null",
  "mode": "ask | agent"
}

→ {
  "response": "string",
  "conversation_id": "string",
  "agent_name": "string",
  "timestamp": "string",
  "metadata": {"token_usage": number, "model": "string"}
}
```

### 3. Intelligent Copilot
```http
POST /api/obsidian/copilot/complete
Content-Type: application/json

{
  "text": "string",
  "cursor_position": number,
  "file_type": "markdown",
  "vault_context": "string | null"
}

→ {
  "completion": "string",
  "suggestions": ["string"],
  "confidence": number
}
```

### 4. Workflow Execution
```http
POST /api/obsidian/workflow
Content-Type: application/json

{
  "goal": "string",
  "context": "string | null",
  "vault_content": "string | null"
}

→ {
  "workflow_id": "string",
  "result": "string",
  "artifacts": ["string"],
  "execution_time": number
}
```

### 5. Agent Management
```http
GET /api/obsidian/agents
→ [{
  "id": "string",
  "name": "string", 
  "description": "string",
  "capabilities": ["string"]
}]

POST /api/obsidian/agents/create
{
  "name": "string",
  "description": "string",
  "instructions": "string"
}
```

### 6. Vault Analysis
```http
POST /api/obsidian/vault/context
{
  "vault_path": "string",
  "analysis_type": "summary | insights | structure",
  "files": ["string"]
}

→ {
  "analysis": "string",
  "insights": ["string"],
  "recommendations": ["string"],
  "vault_stats": {
    "total_files": number,
    "total_words": number,
    "topics": ["string"]
  }
}
```

## 🌐 WebSocket Messages

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/obsidian');

// Send handshake
ws.send(JSON.stringify({
  type: "handshake",
  vault_id: "your-vault-id"
}));
```

### Message Types
```typescript
// Incoming message format
{
  type: "agent_response" | "copilot_suggestion" | "workflow_progress" | "vault_update",
  data: any,
  timestamp: string
}

// Outgoing message format  
{
  type: "ping" | "subscribe" | "unsubscribe",
  payload?: any
}
```

## ⚡ Advanced Features

### Agent Evolution
```http
POST /api/obsidian/agents/evolve
{
  "agent_id": "string",
  "feedback": "string",
  "performance_data": {
    "success_rate": number,
    "user_satisfaction": number
  }
}
```

### Multi-Modal Analysis
```http
POST /api/obsidian/multimodal/analyze
{
  "content": [{
    "type": "text | image | audio | file",
    "data": "string",
    "metadata": object
  }]
}
```

### Marketplace Integration
```http
GET /api/obsidian/marketplace/discover?category=research&rating_min=4.0

POST /api/obsidian/marketplace/install
{
  "agent_id": "string",
  "customization": object
}
```

### Calendar Integration
```http
POST /events/
{
  "title": "string",
  "start": "2025-01-05T14:00:00",
  "end": "2025-01-05T15:00:00",
  "notes": "string | null",
  "calendar": "string"
}

GET /events/
PUT /events/{event_id}
DELETE /events/{event_id}
```

## 🔧 TypeScript Interfaces

```typescript
// Core types
interface ChatRequest {
  message: string;
  conversation_id?: string;
  vault_context?: string;
  mode?: 'ask' | 'agent';
}

interface ChatResponse {
  response: string;
  conversation_id: string;
  agent_name: string;
  timestamp: string;
  metadata: {
    token_usage: number;
    model: string;
  };
}

interface CopilotRequest {
  text: string;
  cursor_position: number;
  file_type: string;
  vault_context?: string;
}

interface CopilotResponse {
  completion: string;
  suggestions: string[];
  confidence: number;
}

interface WorkflowRequest {
  goal: string;
  context?: string;
  vault_content?: string;
}

interface WorkflowResponse {
  workflow_id: string;
  result: string;
  artifacts: string[];
  execution_time: number;
}

// WebSocket message types
interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp: string;
}
```

## 🛠️ Example Implementation

```typescript
class EvoAgentXAPI {
  private baseUrl = 'http://localhost:8000';
  private ws: WebSocket | null = null;

  async chat(message: string, conversationId?: string): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/api/obsidian/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        mode: 'ask'
      })
    });

    if (!response.ok) {
      throw new Error(`Chat failed: ${response.statusText}`);
    }

    return await response.json();
  }

  async getCompletion(text: string, position: number): Promise<CopilotResponse> {
    const response = await fetch(`${this.baseUrl}/api/obsidian/copilot/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        cursor_position: position,
        file_type: 'markdown'
      })
    });

    return await response.json();
  }

  connectWebSocket(onMessage: (message: WebSocketMessage) => void) {
    this.ws = new WebSocket('ws://localhost:8000/ws/obsidian');
    
    this.ws.onopen = () => {
      this.ws?.send(JSON.stringify({
        type: 'handshake',
        vault_id: 'your-vault-id'
      }));
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      onMessage(message);
    };
  }
}
```

## 🚀 Quick Start

1. **Start Backend**: `python run_server.py`
2. **Test Connection**: `curl http://localhost:8000/status`
3. **Implement Client**: Use the API interfaces above
4. **Add WebSocket**: For real-time features
5. **Handle Errors**: Implement proper error handling

## 📚 Documentation Links

- **[Complete API Reference](./docs/api/FRONTEND_API_DOCUMENTATION.md)**
- **[Obsidian Integration Guide](./docs/obsidian-integration.md)**
- **[WebSocket Documentation](./WEBSOCKET_GUIDE.md)**
- **[Setup Guide](./docs/installation.md)**

**Ready for integration! 🎯**
