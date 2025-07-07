"""
Hierarchical Context Template

Provides multi-level context organization with inheritance and cascading.
This template organizes context into clear hierarchies where higher-level
context influences and informs lower-level context decisions.

Hierarchy levels:
- System Level: Core agent identity, fundamental capabilities
- Domain Level: Subject matter expertise, domain-specific knowledge  
- Session Level: Current conversation context, user preferences
- Task Level: Specific task requirements, immediate objectives
- Interaction Level: Turn-by-turn context, immediate responses
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
from collections import defaultdict

from .base_context_template import BaseContextTemplate, ContextItem, ContextLayer, ContextConfig
from ...core.logging import logger


class HierarchyLevel(Enum):
    """Hierarchical levels for context organization"""
    SYSTEM = "system"           # Core identity, fundamental capabilities
    DOMAIN = "domain"           # Subject expertise, domain knowledge
    SESSION = "session"         # Conversation context, user preferences
    TASK = "task"              # Current task, specific objectives
    INTERACTION = "interaction" # Turn-level context, immediate responses


@dataclass
class HierarchicalContextConfig(ContextConfig):
    """Configuration for hierarchical context behavior"""
    # Hierarchy settings
    enable_context_inheritance: bool = True
    enable_context_cascading: bool = True
    max_inheritance_depth: int = 3
    
    # Level-specific limits
    level_token_limits: Dict[str, int] = field(default_factory=lambda: {
        'system': 800,
        'domain': 1200,
        'session': 1000,
        'task': 800,
        'interaction': 600
    })
    
    # Inheritance rules
    inheritance_decay: float = 0.8  # How much relevance decays when inherited
    cascade_threshold: float = 0.7  # Minimum relevance to cascade down
    
    # Priority weights for levels
    level_priority_weights: Dict[str, float] = field(default_factory=lambda: {
        'system': 0.9,      # High priority - core identity
        'domain': 0.8,      # High priority - expertise
        'session': 0.7,     # Medium-high priority - context
        'task': 0.85,       # High priority - current objectives  
        'interaction': 0.6  # Medium priority - immediate context
    })


@dataclass
class ContextHierarchyNode:
    """Represents a node in the context hierarchy"""
    level: HierarchyLevel
    items: List[ContextItem] = field(default_factory=list)
    children: Dict[str, 'ContextHierarchyNode'] = field(default_factory=dict)
    parent: Optional['ContextHierarchyNode'] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_child(self, key: str, child: 'ContextHierarchyNode'):
        """Add a child node"""
        child.parent = self
        self.children[key] = child
    
    def get_inherited_context(self, max_depth: int = 3) -> List[ContextItem]:
        """Get context inherited from parent levels"""
        inherited = []
        
        current = self.parent
        depth = 0
        
        while current and depth < max_depth:
            # Add parent's high-relevance items
            for item in current.items:
                if item.relevance_score >= 0.7:  # Only inherit high-relevance items
                    # Create inherited copy with reduced relevance
                    inherited_item = ContextItem(
                        content=item.content,
                        layer=item.layer,
                        relevance_score=item.relevance_score * (0.8 ** (depth + 1)),
                        timestamp=item.timestamp,
                        source=f"{item.source}_inherited",
                        metadata={**item.metadata, 'inherited_from': current.level.value},
                        importance=item.importance
                    )
                    inherited.append(inherited_item)
            
            current = current.parent
            depth += 1
        
        return inherited
    
    def cascade_context_down(self, cascade_threshold: float = 0.7):
        """Cascade high-relevance context to child levels"""
        high_relevance_items = [
            item for item in self.items 
            if item.relevance_score >= cascade_threshold
        ]
        
        for child in self.children.values():
            for item in high_relevance_items:
                # Create cascaded copy
                cascaded_item = ContextItem(
                    content=item.content,
                    layer=item.layer,
                    relevance_score=item.relevance_score * 0.9,  # Slight relevance reduction
                    timestamp=item.timestamp,
                    source=f"{item.source}_cascaded",
                    metadata={**item.metadata, 'cascaded_from': self.level.value},
                    importance=item.importance
                )
                child.items.append(cascaded_item)


class HierarchicalContextTemplate(BaseContextTemplate):
    """
    Hierarchical context template with multi-level organization.
    
    Features:
    - Context inheritance from higher levels
    - Context cascading to lower levels
    - Level-specific token and item limits
    - Hierarchical relevance scoring
    - Cross-level context relationships
    """
    
    def __init__(
        self,
        instruction: str,
        context_config: Optional[HierarchicalContextConfig] = None,
        **kwargs
    ):
        if context_config is None:
            context_config = HierarchicalContextConfig()
        
        super().__init__(instruction=instruction, context_config=context_config, **kwargs)
        
        # Build context hierarchy
        self.context_hierarchy: Dict[HierarchyLevel, ContextHierarchyNode] = {}
        self._build_hierarchy()
        
        # Level mappings for easy access
        self.level_to_layer_mapping = {
            HierarchyLevel.SYSTEM: ContextLayer.GLOBAL,
            HierarchyLevel.DOMAIN: ContextLayer.GLOBAL,
            HierarchyLevel.SESSION: ContextLayer.SESSION,
            HierarchyLevel.TASK: ContextLayer.TASK,
            HierarchyLevel.INTERACTION: ContextLayer.DYNAMIC
        }
        
        # Cross-references for context relationships
        self.context_relationships: Dict[str, List[str]] = defaultdict(list)
        
    def _build_hierarchy(self):
        """Build the context hierarchy structure"""
        # Create hierarchy nodes
        for level in HierarchyLevel:
            self.context_hierarchy[level] = ContextHierarchyNode(level=level)
        
        # Establish parent-child relationships
        system_node = self.context_hierarchy[HierarchyLevel.SYSTEM]
        domain_node = self.context_hierarchy[HierarchyLevel.DOMAIN]
        session_node = self.context_hierarchy[HierarchyLevel.SESSION]
        task_node = self.context_hierarchy[HierarchyLevel.TASK]
        interaction_node = self.context_hierarchy[HierarchyLevel.INTERACTION]
        
        # System -> Domain -> Session -> Task -> Interaction
        system_node.add_child("domain", domain_node)
        domain_node.add_child("session", session_node)
        session_node.add_child("task", task_node)
        task_node.add_child("interaction", interaction_node)
        
        logger.debug("Built hierarchical context structure")
    
    def add_hierarchical_context(
        self,
        content: str,
        level: HierarchyLevel,
        relevance_score: float = 1.0,
        importance: float = 0.5,
        source: str = "user",
        metadata: Optional[Dict[str, Any]] = None,
        relationships: Optional[List[str]] = None
    ) -> ContextItem:
        """
        Add context to a specific hierarchy level.
        
        Args:
            content: Context content
            level: Hierarchy level to add to
            relevance_score: Initial relevance score
            importance: Importance weight
            source: Source of the context
            metadata: Additional metadata
            relationships: Related context IDs for cross-referencing
        
        Returns:
            Created context item
        """
        # Map hierarchy level to context layer
        layer = self.level_to_layer_mapping.get(level, ContextLayer.DYNAMIC)
        
        # Create context item
        context_item = ContextItem(
            content=content,
            layer=layer,
            relevance_score=relevance_score,
            source=source,
            metadata=metadata or {},
            importance=importance
        )
        
        # Add to hierarchy node
        hierarchy_node = self.context_hierarchy[level]
        hierarchy_node.items.append(context_item)
        
        # Apply level-specific processing
        self._process_hierarchical_context(context_item, level)
        
        # Handle context relationships
        if relationships:
            context_id = f"{level.value}_{len(hierarchy_node.items)}"
            self.context_relationships[context_id].extend(relationships)
        
        # Apply inheritance and cascading if enabled
        if self.context_config.enable_context_inheritance:
            self._apply_inheritance(level)
        
        if self.context_config.enable_context_cascading:
            self._apply_cascading(level)
        
        logger.debug(f"Added hierarchical context to {level.value}: {content[:50]}...")
        return context_item
    
    def get_hierarchical_context(
        self,
        query: Optional[str] = None,
        target_levels: Optional[List[HierarchyLevel]] = None,
        include_inherited: bool = True,
        include_cascaded: bool = True
    ) -> Dict[HierarchyLevel, List[ContextItem]]:
        """
        Get context organized by hierarchy levels.
        
        Args:
            query: Query for semantic filtering
            target_levels: Specific levels to include
            include_inherited: Include inherited context
            include_cascaded: Include cascaded context
        
        Returns:
            Dictionary mapping hierarchy levels to context items
        """
        target_levels = target_levels or list(HierarchyLevel)
        result = {}
        
        for level in target_levels:
            level_context = []
            hierarchy_node = self.context_hierarchy[level]
            
            # Add direct context from this level
            level_context.extend(hierarchy_node.items)
            
            # Add inherited context if enabled
            if include_inherited and self.context_config.enable_context_inheritance:
                inherited = hierarchy_node.get_inherited_context(
                    self.context_config.max_inheritance_depth
                )
                level_context.extend(inherited)
            
            # Apply semantic filtering if query provided
            if query:
                level_context = self._filter_by_semantic_similarity(level_context, query)
            
            # Apply level-specific token limits
            level_context = self._apply_level_token_limits(level_context, level)
            
            # Sort by hierarchical relevance
            level_context = self._sort_by_hierarchical_relevance(level_context, level)
            
            result[level] = level_context
        
        return result
    
    def get_relevant_context(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        include_layers: Optional[List[ContextLayer]] = None
    ) -> List[ContextItem]:
        """
        Get relevant context using hierarchical organization.
        
        Overrides base method to leverage hierarchy for better context selection.
        """
        # Get hierarchical context
        hierarchical_context = self.get_hierarchical_context(
            query=query,
            include_inherited=True,
            include_cascaded=True
        )
        
        # Flatten and prioritize by hierarchy level
        prioritized_context = []
        
        # Process levels in priority order
        level_priorities = [
            (HierarchyLevel.SYSTEM, self.context_config.level_priority_weights.get('system', 0.9)),
            (HierarchyLevel.TASK, self.context_config.level_priority_weights.get('task', 0.85)),
            (HierarchyLevel.DOMAIN, self.context_config.level_priority_weights.get('domain', 0.8)),
            (HierarchyLevel.SESSION, self.context_config.level_priority_weights.get('session', 0.7)),
            (HierarchyLevel.INTERACTION, self.context_config.level_priority_weights.get('interaction', 0.6))
        ]
        
        for level, priority_weight in level_priorities:
            if level in hierarchical_context:
                for item in hierarchical_context[level]:
                    # Apply hierarchy priority boost
                    item.relevance_score = min(item.relevance_score * priority_weight, 1.0)
                    prioritized_context.append(item)
        
        # Remove duplicates (can happen with inheritance/cascading)
        unique_context = self._deduplicate_context(prioritized_context)
        
        # Apply final token limit
        max_tokens = max_tokens or self.context_config.max_context_tokens
        return self._apply_token_limit(unique_context, max_tokens)
    
    def _process_hierarchical_context(self, item: ContextItem, level: HierarchyLevel):
        """Apply level-specific processing to context items"""
        if level == HierarchyLevel.SYSTEM:
            # System-level context is high importance
            item.importance = max(item.importance, 0.8)
            item.metadata['persistent'] = True
            
        elif level == HierarchyLevel.DOMAIN:
            # Domain context gets expertise boost
            item.metadata['domain_expertise'] = True
            item.importance = max(item.importance, 0.7)
            
        elif level == HierarchyLevel.SESSION:
            # Session context is conversation-specific
            item.metadata['session_specific'] = True
            
        elif level == HierarchyLevel.TASK:
            # Task context is highly relevant for current objectives
            item.relevance_score = max(item.relevance_score, 0.8)
            item.metadata['task_relevant'] = True
            
        elif level == HierarchyLevel.INTERACTION:
            # Interaction context is time-sensitive
            item.metadata['time_sensitive'] = True
    
    def _apply_inheritance(self, level: HierarchyLevel):
        """Apply context inheritance from parent levels"""
        if not self.context_config.enable_context_inheritance:
            return
        
        hierarchy_node = self.context_hierarchy[level]
        inherited_context = hierarchy_node.get_inherited_context(
            self.context_config.max_inheritance_depth
        )
        
        # Add inherited context (avoiding duplicates)
        existing_content = {item.content for item in hierarchy_node.items}
        for inherited_item in inherited_context:
            if inherited_item.content not in existing_content:
                hierarchy_node.items.append(inherited_item)
    
    def _apply_cascading(self, level: HierarchyLevel):
        """Apply context cascading to child levels"""
        if not self.context_config.enable_context_cascading:
            return
        
        hierarchy_node = self.context_hierarchy[level]
        hierarchy_node.cascade_context_down(self.context_config.cascade_threshold)
    
    def _apply_level_token_limits(
        self,
        context_items: List[ContextItem],
        level: HierarchyLevel
    ) -> List[ContextItem]:
        """Apply token limits specific to hierarchy level"""
        level_limit = self.context_config.level_token_limits.get(level.value, 1000)
        return self._apply_token_limit(context_items, level_limit)
    
    def _sort_by_hierarchical_relevance(
        self,
        context_items: List[ContextItem],
        level: HierarchyLevel
    ) -> List[ContextItem]:
        """Sort context items by hierarchical relevance"""
        def relevance_key(item: ContextItem) -> float:
            base_relevance = item.get_weighted_relevance(self.context_config.context_decay_factor)
            
            # Apply level-specific boosts
            level_weight = self.context_config.level_priority_weights.get(level.value, 1.0)
            
            # Boost inherited and cascaded context appropriately
            if 'inherited_from' in item.metadata:
                base_relevance *= 0.9  # Slight penalty for inherited
            elif 'cascaded_from' in item.metadata:
                base_relevance *= 0.95  # Very slight penalty for cascaded
            
            return base_relevance * level_weight
        
        return sorted(context_items, key=relevance_key, reverse=True)
    
    def _deduplicate_context(self, context_items: List[ContextItem]) -> List[ContextItem]:
        """Remove duplicate context items based on content similarity"""
        seen_content = set()
        unique_items = []
        
        for item in context_items:
            # Simple deduplication based on content
            content_key = item.content.strip().lower()
            
            if content_key not in seen_content:
                seen_content.add(content_key)
                unique_items.append(item)
        
        return unique_items
    
    def add_context_relationship(self, context_id1: str, context_id2: str, relationship_type: str = "related"):
        """Add a relationship between two context items"""
        self.context_relationships[context_id1].append(f"{relationship_type}:{context_id2}")
        self.context_relationships[context_id2].append(f"{relationship_type}:{context_id1}")
    
    def get_related_context(self, context_id: str) -> List[str]:
        """Get context items related to the given context ID"""
        return self.context_relationships.get(context_id, [])
    
    def clear_hierarchy_level(self, level: HierarchyLevel):
        """Clear all context from a specific hierarchy level"""
        self.context_hierarchy[level].items.clear()
        logger.debug(f"Cleared hierarchy level: {level.value}")
    
    def get_hierarchy_stats(self) -> Dict[str, Any]:
        """Get statistics about the context hierarchy"""
        stats = {
            'levels': {},
            'total_items': 0,
            'inheritance_enabled': self.context_config.enable_context_inheritance,
            'cascading_enabled': self.context_config.enable_context_cascading,
            'relationships': len(self.context_relationships)
        }
        
        for level, node in self.context_hierarchy.items():
            level_stats = {
                'items': len(node.items),
                'children': len(node.children),
                'has_parent': node.parent is not None
            }
            
            # Calculate token usage
            total_chars = sum(len(item.content) for item in node.items)
            level_stats['estimated_tokens'] = total_chars // 4
            level_stats['token_limit'] = self.context_config.level_token_limits.get(level.value, 1000)
            
            stats['levels'][level.value] = level_stats
            stats['total_items'] += len(node.items)
        
        return stats
    
    def render_context_enhanced(
        self,
        query: Optional[str] = None,
        include_layers: Optional[List[ContextLayer]] = None
    ) -> str:
        """
        Render context using hierarchical organization.
        
        Overrides base method to show clear hierarchical structure.
        """
        hierarchical_context = self.get_hierarchical_context(query=query)
        
        if not any(hierarchical_context.values()):
            return ""
        
        context_parts = ["### Hierarchical Context"]
        context_parts.append("Information organized by context hierarchy:")
        
        # Render each level with clear hierarchy
        for level in [HierarchyLevel.SYSTEM, HierarchyLevel.DOMAIN, 
                     HierarchyLevel.SESSION, HierarchyLevel.TASK, 
                     HierarchyLevel.INTERACTION]:
            
            if level not in hierarchical_context or not hierarchical_context[level]:
                continue
                
            items = hierarchical_context[level]
            context_parts.append(f"\n#### {level.value.title()} Level")
            
            for i, item in enumerate(items, 1):
                relevance = item.get_weighted_relevance(self.context_config.context_decay_factor)
                
                # Add inheritance/cascade indicators
                indicators = []
                if 'inherited_from' in item.metadata:
                    indicators.append(f"↑{item.metadata['inherited_from']}")
                if 'cascaded_from' in item.metadata:
                    indicators.append(f"↓{item.metadata['cascaded_from']}")
                
                indicator_str = f" [{', '.join(indicators)}]" if indicators else ""
                
                context_parts.append(
                    f"{i}. {item.content}{indicator_str} (relevance: {relevance:.2f})"
                )
        
        return "\n".join(context_parts) + "\n"