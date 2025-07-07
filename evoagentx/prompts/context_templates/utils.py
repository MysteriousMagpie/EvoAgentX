"""
Context Template Utilities and Helpers

Provides utility functions, factory methods, and helpers for working with
enhanced context templates in EvoAgentX.
"""

from typing import Dict, List, Any, Optional, Union, Type, Callable
from dataclasses import dataclass
import time
import json
from pathlib import Path

from .base_context_template import BaseContextTemplate, ContextItem, ContextLayer, ContextConfig
from .dynamic_context import DynamicContextTemplate, DynamicContextConfig, ConversationPhase
from .hierarchical_context import HierarchicalContextTemplate, HierarchicalContextConfig, HierarchyLevel
from .role_based_context import RoleBasedContextTemplate, RoleBasedContextConfig, AgentRole, RoleProfile, ExpertiseDomain, InteractionStyle
from .task_specific_context import TaskSpecificContextTemplate, TaskSpecificContextConfig, TaskType, TaskProfile, TaskComplexity, TaskDomain

from ...core.logging import logger


class ContextTemplateFactory:
    """Factory for creating different types of context templates"""
    
    @staticmethod
    def create_dynamic_template(
        instruction: str,
        config: Optional[DynamicContextConfig] = None,
        **kwargs
    ) -> DynamicContextTemplate:
        """Create a dynamic context template with conversation adaptation"""
        return DynamicContextTemplate(
            instruction=instruction,
            context_config=config or DynamicContextConfig(),
            **kwargs
        )
    
    @staticmethod
    def create_hierarchical_template(
        instruction: str,
        config: Optional[HierarchicalContextConfig] = None,
        **kwargs
    ) -> HierarchicalContextTemplate:
        """Create a hierarchical context template with multi-level organization"""
        return HierarchicalContextTemplate(
            instruction=instruction,
            context_config=config or HierarchicalContextConfig(),
            **kwargs
        )
    
    @staticmethod
    def create_role_based_template(
        instruction: str,
        role: AgentRole,
        expertise_domains: List[ExpertiseDomain] = None,
        interaction_style: InteractionStyle = InteractionStyle.CONVERSATIONAL,
        config: Optional[RoleBasedContextConfig] = None,
        **kwargs
    ) -> RoleBasedContextTemplate:
        """Create a role-based context template for specialized agents"""
        if expertise_domains is None:
            expertise_domains = [ExpertiseDomain.GENERAL]
        
        role_profile = RoleProfile(
            role=role,
            expertise_domains=expertise_domains,
            interaction_style=interaction_style
        )
        
        return RoleBasedContextTemplate(
            instruction=instruction,
            role_profile=role_profile,
            context_config=config or RoleBasedContextConfig(),
            **kwargs
        )
    
    @staticmethod
    def create_task_specific_template(
        instruction: str,
        task_type: TaskType,
        complexity: TaskComplexity = TaskComplexity.MODERATE,
        domain: TaskDomain = TaskDomain.SOFTWARE_ENGINEERING,
        config: Optional[TaskSpecificContextConfig] = None,
        **kwargs
    ) -> TaskSpecificContextTemplate:
        """Create a task-specific context template optimized for specific work types"""
        task_profile = TaskProfile(
            task_type=task_type,
            complexity=complexity,
            domain=domain
        )
        
        return TaskSpecificContextTemplate(
            instruction=instruction,
            task_profile=task_profile,
            context_config=config or TaskSpecificContextConfig(),
            **kwargs
        )
    
    @staticmethod
    def create_hybrid_template(
        instruction: str,
        template_types: List[str],
        configs: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> BaseContextTemplate:
        """
        Create a hybrid template combining multiple approaches.
        
        Note: This creates a composite that delegates to the most appropriate
        template based on the current context.
        """
        configs = configs or {}
        
        # For now, create a base template with enhanced capabilities
        # In a full implementation, this would create a composite template
        return BaseContextTemplate(
            instruction=instruction,
            context_config=ContextConfig(**configs.get('base', {})),
            **kwargs
        )


class ContextPresets:
    """Predefined context configurations for common use cases"""
    
    @staticmethod
    def conversational_agent() -> DynamicContextConfig:
        """Configuration for conversational agents with high engagement tracking"""
        return DynamicContextConfig(
            max_context_tokens=3000,
            enable_phase_detection=True,
            enable_engagement_tracking=True,
            enable_topic_tracking=True,
            adapt_context_to_phase=True,
            adapt_context_to_engagement=True
        )
    
    @staticmethod
    def research_assistant() -> RoleBasedContextConfig:
        """Configuration for research-focused agents"""
        return RoleBasedContextConfig(
            max_context_tokens=4000,
            enable_role_adaptation=True,
            enable_domain_expertise_boost=True,
            expertise_context_boost=0.4,
            role_token_multipliers={'research_assistant': 1.3}
        )
    
    @staticmethod
    def code_assistant() -> TaskSpecificContextConfig:
        """Configuration for coding and development tasks"""
        return TaskSpecificContextConfig(
            max_context_tokens=3500,
            enable_task_adaptation=True,
            enable_complexity_scaling=True,
            task_relevance_weight=0.5,
            complexity_token_multipliers={
                'simple': 0.8,
                'moderate': 1.0,
                'complex': 1.4,
                'expert': 1.6
            }
        )
    
    @staticmethod
    def learning_tutor() -> HierarchicalContextConfig:
        """Configuration for educational and tutoring agents"""
        return HierarchicalContextConfig(
            max_context_tokens=3500,
            enable_context_inheritance=True,
            enable_context_cascading=True,
            level_priority_weights={
                'system': 0.9,
                'domain': 0.85,
                'session': 0.8,
                'task': 0.9,
                'interaction': 0.7
            }
        )
    
    @staticmethod
    def minimal_context() -> ContextConfig:
        """Minimal context configuration for simple tasks"""
        return ContextConfig(
            max_context_tokens=1500,
            max_context_items=10,
            context_relevance_threshold=0.8,
            enable_context_ranking=True,
            enable_context_compression=False
        )
    
    @staticmethod
    def comprehensive_context() -> ContextConfig:
        """Comprehensive context configuration for complex tasks"""
        return ContextConfig(
            max_context_tokens=6000,
            max_context_items=30,
            context_relevance_threshold=0.6,
            enable_context_ranking=True,
            enable_context_compression=True,
            compression_ratio=0.4
        )


class ContextAnalyzer:
    """Utility for analyzing and optimizing context usage"""
    
    @staticmethod
    def analyze_context_efficiency(template: BaseContextTemplate) -> Dict[str, Any]:
        """Analyze how efficiently context is being used"""
        stats = template.get_context_stats()
        
        analysis = {
            'total_items': stats['total_items'],
            'estimated_tokens': stats['estimated_tokens'],
            'token_utilization': stats['estimated_tokens'] / stats['config']['max_tokens'],
            'layer_distribution': stats['by_layer'],
            'efficiency_score': 0.0,
            'recommendations': []
        }
        
        # Calculate efficiency score (0-1)
        token_efficiency = min(analysis['token_utilization'], 1.0)
        item_efficiency = min(stats['total_items'] / stats['config']['max_items'], 1.0)
        analysis['efficiency_score'] = (token_efficiency + item_efficiency) / 2
        
        # Generate recommendations
        if analysis['token_utilization'] > 0.9:
            analysis['recommendations'].append("Consider increasing token limit or enabling compression")
        elif analysis['token_utilization'] < 0.3:
            analysis['recommendations'].append("Context underutilized - consider adding more relevant context")
        
        if stats['total_items'] < 5:
            analysis['recommendations'].append("Low context count - consider adding more diverse context sources")
        
        return analysis
    
    @staticmethod
    def suggest_context_improvements(
        template: BaseContextTemplate,
        query_history: List[str] = None
    ) -> List[str]:
        """Suggest improvements to context configuration"""
        suggestions = []
        stats = template.get_context_stats()
        
        # Analyze query patterns if provided
        if query_history:
            query_analysis = ContextAnalyzer._analyze_query_patterns(query_history)
            
            if query_analysis['avg_complexity'] > 0.7:
                suggestions.append("Consider using TaskSpecificContextTemplate for complex queries")
            
            if query_analysis['topic_diversity'] > 0.8:
                suggestions.append("Consider using HierarchicalContextTemplate for diverse topics")
            
            if query_analysis['engagement_indicators'] > 0.6:
                suggestions.append("Consider using DynamicContextTemplate for conversational patterns")
        
        # Analyze current performance
        if stats['estimated_tokens'] > stats['config']['max_tokens'] * 0.8:
            suggestions.append("Increase token limit or enable context compression")
        
        # Check layer balance
        layer_counts = stats['by_layer']
        if layer_counts.get('global', 0) > layer_counts.get('dynamic', 0) * 2:
            suggestions.append("Add more dynamic context for current conversation")
        
        return suggestions
    
    @staticmethod
    def _analyze_query_patterns(queries: List[str]) -> Dict[str, float]:
        """Analyze patterns in user queries"""
        # Simplified analysis - in practice this would be more sophisticated
        total_length = sum(len(q.split()) for q in queries)
        avg_length = total_length / len(queries) if queries else 0
        
        # Count question indicators
        question_count = sum(1 for q in queries if '?' in q or q.lower().startswith(('what', 'how', 'why', 'when', 'where')))
        
        # Count unique words for topic diversity
        all_words = set()
        for query in queries:
            all_words.update(query.lower().split())
        
        return {
            'avg_complexity': min(avg_length / 20, 1.0),  # Normalized by typical length
            'topic_diversity': min(len(all_words) / (total_length or 1), 1.0),
            'engagement_indicators': question_count / len(queries) if queries else 0,
            'query_count': len(queries)
        }


class ContextSerializer:
    """Utility for saving and loading context templates"""
    
    @staticmethod
    def save_context_template(
        template: BaseContextTemplate,
        filepath: Union[str, Path],
        include_context_items: bool = True
    ) -> bool:
        """Save a context template to a file"""
        try:
            data = {
                'template_type': template.__class__.__name__,
                'instruction': template.instruction,
                'config': template.context_config.__dict__,
                'stats': template.get_context_stats(),
                'timestamp': time.time()
            }
            
            if include_context_items:
                # Serialize context items
                context_items = {}
                for layer, items in template._context_layers.items():
                    context_items[layer.value] = [
                        {
                            'content': item.content,
                            'relevance_score': item.relevance_score,
                            'timestamp': item.timestamp,
                            'source': item.source,
                            'metadata': item.metadata,
                            'importance': item.importance
                        }
                        for item in items
                    ]
                data['context_items'] = context_items
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved context template to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save context template: {e}")
            return False
    
    @staticmethod
    def load_context_template(filepath: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Load a context template from a file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Loaded context template from {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load context template: {e}")
            return None


class ContextMetrics:
    """Utility for tracking context template performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'context_retrievals': 0,
            'average_relevance': 0.0,
            'token_usage': [],
            'layer_usage': defaultdict(int),
            'query_patterns': [],
            'performance_history': []
        }
    
    def record_context_retrieval(
        self,
        template: BaseContextTemplate,
        query: str,
        retrieved_items: List[ContextItem],
        response_quality: Optional[float] = None
    ):
        """Record metrics for a context retrieval operation"""
        self.metrics['context_retrievals'] += 1
        
        # Calculate average relevance
        if retrieved_items:
            avg_relevance = sum(item.relevance_score for item in retrieved_items) / len(retrieved_items)
            self.metrics['average_relevance'] = (
                (self.metrics['average_relevance'] * (self.metrics['context_retrievals'] - 1) + avg_relevance) /
                self.metrics['context_retrievals']
            )
        
        # Record token usage
        total_tokens = sum(len(item.content) // 4 for item in retrieved_items)
        self.metrics['token_usage'].append(total_tokens)
        
        # Record layer usage
        for item in retrieved_items:
            self.metrics['layer_usage'][item.layer.value] += 1
        
        # Record query pattern
        self.metrics['query_patterns'].append({
            'query_length': len(query.split()),
            'items_retrieved': len(retrieved_items),
            'timestamp': time.time()
        })
        
        # Record performance
        if response_quality is not None:
            self.metrics['performance_history'].append({
                'relevance': avg_relevance if retrieved_items else 0,
                'quality': response_quality,
                'token_count': total_tokens,
                'timestamp': time.time()
            })
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of context template performance"""
        if not self.metrics['context_retrievals']:
            return {'status': 'no_data', 'message': 'No context retrievals recorded'}
        
        return {
            'total_retrievals': self.metrics['context_retrievals'],
            'average_relevance': self.metrics['average_relevance'],
            'average_tokens': sum(self.metrics['token_usage']) / len(self.metrics['token_usage']),
            'layer_distribution': dict(self.metrics['layer_usage']),
            'performance_trend': self._calculate_performance_trend(),
            'recommendations': self._generate_performance_recommendations()
        }
    
    def _calculate_performance_trend(self) -> str:
        """Calculate whether performance is improving, declining, or stable"""
        if len(self.metrics['performance_history']) < 3:
            return 'insufficient_data'
        
        recent_performance = self.metrics['performance_history'][-5:]
        earlier_performance = self.metrics['performance_history'][-10:-5] if len(self.metrics['performance_history']) >= 10 else []
        
        if not earlier_performance:
            return 'insufficient_data'
        
        recent_avg = sum(p['quality'] for p in recent_performance) / len(recent_performance)
        earlier_avg = sum(p['quality'] for p in earlier_performance) / len(earlier_performance)
        
        if recent_avg > earlier_avg + 0.1:
            return 'improving'
        elif recent_avg < earlier_avg - 0.1:
            return 'declining'
        else:
            return 'stable'
    
    def _generate_performance_recommendations(self) -> List[str]:
        """Generate recommendations based on performance metrics"""
        recommendations = []
        
        if self.metrics['average_relevance'] < 0.6:
            recommendations.append("Consider tuning relevance thresholds")
        
        avg_tokens = sum(self.metrics['token_usage']) / len(self.metrics['token_usage'])
        if avg_tokens > 3000:
            recommendations.append("Context may be too verbose - consider compression")
        elif avg_tokens < 500:
            recommendations.append("Context may be too sparse - consider adding more sources")
        
        # Check layer balance
        layer_counts = self.metrics['layer_usage']
        total_usage = sum(layer_counts.values())
        
        if total_usage > 0:
            global_ratio = layer_counts.get('global', 0) / total_usage
            dynamic_ratio = layer_counts.get('dynamic', 0) / total_usage
            
            if global_ratio > 0.7:
                recommendations.append("Consider adding more dynamic context")
            elif dynamic_ratio > 0.7:
                recommendations.append("Consider adding more persistent context")
        
        return recommendations


# Convenience functions
def create_conversational_agent(instruction: str, **kwargs) -> DynamicContextTemplate:
    """Quick factory function for conversational agents"""
    return ContextTemplateFactory.create_dynamic_template(
        instruction=instruction,
        config=ContextPresets.conversational_agent(),
        **kwargs
    )


def create_code_assistant(instruction: str, **kwargs) -> TaskSpecificContextTemplate:
    """Quick factory function for code assistants"""
    return ContextTemplateFactory.create_task_specific_template(
        instruction=instruction,
        task_type=TaskType.CODE_GENERATION,
        complexity=TaskComplexity.MODERATE,
        domain=TaskDomain.SOFTWARE_ENGINEERING,
        config=ContextPresets.code_assistant(),
        **kwargs
    )


def create_research_assistant(instruction: str, **kwargs) -> RoleBasedContextTemplate:
    """Quick factory function for research assistants"""
    return ContextTemplateFactory.create_role_based_template(
        instruction=instruction,
        role=AgentRole.RESEARCH_ASSISTANT,
        expertise_domains=[ExpertiseDomain.SCIENCE],
        interaction_style=InteractionStyle.FORMAL,
        config=ContextPresets.research_assistant(),
        **kwargs
    )


def analyze_template_performance(template: BaseContextTemplate) -> Dict[str, Any]:
    """Quick function to analyze template performance"""
    analyzer = ContextAnalyzer()
    return analyzer.analyze_context_efficiency(template)