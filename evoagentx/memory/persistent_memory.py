"""
Advanced Persistent Memory Framework for EvoAgentX Agents

This module provides a flexible, configurable memory system that can be
attached to any agent to provide persistent context, progressive summarization,
and vector-based retrieval of historical information.

This builds upon the existing memory system but adds:
- Progressive summarization
- Vector embeddings for semantic retrieval
- Configurable memory strategies
- Modular attachment to any agent
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Protocol
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import threading
from pathlib import Path
import logging

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False
    np = None
    SentenceTransformer = None
    print("Warning: sentence-transformers not available. Vector embeddings disabled.")

logger = logging.getLogger(__name__)


@dataclass
class MemoryConfig:
    """Configuration for memory behavior"""
    # Working memory limits
    max_working_memory_tokens: int = 2000
    max_working_memory_messages: int = 20
    
    # Summarization settings
    summarize_threshold: int = 5  # Number of summaries before vectorizing
    summary_overlap_ratio: float = 0.1  # How much overlap when summarizing
    auto_summarize: bool = True
    
    # Vector storage settings
    enable_vector_store: bool = True
    embedding_model: str = "all-MiniLM-L6-v2"
    vector_similarity_threshold: float = 0.7
    max_retrieved_memories: int = 3
    
    # Database settings
    db_path: str = "agent_memory.sqlite"
    session_timeout_hours: int = 24
    
    # Privacy and cleanup
    auto_cleanup_days: int = 30
    enable_encryption: bool = False
    
    # Performance settings
    batch_size: int = 10
    cache_size: int = 100


@dataclass
class MemoryItem:
    """Individual memory item"""
    id: str
    agent_id: str
    session_id: str
    content: str
    item_type: str  # "message", "summary", "reflection", "user", "assistant"
    metadata: Dict[str, Any]
    timestamp: datetime
    tokens: int = 0
    importance: float = 1.0  # 0-1 importance score for retention
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['metadata'] = json.dumps(self.metadata)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['metadata'] = json.loads(data['metadata']) if isinstance(data['metadata'], str) else data['metadata']
        return cls(**data)


class MemoryBackend(ABC):
    """Abstract base class for memory storage backends"""
    
    @abstractmethod
    def save_item(self, item: MemoryItem) -> None:
        pass
    
    @abstractmethod
    def get_session_items(self, agent_id: str, session_id: str) -> List[MemoryItem]:
        pass
    
    @abstractmethod
    def get_recent_items(self, agent_id: str, limit: int = 10) -> List[MemoryItem]:
        pass
    
    @abstractmethod
    def search_items(self, agent_id: str, query: str, limit: int = 10) -> List[MemoryItem]:
        pass
    
    @abstractmethod
    def cleanup_old_items(self, days: int) -> int:
        pass


class SQLiteMemoryBackend(MemoryBackend):
    """SQLite-based memory storage with full-text search"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            # Main memory table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_items (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    metadata TEXT,
                    timestamp TEXT NOT NULL,
                    tokens INTEGER DEFAULT 0,
                    importance REAL DEFAULT 1.0
                )
            """)
            
            # Full-text search table
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                    id, agent_id, content, item_type,
                    content='memory_items', content_rowid='rowid'
                )
            """)
            
            # Indexes for performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_session 
                ON memory_items(agent_id, session_id, timestamp DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_type_time 
                ON memory_items(agent_id, item_type, timestamp DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_importance 
                ON memory_items(agent_id, importance DESC, timestamp DESC)
            """)
    
    def save_item(self, item: MemoryItem) -> None:
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                data = item.to_dict()
                
                # Insert into main table
                conn.execute("""
                    INSERT OR REPLACE INTO memory_items 
                    (id, agent_id, session_id, content, item_type, metadata, timestamp, tokens, importance)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['id'], data['agent_id'], data['session_id'], 
                    data['content'], data['item_type'], data['metadata'],
                    data['timestamp'], data['tokens'], data['importance']
                ))
                
                # Update FTS table
                conn.execute("""
                    INSERT OR REPLACE INTO memory_fts(id, agent_id, content, item_type)
                    VALUES (?, ?, ?, ?)
                """, (data['id'], data['agent_id'], data['content'], data['item_type']))
    
    def get_session_items(self, agent_id: str, session_id: str) -> List[MemoryItem]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM memory_items 
                WHERE agent_id = ? AND session_id = ?
                ORDER BY timestamp ASC
            """, (agent_id, session_id))
            
            return [MemoryItem.from_dict(dict(row)) for row in cursor.fetchall()]
    
    def get_recent_items(self, agent_id: str, limit: int = 10) -> List[MemoryItem]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM memory_items 
                WHERE agent_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (agent_id, limit))
            
            return [MemoryItem.from_dict(dict(row)) for row in cursor.fetchall()]
    
    def search_items(self, agent_id: str, query: str, limit: int = 10) -> List[MemoryItem]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT m.* FROM memory_items m
                JOIN memory_fts f ON m.id = f.id
                WHERE f.agent_id = ? AND memory_fts MATCH ?
                ORDER BY rank, m.importance DESC, m.timestamp DESC
                LIMIT ?
            """, (agent_id, query, limit))
            
            return [MemoryItem.from_dict(dict(row)) for row in cursor.fetchall()]
    
    def cleanup_old_items(self, days: int) -> int:
        cutoff = datetime.now() - timedelta(days=days)
        with sqlite3.connect(self.db_path) as conn:
            # Clean main table
            cursor = conn.execute("""
                DELETE FROM memory_items 
                WHERE timestamp < ? AND importance < 0.8
            """, (cutoff.isoformat(),))
            
            # Clean FTS table
            conn.execute("""
                DELETE FROM memory_fts 
                WHERE id NOT IN (SELECT id FROM memory_items)
            """)
            
            return cursor.rowcount


