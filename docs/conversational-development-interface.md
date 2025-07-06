# Conversational Development Interface (CDI) - Chat-Only Mode

## Overview

The Conversational Development Interface enables users to describe Obsidian plugin feature requests or code changes in natural language. The plugin parses the request, identifies the target file and intent, sends it to a backend agent (via EvoAgentX), receives generated code (patch or full file), and asks the user whether to apply the change.

## Architecture

### Core Components

- **Frontend**: `ChatModal.tsx`, `ConversationalDevelopment.tsx`, `api-client.ts`
- **Backend**: `conversational_dev_parser.py`, `conversational_code_generator.py`, `obsidian_routes.py`
- **Integration**: VaultPilot's Copilot and workflow automation features

### API Endpoints

- `POST /api/obsidian/intelligence/parse` - Parse natural language requests
- `POST /api/obsidian/agents/execute` - Execute code generation agents
- `POST /api/obsidian/workflow/apply-changes` - Apply code changes to files
- `POST /api/obsidian/validate-code` - Validate generated code
- `POST /api/obsidian/save-session` - Save development sessions

## Chat Loop Flow

### 1. User Input
User enters a development-related prompt in the chat window:
- "Add a dark mode toggle to settings"
- "Fix the API error handling in auth.service.ts"
- "Create a user authentication component"
- "Add unit tests for the user service"

### 2. Request Parsing
Plugin calls `parseDevRequest()` to extract:
- **Intent**: `create`, `modify`, `delete`, `refactor`, `add_feature`, `fix_bug`, `optimize`, `test`, `document`
- **Target File**: Identified file path or auto-detection
- **Description**: Structured description of the change
- **Confidence**: Parser confidence level (0.0-1.0)
- **Complexity**: Estimated complexity (`low`, `medium`, `high`)

```typescript
interface ParsedDevRequest {
  intent: 'create' | 'modify' | 'delete' | 'refactor' | 'add_feature' | 'fix_bug' | 'optimize' | 'test' | 'document';
  targetFile?: string;
  description: string;
  confidence: number;
  requiredFiles?: string[];
  suggestedApproach?: string;
  estimatedComplexity?: 'low' | 'medium' | 'high';
  dependencies?: string[];
  riskFactors?: string[];
}
```

### 3. Code Generation
Structured request is sent to the backend agent:
- **Agent Types**: `code_generator`, `refactor_agent`, `test_generator`, `documentation_agent`
- **Context**: Project path, required files, constraints
- **Mode**: `conversational` for interactive chat mode

```typescript
interface CodeGenerationRequest {
  agent_type: 'code_generator' | 'refactor_agent' | 'test_generator' | 'documentation_agent';
  request: {
    intent: string;
    targetFile?: string;
    description: string;
    context?: {
      projectPath?: string;
      requiredFiles?: string[];
      approach?: string;
      constraints?: string[];
      mode?: 'conversational' | 'batch';
    };
  };
}
```

### 4. Code Preview
The backend returns generated code with metadata:
- **Generated Code**: Patch, full file, or multiple files
- **Diff Summary**: Human-readable description of changes
- **Explanations**: What the code does
- **Warnings**: Important notes or potential issues
- **Dependencies**: Required packages or imports

```typescript
interface GeneratedCode {
  type: 'patch' | 'full_file' | 'multiple_files' | 'directory_structure';
  content: string | Record<string, string>;
  diffSummary?: string;
  explanations?: string[];
  warnings?: string[];
  dependencies?: string[];
  testSuggestions?: string[];
  rollbackInfo?: {
    backupPath?: string;
    restoreCommands?: string[];
  };
}
```

### 5. User Approval
UI displays code preview and asks: **"Apply this? (Y/N)"**

User can respond with:
- `yes`, `y`, `apply`, `approve`, `ok` - Apply the changes
- `no`, `n`, `cancel`, `reject` - Reject the changes
- `modify [instructions]` - Request modifications

### 6. Change Application
On confirmation, plugin calls `applyPatch()` to:
- Create automatic backups
- Validate syntax and types
- Apply changes to the codebase
- Run tests (optional)
- Trigger plugin reload

