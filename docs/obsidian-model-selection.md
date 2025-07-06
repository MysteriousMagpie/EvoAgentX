# Enhanced Model Selection for VaultPilot Obsidian Plugin

## Overview

The EvoAgentX framework now includes a robust model selection system that intelligently chooses the optimal AI model for each task in your Obsidian vault. This system integrates seamlessly with the VaultPilot plugin through the devpipe communication framework.

## Key Features

### 🧠 Intelligent Model Selection
- **Task-Aware Selection**: Automatically chooses the best model based on the type of task (chat, code generation, vault management, etc.)
- **Performance-Based Optimization**: Learns from past performance to improve future selections
- **Cost-Aware Decisions**: Balances performance with cost considerations based on your preferences
- **Real-Time Health Monitoring**: Tracks model availability and performance in real-time

### 🔄 Automatic Fallback System
- **Smart Fallbacks**: Automatically switches to backup models when primary models are unavailable
- **Graceful Degradation**: Maintains functionality even when preferred models fail
- **Transparent Operation**: Shows you which model is being used and why

### ⚡ Performance Optimization
- **Response Time Tracking**: Monitors and optimizes for faster responses
- **Success Rate Monitoring**: Tracks model reliability for different task types
- **Quality Metrics**: Learns from user feedback to improve selections

## API Endpoints for Obsidian Plugin

### Model Selection

#### `POST /api/obsidian/models/select`
Select the optimal model for a specific task.

**Request:**
```typescript
interface ModelSelectionRequest {
  task_type: "chat" | "code_generation" | "text_analysis" | "reasoning" | 
             "creative_writing" | "summarization" | "translation" | "vault_management";
  preferred_models?: string[];           // Optional preferred model order
  constraints?: {
    max_cost_per_request?: number;       // Maximum acceptable cost
    min_success_rate?: number;           // Minimum success rate (0-1)
    max_response_time?: number;          // Maximum response time in seconds
    require_healthy_status?: boolean;    // Require healthy model status
  };
  context?: {
    vault_path?: string;                 // Current vault path
    file_context?: string;               // Context about current file/task
    user_preferences?: object;           // User-specific preferences
  };
}
```

**Response:**
```typescript
interface ModelSelectionResponse {
  success: boolean;
  selected_model?: {
    name: string;                        // Model identifier
    provider: string;                    // Model provider (openai, anthropic, etc.)
    model_id: string;                    // Specific model ID
    capabilities: string[];              // Supported task types
    performance_metrics?: {
      success_rate: number;              // Historical success rate
      avg_response_time: number;         // Average response time
      cost_per_request: number;          // Average cost per request
    };
  };
  fallback_models?: string[];            // Available fallback models
  reasoning?: string;                    // Explanation of selection
  error?: string;                        // Error message if selection failed
}
```

### Model Health Status

#### `POST /api/obsidian/models/health`
Get comprehensive health status for all or specific models.

**Request:**
```typescript
interface ModelHealthRequest {
  models?: string[];                     // Specific models to check (optional)
  include_metrics?: boolean;             // Include detailed metrics
}
```

**Response:**
```typescript
interface ModelHealthResponse {
  models: {
    [modelName: string]: {
      status: "healthy" | "degraded" | "failed" | "unknown";
      success_rate: number;
      total_requests: number;
      average_response_time: number;
      cost_per_success: number;
      last_success?: string;             // ISO timestamp
      last_failure?: string;             // ISO timestamp
      capabilities: string[];
      task_performance: {                // Performance per task type
        [taskType: string]: number;
      };
    };
  };
  summary: {
    total_models: number;
    healthy_models: number;
    degraded_models: number;
    failed_models: number;
    unknown_models: number;
  };
  timestamp: string;                     // When health check was performed
}
```

### User Preferences

#### `POST /api/obsidian/models/preferences`
Update user preferences for model selection.

**Request:**
```typescript
interface ModelPreferencesRequest {
  task_preferences?: {
    [taskType: string]: string[];        // Preferred models per task type
  };
  cost_constraints?: {
    [taskType: string]: number;          // Max cost per task type
  };
  performance_requirements?: {
    [taskType: string]: {
      min_success_rate?: number;
      max_response_time?: number;
    };
  };
}
```

### Available Models

#### `GET /api/obsidian/models/available`
Get list of all available models and their capabilities.

**Response:**
```typescript
interface AvailableModelsResponse {
  models: Array<{
    name: string;
    capabilities: string[];
    status: "healthy" | "degraded" | "failed" | "unknown";
  }>;
  total_count: number;
  task_types: string[];                  // All supported task types
}
```

## DevPipe Integration

The model selection system communicates with the Obsidian plugin through the devpipe framework using structured JSON messages.

### Message Types

#### Model Selection Request
```json
{
  "header": {
    "message_type": "model_selection_request",
    "sender": "frontend",
    "recipient": "ai_agent"
  },
  "payload": {
    "task_type": "vault_management",
    "preferred_models": ["gpt-4o-mini"],
    "constraints": {
      "max_cost_per_request": 0.05,
      "min_success_rate": 0.8
    },
    "context": {
      "vault_path": "/path/to/vault",
      "file_context": "organizing notes"
    }
  }
}
```

