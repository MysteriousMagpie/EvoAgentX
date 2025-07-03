# Intent Classification Module

This module provides automatic intent classification for the EvoAgentX Obsidian integration, allowing the system to automatically switch between "ask" and "agent" modes based on user input.

## Overview

The intent classifier uses OpenAI text embeddings (`text-embedding-3-small`) to classify user messages into two categories:

- **ASK mode**: Questions, explanations, definitions (e.g., "what is machine learning?")
- **AGENT mode**: Action requests, task creation, scheduling (e.g., "create a project plan")

## Features

- 🧠 **Embedding-based classification** using cosine similarity
- 💾 **Intelligent caching** with SHA256 hash validation
- 🔄 **Async/await support** for non-blocking operations
- 🐛 **Debug mode** with detailed explanation
- ⚡ **Fast lookup** after initial embedding computation
- 🛡️ **Robust error handling** with meaningful messages

## Usage

### Basic Classification

```python
from evoagentx.intents import classify_intent, Intent

# Simple classification
result = await classify_intent("create a task list for next week")
print(f"Intent: {result.intent}")  # Intent.AGENT
print(f"Confidence: {result.confidence:.3f}")  # e.g., 0.847
```

### Debug Mode

```python
from evoagentx.intents import explain_intent

# Get detailed explanation
debug = await explain_intent("what is machine learning?")
print(f"Intent: {debug.intent}")  # Intent.ASK  
print(f"Confidence: {debug.confidence:.3f}")
print(f"Best match: {debug.top_example}")  # e.g., "explain this concept"
print(f"Match score: {debug.example_score:.3f}")
```

### Integration Example

```python
from evoagentx.intents import classify_intent, Intent

async def auto_route_chat(message: str):
    """Route chat message to appropriate handler based on intent."""
    result = await classify_intent(message)
    
    if result.intent == Intent.AGENT:
        return await handle_agent_workflow(message)
    else:
        return await handle_ask_query(message)
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required OpenAI API key for embeddings

### Prototype Examples

The classifier is trained on these prototype examples:

**Agent Examples** (action/task-oriented):
- "generate a plan for my week"
- "create a task list" 
- "schedule my meetings"
- "refactor this text"
- "build a project outline"

**Ask Examples** (question/explanation-oriented):
- "what is a project outline"
- "explain this concept"
- "summarize this paragraph"
- "define intent detection"
- "how does this work"

## Caching

Embeddings are automatically cached to `.cache/intent_vectors.json` to avoid redundant API calls:

- ✅ Cache is validated using SHA256 hash of prototype examples
- ✅ Automatic cache invalidation when examples change
- ✅ Graceful fallback to API calls when cache is invalid

## Error Handling

The module provides clear error messages for common issues:

```python
# Missing API key
RuntimeError: "OPENAI_API_KEY environment variable is required but not set."

# API errors  
RuntimeError: "OpenAI API request failed with status 401: Unauthorized"
```

## Performance

- **Initial Setup**: ~2-3 seconds (embedding prototype examples)
- **Subsequent Calls**: ~0.5-1 second (embedding input + similarity calculation)
- **Cache Hits**: ~0.1 second (similarity calculation only)

## Testing

Run the test suite:

```bash
# Run all intent classifier tests
pytest tests/test_intent_classifier.py -v

# Run with coverage
pytest tests/test_intent_classifier.py --cov=evoagentx/intents
```

## Dependencies

- `numpy>=1.26.4` - Vector operations and cosine similarity
- `httpx>=0.24.1` - Async HTTP client for OpenAI API
- `openai>=1.55.3` - OpenAI API compatibility (endpoint format)

## Future Enhancements (TODOs)

- [ ] **Force prefix**: Accept `/agent {prompt}` to force AGENT classification
- [ ] **Local fallback**: Use sentence-transformers when `EAX_LOCAL_EMBEDDINGS=true`
- [ ] **Online learning**: Persist user corrections and re-rank examples

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │    │ Intent Classifier │    │ OpenAI Embeddings│
│                 │───▶│                  │───▶│                 │
│ "plan my week"  │    │ Cosine Similarity │    │ text-embedding-3│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │  Result: AGENT   │
                        │  Confidence: 87% │
                        └──────────────────┘
```

## Integration Points

### Obsidian Chat Endpoint

The intent classifier integrates with `server/api/obsidian.py`:

```python
# Before routing to ask/agent logic
intent_result = await classify_intent(request.message)
effective_mode = intent_result.intent.value  # "ask" or "agent"
```

### WebSocket Layer

For real-time classification feedback in development mode:

```python
# Send classification debug info via WebSocket  
debug_info = await explain_intent(message)
await websocket.send_json({
    "type": "intent_debug",
    "data": debug_info.__dict__
})
```

## License

MIT License - see LICENSE file for details.
