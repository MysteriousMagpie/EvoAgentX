# EvoAgentX Backend API Documentation for Frontend

This document explains exactly what the backend expects to receive from the frontend for each API endpoint.

## Base URL
- Development: `http://localhost:8000`
- All API endpoints are prefixed with the base URL

## Headers
For all requests, include:
```javascript
{
  "Content-Type": "application/json",
  "Accept": "application/json"
}
```

## API Endpoints

### 1. Code Execution API

#### POST `/execute`
Execute code in a Docker container.

**Request Body:**
```javascript
{
  "code": "print('Hello World')",           // Required: string - Code to execute
  "runtime": "python:3.11",                // Optional: string - Runtime environment
  "limits": {                               // Optional: Resource limits
    "memory": "512m",                       // Optional: string - Memory limit
    "cpus": "1.0",                         // Optional: string - CPU limit  
    "pids": 64,                            // Optional: number - Process limit
    "timeout": 20                          // Optional: number - Timeout in seconds
  }
}
```

**Allowed Runtimes:**
- `"python:3.11"` (default)
- `"node:20"`
- `"python:3.11-gpu"`

**Response:**
```javascript
{
  "stdout": "Hello World\n",               // string - Standard output
  "stderr": "",                            // string - Error output
  "exit_code": 0,                          // number - Exit code (0 = success)
  "runtime_seconds": 0.123                 // number - Execution time
}
```

**Example Frontend Code:**
```javascript
const executeCode = async (code, runtime = "python:3.11") => {
  const response = await fetch('http://localhost:8000/execute', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      code: code,
      runtime: runtime
    })
  });
  return await response.json();
};
```

---

### 2. Workflow Runner API

#### POST `/run`
Run an EvoAgent workflow with a goal.

**Request Body:**
```javascript
{
  "goal": "Analyze the data and create a report"  // Required: string - Goal description (min 10 chars)
}
```

**Response:**
```javascript
{
  "goal": "Analyze the data and create a report", // string - Original goal
  "output": "Report has been generated...",       // string - Workflow output
  "graph": {                                      // object|null - Execution graph
    "nodes": [...],
    "edges": [...]
  }
}
```

**Example Frontend Code:**
```javascript
const runWorkflow = async (goal) => {
  const response = await fetch('http://localhost:8000/run', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      goal: goal
    })
  });
  return await response.json();
};
```

---

### 3. Obsidian Integration API

All Obsidian endpoints are prefixed with `/api/obsidian`

#### POST `/api/obsidian/chat`
Chat with an AI agent.

**Request Body:**
```javascript
{
  "message": "How can I organize my notes better?", // Required: string - User message
  "conversation_id": "uuid-string",                 // Optional: string - Conversation ID
  "agent_name": "ObsidianAssistant",               // Optional: string - Agent name
  "context": {                                      // Optional: object - Additional context
    "vault_name": "MyVault",
    "current_file": "notes.md"
  }
}
```

**Response:**
```javascript
{
  "response": "Here are some tips for organizing notes...", // string - Agent response
  "conversation_id": "uuid-string",                        // string - Conversation ID
  "agent_name": "ObsidianAssistant",                       // string - Agent name
  "timestamp": "2025-06-27T10:30:00.123456",              // string - ISO timestamp
  "metadata": {                                            // object|null - Additional data
    "token_usage": 150,
    "model": "gpt-4o-mini"
  }
}
```

#### POST `/api/obsidian/conversation/history`
Get conversation history.

**Request Body:**
```javascript
{
  "conversation_id": "uuid-string",  // Required: string - Conversation ID
  "limit": 50                        // Optional: number - Message limit (default: 50)
}
```

**Response:**
```javascript
{
  "conversation_id": "uuid-string",   // string - Conversation ID
  "messages": [                       // array - Message history
    {
      "role": "user",                 // string - "user" or "assistant"
      "content": "Hello",             // string - Message content
      "timestamp": "2025-06-27T10:30:00.123456" // string|null - ISO timestamp
    }
  ],
  "total_count": 10                   // number - Total message count
}
```

#### POST `/api/obsidian/workflow`
Execute a workflow through Obsidian.

**Request Body:**
```javascript
{
  "goal": "Create a summary of my research notes", // Required: string - Workflow goal
  "context": {                                     // Optional: object - Additional context
    "vault_files": ["research.md", "notes.md"],
    "user_preferences": {...}
  }
}
```

**Response:**
```javascript
{
  "goal": "Create a summary of my research notes", // string - Original goal
  "output": "Summary: Your research covers...",     // string - Workflow output
  "graph": {...},                                   // object|null - Execution graph
  "execution_id": "uuid-string",                    // string - Execution ID
  "status": "completed"                             // string - Execution status
}
```

#### POST `/api/obsidian/intelligence/parse`
Parse user input with intelligence analysis.

