# VaultPilot EvoAgentX Integration Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing VaultPilot integration into your EvoAgentX server. The integration enables Obsidian users to access AI-powered knowledge management features through the VaultPilot plugin.

## Architecture Overview

```
VaultPilot (Obsidian Plugin) ←→ EvoAgentX Server ←→ Your AI Services
                                      ↓
                              Integration Package
                              • API Routes
                              • Pydantic Models  
                              • Service Classes
                              • WebSocket Handler
                              • Copilot Agent
```

## Integration Components

### 1. Core Files Included

| File | Purpose | Status |
|------|---------|--------|
| `api_models.py` | Pydantic models for all endpoints | ✅ Complete |
| `obsidian_routes.py` | FastAPI route definitions | ✅ Complete (stubs) |
| `vault_analyzer.py` | Vault analysis service | ✅ Complete (stubs) |
| `copilot_engine.py` | Auto-completion service | ✅ Complete (stubs) |
| `workflow_processor.py` | Complex workflow execution | ✅ Complete (stubs) |
| `agent_manager.py` | AI agent management | ✅ Complete (stubs) |
| `websocket_handler.py` | Real-time communication | ✅ Complete |
| `cors_config.py` | CORS configuration | ✅ Complete |
| `vaultpilot_copilot_prompt.md` | Copilot agent prompt | ✅ Complete |

### 2. Implementation Status

#### ✅ Working Endpoints (EvoAgentX)
- `GET /status` - Health check
- `POST /chat` - Basic chat functionality  
- `POST /copilot` - Copilot completions
- `POST /workflow` - Workflow execution
- `GET /agents` - Agent listing

#### 🔧 Need Implementation (Business Logic)
- `POST /api/obsidian/vault/context` - Vault analysis
- `POST /api/obsidian/planning/tasks` - Task planning
- `POST /api/obsidian/intelligence/parse` - Content parsing
- `POST /api/obsidian/memory/update` - Memory updates
- `WS /ws/obsidian` - WebSocket connection

#### ❌ Optional/Future
- Advanced vault indexing
- Multi-user session management
- Plugin marketplace integration

## Step-by-Step Implementation

### Step 1: Install Dependencies

```bash
pip install fastapi uvicorn websockets pydantic python-multipart
```

### Step 2: Copy Integration Files

Copy all files from this integration package to your EvoAgentX project:

```
your_evoagentx_project/
├── vaultpilot_integration/
│   ├── __init__.py
│   ├── api_models.py
│   ├── obsidian_routes.py
│   ├── vault_analyzer.py
│   ├── copilot_engine.py
│   ├── workflow_processor.py
│   ├── agent_manager.py
│   ├── websocket_handler.py
│   └── cors_config.py
└── prompts/
    └── vaultpilot_copilot_prompt.md
```

### Step 3: Update Main FastAPI App

Add the VaultPilot routes to your main FastAPI application:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from vaultpilot_integration.obsidian_routes import obsidian_router
from vaultpilot_integration.cors_config import get_cors_config
from vaultpilot_integration.websocket_handler import websocket_manager

app = FastAPI(title="EvoAgentX", version="1.0.0")

# Add CORS middleware
cors_config = get_cors_config()
app.add_middleware(CORSMiddleware, **cors_config)

# Include VaultPilot routes
app.include_router(obsidian_router, prefix="/api/obsidian")

# Add WebSocket endpoint
@app.websocket("/ws/obsidian")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    # Handle WebSocket communication
```

### Step 4: Implement Service Integrations

#### A. Integrate with Your AI System

Update the service classes to connect with your existing AI infrastructure:

```python
# In copilot_engine.py
async def _generate_suggestions(self, context: str, intent: str, file_type: str) -> List[str]:
    # Replace with your AI completion API
    response = await your_ai_service.complete(
        prompt=f"Context: {context}\nIntent: {intent}",
        max_tokens=100
    )
    return response.suggestions

# In workflow_processor.py  
async def _execute_agent_task_internal(self, agent: Agent, request: AgentExecuteRequest) -> str:
    # Replace with your agent execution system
    response = await your_agent_system.execute(
        agent_id=agent.id,
        task=request.task,
        context=request.context
    )
    return response.text
```

#### B. Integrate with Your Database

Add database connections for persistence:

```python
# In agent_manager.py
async def create_agent(self, request: AgentCreateRequest) -> Agent:
    agent = Agent(...)
    
    # Save to your database
    await your_db.agents.insert(agent.dict())
    
    return agent
```

#### C. Connect Vault Analysis

Implement actual vault file system analysis:

```python
# In vault_analyzer.py
async def analyze_vault(self, vault_path: str) -> VaultAnalysisResponse:
    # Implement actual file system scanning
    files = []
    for root, dirs, filenames in os.walk(vault_path):
        for filename in filenames:
            if filename.endswith('.md'):
                files.append(os.path.join(root, filename))
    
    # Analyze content with your AI system
    analysis = await your_ai_service.analyze_vault_content(files)
    
    return VaultAnalysisResponse(...)