#### Model Health Status Update
```json
{
  "header": {
    "message_type": "model_health_status",
    "sender": "backend",
    "recipient": "frontend"
  },
  "payload": {
    "models": {
      "gpt-4o-mini": {
        "status": "healthy",
        "success_rate": 0.95,
        "average_response_time": 1.2
      }
    },
    "summary": {
      "healthy_models": 2,
      "total_models": 3
    }
  }
}
```

#### Performance Update
```json
{
  "header": {
    "message_type": "model_performance_update",
    "sender": "ai_agent",
    "recipient": "backend"
  },
  "payload": {
    "model_name": "gpt-4o-mini",
    "task_type": "vault_management",
    "success": true,
    "response_time": 2.1,
    "cost": 0.003,
    "quality_score": 0.9
  }
}
```

## Integration Guide for Plugin Developers

### 1. Basic Model Selection

```typescript
// Request optimal model for a chat task
const response = await fetch(`${serverUrl}/api/obsidian/models/select`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    task_type: "chat",
    context: {
      vault_path: app.vault.adapter.basePath,
      file_context: "User asking about note organization"
    }
  })
});

const modelSelection = await response.json();
if (modelSelection.success) {
  console.log(`Using model: ${modelSelection.selected_model.name}`);
  console.log(`Reasoning: ${modelSelection.reasoning}`);
}
```

### 2. Health Monitoring

```typescript
// Check model health status
const healthResponse = await fetch(`${serverUrl}/api/obsidian/models/health`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    include_metrics: true
  })
});

const health = await healthResponse.json();
const healthyModels = Object.keys(health.models).filter(
  model => health.models[model].status === 'healthy'
);
console.log(`${healthyModels.length} healthy models available`);
```

### 3. User Preferences

```typescript
// Update user preferences
const prefsResponse = await fetch(`${serverUrl}/api/obsidian/models/preferences`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    task_preferences: {
      chat: ["gpt-4o-mini", "gpt-3.5-turbo"],
      vault_management: ["gpt-4o-mini"],
      code_generation: ["gpt-4o", "gpt-4o-mini"]
    },
    cost_constraints: {
      chat: 0.01,          // Max $0.01 per chat
      vault_management: 0.05 // Max $0.05 per vault operation
    }
  })
});
```

### 4. DevPipe Communication

The plugin can listen for real-time updates through the devpipe framework:

```typescript
// Monitor devpipe for model health updates
const devpipeMonitor = new DevPipeMonitor('/path/to/devpipe');

devpipeMonitor.on('model_health_status', (message) => {
  const healthData = message.payload;
  updateModelStatusUI(healthData);
});

devpipeMonitor.on('model_performance_update', (message) => {
  const perfData = message.payload;
  logModelPerformance(perfData);
});
```

## Best Practices

### 1. Task Type Selection
- Use specific task types for better model selection
- `vault_management` for file operations and organization
- `chat` for conversational interactions
- `text_analysis` for content analysis and extraction
- `code_generation` for generating code snippets

### 2. Context Provision
- Always provide vault context when possible
- Include file-specific context for better model selection
- Pass user preferences to personalize selection

### 3. Error Handling
- Always check the `success` field in responses
- Implement fallback logic for when model selection fails
- Handle degraded model scenarios gracefully

### 4. Performance Optimization
- Cache model selections for similar tasks
- Monitor performance metrics to identify improvement opportunities
- Use the preferences API to optimize selections over time

## Configuration

### Environment Variables
```bash
# DevPipe integration path
DEVPIPE_PATH=/path/to/evoagentx/dev-pipe

# Model selection preferences
MODEL_SELECTION_ENABLED=true
MODEL_HEALTH_MONITORING=true
MODEL_PERFORMANCE_TRACKING=true
```

### Plugin Settings
```typescript
interface ModelSelectionSettings {
  enableIntelligentSelection: boolean;   // Enable smart model selection
  preferFastModels: boolean;             // Prioritize response time
  costConscious: boolean;                // Prioritize cost efficiency
  maxCostPerRequest: number;             // Global cost limit
  fallbackEnabled: boolean;              // Enable automatic fallbacks
  healthMonitoringInterval: number;      // Health check frequency (seconds)
}
```

## Troubleshooting

### Common Issues

1. **Model Selection Fails**
   - Check if models are properly configured
   - Verify API keys are set
   - Check model health status

2. **DevPipe Communication Issues**
   - Verify devpipe path is correct
   - Check file permissions
   - Monitor devpipe logs

3. **Performance Issues**
   - Review model selection criteria
   - Check network connectivity
   - Monitor response times

### Debug Mode
Enable debug logging to see detailed model selection decisions:

```typescript
const response = await fetch(`${serverUrl}/api/obsidian/models/select?debug=true`, {
  // ... request details
});
```

## Advanced Features

### Custom Model Registration
```typescript
// Register a custom model configuration
const customModel = {
  name: "custom-gpt-4",
  provider: "openai", 
  model_id: "gpt-4",
  capabilities: ["reasoning", "analysis"],
  cost_per_1k_tokens: 0.03,
  priority: 1
};
```

### Performance Analytics
```typescript
// Get detailed performance analytics
const analytics = await fetch(`${serverUrl}/api/obsidian/models/analytics`, {
  method: 'POST',
  body: JSON.stringify({
    time_range: "last_7_days",
    task_types: ["chat", "vault_management"],
    include_costs: true
  })
});
```

This enhanced model selection system provides intelligent, adaptive AI capabilities that improve over time based on usage patterns and user preferences, making your Obsidian vault management more efficient and cost-effective.
