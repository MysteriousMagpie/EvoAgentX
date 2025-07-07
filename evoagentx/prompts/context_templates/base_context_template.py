"""
Base Context Template Classes

Provides the foundation for advanced context management in EvoAgentX,
extending the existing PromptTemplate with context-aware capabilities.
"""

from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
from datetime import datetime

from ..template import PromptTemplate
from ...memory.persistent_memory import MemoryConfig
from ...core.logging import logger


class ContextLayer(Enum):
    """Defines the different layers of context hierarchy"""
    GLOBAL = "global"      # System-wide context (agent identity, core capabilities)
    SESSION = "session"    # Session-specific context (current conversation, user preferences)
    TASK = "task"         # Task-specific context (current objective, immediate requirements)
    DYNAMIC = "dynamic"   # Real-time context (recent messages, current state)


@dataclass
class ContextConfig:
    """Configuration for context template behavior"""
    # Context limits and thresholds
    max_context_tokens: int = 4000
    max_context_items: int = 20
    context_relevance_threshold: float = 0.7
    
    # Context layers to include
    enabled_layers: List[ContextLayer] = field(default_factory=lambda: [
        ContextLayer.GLOBAL, ContextLayer.SESSION, ContextLayer.TASK, ContextLayer.DYNAMIC
    ])
    
    # Context ranking and selection
    enable_context_ranking: bool = True
    context_decay_factor: float = 0.95  # How quickly context relevance decays over time
    prioritize_recent_context: bool = True
    
    # Context compression and optimization
    enable_context_compression: bool = True
    compression_ratio: float = 0.3  # Target compression when context is too long
    preserve_key_information: bool = True
    
    # Integration settings
    memory_integration: bool = True
    vector_search_enabled: bool = True
    semantic_similarity_threshold: float = 0.75


@dataclass
class ContextItem:
    """Represents a single piece of context information"""
    content: str
    layer: ContextLayer
    relevance_score: float = 1.0
    timestamp: float = field(default_factory=time.time)
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5  # 0.0 = low, 1.0 = critical
    
    def is_fresh(self, max_age_seconds: int = 3600) -> bool:
        """Check if context item is still fresh"""
        return (time.time() - self.timestamp) < max_age_seconds
    
    def get_age_factor(self, decay_factor: float = 0.95) -> float:
        """Calculate age-based relevance factor"""
        age_hours = (time.time() - self.timestamp) / 3600
        return decay_factor ** age_hours
    
    def get_weighted_relevance(self, decay_factor: float = 0.95) -> float:
        """Get relevance score adjusted for age and importance"""
        age_factor = self.get_age_factor(decay_factor)
        return self.relevance_score * self.importance * age_factor