class VectorMemoryStore:
    """Vector embeddings store for semantic memory retrieval"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if not HAS_EMBEDDINGS or SentenceTransformer is None:
            raise ImportError("sentence-transformers required for vector store")
        
        self.model = SentenceTransformer(model_name)
        self.embeddings = []
        self.items = []
        self.item_map = {}  # id -> index mapping
    
    def add_item(self, item: MemoryItem) -> None:
        """Add item to vector store"""
        if not HAS_EMBEDDINGS:
            return
            
        try:
            embedding = self.model.encode(item.content)
            
            if item.id in self.item_map:
                # Update existing
                idx = self.item_map[item.id]
                self.embeddings[idx] = embedding
                self.items[idx] = item
            else:
                # Add new
                self.embeddings.append(embedding)
                self.items.append(item)
                self.item_map[item.id] = len(self.items) - 1
                
        except Exception as e:
            logger.warning(f"Failed to create embedding for item {item.id}: {e}")
    
    def find_similar(self, query: str, threshold: float = 0.7, limit: int = 3) -> List[MemoryItem]:
        """Find semantically similar memories"""
        if not self.embeddings or not HAS_EMBEDDINGS or np is None:
            return []
        
        try:
            query_embedding = self.model.encode(query)
            embeddings_array = np.array(self.embeddings)
            
            # Calculate cosine similarity
            similarities = np.dot(embeddings_array, query_embedding) / (
                np.linalg.norm(embeddings_array, axis=1) * np.linalg.norm(query_embedding)
            )
            
            # Get indices of items above threshold, sorted by similarity
            similar_indices = np.where(similarities >= threshold)[0]
            similar_indices = similar_indices[np.argsort(similarities[similar_indices])[::-1]]
            
            return [self.items[i] for i in similar_indices[:limit]]
            
        except Exception as e:
            logger.warning(f"Failed to find similar memories: {e}")
            return []
    
    def remove_item(self, item_id: str) -> bool:
        """Remove item from vector store"""
        if item_id not in self.item_map:
            return False
        
        idx = self.item_map[item_id]
        del self.embeddings[idx]
        del self.items[idx]
        del self.item_map[item_id]
        
        # Update mapping for remaining items
        for i in range(idx, len(self.items)):
            self.item_map[self.items[i].id] = i
        
        return True


class PersistentMemoryManager:
    """Advanced memory manager with progressive summarization and vector retrieval"""
    
    def __init__(self, agent_id: str, config: Optional[MemoryConfig] = None):
        self.agent_id = agent_id
        self.config = config or MemoryConfig()
        
        # Initialize storage backend
        self.backend = SQLiteMemoryBackend(self.config.db_path)
        
        # Initialize vector store if enabled
        self.vector_store = None
        if self.config.enable_vector_store and HAS_EMBEDDINGS:
            try:
                self.vector_store = VectorMemoryStore(self.config.embedding_model)
                self._load_vector_store()
            except Exception as e:
                logger.warning(f"Could not initialize vector store: {e}")
        
        # Session management
        self.current_session_id = self._generate_session_id()
        self.working_memory: List[MemoryItem] = []
        self.pending_summaries: List[MemoryItem] = []
        
        # Load current session
        self._load_current_session()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{self.agent_id}_{timestamp}_{hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]}"
    
    def _generate_item_id(self, content: str) -> str:
        """Generate unique item ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{self.agent_id}_{content}_{timestamp}".encode()).hexdigest()[:16]
    
    def _count_tokens(self, items: List[MemoryItem]) -> int:
        """Estimate token count"""
        return sum(item.tokens or len(item.content) // 4 for item in items)
    
    def _load_current_session(self) -> None:
        """Load current session from storage"""
        try:
            session_items = self.backend.get_session_items(self.agent_id, self.current_session_id)
            self.working_memory = [item for item in session_items if item.item_type in ["message", "user", "assistant"]]
            self.pending_summaries = [item for item in session_items if item.item_type == "summary"]
        except Exception as e:
            logger.warning(f"Failed to load session {self.current_session_id}: {e}")
    
    def _load_vector_store(self) -> None:
        """Load existing summaries into vector store"""
        if not self.vector_store:
            return
        
        try:
            recent_summaries = self.backend.get_recent_items(self.agent_id, limit=100)
            summaries = [item for item in recent_summaries if item.item_type in ["summary", "reflection"]]
            
            for summary in summaries:
                self.vector_store.add_item(summary)
                
            logger.info(f"Loaded {len(summaries)} items into vector store")
        except Exception as e:
            logger.warning(f"Failed to load vector store: {e}")
    
    def add_message(self, content: str, role: str = "user", metadata: Optional[Dict] = None, importance: float = 1.0) -> str:
        """Add a new message to memory"""
        item = MemoryItem(
            id=self._generate_item_id(content),
            agent_id=self.agent_id,
            session_id=self.current_session_id,
            content=content,
            item_type=role,
            metadata=metadata or {},
            timestamp=datetime.now(),
            tokens=len(content) // 4,
            importance=importance
        )
        
        # Add to working memory
        self.working_memory.append(item)
        
        # Save to backend
        try:
            self.backend.save_item(item)
        except Exception as e:
            logger.error(f"Failed to save item {item.id}: {e}")
        
        # Check if summarization is needed
        if self.config.auto_summarize:
            self._check_summarization_needed()
        
        return item.id
    
    def _check_summarization_needed(self) -> None:
        """Check if working memory needs summarization"""
        total_tokens = self._count_tokens(self.working_memory)
        total_messages = len(self.working_memory)
        
        if (total_tokens > self.config.max_working_memory_tokens or 
            total_messages > self.config.max_working_memory_messages):
            self._summarize_working_memory()
    
    def _summarize_working_memory(self) -> None:
        """Summarize oldest portion of working memory"""
        if len(self.working_memory) < 4:
            return
        
        # Calculate split point with overlap
        split_point = len(self.working_memory) // 2
        overlap = max(1, int(split_point * self.config.summary_overlap_ratio))
        
        to_summarize = self.working_memory[:split_point + overlap]
        self.working_memory = self.working_memory[split_point:]
        
        # Generate summary
        summary_content = self._generate_summary(to_summarize)
        
        # Calculate importance based on content
        avg_importance = sum(item.importance for item in to_summarize) / len(to_summarize)
        
        # Create summary item
        summary_item = MemoryItem(
            id=self._generate_item_id(summary_content),
            agent_id=self.agent_id,
            session_id=self.current_session_id,
            content=summary_content,
            item_type="summary",
            metadata={
                "summarized_items": len(to_summarize),
                "time_range": {
                    "start": to_summarize[0].timestamp.isoformat(),
                    "end": to_summarize[-1].timestamp.isoformat()
                }
            },
            timestamp=datetime.now(),
            tokens=len(summary_content) // 4,
            importance=avg_importance
        )
        
        # Save summary
        self.pending_summaries.append(summary_item)
        self.backend.save_item(summary_item)
        
        # Add to vector store if available
        if self.vector_store:
            self.vector_store.add_item(summary_item)
        
        # Check if we need to consolidate summaries
        if len(self.pending_summaries) >= self.config.summarize_threshold:
            self._consolidate_summaries()
    
    def _generate_summary(self, items: List[MemoryItem]) -> str:
        """Generate summary of memory items"""
        # TODO: Replace with actual LLM-based summarization
        contents = [f"{item.metadata.get('role', 'unknown')}: {item.content}" for item in items]
        combined = "\n".join(contents)
        
        if len(combined) <= 300:
            return f"Conversation summary: {combined}"
        
        # Simple truncation with context
        return f"Summary of {len(items)} messages from {items[0].timestamp.strftime('%H:%M')} to {items[-1].timestamp.strftime('%H:%M')}: {combined[:200]}..."
    
    def _consolidate_summaries(self) -> None:
        """Consolidate multiple summaries into a higher-level summary"""
        if len(self.pending_summaries) < 2:
            return
        
        # Create consolidated summary
        consolidated_content = self._generate_summary(self.pending_summaries)
        avg_importance = sum(s.importance for s in self.pending_summaries) / len(self.pending_summaries)
        
        consolidated_item = MemoryItem(
            id=self._generate_item_id(consolidated_content),
            agent_id=self.agent_id,
            session_id=self.current_session_id,
            content=consolidated_content,
            item_type="reflection",
            metadata={
                "consolidated_summaries": len(self.pending_summaries),
                "consolidation_level": 2
            },
            timestamp=datetime.now(),
            tokens=len(consolidated_content) // 4,
            importance=min(1.0, avg_importance * 1.1)  # Slight importance boost
        )
        
        # Save consolidated summary
        self.backend.save_item(consolidated_item)
        
        # Add to vector store
        if self.vector_store:
            self.vector_store.add_item(consolidated_item)
        
        # Clear pending summaries
        self.pending_summaries = []
    
    def get_context(self, query: Optional[str] = None, include_summaries: bool = True, max_items: int = 50) -> List[str]:
        """Get relevant context for current conversation"""
        context_items = []
        
        # Always include working memory (most recent)
        context_items.extend(self.working_memory)
        
        # Add pending summaries
        if include_summaries:
            context_items.extend(self.pending_summaries)
        
        # Add semantically relevant memories if query provided
        if query and self.vector_store:
            try:
                similar_memories = self.vector_store.find_similar(
                    query,
                    threshold=self.config.vector_similarity_threshold,
                    limit=self.config.max_retrieved_memories
                )
                
                # Add with special marking
                for memory in similar_memories:
                    if memory not in context_items:  # Avoid duplicates
                        context_items.insert(0, memory)
                        
            except Exception as e:
                logger.warning(f"Failed to retrieve similar memories: {e}")
        
        # Sort by timestamp and importance, limit results
        context_items.sort(key=lambda x: (x.timestamp, x.importance), reverse=True)
        context_items = context_items[:max_items]
        
        # Format for output
        formatted_context = []
        for item in context_items:
            prefix = {
                "user": "User",
                "assistant": "Assistant", 
                "summary": "Summary",
                "reflection": "Past Context"
            }.get(item.item_type, item.item_type.title())
            
            formatted_context.append(f"[{prefix}] {item.content}")
        
        return formatted_context
    
    def search_memory(self, query: str, limit: int = 10) -> List[MemoryItem]:
        """Search memory using full-text search"""
        try:
            return self.backend.search_items(self.agent_id, query, limit)
        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return []
    
    def start_new_session(self) -> str:
        """Start a new conversation session"""
        # Consolidate any pending summaries from current session
        if self.pending_summaries:
            self._consolidate_summaries()
        
        # Generate new session
        self.current_session_id = self._generate_session_id()
        self.working_memory = []
        self.pending_summaries = []
        
        logger.info(f"Started new session: {self.current_session_id}")
        return self.current_session_id
    
    def cleanup_old_memories(self) -> int:
        """Clean up old memories based on config"""
        try:
            return self.backend.cleanup_old_items(self.config.auto_cleanup_days)
        except Exception as e:
            logger.error(f"Memory cleanup failed: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        return {
            "agent_id": self.agent_id,
            "current_session": self.current_session_id,
            "working_memory_items": len(self.working_memory),
            "pending_summaries": len(self.pending_summaries),
            "working_memory_tokens": self._count_tokens(self.working_memory),
            "vector_store_enabled": self.vector_store is not None,
            "vector_store_items": len(self.vector_store.items) if self.vector_store else 0,
            "config": asdict(self.config)
        }


# Mixin class for easy integration
class MemoryCapableMixin:
    """Mixin to add memory capabilities to any agent class"""
    
    def __init__(self, *args, memory_config: Optional[MemoryConfig] = None, **kwargs):
        super().__init__(*args, **kwargs)
        agent_id = getattr(self, 'agent_id', None) or getattr(self, 'name', None) or self.__class__.__name__
        self.memory = PersistentMemoryManager(agent_id, memory_config)
    
    def remember(self, content: str, role: str = "user", metadata: Optional[Dict] = None, importance: float = 1.0) -> str:
        """Add content to memory"""
        return self.memory.add_message(content, role, metadata, importance)
    
    def recall(self, query: Optional[str] = None, include_summaries: bool = True) -> List[str]:
        """Get relevant context from memory"""
        return self.memory.get_context(query, include_summaries)
    
    def search_memories(self, query: str, limit: int = 10) -> List[MemoryItem]:
        """Search through memory"""
        return self.memory.search_memory(query, limit)
    
    def forget_old(self) -> int:
        """Clean up old memories"""
        return self.memory.cleanup_old_memories()
    
    def new_session(self) -> str:
        """Start a new memory session"""
        return self.memory.start_new_session()
    
    def memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return self.memory.get_stats()


# Decorator for easy memory integration
def with_persistent_memory(config: Optional[MemoryConfig] = None):
    """Decorator to add persistent memory capabilities to an agent class"""
    def decorator(agent_class):
        class MemoryEnabledAgent(MemoryCapableMixin, agent_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, memory_config=config, **kwargs)
        
        return MemoryEnabledAgent
    return decorator
