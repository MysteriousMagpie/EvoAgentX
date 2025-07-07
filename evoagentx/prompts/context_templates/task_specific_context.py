"""
Task-Specific Context Template

Provides context templates optimized for specific task types and domains.
This template adapts context selection based on the type of task being performed,
ensuring that the most relevant knowledge and examples are prioritized.

Task Categories:
- Code Generation: Programming, debugging, code review
- Data Analysis: Statistics, visualization, insights
- Research: Information gathering, synthesis, citations
- Creative Writing: Storytelling, content creation, ideation
- Problem Solving: Troubleshooting, debugging, solutions
- Planning: Project management, strategy, organization
- Learning: Education, explanations, tutorials
"""

from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import re
from collections import defaultdict, Counter

from .base_context_template import BaseContextTemplate, ContextItem, ContextLayer, ContextConfig
from ...core.logging import logger


class TaskType(Enum):
    """Different types of tasks with specific context needs"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DEBUGGING = "debugging"
    DATA_ANALYSIS = "data_analysis"
    RESEARCH = "research"
    CREATIVE_WRITING = "creative_writing"
    PROBLEM_SOLVING = "problem_solving"
    PLANNING = "planning"
    LEARNING = "learning"
    EXPLANATION = "explanation"
    COMPARISON = "comparison"
    SYNTHESIS = "synthesis"
    OPTIMIZATION = "optimization"
    DESIGN = "design"


class TaskComplexity(Enum):
    """Task complexity levels"""
    SIMPLE = "simple"        # Basic, straightforward tasks
    MODERATE = "moderate"    # Standard complexity
    COMPLEX = "complex"      # Multi-step, intricate tasks
    EXPERT = "expert"        # Highly specialized tasks


class TaskDomain(Enum):
    """Specific domains for task specialization"""
    SOFTWARE_ENGINEERING = "software_engineering"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "machine_learning"
    WEB_DEVELOPMENT = "web_development"
    SYSTEMS_ADMINISTRATION = "systems_administration"
    ACADEMIC_RESEARCH = "academic_research"
    BUSINESS_ANALYSIS = "business_analysis"
    CREATIVE_ARTS = "creative_arts"
    EDUCATION = "education"
    TECHNICAL_WRITING = "technical_writing"


@dataclass
class TaskProfile:
    """Profile defining a specific task and its requirements"""
    task_type: TaskType
    complexity: TaskComplexity
    domain: TaskDomain
    
    # Task characteristics
    requires_examples: bool = True
    requires_step_by_step: bool = False
    requires_background_theory: bool = False
    requires_best_practices: bool = True
    requires_error_handling: bool = False
    
    # Context preferences
    preferred_context_length: str = "medium"  # short, medium, long, comprehensive
    technical_depth: str = "medium"  # basic, medium, advanced, expert
    
    # Task-specific metadata
    expected_output_type: str = "text"
    interaction_pattern: str = "single_response"  # single_response, iterative, collaborative
    
    # Keywords and patterns
    key_concepts: Set[str] = field(default_factory=set)
    relevant_technologies: Set[str] = field(default_factory=set)
    common_patterns: List[str] = field(default_factory=list)


@dataclass
class TaskSpecificContextConfig(ContextConfig):
    """Configuration for task-specific context behavior"""
    # Task adaptation settings
    enable_task_adaptation: bool = True
    enable_complexity_scaling: bool = True
    enable_domain_specialization: bool = True
    
    # Context selection weights
    task_relevance_weight: float = 0.4
    complexity_weight: float = 0.2
    domain_weight: float = 0.3
    recency_weight: float = 0.1
    
    # Task-specific limits
    complexity_token_multipliers: Dict[str, float] = field(default_factory=lambda: {
        'simple': 0.7,      # Less context for simple tasks
        'moderate': 1.0,    # Standard context
        'complex': 1.3,     # More context for complex tasks
        'expert': 1.5       # Maximum context for expert tasks
    })
    
    # Domain specialization
    domain_context_boost: float = 0.3
    cross_domain_penalty: float = 0.1


class TaskSpecificContextTemplate(BaseContextTemplate):
    """
    Task-specific context template for optimized task performance.
    
    Features:
    - Task-type specific context filtering and prioritization
    - Complexity-based context scaling
    - Domain specialization with cross-domain knowledge
    - Context patterns matched to task requirements
    - Dynamic task classification and adaptation
    """
    
    def __init__(
        self,
        instruction: str,
        task_profile: TaskProfile,
        context_config: Optional[TaskSpecificContextConfig] = None,
        **kwargs
    ):
        if context_config is None:
            context_config = TaskSpecificContextConfig()
        
        super().__init__(instruction=instruction, context_config=context_config, **kwargs)
        
        self.task_profile = task_profile
        
        # Task classification patterns
        self._task_classification_patterns: Dict[TaskType, List[str]] = {}
        self._setup_task_patterns()
        
        # Task-specific context processors
        self._task_processors: Dict[TaskType, Callable] = {}
        self._complexity_processors: Dict[TaskComplexity, Callable] = {}
        self._domain_processors: Dict[TaskDomain, Callable] = {}
        
        # Context templates for each task type
        self._task_context_templates: Dict[TaskType, Dict[str, Any]] = {}
        self._setup_task_templates()
        
        # Initialize task-specific processing
        self._setup_task_processing()
        
        # Task execution state
        self.current_subtasks: List[str] = []
        self.completed_steps: List[str] = []
        self.task_progress: float = 0.0
    
    def _setup_task_patterns(self):
        """Setup patterns for automatic task type classification"""
        self._task_classification_patterns = {
            TaskType.CODE_GENERATION: [
                r'\b(write|create|implement|build|develop|code|program)\b.*\b(function|class|method|algorithm|script|application)\b',
                r'\b(generate|produce).*code\b',
                r'\bimplement.*\b(in|using|with)\s+(python|javascript|java|c\+\+|go|rust)\b'
            ],
            TaskType.CODE_REVIEW: [
                r'\b(review|check|analyze|examine|evaluate).*code\b',
                r'\b(find|identify).*\b(bugs|errors|issues|problems)\b',
                r'\bcode.*\b(quality|standards|best practices)\b'
            ],
            TaskType.DEBUGGING: [
                r'\b(debug|fix|solve|troubleshoot)\b',
                r'\b(error|bug|issue|problem).*\b(fix|solve|resolve)\b',
                r'\b(not working|broken|failing)\b'
            ],
            TaskType.DATA_ANALYSIS: [
                r'\b(analyze|examine|study).*data\b',
                r'\b(statistics|statistical|correlation|regression)\b',
                r'\b(dataset|dataframe|csv|excel)\b.*\b(analyze|process)\b'
            ],
            TaskType.RESEARCH: [
                r'\b(research|investigate|study|explore)\b',
                r'\b(find|gather|collect).*\b(information|sources|evidence)\b',
                r'\b(literature|academic|scholarly).*\b(review|search)\b'
            ],
            TaskType.CREATIVE_WRITING: [
                r'\b(write|create|compose).*\b(story|article|blog|content)\b',
                r'\b(creative|imaginative|original)\b.*writing\b',
                r'\b(brainstorm|ideate|generate).*\b(ideas|concepts)\b'
            ],
            TaskType.PROBLEM_SOLVING: [
                r'\b(solve|resolve|address).*problem\b',
                r'\b(how to|way to|method to|approach to)\b',
                r'\b(solution|answer|resolution)\b'
            ],
            TaskType.PLANNING: [
                r'\b(plan|organize|schedule|structure)\b',
                r'\b(strategy|roadmap|timeline|milestone)\b',
                r'\b(project.*management|task.*planning)\b'
            ],
            TaskType.LEARNING: [
                r'\b(learn|understand|study|master)\b',
                r'\b(teach|explain|show|demonstrate)\b.*\b(how to|what is|why)\b',
                r'\b(tutorial|guide|lesson|course)\b'
            ],
            TaskType.EXPLANATION: [
                r'\b(explain|describe|clarify|elaborate)\b',
                r'\b(what is|what are|how does|why does)\b',
                r'\b(definition|meaning|concept)\b'
            ]
        }
    
    def _setup_task_templates(self):
        """Setup context templates for each task type"""
        self._task_context_templates = {
            TaskType.CODE_GENERATION: {
                'required_context_types': ['examples', 'best_practices', 'syntax', 'patterns'],
                'preferred_layers': [ContextLayer.TASK, ContextLayer.GLOBAL],
                'context_organization': 'technical',
                'include_error_handling': True,
                'include_documentation': True
            },
            TaskType.CODE_REVIEW: {
                'required_context_types': ['standards', 'best_practices', 'common_issues', 'patterns'],
                'preferred_layers': [ContextLayer.GLOBAL, ContextLayer.SESSION],
                'context_organization': 'analytical',
                'include_checklists': True,
                'include_metrics': True
            },
            TaskType.DEBUGGING: {
                'required_context_types': ['error_patterns', 'solutions', 'troubleshooting', 'tools'],
                'preferred_layers': [ContextLayer.DYNAMIC, ContextLayer.TASK],
                'context_organization': 'problem_solving',
                'include_step_by_step': True,
                'include_diagnostics': True
            },
            TaskType.DATA_ANALYSIS: {
                'required_context_types': ['methods', 'tools', 'examples', 'interpretation'],
                'preferred_layers': [ContextLayer.TASK, ContextLayer.GLOBAL],
                'context_organization': 'analytical',
                'include_statistical_background': True,
                'include_visualization': True
            },
            TaskType.RESEARCH: {
                'required_context_types': ['sources', 'methods', 'criteria', 'synthesis'],
                'preferred_layers': [ContextLayer.SESSION, ContextLayer.GLOBAL],
                'context_organization': 'academic',
                'include_citations': True,
                'include_evaluation_criteria': True
            },
            TaskType.CREATIVE_WRITING: {
                'required_context_types': ['inspiration', 'techniques', 'examples', 'structure'],
                'preferred_layers': [ContextLayer.SESSION, ContextLayer.TASK],
                'context_organization': 'creative',
                'include_style_guides': True,
                'include_brainstorming': True
            },
            TaskType.PROBLEM_SOLVING: {
                'required_context_types': ['approaches', 'examples', 'frameworks', 'tools'],
                'preferred_layers': [ContextLayer.TASK, ContextLayer.DYNAMIC],
                'context_organization': 'systematic',
                'include_step_by_step': True,
                'include_alternatives': True
            },
            TaskType.PLANNING: {
                'required_context_types': ['frameworks', 'templates', 'examples', 'best_practices'],
                'preferred_layers': [ContextLayer.GLOBAL, ContextLayer.TASK],
                'context_organization': 'structured',
                'include_timelines': True,
                'include_dependencies': True
            },
            TaskType.LEARNING: {
                'required_context_types': ['fundamentals', 'examples', 'exercises', 'progression'],
                'preferred_layers': [ContextLayer.GLOBAL, ContextLayer.SESSION],
                'context_organization': 'educational',
                'include_prerequisites': True,
                'include_practice': True
            },
            TaskType.EXPLANATION: {
                'required_context_types': ['definitions', 'examples', 'analogies', 'context'],
                'preferred_layers': [ContextLayer.GLOBAL, ContextLayer.SESSION],
                'context_organization': 'explanatory',
                'include_multiple_perspectives': True,
                'include_clarifications': True
            }
        }
    
    def _setup_task_processing(self):
        """Setup task-specific processing functions"""
        self._task_processors.update({
            TaskType.CODE_GENERATION: self._process_code_generation_context,
            TaskType.CODE_REVIEW: self._process_code_review_context,
            TaskType.DEBUGGING: self._process_debugging_context,
            TaskType.DATA_ANALYSIS: self._process_data_analysis_context,
            TaskType.RESEARCH: self._process_research_context,
            TaskType.CREATIVE_WRITING: self._process_creative_writing_context,
            TaskType.PROBLEM_SOLVING: self._process_problem_solving_context,
            TaskType.PLANNING: self._process_planning_context,
            TaskType.LEARNING: self._process_learning_context,
            TaskType.EXPLANATION: self._process_explanation_context
        })
        
        self._complexity_processors.update({
            TaskComplexity.SIMPLE: self._process_simple_complexity,
            TaskComplexity.MODERATE: self._process_moderate_complexity,
            TaskComplexity.COMPLEX: self._process_complex_complexity,
            TaskComplexity.EXPERT: self._process_expert_complexity
        })
        
        self._domain_processors.update({
            TaskDomain.SOFTWARE_ENGINEERING: self._process_software_domain,
            TaskDomain.DATA_SCIENCE: self._process_data_science_domain,
            TaskDomain.MACHINE_LEARNING: self._process_ml_domain,
            TaskDomain.WEB_DEVELOPMENT: self._process_web_dev_domain
        })
    
    def classify_task_from_query(self, query: str) -> Tuple[TaskType, float]:
        """
        Automatically classify task type from user query.
        
        Args:
            query: User's query or instruction
            
        Returns:
            Tuple of (predicted_task_type, confidence_score)
        """
        query_lower = query.lower()
        task_scores = {}
        
        for task_type, patterns in self._task_classification_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower))
                score += matches
            
            if score > 0:
                task_scores[task_type] = score
        
        if not task_scores:
            return TaskType.PROBLEM_SOLVING, 0.3  # Default fallback
        
        best_task = max(task_scores.keys(), key=lambda t: task_scores[t])
        max_score = task_scores[best_task]
        
        # Normalize confidence (rough heuristic)
        confidence = min(max_score / 3.0, 1.0)
        
        return best_task, confidence
    
    def add_task_context(
        self,
        content: str,
        context_type: str,
        task_relevance: float = 1.0,
        complexity_level: Optional[TaskComplexity] = None,
        domain_specific: bool = False,
        **kwargs
    ) -> ContextItem:
        """
        Add context specifically optimized for the current task.
        
        Args:
            content: Context content
            context_type: Type of context (e.g., 'example', 'best_practice', 'tool')
            task_relevance: How relevant this is to the current task type
            complexity_level: Complexity level this context is appropriate for
            domain_specific: Whether this is domain-specific context
            **kwargs: Additional context item parameters
        
        Returns:
            Created context item with task-specific processing applied
        """
        # Determine layer based on task template
        layer = self._determine_task_context_layer(context_type)
        
        # Create context item
        context_item = self.add_context(
            content=content,
            layer=layer,
            relevance_score=task_relevance,
            source=f"task_{self.task_profile.task_type.value}",
            metadata={
                'context_type': context_type,
                'task_type': self.task_profile.task_type.value,
                'complexity_level': complexity_level.value if complexity_level else None,
                'domain_specific': domain_specific,
                'task_relevance': task_relevance,
                **kwargs.get('metadata', {})
            },
            **{k: v for k, v in kwargs.items() if k != 'metadata'}
        )
        
        # Apply task-specific processing
        self._apply_task_processing(context_item, context_type)
        
        return context_item
    
    def get_relevant_context(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        include_layers: Optional[List[ContextLayer]] = None
    ) -> List[ContextItem]:
        """
        Get context optimized for the current task type and complexity.
        
        Overrides base method to apply task-specific optimization.
        """
        # Apply complexity-based token scaling
        if max_tokens:
            complexity_multiplier = self.context_config.complexity_token_multipliers.get(
                self.task_profile.complexity.value, 1.0
            )
            max_tokens = int(max_tokens * complexity_multiplier)
        
        # Get base context
        base_context = super().get_relevant_context(query, max_tokens, include_layers)
        
        # Apply task-specific filtering and boosting
        if self.context_config.enable_task_adaptation:
            base_context = self._apply_task_filtering(base_context)
            base_context = self._apply_task_boosting(base_context, query)
        
        # Apply complexity scaling
        if self.context_config.enable_complexity_scaling:
            base_context = self._apply_complexity_scaling(base_context)
        
        # Apply domain specialization
        if self.context_config.enable_domain_specialization:
            base_context = self._apply_domain_specialization(base_context)
        
        # Organize context according to task requirements
        base_context = self._organize_task_context(base_context)
        
        return base_context
    
    def _determine_task_context_layer(self, context_type: str) -> ContextLayer:
        """Determine appropriate context layer based on task template"""
        task_template = self._task_context_templates.get(self.task_profile.task_type, {})
        preferred_layers = task_template.get('preferred_layers', [ContextLayer.SESSION])
        
        # Context type to layer mapping
        type_layer_mapping = {
            'example': ContextLayer.SESSION,
            'best_practice': ContextLayer.GLOBAL,
            'tool': ContextLayer.GLOBAL,
            'current_step': ContextLayer.TASK,
            'immediate': ContextLayer.DYNAMIC,
            'background': ContextLayer.GLOBAL
        }
        
        suggested_layer = type_layer_mapping.get(context_type, ContextLayer.SESSION)
        
        # Use suggested layer if it's in preferred layers, otherwise use first preferred
        return suggested_layer if suggested_layer in preferred_layers else preferred_layers[0]
    
    def _apply_task_processing(self, context_item: ContextItem, context_type: str):
        """Apply task-specific processing to context items"""
        # Apply task type processor
        if self.task_profile.task_type in self._task_processors:
            self._task_processors[self.task_profile.task_type](context_item, context_type)
        
        # Apply complexity processor
        if self.task_profile.complexity in self._complexity_processors:
            self._complexity_processors[self.task_profile.complexity](context_item, context_type)
        
        # Apply domain processor
        if self.task_profile.domain in self._domain_processors:
            self._domain_processors[self.task_profile.domain](context_item, context_type)
    
    def _apply_task_filtering(self, context_items: List[ContextItem]) -> List[ContextItem]:
        """Apply task-specific context filtering"""
        task_template = self._task_context_templates.get(self.task_profile.task_type, {})
        required_types = set(task_template.get('required_context_types', []))
        
        if not required_types:
            return context_items
        
        # Prioritize required context types for this task
        filtered_items = []
        for item in context_items:
            context_type = item.metadata.get('context_type', 'general')
            task_relevance = item.metadata.get('task_relevance', 0.5)
            
            # Include high relevance items or items of required types
            if context_type in required_types or item.relevance_score >= 0.7 or task_relevance >= 0.8:
                # Boost required types
                if context_type in required_types:
                    item.relevance_score = min(item.relevance_score + 0.25, 1.0)
                filtered_items.append(item)
        
        return filtered_items
    
    def _apply_task_boosting(self, context_items: List[ContextItem], query: Optional[str] = None) -> List[ContextItem]:
        """Apply task-specific relevance boosting"""
        # Boost items that mention task-relevant concepts
        task_keywords = set()
        task_keywords.update(self.task_profile.key_concepts)
        task_keywords.update(self.task_profile.relevant_technologies)
        
        for item in context_items:
            content_lower = item.content.lower()
            
            # Count keyword matches
            keyword_matches = sum(1 for keyword in task_keywords if keyword in content_lower)
            
            if keyword_matches > 0:
                boost = min(keyword_matches * 0.1, 0.3)
                item.relevance_score = min(item.relevance_score + boost, 1.0)
                item.metadata['task_keyword_matches'] = keyword_matches
        
        # Boost based on task type match
        for item in context_items:
            item_task_type = item.metadata.get('task_type')
            if item_task_type == self.task_profile.task_type.value:
                item.relevance_score = min(item.relevance_score + 0.2, 1.0)
        
        return context_items
    
    def _apply_complexity_scaling(self, context_items: List[ContextItem]) -> List[ContextItem]:
        """Scale context based on task complexity"""
        complexity_level = self.task_profile.complexity
        
        for item in context_items:
            item_complexity = item.metadata.get('complexity_level')
            
            if item_complexity:
                # Boost items matching current complexity level
                if item_complexity == complexity_level.value:
                    item.relevance_score = min(item.relevance_score + 0.15, 1.0)
                # Penalize items that are too complex or too simple
                elif (complexity_level == TaskComplexity.SIMPLE and item_complexity in ['complex', 'expert']) or \
                     (complexity_level == TaskComplexity.EXPERT and item_complexity == 'simple'):
                    item.relevance_score = max(item.relevance_score - 0.1, 0.0)
        
        return context_items
    
    def _apply_domain_specialization(self, context_items: List[ContextItem]) -> List[ContextItem]:
        """Apply domain-specific context adjustments"""
        current_domain = self.task_profile.domain
        
        for item in context_items:
            if item.metadata.get('domain_specific'):
                item_domain = item.metadata.get('domain')
                
                if item_domain == current_domain.value:
                    # Boost domain-matching items
                    item.relevance_score = min(
                        item.relevance_score + self.context_config.domain_context_boost, 1.0
                    )
                elif item_domain and item_domain != current_domain.value:
                    # Small penalty for cross-domain items
                    item.relevance_score = max(
                        item.relevance_score - self.context_config.cross_domain_penalty, 0.0
                    )
        
        return context_items
    
    def _organize_task_context(self, context_items: List[ContextItem]) -> List[ContextItem]:
        """Organize context according to task requirements"""
        task_template = self._task_context_templates.get(self.task_profile.task_type, {})
        organization_style = task_template.get('context_organization', 'default')
        
        if organization_style == 'technical':
            # Prioritize: examples, best practices, syntax, error handling
            priority_order = ['example', 'best_practice', 'syntax', 'error_handling', 'documentation']
        elif organization_style == 'analytical':
            # Prioritize: methods, standards, metrics, analysis
            priority_order = ['method', 'standard', 'metric', 'analysis', 'checklist']
        elif organization_style == 'problem_solving':
            # Prioritize: diagnostics, solutions, step-by-step, alternatives
            priority_order = ['diagnostic', 'solution', 'step_by_step', 'alternative', 'tool']
        elif organization_style == 'educational':
            # Prioritize: fundamentals, examples, progression, practice
            priority_order = ['fundamental', 'example', 'progression', 'practice', 'exercise']
        else:
            return context_items  # No special organization
        
        # Sort items by priority order
        def get_priority(item: ContextItem) -> int:
            context_type = item.metadata.get('context_type', 'general')
            try:
                return priority_order.index(context_type)
            except ValueError:
                return len(priority_order)  # Unknown types go last
        
        return sorted(context_items, key=lambda item: (
            get_priority(item),
            -item.get_weighted_relevance(self.context_config.context_decay_factor)
        ))
    
    # Task-specific processing methods
    def _process_code_generation_context(self, item: ContextItem, context_type: str):
        """Process context for code generation tasks"""
        if context_type in ['example', 'template', 'pattern']:
            item.importance = min(item.importance + 0.3, 1.0)
        
        item.metadata['requires_syntax_highlighting'] = True
        
        if 'error' in item.content.lower():
            item.metadata['includes_error_handling'] = True
    
    def _process_code_review_context(self, item: ContextItem, context_type: str):
        """Process context for code review tasks"""
        if context_type in ['standard', 'best_practice', 'checklist']:
            item.importance = min(item.importance + 0.25, 1.0)
        
        item.metadata['review_focus'] = True
    
    def _process_debugging_context(self, item: ContextItem, context_type: str):
        """Process context for debugging tasks"""
        if context_type in ['error_pattern', 'solution', 'diagnostic']:
            item.importance = min(item.importance + 0.35, 1.0)
        
        item.metadata['debugging_relevant'] = True
    
    def _process_data_analysis_context(self, item: ContextItem, context_type: str):
        """Process context for data analysis tasks"""
        if context_type in ['method', 'tool', 'visualization']:
            item.importance = min(item.importance + 0.25, 1.0)
        
        item.metadata['analytical'] = True
    
    def _process_research_context(self, item: ContextItem, context_type: str):
        """Process context for research tasks"""
        if context_type in ['source', 'method', 'citation']:
            item.importance = min(item.importance + 0.2, 1.0)
        
        item.metadata['research_quality'] = True
    
    def _process_creative_writing_context(self, item: ContextItem, context_type: str):
        """Process context for creative writing tasks"""
        if context_type in ['inspiration', 'technique', 'style']:
            item.importance = min(item.importance + 0.2, 1.0)
        
        item.metadata['creative'] = True
    
    def _process_problem_solving_context(self, item: ContextItem, context_type: str):
        """Process context for problem solving tasks"""
        if context_type in ['approach', 'framework', 'solution']:
            item.importance = min(item.importance + 0.3, 1.0)
        
        item.metadata['solution_oriented'] = True
    
    def _process_planning_context(self, item: ContextItem, context_type: str):
        """Process context for planning tasks"""
        if context_type in ['framework', 'template', 'timeline']:
            item.importance = min(item.importance + 0.25, 1.0)
        
        item.metadata['planning_relevant'] = True
    
    def _process_learning_context(self, item: ContextItem, context_type: str):
        """Process context for learning tasks"""
        if context_type in ['fundamental', 'progression', 'exercise']:
            item.importance = min(item.importance + 0.3, 1.0)
        
        item.metadata['educational'] = True
    
    def _process_explanation_context(self, item: ContextItem, context_type: str):
        """Process context for explanation tasks"""
        if context_type in ['definition', 'example', 'analogy']:
            item.importance = min(item.importance + 0.25, 1.0)
        
        item.metadata['explanatory'] = True
    
    # Complexity processing methods
    def _process_simple_complexity(self, item: ContextItem, context_type: str):
        """Process context for simple complexity tasks"""
        item.metadata['complexity_simple'] = True
        # Prefer shorter, more direct content
        if len(item.content) > 500:
            item.relevance_score = max(item.relevance_score - 0.1, 0.0)
    
    def _process_moderate_complexity(self, item: ContextItem, context_type: str):
        """Process context for moderate complexity tasks"""
        item.metadata['complexity_moderate'] = True
    
    def _process_complex_complexity(self, item: ContextItem, context_type: str):
        """Process context for complex tasks"""
        item.metadata['complexity_complex'] = True
        # Boost comprehensive content
        if len(item.content) > 1000:
            item.relevance_score = min(item.relevance_score + 0.1, 1.0)
    
    def _process_expert_complexity(self, item: ContextItem, context_type: str):
        """Process context for expert-level tasks"""
        item.metadata['complexity_expert'] = True
        item.importance = min(item.importance + 0.2, 1.0)
    
    # Domain processing methods
    def _process_software_domain(self, item: ContextItem, context_type: str):
        """Process context for software engineering domain"""
        item.metadata['domain'] = 'software_engineering'
        if any(keyword in item.content.lower() for keyword in ['architecture', 'design pattern', 'testing']):
            item.relevance_score = min(item.relevance_score + 0.15, 1.0)
    
    def _process_data_science_domain(self, item: ContextItem, context_type: str):
        """Process context for data science domain"""
        item.metadata['domain'] = 'data_science'
        if any(keyword in item.content.lower() for keyword in ['pandas', 'numpy', 'analysis', 'visualization']):
            item.relevance_score = min(item.relevance_score + 0.15, 1.0)
    
    def _process_ml_domain(self, item: ContextItem, context_type: str):
        """Process context for machine learning domain"""
        item.metadata['domain'] = 'machine_learning'
        if any(keyword in item.content.lower() for keyword in ['model', 'training', 'prediction', 'algorithm']):
            item.relevance_score = min(item.relevance_score + 0.15, 1.0)
    
    def _process_web_dev_domain(self, item: ContextItem, context_type: str):
        """Process context for web development domain"""
        item.metadata['domain'] = 'web_development'
        if any(keyword in item.content.lower() for keyword in ['html', 'css', 'javascript', 'frontend', 'backend']):
            item.relevance_score = min(item.relevance_score + 0.15, 1.0)
    
    def update_task_progress(self, step: str, completed: bool = True):
        """Update task execution progress"""
        if completed:
            self.completed_steps.append(step)
            self.task_progress = len(self.completed_steps) / max(len(self.current_subtasks), 1)
        else:
            if step not in self.current_subtasks:
                self.current_subtasks.append(step)
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Get statistics about task-specific context usage"""
        stats = {
            'task_type': self.task_profile.task_type.value,
            'complexity': self.task_profile.complexity.value,
            'domain': self.task_profile.domain.value,
            'progress': self.task_progress,
            'completed_steps': len(self.completed_steps),
            'current_subtasks': len(self.current_subtasks),
            'context_stats': self.get_context_stats()
        }
        
        # Count context by task relevance
        high_relevance_count = sum(
            1 for layer in self._context_layers.values()
            for item in layer
            if item.metadata.get('task_relevance', 0) >= 0.8
        )
        
        stats['high_task_relevance_items'] = high_relevance_count
        
        return stats