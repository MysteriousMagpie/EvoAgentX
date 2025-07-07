"""
Enhanced Context Templates for EvoAgentX

This module provides advanced context management templates that extend the base
PromptTemplate system with intelligent context injection, hierarchical organization,
and adaptive context selection based on conversation state and agent roles.

Key Features:
- Dynamic context adaptation based on conversation flow
- Hierarchical context organization (global → session → task)
- Role-specific context templates for different agent types
- Task-specific context patterns for domain expertise
- Context relevance scoring and automatic pruning
- Memory-driven context retrieval integration
"""

from .base_context_template import BaseContextTemplate, ContextLayer, ContextConfig
from .dynamic_context import DynamicContextTemplate
from .hierarchical_context import HierarchicalContextTemplate
from .role_based_context import RoleBasedContextTemplate
from .task_specific_context import TaskSpecificContextTemplate

__all__ = [
    "BaseContextTemplate",
    "ContextLayer", 
    "ContextConfig",
    "DynamicContextTemplate",
    "HierarchicalContextTemplate", 
    "RoleBasedContextTemplate",
    "TaskSpecificContextTemplate"
]