class BaseContextTemplate(PromptTemplate):
    """
    Enhanced prompt template with intelligent context management.
    
    Extends the base PromptTemplate to provide:
    - Hierarchical context organization
    - Dynamic context selection based on relevance
    - Memory integration for context retrieval
    - Context compression and optimization
    """
    
    def __init__(
        self,
        instruction: str,
        context_config: Optional[ContextConfig] = None,
        memory_config: Optional[MemoryConfig] = None,
        **kwargs
    ):
        super().__init__(instruction=instruction, **kwargs)
        self.context_config = context_config or ContextConfig()
        self.memory_config = memory_config
        
        # Context storage
        self._context_layers: Dict[ContextLayer, List[ContextItem]] = {
            layer: [] for layer in ContextLayer
        }
        
        # Context processing functions
        self._context_processors: Dict[ContextLayer, Callable] = {}
        self._relevance_scorers: List[Callable] = []
        
        # Initialize default processors
        self._setup_default_processors()
    
    def _setup_default_processors(self):
        """Setup default context processing functions"""
        self._context_processors[ContextLayer.GLOBAL] = self._process_global_context
        self._context_processors[ContextLayer.SESSION] = self._process_session_context
        self._context_processors[ContextLayer.TASK] = self._process_task_context
        self._context_processors[ContextLayer.DYNAMIC] = self._process_dynamic_context
        
        # Default relevance scorers
        self._relevance_scorers.extend([
            self._score_semantic_relevance,
            self._score_temporal_relevance,
            self._score_importance_relevance
        ])
    
    def add_context(
        self,
        content: str,
        layer: ContextLayer,
        relevance_score: float = 1.0,
        importance: float = 0.5,
        source: str = "user",
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContextItem:
        """Add a new context item to the specified layer"""
        context_item = ContextItem(
            content=content,
            layer=layer,
            relevance_score=relevance_score,
            source=source,
            metadata=metadata or {},
            importance=importance
        )
        
        self._context_layers[layer].append(context_item)
        
        # Apply layer-specific processing
        if layer in self._context_processors:
            self._context_processors[layer](context_item)
        
        logger.debug(f"Added context to {layer.value}: {content[:50]}...")
        return context_item
    
    def get_context_for_layer(self, layer: ContextLayer, max_items: int = 10) -> List[ContextItem]:
        """Get context items for a specific layer, sorted by relevance"""
        items = self._context_layers[layer]
        
        if self.context_config.enable_context_ranking:
            # Sort by weighted relevance (includes age decay)
            items = sorted(
                items,
                key=lambda x: x.get_weighted_relevance(self.context_config.context_decay_factor),
                reverse=True
            )
        
        return items[:max_items]
    
    def get_relevant_context(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        include_layers: Optional[List[ContextLayer]] = None
    ) -> List[ContextItem]:
        """
        Get the most relevant context items across all enabled layers.
        
        Args:
            query: Optional query to find semantically similar context
            max_tokens: Maximum tokens to include (overrides config)
            include_layers: Specific layers to include (overrides config)
        
        Returns:
            List of context items sorted by relevance
        """
        max_tokens = max_tokens or self.context_config.max_context_tokens
        include_layers = include_layers or self.context_config.enabled_layers
        
        # Collect context from all enabled layers
        all_context = []
        for layer in include_layers:
            layer_context = self.get_context_for_layer(layer)
            all_context.extend(layer_context)
        
        # Apply semantic filtering if query provided
        if query and self.context_config.vector_search_enabled:
            all_context = self._filter_by_semantic_similarity(all_context, query)
        
        # Apply relevance threshold
        filtered_context = [
            item for item in all_context
            if item.get_weighted_relevance(self.context_config.context_decay_factor) 
            >= self.context_config.context_relevance_threshold
        ]
        
        # Sort by final relevance score
        filtered_context.sort(
            key=lambda x: x.get_weighted_relevance(self.context_config.context_decay_factor),
            reverse=True
        )
        
        # Apply token limit
        return self._apply_token_limit(filtered_context, max_tokens)
    
    def render_context_enhanced(
        self,
        query: Optional[str] = None,
        include_layers: Optional[List[ContextLayer]] = None
    ) -> str:
        """
        Render context using the enhanced context system.
        
        This replaces the base render_context method with intelligent
        context selection and formatting.
        """
        relevant_context = self.get_relevant_context(query, include_layers=include_layers)
        
        if not relevant_context:
            return ""
        
        # Group context by layer for better organization
        context_by_layer = {}
        for item in relevant_context:
            if item.layer not in context_by_layer:
                context_by_layer[item.layer] = []
            context_by_layer[item.layer].append(item)
        
        # Build context string with layer headers
        context_parts = ["### Context"]
        context_parts.append("Here is relevant background information organized by context layer:")
        
        for layer in [ContextLayer.GLOBAL, ContextLayer.SESSION, ContextLayer.TASK, ContextLayer.DYNAMIC]:
            if layer not in context_by_layer:
                continue
                
            items = context_by_layer[layer]
            context_parts.append(f"\n#### {layer.value.title()} Context")
            
            for i, item in enumerate(items, 1):
                # Include relevance score for debugging (can be removed in production)
                score = item.get_weighted_relevance(self.context_config.context_decay_factor)
                context_parts.append(f"{i}. {item.content} (relevance: {score:.2f})")
        
        return "\n".join(context_parts) + "\n"
    
    def clear_context_layer(self, layer: ContextLayer):
        """Clear all context from a specific layer"""
        self._context_layers[layer].clear()
        logger.debug(f"Cleared context layer: {layer.value}")
    
    def clear_old_context(self, max_age_hours: int = 24):
        """Remove context items older than specified age"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for layer in self._context_layers:
            original_count = len(self._context_layers[layer])
            self._context_layers[layer] = [
                item for item in self._context_layers[layer]
                if (current_time - item.timestamp) <= max_age_seconds
            ]
            removed_count = original_count - len(self._context_layers[layer])
            if removed_count > 0:
                logger.debug(f"Removed {removed_count} old context items from {layer.value}")
    
    def get_context_stats(self) -> Dict[str, Any]:
        """Get statistics about current context usage"""
        stats = {
            "total_items": sum(len(items) for items in self._context_layers.values()),
            "by_layer": {layer.value: len(items) for layer, items in self._context_layers.items()},
            "config": {
                "max_tokens": self.context_config.max_context_tokens,
                "max_items": self.context_config.max_context_items,
                "relevance_threshold": self.context_config.context_relevance_threshold
            }
        }
        
        # Calculate estimated token usage (rough estimate: 4 chars per token)
        total_chars = sum(
            len(item.content) 
            for items in self._context_layers.values() 
            for item in items
        )
        stats["estimated_tokens"] = total_chars // 4
        
        return stats
    
    # Context processing methods (to be overridden by subclasses)
    def _process_global_context(self, item: ContextItem):
        """Process global context items (agent identity, capabilities)"""
        # Default: mark as high importance for global context
        item.importance = max(item.importance, 0.8)
    
    def _process_session_context(self, item: ContextItem):
        """Process session context items (conversation history, preferences)"""
        # Default: standard importance
        pass
    
    def _process_task_context(self, item: ContextItem):
        """Process task-specific context items (current objectives)"""
        # Default: high relevance for task context
        item.relevance_score = max(item.relevance_score, 0.9)
    
    def _process_dynamic_context(self, item: ContextItem):
        """Process dynamic context items (recent messages, current state)"""
        # Default: time-sensitive, higher importance for recent items
        item.importance = min(item.importance + 0.2, 1.0)
    
    # Relevance scoring methods
    def _score_semantic_relevance(self, item: ContextItem, query: str) -> float:
        """Score context item based on semantic similarity to query"""
        # Placeholder - would integrate with sentence transformers in practice
        # For now, use simple keyword matching
        query_words = set(query.lower().split())
        item_words = set(item.content.lower().split())
        
        if not query_words:
            return item.relevance_score
        
        overlap = len(query_words.intersection(item_words))
        return overlap / len(query_words)
    
    def _score_temporal_relevance(self, item: ContextItem, current_time: float = None) -> float:
        """Score context item based on temporal relevance"""
        if current_time is None:
            current_time = time.time()
        
        return item.get_age_factor(self.context_config.context_decay_factor)
    
    def _score_importance_relevance(self, item: ContextItem) -> float:
        """Score context item based on importance"""
        return item.importance
    
    def _filter_by_semantic_similarity(
        self, 
        items: List[ContextItem], 
        query: str
    ) -> List[ContextItem]:
        """Filter context items by semantic similarity to query"""
        if not query:
            return items
        
        # Update relevance scores based on semantic similarity
        for item in items:
            semantic_score = self._score_semantic_relevance(item, query)
            if semantic_score >= self.context_config.semantic_similarity_threshold:
                # Boost relevance for semantically similar items
                item.relevance_score = min(item.relevance_score + semantic_score * 0.3, 1.0)
        
        # Filter out items below threshold
        return [
            item for item in items
            if self._score_semantic_relevance(item, query) >= self.context_config.semantic_similarity_threshold
        ]
    
    def _apply_token_limit(self, items: List[ContextItem], max_tokens: int) -> List[ContextItem]:
        """Apply token limit while preserving most important context"""
        if not items:
            return items
        
        # Rough token estimation: 4 characters per token
        current_tokens = 0
        selected_items = []
        
        for item in items:
            item_tokens = len(item.content) // 4
            if current_tokens + item_tokens <= max_tokens:
                selected_items.append(item)
                current_tokens += item_tokens
            else:
                # Try compression if enabled
                if self.context_config.enable_context_compression:
                    compressed_content = self._compress_context_item(item, max_tokens - current_tokens)
                    if compressed_content:
                        compressed_item = ContextItem(
                            content=compressed_content,
                            layer=item.layer,
                            relevance_score=item.relevance_score,
                            timestamp=item.timestamp,
                            source=item.source + "_compressed",
                            metadata=item.metadata,
                            importance=item.importance
                        )
                        selected_items.append(compressed_item)
                break
        
        return selected_items
    
    def _compress_context_item(self, item: ContextItem, max_tokens: int) -> Optional[str]:
        """Compress a context item to fit within token limit"""
        target_chars = max_tokens * 4
        
        if len(item.content) <= target_chars:
            return item.content
        
        # Simple compression: take first and last parts
        if self.context_config.preserve_key_information:
            first_part_chars = target_chars // 2
            last_part_chars = target_chars - first_part_chars - 10  # Account for ellipsis
            
            if last_part_chars > 0:
                return (
                    item.content[:first_part_chars] + 
                    " [...] " + 
                    item.content[-last_part_chars:]
                )
        
        # Fallback: just truncate
        return item.content[:target_chars] + "..."