```typescript
interface ApplyChangesRequest {
  changes: {
    type: GeneratedCode['type'];
    content: GeneratedCode['content'];
    targetFile?: string;
    projectPath?: string;
  };
  metadata?: {
    intent?: string;
    description?: string;
    diffSummary?: string;
    authorInfo?: {
      source: 'conversational_dev';
      timestamp: string;
      userRequest: string;
    };
  };
  options?: {
    createBackup?: boolean;
    validateSyntax?: boolean;
    runTests?: boolean;
    autoReload?: boolean;
  };
}
```

## Implementation Status

### ✅ Completed Features

1. **Chat Interface**: Full chat modal with development mode
2. **Request Parsing**: Natural language to structured request conversion
3. **Code Generation**: Agent-based code generation with multiple types
4. **Code Preview**: Syntax-highlighted preview with diff summary
5. **User Approval**: Interactive approval workflow
6. **Change Application**: File modification with backup and validation
7. **Real-time Updates**: WebSocket support for progress tracking
8. **Error Handling**: Comprehensive error handling and user feedback

### 🚧 In Progress

1. **File Modification Logic**: Complete implementation of file writing
2. **Test Execution**: Automated test running after changes
3. **Session Storage**: Persistent development session history

### 🔄 Future Enhancements

1. **Advanced Validation**: More sophisticated code analysis
2. **Rollback System**: Easy undo for applied changes
3. **Batch Operations**: Multiple changes in one session
4. **Plugin Integration**: Deep Obsidian plugin API integration

## Usage Examples

### Creating New Features
```
User: "Add a dark mode toggle to the settings page"

System:
🎯 Request Analysis:
• Intent: add_feature
• Target: settings/index.tsx
• Confidence: 95.2%
• Complexity: medium

⚙️ Generated Code:
[Shows toggle component with state management]

Apply this? (Y/N)
```

### Fixing Bugs
```
User: "Fix the API error handling in auth.service.ts"

System:
🎯 Request Analysis:
• Intent: fix_bug
• Target: services/auth.service.ts
• Confidence: 87.3%
• Complexity: low

⚙️ Generated Code:
[Shows improved error handling with try-catch blocks]

Apply this? (Y/N)
```

### Refactoring Code
```
User: "Refactor the dashboard to use React hooks"

System:
🎯 Request Analysis:
• Intent: refactor
• Target: components/Dashboard.tsx
• Confidence: 91.8%
• Complexity: high

⚠️ Important Notes:
• This will convert class component to functional component
• Existing state management will be updated
• Component lifecycle methods will be replaced with useEffect

⚙️ Generated Code:
[Shows hooks-based refactored component]

Apply this? (Y/N)
```

## Related Modules

- **api-client.ts**: Main API integration for CDI workflow
- **ChatModal.tsx**: Primary chat interface component
- **ConversationalDevSettings.tsx**: Settings and configuration
- **conversational_dev_parser.py**: Backend request parsing
- **conversational_code_generator.py**: Backend code generation
- **obsidian_routes.py**: FastAPI endpoints for CDI

## Integration with VaultPilot

The CDI extends VaultPilot's existing capabilities:
- **Copilot Features**: Leverages existing AI completion engine
- **Workflow Automation**: Uses workflow processor for complex tasks
- **Vault Analysis**: Integrates with vault context understanding
- **Agent Management**: Extends existing agent framework

## Configuration

### Frontend Settings
```typescript
interface CDISettings {
  autoApply: boolean;              // Auto-apply low-risk changes
  showDiffPreview: boolean;        // Show detailed diff previews
  createBackups: boolean;          // Always create backups
  runTestsAfterApply: boolean;     // Run tests after changes
  defaultAgentType: string;        // Preferred agent type
  confidenceThreshold: number;     // Minimum confidence for auto-suggestions
}
```

### Backend Configuration
```python
class CDIConfig:
    MAX_REQUEST_SIZE: int = 10000    # Max characters in request
    DEFAULT_AGENT_TYPE: str = "code_generator"
    BACKUP_RETENTION_DAYS: int = 7
    ENABLE_SYNTAX_VALIDATION: bool = True
    ENABLE_TEST_EXECUTION: bool = False
    PROJECT_ROOT_DETECTION: bool = True
```

This system provides a seamless, conversational approach to code development within Obsidian, making complex development tasks accessible through natural language interaction.
