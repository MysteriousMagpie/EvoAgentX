# Extracted React Frontend Patterns

## API Endpoints Used by Frontend

### Core EvoAgentX API
- `POST /api/analyze-code` - Code analysis with interpreter recommendations
- `GET /api/interpreter/config` - Get interpreter configuration
- `POST /api/interpreter/execute` - Execute code with interpreter

### VaultPilot/Obsidian API
- `POST /api/obsidian/intelligence/parse` - Parse development requests
- `POST /api/obsidian/agents/execute` - Execute code generation agents
- `POST /api/obsidian/workflow/apply-changes` - Apply generated code changes
- `POST /api/obsidian/validate-code` - Validate code before applying

### WebSocket Connections
- Real-time chat communication
- Development session updates
- File change notifications

## Component Patterns to Remember

### ConversationalDevelopment.tsx
```typescript
interface ConversationalDevelopmentProps {
  onClose: () => void;
}

// Key patterns:
- Message history management
- Real-time WebSocket communication
- Error handling and user feedback
- Code generation request flow
- File change application workflow
```

### InterpreterSelector.tsx
```typescript
interface InterpreterSelectorProps {
  onAnalysisComplete?: (analysis: CodeAnalysis) => void;
}

// Key patterns:
- Code analysis triggering
- Interpreter recommendation display
- Configuration management
- Results visualization
```

### API Client Patterns
```typescript
// Error handling
try {
  const response = await fetch(endpoint, config);
  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }
  const result = await response.json();
  return result;
} catch (error) {
  console.error('API Error:', error);
  throw error;
}

// WebSocket connection
const ws = new WebSocket(wsUrl);
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  handleMessage(data);
};
```

## State Management Patterns

### Development Session State
```typescript
interface DevSessionState {
  messages: ChatMessage[];
  currentFile?: string;
  pendingChanges?: CodeChange[];
  analysisResults?: CodeAnalysis;
  interpreterConfig?: InterpreterConfig;
}
```

### Error Handling
```typescript
interface ErrorState {
  hasError: boolean;
  errorMessage?: string;
  errorCode?: string;
}
```

## UI/UX Patterns Worth Preserving

### Loading States
- Show spinner during API calls
- Progress indicators for long operations
- Skeleton loading for chat history

### Error Feedback
- Toast notifications for quick feedback
- Detailed error messages in modal
- Retry mechanisms for failed operations

### User Interactions
- Auto-save draft messages
- Keyboard shortcuts for common actions
- Context menus for code actions

## Migration Notes for Obsidian

### Commands to Implement
1. `evoagentx-analyze-code` - ✅ Added to vault-management-commands.ts
2. `evoagentx-select-interpreter` - ✅ Added to vault-management-commands.ts  
3. `evoagentx-execute-code` - ✅ Added to vault-management-commands.ts
4. `evoagentx-dev-chat` - Still needed
5. `evoagentx-apply-changes` - Still needed

### Settings to Migrate
- API endpoint configuration
- Interpreter preferences
- Auto-save settings
- WebSocket connection settings

### Modal/UI Components Needed
- Code analysis results display
- Interpreter selection interface
- Development chat interface
- Code change preview/approval

This document preserves the key patterns and functionality from the React frontend for reference during the Obsidian migration.
