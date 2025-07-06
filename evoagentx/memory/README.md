# Persistent Memory Framework for EvoAgentX

A modular, configurable persistent memory system that can be easily added to any agent to provide:

- **Progressive Summarization**: Automatically summarizes old conversations to save tokens
- **Vector-based Retrieval**: Finds semantically relevant past memories  
- **Flexible Configuration**: Customizable memory behavior for different use cases
- **Easy Integration**: Mixin classes and decorators for quick setup

## 🚀 Quick Start

### Option 1: Using the Mixin Class

```python
from evoagentx.memory import MemoryCapableMixin, MemoryConfig

class MyAgent(MemoryCapableMixin):
    def __init__(self, name: str):
        self.name = name
        self.agent_id = f"agent_{name}"
        
        # Configure memory behavior
        memory_config = MemoryConfig(
            max_working_memory_tokens=2000,
            enable_vector_store=True,
            auto_cleanup_days=30
        )
        super().__init__(memory_config=memory_config)
    
    def chat(self, message: str) -> str:
        # Remember user message
        self.remember(message, role="user")
        
        # Get relevant context
        context = self.recall(query=message)
        
        # Generate response (your logic here)
        response = self.generate_response(message, context)
        
        # Remember response
        self.remember(response, role="assistant")
        
        return response
```

### Option 2: Using the Decorator

```python
from evoagentx.memory import with_persistent_memory, MemoryConfig

@with_persistent_memory(MemoryConfig(
    max_working_memory_messages=15,
    summarize_threshold=5
))
class ChatBot:
    def __init__(self, name: str):
        self.name = name
        self.agent_id = f"bot_{name}"
    
    def respond(self, message: str) -> str:
        self.remember(message, "user")
        context = self.recall(query=message)
        response = f"Response to: {message}"
        self.remember(response, "assistant")
        return response
```

### Option 3: Direct Memory Manager

```python
from evoagentx.memory import PersistentMemoryManager, MemoryConfig

class CustomAgent:
    def __init__(self, agent_id: str):
        config = MemoryConfig(
            max_working_memory_tokens=3000,
            enable_vector_store=True,
            vector_similarity_threshold=0.6
        )
        self.memory = PersistentMemoryManager(agent_id, config)
    
    def process(self, input_text: str) -> str:
        # Add to memory with metadata
        self.memory.add_message(
            content=input_text,
            role="user", 
            metadata={"source": "api", "priority": "high"},
            importance=0.8
        )
        
        # Get context with semantic search
        context = self.memory.get_context(query=input_text)
        
        # Search specific memories
        related = self.memory.search_memory("similar topic")
        
        return f"Processed with {len(context)} context items"
```

## 🔧 Configuration Options

The `MemoryConfig` class provides extensive customization:

```python
from evoagentx.memory import MemoryConfig

config = MemoryConfig(
    # Working memory limits
    max_working_memory_tokens=2000,     # Token limit before summarization
    max_working_memory_messages=20,     # Message count limit
    
    # Summarization settings  
    summarize_threshold=5,              # Summaries before vectorization
    summary_overlap_ratio=0.1,          # Overlap when summarizing
    auto_summarize=True,                # Enable automatic summarization
    
    # Vector search settings
    enable_vector_store=True,           # Enable semantic search
    embedding_model="all-MiniLM-L6-v2", # Sentence transformer model
    vector_similarity_threshold=0.7,    # Similarity threshold
    max_retrieved_memories=3,           # Max memories to retrieve
    
    # Storage settings
    db_path="agent_memory.sqlite",      # Database file path
    session_timeout_hours=24,           # Session timeout
    
    # Cleanup settings
    auto_cleanup_days=30,               # Auto-delete old memories
    enable_encryption=False             # Enable content encryption
)
```

## 🎛️ Preset Configurations

Use predefined configurations for common scenarios:

```python
from evoagentx.memory.usage_examples import MemoryPresets

# Lightweight for simple agents
lightweight_config = MemoryPresets.lightweight()

# Optimized for chat/conversation
chat_config = MemoryPresets.conversational()

# Long-term memory for research agents  
research_config = MemoryPresets.research()

# High performance with minimal memory
performance_config = MemoryPresets.high_performance()
```

## 💡 Key Features

### Progressive Summarization
- Automatically summarizes old conversations when memory gets full
- Preserves important information while reducing token usage
- Configurable overlap and summarization thresholds

### Vector-based Semantic Search
- Uses sentence transformers to find relevant past memories
- Retrieves contextually similar conversations
- Optional feature that can be disabled for lightweight usage

### Flexible Storage
- SQLite backend with full-text search
- Automatic database creation and management
- Thread-safe operations

### Memory Management
- Automatic cleanup of old memories
- Importance scoring for retention decisions
- Session management for conversation boundaries

### Easy Integration
- Mixin classes for inheritance-based integration
- Decorators for quick setup
- Direct manager usage for full control

## 🧪 Testing

Run the included tests to verify functionality:

```bash
cd evoagentx/memory
python test_memory_framework.py
```

The tests verify:
- Basic memory operations (add, recall, search)
- Summarization functionality
- Mixin class integration
- Configuration handling

## 📋 Requirements

### Core Requirements
- Python 3.8+
- sqlite3 (included with Python)

### Optional Requirements
- `sentence-transformers` - For vector embeddings and semantic search
- `numpy` - For vector similarity calculations

Install optional dependencies:
```bash
pip install sentence-transformers numpy
```

The framework gracefully degrades without these dependencies - vector search will be disabled but all other functionality remains available.

## 🔍 API Reference

### MemoryCapableMixin Methods

- `remember(content, role, metadata, importance)` - Add content to memory
- `recall(query, include_summaries)` - Get relevant context  
- `search_memories(query, limit)` - Search memory with full-text search
- `forget_old()` - Clean up old memories
- `new_session()` - Start a new conversation session
- `memory_stats()` - Get memory usage statistics

### PersistentMemoryManager Methods

- `add_message(content, role, metadata, importance)` - Add new memory item
- `get_context(query, include_summaries, max_items)` - Get conversation context
- `search_memory(query, limit)` - Search with full-text
- `start_new_session()` - Begin new session
- `cleanup_old_memories()` - Remove old items
- `get_stats()` - Get detailed statistics

## 🛠️ Advanced Usage

### Custom Summarization
```python
class MyAgent(MemoryCapableMixin):
    def custom_summarize(self, items):
        # Override summarization logic
        self.memory._generate_summary = self.my_summary_function
```

### Memory Importance Scoring
```python
# Higher importance memories are kept longer
agent.remember(
    "Critical project deadline tomorrow!", 
    role="user",
    importance=0.9  # High importance
)

agent.remember(
    "Random thought about weather",
    role="user", 
    importance=0.3  # Low importance
)
```

### Session Boundaries
```python
# Work on project A
agent.remember("Working on feature X", "user")
agent.remember("Implementing authentication", "user")

# Switch to project B - start new session
agent.new_session()
agent.remember("Now working on different project", "user")

# Previous context is still searchable but not in working memory
```

## 🤝 Integration with Existing EvoAgentX

This framework integrates seamlessly with existing EvoAgentX agents:

```python
from evoagentx.agents import SomeExistingAgent
from evoagentx.memory import MemoryCapableMixin

class MemoryEnabledAgent(MemoryCapableMixin, SomeExistingAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Now has memory capabilities!
```

The framework is designed to be non-intrusive and can be added to any existing agent without changing core functionality.