**Request Body:**
```javascript
{
  "user_id": "user-123",              // Required: string - User ID
  "history": [                        // Required: array - Conversation history
    {
      "role": "user",                 // Required: string - Message role
      "content": "Hello"              // Required: string - Message content
    }
  ],
  "user_input": "What should I do next?" // Required: string - Current user input
}
```

**Response:**
```javascript
{
  "response": "Based on your history, I suggest...", // string - Parsed response
  "parsed_data": {                                   // object|null - Extracted data
    "intent": "planning",
    "entities": ["task", "schedule"]
  },
  "follow_up_needed": false                          // boolean - If follow-up required
}
```

---

### 4. Calendar API

All calendar endpoints are prefixed with `/events`

#### POST `/events/`
Create a new calendar event.

**Request Body:**
```javascript
{
  "title": "Team Meeting",                    // Required: string - Event title
  "start": "2025-06-27T14:00:00",           // Required: string - ISO datetime
  "end": "2025-06-27T16:00:00",             // Required: string - ISO datetime
  "notes": "Discuss project progress",       // Optional: string - Event notes
  "calendar": "Home"                         // Optional: string - Calendar name (default: "Home")
}
```

**Response:**
```javascript
{
  "id": "uuid-string",                       // string - Event ID
  "uid": "calendar-uid",                     // string|null - Calendar system UID
  "title": "Team Meeting",                   // string - Event title
  "start": "2025-06-27T14:00:00",           // string - ISO datetime
  "end": "2025-06-27T16:00:00",             // string - ISO datetime
  "notes": "Discuss project progress",       // string|null - Event notes
  "calendar": "Home"                         // string - Calendar name
}
```

#### GET `/events/`
List all events.

**Response:**
```javascript
[
  {
    "id": "uuid-string",
    "uid": "calendar-uid",
    "title": "Team Meeting",
    "start": "2025-06-27T14:00:00",
    "end": "2025-06-27T16:00:00",
    "notes": "Discuss project progress",
    "calendar": "Home"
  }
]
```

#### PUT `/events/{event_id}`
Update an existing event.

**Request Body:** (Same as POST `/events/`)

#### DELETE `/events/{event_id}`
Delete an event. Returns status 204 (No Content) on success.

---

### 5. Status API

#### GET `/status`
Get service health status.

**Response:**
```javascript
{
  "status": "ok",           // string - Service status
  "version": "1.0.0"        // string - EvoAgentX version
}
```

---

## WebSocket Connections

### Regular WebSocket: `/ws`
General purpose WebSocket for real-time updates.

### Obsidian WebSocket: `/ws/obsidian`
Specialized WebSocket for Obsidian plugin communication.

**Connection URL:**
```javascript
ws://localhost:8000/ws/obsidian?vault_id=optional-vault-id
```

**Message Format:**
```javascript
{
  "type": "ping|chat_message|vault_update", // string - Message type
  "content": "message content",              // string - Message content
  "vault_id": "vault-123",                   // string - Vault identifier
  "timestamp": "2025-06-27T10:30:00.123456" // string - ISO timestamp
}
```

---

## Error Handling

All endpoints return standardized error responses:

### Validation Error (422)
```javascript
{
  "error": "Validation Error",
  "message": "The request data doesn't match the expected format",
  "validation_errors": [
    {
      "loc": ["field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "url": "/api/endpoint",
  "method": "POST"
}
```

### Client Error (400)
```javascript
{
  "detail": "Invalid runtime"  // string - Error description
}
```

### Server Error (500)
```javascript
{
  "detail": "EvoAgent failed"  // string - Error description
}
```

---

## Important Notes

1. **Content-Type**: Always use `application/json` for POST/PUT requests
2. **CORS**: The backend accepts requests from `localhost:5173`, `localhost:5174`, and other configured origins
3. **Conversation IDs**: If not provided, a new UUID will be generated automatically
4. **Timestamps**: All timestamps are in ISO 8601 format
5. **Optional Fields**: Fields marked as optional can be omitted from requests
6. **Validation**: The backend validates all request data strictly - ensure all required fields are present

## Example Complete Frontend Integration

```javascript
class EvoAgentXAPI {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  async post(endpoint, data) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${await response.text()}`);
    }
    
    return await response.json();
  }

  // Chat with agent
  async chat(message, conversationId = null, agentName = null) {
    return await this.post('/api/obsidian/chat', {
      message,
      conversation_id: conversationId,
      agent_name: agentName
    });
  }

  // Execute code
  async executeCode(code, runtime = 'python:3.11') {
    return await this.post('/execute', {
      code,
      runtime
    });
  }

  // Run workflow
  async runWorkflow(goal) {
    return await this.post('/run', {
      goal
    });
  }

  // Create calendar event
  async createEvent(title, start, end, notes = null) {
    return await this.post('/events/', {
      title,
      start,
      end,
      notes
    });
  }
}

// Usage
const api = new EvoAgentXAPI();
const chatResponse = await api.chat("Hello, how can you help me?");
console.log(chatResponse.response);
```

This documentation should help your frontend team understand exactly what data formats the backend expects and how to structure their API calls correctly.