```

### Step 5: Configure the Copilot Agent

#### A. Add Copilot Agent to Your System

Use the provided prompt template (`vaultpilot_copilot_prompt.md`) to create a specialized copilot agent in your system:

```python
# Example agent creation
copilot_agent = await your_agent_system.create_agent(
    name="VaultPilot Copilot",
    system_prompt=open("prompts/vaultpilot_copilot_prompt.md").read(),
    capabilities=["knowledge_management", "writing_assistance", "auto_completion"]
)
```

#### B. Configure Auto-Completion

Set up intelligent auto-completion based on vault context:

```python
# In copilot_engine.py
async def get_completion(self, request: CopilotRequest) -> CopilotResponse:
    # Extract context from user's vault
    context = await self.vault_analyzer.get_vault_context(request.vault_path)
    
    # Generate contextual suggestions
    suggestions = await your_ai_service.complete(
        text=request.text,
        context=context,
        cursor_position=request.cursor_position
    )
    
    return CopilotResponse(suggestions=suggestions)
```

### Step 6: Test the Integration

#### A. Test Health Check
```bash
curl http://localhost:8000/status
```

#### B. Test Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/obsidian/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "vault_context": "My notes..."}'
```

#### C. Test Copilot
```bash
curl -X POST http://localhost:8000/api/obsidian/copilot \
  -H "Content-Type: application/json" \
  -d '{"text": "Today I learned", "cursor_position": 15, "file_type": "markdown"}'
```

#### D. Test WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/obsidian');
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

### Step 7: Configure VaultPilot Plugin

Update the VaultPilot plugin settings in Obsidian:

1. Open Settings → Community Plugins → VaultPilot
2. Set Backend URL: `http://localhost:8000`
3. Set API Key: (your API key)
4. Enable WebSocket: Yes
5. Test connection

## Advanced Configuration

### Custom Agent Creation

Create domain-specific agents for your users:

```python
# Research agent example
research_agent = await agent_manager.create_agent(AgentCreateRequest(
    name="Research Assistant",
    description="Specialized in academic research and analysis",
    system_prompt="You are a research assistant specialized in...",
    capabilities=["research_synthesis", "citation_management", "literature_review"]
))
```

### Workflow Templates

Define reusable workflow templates:

```python
# Study plan workflow template
study_workflow = WorkflowTemplate(
    name="Study Plan Creation",
    steps=[
        "analyze_subject_domain",
        "identify_learning_resources", 
        "create_study_schedule",
        "setup_progress_tracking"
    ]
)
```

### Real-time Features

Implement real-time collaboration:

```python
# Broadcast updates to all connected clients
await websocket_manager.broadcast({
    "type": "vault_sync",
    "data": {"file_updated": "project_notes.md"}
})
```

## Monitoring & Analytics

### Add Logging

```python
import logging

logger = logging.getLogger("vaultpilot")

@obsidian_router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    logger.info(f"Chat request: {request.message[:50]}...")
    # ... implementation
```

### Track Usage Metrics

```python
# Track API usage
@obsidian_router.middleware("http")
async def track_usage(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log metrics
    await your_analytics.track_api_call(
        endpoint=str(request.url),
        method=request.method,
        duration=process_time,
        status_code=response.status_code
    )
    
    return response
```

## Security Considerations

### API Authentication

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_api_key(token: str = Depends(security)):
    if not await your_auth_system.verify_key(token.credentials):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return token.credentials

# Protect endpoints
@obsidian_router.post("/chat")
async def chat_endpoint(request: ChatRequest, api_key: str = Depends(verify_api_key)):
    # ... implementation
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@obsidian_router.post("/chat")
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, chat_request: ChatRequest):
    # ... implementation
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Check CORS configuration in `cors_config.py`
2. **WebSocket Connection Failed**: Verify WebSocket endpoint and port
3. **404 on Health Check**: Ensure `/status` endpoint exists
4. **Slow Responses**: Check AI service response times

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In your service implementations
logger = logging.getLogger(__name__)
logger.debug(f"Processing request: {request}")
```

### Performance Optimization

1. **Caching**: Implement response caching for repeated queries
2. **Async Processing**: Use background tasks for long operations
3. **Connection Pooling**: Pool database and AI service connections
4. **Response Compression**: Enable gzip compression

## Next Steps

1. **Complete Service Implementations**: Replace placeholder logic with actual AI integrations
2. **Add Authentication**: Implement proper user authentication and authorization
3. **Scale Infrastructure**: Prepare for production deployment with load balancing
4. **Monitor Performance**: Set up monitoring and alerting for the integration
5. **User Feedback**: Collect feedback from VaultPilot users to improve features

## Support & Resources

- **VaultPilot Documentation**: See `/vaultpilot/README.md`
- **API Reference**: Auto-generated at `/docs` when FastAPI is running
- **WebSocket Testing**: Use browser dev tools or WebSocket testing tools
- **Error Reporting**: Check server logs and FastAPI exception handling

For questions or issues with this integration, refer to the VaultPilot project documentation or create an issue in the repository.
