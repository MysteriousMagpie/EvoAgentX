# EvoAgentX Obsidian Plugin

This is an example Obsidian plugin that integrates with the EvoAgentX backend to provide AI-powered features within your Obsidian vault.

## Features

- **Agent Chat**: Chat with AI agents directly in Obsidian
- **Copilot Completion**: Get intelligent text completions while writing
- **Workflow Execution**: Run complex agentic workflows from Obsidian
- **Vault Analysis**: Analyze your vault content for insights and connections
- **Real-time Communication**: WebSocket support for live interactions

## Installation

### Prerequisites

1. **EvoAgentX Server**: Make sure the EvoAgentX server is running
   ```bash
   cd server
   python -m uvicorn main:sio_app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Environment Variables**: Set your OpenAI API key
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

### Plugin Installation

1. **Manual Installation** (for development):
   ```bash
   # Clone or copy this plugin to your Obsidian plugins folder
   cd /path/to/your/vault/.obsidian/plugins/
   mkdir evoagentx
   cp -r /path/to/EvoAgentX/examples/obsidian-plugin/* evoagentx/
   
   # Install dependencies and build
   cd evoagentx
   npm install
   npm run build
   ```

2. **Enable the Plugin**:
   - Open Obsidian Settings
   - Go to Community plugins
   - Enable "EvoAgentX"

## Usage

### 1. Configure Settings

Go to Settings > EvoAgentX and configure:
- **Server URL**: Default is `http://localhost:8000`
- **Enable Copilot**: Toggle AI text completion
- **Enable Realtime**: Toggle WebSocket features

### 2. Basic Commands

The plugin adds several commands accessible via the command palette (Cmd/Ctrl + P):

- **Open EvoAgentX Chat**: Start a conversation with an AI agent
- **Get AI Completion**: Get text completion at cursor position
- **Execute Workflow**: Run a complex agentic workflow
- **Analyze Vault Context**: Get AI insights about your vault

### 3. Chat Interface

Click the EvoAgentX icon in the ribbon or use the "Open EvoAgentX Chat" command to open a chat modal where you can:

- Ask questions about your notes
- Get help with writing and organization
- Request summaries or explanations
- Plan tasks and projects

### 4. Copilot Features

With copilot enabled:
- Use "Get AI Completion" command while writing
- The AI will suggest text based on your current context
- Completions consider your cursor position and file type

### 5. Workflow Execution

Use "Execute Workflow" to:
- Create study plans
- Generate outlines
- Plan projects
- Organize information
- Automate complex tasks

Results are automatically saved as new notes in your vault.

### 6. Vault Analysis

Use "Analyze Vault Context" to:
- Get insights about your knowledge base
- Find connections between notes
- Identify gaps in your knowledge
- Get suggestions for organization

## API Integration Examples

### Basic Chat

```typescript
const response = await fetch('http://localhost:8000/api/obsidian/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "Help me organize my machine learning notes"
  })
});

const data = await response.json();
console.log(data.response);
```

### Text Completion

```typescript
const completion = await fetch('http://localhost:8000/api/obsidian/copilot/complete', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: "The benefits of AI include",
    cursor_position: 25,
    file_type: "markdown"
  })
});

const result = await completion.json();
console.log(result.completion);
```

### Workflow Execution

```typescript
const workflow = await fetch('http://localhost:8000/api/obsidian/workflow', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    goal: "Create a study plan for machine learning"
  })
});

const result = await workflow.json();
console.log(result.output);
```

## WebSocket Integration

For real-time features:

```typescript
const ws = new WebSocket('ws://localhost:8000/ws/obsidian');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'agent_response':
      // Handle chat responses
      break;
    case 'workflow_progress':
      // Show progress updates
      break;
    case 'copilot_suggestion':
      // Display suggestions
      break;
  }
};
```

## Development

### Building

```bash
npm install
npm run dev  # For development with watching
npm run build  # For production build
```

### File Structure

```
obsidian-plugin/
├── main.ts              # Main plugin code
├── manifest.json        # Plugin manifest
├── package.json         # Dependencies
├── tsconfig.json        # TypeScript config
├── esbuild.config.mjs   # Build configuration
└── README.md           # This file
```

### Key Components

1. **EvoAgentXPlugin**: Main plugin class
2. **ChatModal**: Interactive chat interface
3. **WorkflowModal**: Workflow execution interface
4. **EvoAgentXSettingTab**: Plugin settings
5. **WebSocket Manager**: Real-time communication

### API Methods

- `chatWithAgent(message)`: Send chat message to agent
- `getCompletion(editor)`: Get text completion
- `executeWorkflow(goal)`: Run workflow
- `analyzeVaultContext()`: Analyze vault content

## Troubleshooting

### Common Issues

1. **Connection Error**: 
   - Ensure EvoAgentX server is running on http://localhost:8000
   - Check that the server URL in settings is correct
   - Verify your OpenAI API key is set

2. **Plugin Not Loading**:
   - Check the browser console for errors
   - Ensure all dependencies are installed
   - Try rebuilding with `npm run build`

3. **WebSocket Issues**:
   - Disable and re-enable realtime features in settings
   - Check firewall settings
   - Verify WebSocket endpoint is accessible

### Testing Connection

Use the "Test Connection" button in settings to verify the server is accessible.

### Debug Mode

Enable developer tools in Obsidian (View > Toggle Developer Tools) to see console logs and debug information.

## Contributing

This is an example plugin. For the main EvoAgentX project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see the main EvoAgentX repository for details.

## Support

- **GitHub**: [EvoAgentX Repository](https://github.com/EvoAgentX/EvoAgentX)
- **Discord**: Join our community Discord
- **Documentation**: Full API docs at http://localhost:8000/docs
