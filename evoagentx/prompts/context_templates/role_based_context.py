"""
Role-Based Context Template

Provides context templates specialized for different agent roles and personas.
This template adapts context selection and presentation based on the agent's
role, expertise domain, and interaction style.

Agent Roles:
- Research Assistant: Academic, analytical, evidence-based
- Code Assistant: Technical, practical, solution-oriented  
- Creative Assistant: Imaginative, exploratory, inspirational
- Planning Assistant: Organized, strategic, goal-oriented
- Teaching Assistant: Educational, patient, step-by-step
- Support Assistant: Helpful, empathetic, problem-solving
"""

from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import time

from .base_context_template import BaseContextTemplate, ContextItem, ContextLayer, ContextConfig
from ...core.logging import logger


class AgentRole(Enum):
    """Different agent roles with distinct context needs"""
    RESEARCH_ASSISTANT = "research_assistant"
    CODE_ASSISTANT = "code_assistant"
    CREATIVE_ASSISTANT = "creative_assistant"
    PLANNING_ASSISTANT = "planning_assistant"
    TEACHING_ASSISTANT = "teaching_assistant"
    SUPPORT_ASSISTANT = "support_assistant"
    ANALYST = "analyst"
    CONSULTANT = "consultant"
    GENERAL_ASSISTANT = "general_assistant"


class ExpertiseDomain(Enum):
    """Domain expertise areas"""
    TECHNOLOGY = "technology"
    SCIENCE = "science"
    BUSINESS = "business"
    EDUCATION = "education"
    CREATIVE_ARTS = "creative_arts"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    LEGAL = "legal"
    ENGINEERING = "engineering"
    GENERAL = "general"


class InteractionStyle(Enum):
    """Different interaction styles"""
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    EDUCATIONAL = "educational"
    CONVERSATIONAL = "conversational"
    PROFESSIONAL = "professional"


@dataclass
class RoleProfile:
    """Profile defining a specific agent role"""
    role: AgentRole
    expertise_domains: List[ExpertiseDomain]
    interaction_style: InteractionStyle
    primary_capabilities: List[str]
    context_preferences: Dict[str, Any] = field(default_factory=dict)
    response_patterns: List[str] = field(default_factory=list)
    
    # Context filtering preferences
    preferred_context_types: Set[str] = field(default_factory=set)
    avoided_context_types: Set[str] = field(default_factory=set)
    
    # Role-specific metadata
    formality_level: float = 0.5  # 0.0 = very casual, 1.0 = very formal
    detail_preference: float = 0.5  # 0.0 = brief, 1.0 = comprehensive
    creativity_factor: float = 0.5  # 0.0 = conservative, 1.0 = highly creative


@dataclass
class RoleBasedContextConfig(ContextConfig):
    """Configuration for role-based context behavior"""
    # Role adaptation settings
    enable_role_adaptation: bool = True
    enable_domain_expertise_boost: bool = True
    enable_style_adaptation: bool = True
    
    # Context filtering by role
    role_context_filtering: bool = True
    expertise_context_boost: float = 0.3
    
    # Role-specific limits
    role_token_multipliers: Dict[str, float] = field(default_factory=lambda: {
        'research_assistant': 1.2,    # More context for research
        'code_assistant': 1.0,        # Standard context
        'creative_assistant': 0.8,    # Less structured context
        'planning_assistant': 1.1,    # Slightly more context
        'teaching_assistant': 1.3,    # More explanatory context
        'support_assistant': 0.9      # Focused, helpful context
    })


class RoleBasedContextTemplate(BaseContextTemplate):
    """
    Role-based context template for specialized agent personas.
    
    Features:
    - Role-specific context filtering and boosting
    - Domain expertise context enhancement
    - Interaction style adaptation
    - Context presentation tailored to role requirements
    - Dynamic role switching capabilities
    """
    
    def __init__(
        self,
        instruction: str,
        role_profile: RoleProfile,
        context_config: Optional[RoleBasedContextConfig] = None,
        **kwargs
    ):
        if context_config is None:
            context_config = RoleBasedContextConfig()
        
        super().__init__(instruction=instruction, context_config=context_config, **kwargs)
        
        self.role_profile = role_profile
        
        # Role-specific context processors
        self._role_processors: Dict[AgentRole, Callable] = {}
        self._domain_processors: Dict[ExpertiseDomain, Callable] = {}
        self._style_processors: Dict[InteractionStyle, Callable] = {}
        
        # Context filtering rules
        self._setup_role_filters()
        
        # Role-specific context patterns
        self._setup_role_patterns()
        
        # Initialize role-specific processing
        self._setup_role_processing()
    
    def _setup_role_filters(self):
        """Setup context filtering rules for different roles"""
        self.role_context_filters = {
            AgentRole.RESEARCH_ASSISTANT: {
                'preferred_types': {'evidence', 'data', 'citations', 'methodology', 'analysis'},
                'boosted_keywords': {'research', 'study', 'evidence', 'data', 'analysis', 'findings'},
                'context_style': 'academic',
                'formality_boost': 0.2
            },
            AgentRole.CODE_ASSISTANT: {
                'preferred_types': {'code', 'technical', 'documentation', 'examples', 'best_practices'},
                'boosted_keywords': {'function', 'class', 'method', 'algorithm', 'implementation'},
                'context_style': 'technical',
                'detail_boost': 0.3
            },
            AgentRole.CREATIVE_ASSISTANT: {
                'preferred_types': {'inspiration', 'examples', 'brainstorming', 'alternatives'},
                'boosted_keywords': {'creative', 'innovative', 'unique', 'original', 'artistic'},
                'context_style': 'inspirational',
                'creativity_boost': 0.4
            },
            AgentRole.PLANNING_ASSISTANT: {
                'preferred_types': {'strategy', 'timeline', 'resources', 'objectives', 'milestones'},
                'boosted_keywords': {'plan', 'strategy', 'goal', 'objective', 'timeline', 'steps'},
                'context_style': 'structured',
                'organization_boost': 0.3
            },
            AgentRole.TEACHING_ASSISTANT: {
                'preferred_types': {'explanations', 'examples', 'fundamentals', 'step_by_step'},
                'boosted_keywords': {'explain', 'understand', 'learn', 'concept', 'example'},
                'context_style': 'educational',
                'clarity_boost': 0.4
            },
            AgentRole.SUPPORT_ASSISTANT: {
                'preferred_types': {'solutions', 'troubleshooting', 'guidance', 'help'},
                'boosted_keywords': {'help', 'solve', 'fix', 'support', 'assistance', 'guidance'},
                'context_style': 'helpful',
                'empathy_boost': 0.2
            }
        }
    
    def _setup_role_patterns(self):
        """Setup context patterns specific to each role"""
        self.role_context_patterns = {
            AgentRole.RESEARCH_ASSISTANT: [
                "Based on research findings...",
                "Evidence suggests...", 
                "Studies indicate...",
                "Data analysis reveals..."
            ],
            AgentRole.CODE_ASSISTANT: [
                "Here's the implementation...",
                "The code structure should...",
                "Best practice is to...",
                "This function handles..."
            ],
            AgentRole.CREATIVE_ASSISTANT: [
                "Imagine if we...",
                "An innovative approach could be...",
                "Creative possibilities include...",
                "Thinking outside the box..."
            ],
            AgentRole.PLANNING_ASSISTANT: [
                "The strategic approach is...",
                "Breaking this down into steps...",
                "The timeline should include...",
                "Key milestones are..."
            ],
            AgentRole.TEACHING_ASSISTANT: [
                "Let me explain this step by step...",
                "The fundamental concept is...",
                "To understand this, consider...",
                "A helpful example is..."
            ],
            AgentRole.SUPPORT_ASSISTANT: [
                "I'm here to help you...",
                "Let's solve this together...",
                "The solution is...",
                "I understand your concern..."
            ]
        }
    
    def _setup_role_processing(self):
        """Setup role-specific context processing functions"""
        self._role_processors.update({
            AgentRole.RESEARCH_ASSISTANT: self._process_research_context,
            AgentRole.CODE_ASSISTANT: self._process_code_context,
            AgentRole.CREATIVE_ASSISTANT: self._process_creative_context,
            AgentRole.PLANNING_ASSISTANT: self._process_planning_context,
            AgentRole.TEACHING_ASSISTANT: self._process_teaching_context,
            AgentRole.SUPPORT_ASSISTANT: self._process_support_context
        })
        
        self._domain_processors.update({
            ExpertiseDomain.TECHNOLOGY: self._process_tech_domain,
            ExpertiseDomain.SCIENCE: self._process_science_domain,
            ExpertiseDomain.BUSINESS: self._process_business_domain,
            ExpertiseDomain.EDUCATION: self._process_education_domain
        })
        
        self._style_processors.update({
            InteractionStyle.FORMAL: self._process_formal_style,
            InteractionStyle.CASUAL: self._process_casual_style,
            InteractionStyle.TECHNICAL: self._process_technical_style,
            InteractionStyle.EDUCATIONAL: self._process_educational_style
        })
    
    def add_role_specific_context(
        self,
        content: str,
        context_type: str,
        relevance_score: float = 1.0,
        domain_specific: bool = False,
        **kwargs
    ) -> ContextItem:
        """
        Add context specifically tailored for the current role.
        
        Args:
            content: Context content
            context_type: Type of context (e.g., 'evidence', 'code', 'example')
            relevance_score: Initial relevance score
            domain_specific: Whether this context is domain-specific
            **kwargs: Additional context item parameters
        
        Returns:
            Created context item with role-specific processing applied
        """
        # Determine appropriate layer based on role and context type
        layer = self._determine_context_layer(context_type)
        
        # Create context item
        context_item = self.add_context(
            content=content,
            layer=layer,
            relevance_score=relevance_score,
            source=f"role_{self.role_profile.role.value}",
            metadata={
                'context_type': context_type,
                'role': self.role_profile.role.value,
                'domain_specific': domain_specific,
                **kwargs.get('metadata', {})
            },
            **{k: v for k, v in kwargs.items() if k != 'metadata'}
        )
        
        # Apply role-specific processing
        self._apply_role_processing(context_item, context_type)
        
        return context_item
    
    def get_relevant_context(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        include_layers: Optional[List[ContextLayer]] = None
    ) -> List[ContextItem]:
        """
        Get context tailored for the current agent role.
        
        Overrides base method to apply role-specific filtering and boosting.
        """
        # Apply role-specific token multiplier
        if max_tokens:
            role_multiplier = self.context_config.role_token_multipliers.get(
                self.role_profile.role.value, 1.0
            )
            max_tokens = int(max_tokens * role_multiplier)
        
        # Get base context
        base_context = super().get_relevant_context(query, max_tokens, include_layers)
        
        # Apply role-specific filtering
        if self.context_config.role_context_filtering:
            base_context = self._apply_role_filtering(base_context)
        
        # Apply domain expertise boosting
        if self.context_config.enable_domain_expertise_boost:
            base_context = self._apply_domain_boosting(base_context)
        
        # Apply role-specific relevance adjustments
        base_context = self._apply_role_relevance_adjustments(base_context, query)
        
        return base_context
    
    def _determine_context_layer(self, context_type: str) -> ContextLayer:
        """Determine appropriate context layer based on context type and role"""
        # Role-specific layer mapping
        layer_mappings = {
            'identity': ContextLayer.GLOBAL,
            'capabilities': ContextLayer.GLOBAL, 
            'examples': ContextLayer.SESSION,
            'current_task': ContextLayer.TASK,
            'immediate': ContextLayer.DYNAMIC,
            'conversation': ContextLayer.DYNAMIC
        }
        
        return layer_mappings.get(context_type, ContextLayer.SESSION)
    
    def _apply_role_processing(self, context_item: ContextItem, context_type: str):
        """Apply role-specific processing to context items"""
        # Apply role processor
        if self.role_profile.role in self._role_processors:
            self._role_processors[self.role_profile.role](context_item, context_type)
        
        # Apply domain processors
        for domain in self.role_profile.expertise_domains:
            if domain in self._domain_processors:
                self._domain_processors[domain](context_item, context_type)
        
        # Apply style processor
        if self.role_profile.interaction_style in self._style_processors:
            self._style_processors[self.role_profile.interaction_style](context_item, context_type)
    
    def _apply_role_filtering(self, context_items: List[ContextItem]) -> List[ContextItem]:
        """Apply role-specific context filtering"""
        role_filters = self.role_context_filters.get(self.role_profile.role, {})
        preferred_types = role_filters.get('preferred_types', set())
        
        if not preferred_types:
            return context_items
        
        # Filter and boost preferred context types
        filtered_items = []
        for item in context_items:
            context_type = item.metadata.get('context_type', 'general')
            
            # Include if it's a preferred type or high relevance
            if context_type in preferred_types or item.relevance_score >= 0.8:
                # Boost preferred types
                if context_type in preferred_types:
                    item.relevance_score = min(item.relevance_score + 0.2, 1.0)
                filtered_items.append(item)
        
        return filtered_items
    
    def _apply_domain_boosting(self, context_items: List[ContextItem]) -> List[ContextItem]:
        """Boost context items relevant to the agent's expertise domains"""
        domain_keywords = self._get_domain_keywords()
        
        for item in context_items:
            content_lower = item.content.lower()
            
            # Check for domain-specific keywords
            domain_matches = sum(1 for keyword in domain_keywords if keyword in content_lower)
            
            if domain_matches > 0:
                boost = min(domain_matches * 0.1, self.context_config.expertise_context_boost)
                item.relevance_score = min(item.relevance_score + boost, 1.0)
                item.metadata['domain_boosted'] = True
        
        return context_items
    
    def _apply_role_relevance_adjustments(
        self,
        context_items: List[ContextItem],
        query: Optional[str] = None
    ) -> List[ContextItem]:
        """Apply role-specific relevance adjustments"""
        role_filters = self.role_context_filters.get(self.role_profile.role, {})
        boosted_keywords = role_filters.get('boosted_keywords', set())
        
        if query and boosted_keywords:
            query_lower = query.lower()
            
            for item in context_items:
                # Boost items that contain role-relevant keywords from the query
                keyword_matches = sum(
                    1 for keyword in boosted_keywords 
                    if keyword in query_lower and keyword in item.content.lower()
                )
                
                if keyword_matches > 0:
                    boost = min(keyword_matches * 0.15, 0.3)
                    item.relevance_score = min(item.relevance_score + boost, 1.0)
        
        return context_items
    
    def _get_domain_keywords(self) -> Set[str]:
        """Get keywords relevant to the agent's expertise domains"""
        domain_keywords = {
            ExpertiseDomain.TECHNOLOGY: {
                'software', 'programming', 'algorithm', 'database', 'api', 'framework',
                'code', 'development', 'tech', 'digital', 'system', 'platform'
            },
            ExpertiseDomain.SCIENCE: {
                'research', 'study', 'experiment', 'hypothesis', 'data', 'analysis',
                'theory', 'method', 'scientific', 'evidence', 'peer-reviewed'
            },
            ExpertiseDomain.BUSINESS: {
                'strategy', 'market', 'revenue', 'profit', 'customer', 'business',
                'management', 'operations', 'sales', 'marketing', 'competitive'
            },
            ExpertiseDomain.EDUCATION: {
                'learning', 'teaching', 'education', 'curriculum', 'pedagogy',
                'student', 'instruction', 'knowledge', 'skill', 'academic'
            }
        }
        
        all_keywords = set()
        for domain in self.role_profile.expertise_domains:
            all_keywords.update(domain_keywords.get(domain, set()))
        
        return all_keywords
    
    # Role-specific processing methods
    def _process_research_context(self, item: ContextItem, context_type: str):
        """Process context for research assistant role"""
        if context_type in ['evidence', 'data', 'analysis']:
            item.importance = min(item.importance + 0.2, 1.0)
            item.metadata['evidence_based'] = True
        
        # Boost academic and research-oriented content
        if any(keyword in item.content.lower() for keyword in ['study', 'research', 'data']):
            item.relevance_score = min(item.relevance_score + 0.1, 1.0)
    
    def _process_code_context(self, item: ContextItem, context_type: str):
        """Process context for code assistant role"""
        if context_type in ['code', 'technical', 'implementation']:
            item.importance = min(item.importance + 0.25, 1.0)
            item.metadata['technical'] = True
        
        # Boost code-related content
        if any(keyword in item.content.lower() for keyword in ['function', 'class', 'method']):
            item.relevance_score = min(item.relevance_score + 0.15, 1.0)
    
    def _process_creative_context(self, item: ContextItem, context_type: str):
        """Process context for creative assistant role"""
        if context_type in ['inspiration', 'brainstorming', 'alternatives']:
            item.importance = min(item.importance + 0.2, 1.0)
            item.metadata['creative'] = True
        
        # Reduce formality, increase creativity indicators
        item.metadata['creativity_factor'] = self.role_profile.creativity_factor
    
    def _process_planning_context(self, item: ContextItem, context_type: str):
        """Process context for planning assistant role"""
        if context_type in ['strategy', 'timeline', 'objectives']:
            item.importance = min(item.importance + 0.3, 1.0)
            item.metadata['strategic'] = True
    
    def _process_teaching_context(self, item: ContextItem, context_type: str):
        """Process context for teaching assistant role"""
        if context_type in ['explanations', 'examples', 'fundamentals']:
            item.importance = min(item.importance + 0.25, 1.0)
            item.metadata['educational'] = True
        
        # Boost clear, explanatory content
        if any(keyword in item.content.lower() for keyword in ['explain', 'example', 'understand']):
            item.relevance_score = min(item.relevance_score + 0.2, 1.0)
    
    def _process_support_context(self, item: ContextItem, context_type: str):
        """Process context for support assistant role"""
        if context_type in ['solutions', 'troubleshooting', 'help']:
            item.importance = min(item.importance + 0.2, 1.0)
            item.metadata['helpful'] = True
    
    # Domain processing methods
    def _process_tech_domain(self, item: ContextItem, context_type: str):
        """Process context for technology domain"""
        item.metadata['domain'] = 'technology'
        if 'technical' not in item.metadata:
            item.metadata['technical'] = True
    
    def _process_science_domain(self, item: ContextItem, context_type: str):
        """Process context for science domain"""
        item.metadata['domain'] = 'science'
        item.metadata['evidence_based'] = True
    
    def _process_business_domain(self, item: ContextItem, context_type: str):
        """Process context for business domain"""
        item.metadata['domain'] = 'business'
        item.metadata['strategic'] = True
    
    def _process_education_domain(self, item: ContextItem, context_type: str):
        """Process context for education domain"""
        item.metadata['domain'] = 'education'
        item.metadata['educational'] = True
    
    # Style processing methods
    def _process_formal_style(self, item: ContextItem, context_type: str):
        """Process context for formal interaction style"""
        item.metadata['formality_level'] = 'high'
        item.metadata['professional'] = True
    
    def _process_casual_style(self, item: ContextItem, context_type: str):
        """Process context for casual interaction style"""
        item.metadata['formality_level'] = 'low'
        item.metadata['conversational'] = True
    
    def _process_technical_style(self, item: ContextItem, context_type: str):
        """Process context for technical interaction style"""
        item.metadata['technical_style'] = True
        item.metadata['detail_level'] = 'high'
    
    def _process_educational_style(self, item: ContextItem, context_type: str):
        """Process context for educational interaction style"""
        item.metadata['educational_style'] = True
        item.metadata['clarity_priority'] = 'high'
    
    def switch_role(self, new_role_profile: RoleProfile):
        """Switch to a new role profile"""
        old_role = self.role_profile.role
        self.role_profile = new_role_profile
        
        # Re-process existing context items for new role
        for layer in self._context_layers.values():
            for item in layer:
                self._apply_role_processing(item, item.metadata.get('context_type', 'general'))
        
        logger.info(f"Switched role from {old_role.value} to {new_role_profile.role.value}")
    
    def get_role_stats(self) -> Dict[str, Any]:
        """Get statistics about role-specific context usage"""
        stats = {
            'current_role': self.role_profile.role.value,
            'expertise_domains': [d.value for d in self.role_profile.expertise_domains],
            'interaction_style': self.role_profile.interaction_style.value,
            'context_stats': self.get_context_stats()
        }
        
        # Count context by type
        context_by_type = {}
        for layer in self._context_layers.values():
            for item in layer:
                context_type = item.metadata.get('context_type', 'general')
                context_by_type[context_type] = context_by_type.get(context_type, 0) + 1
        
        stats['context_by_type'] = context_by_type
        
        # Calculate role-specific metrics
        role_processed_items = sum(
            1 for layer in self._context_layers.values()
            for item in layer
            if item.source.startswith(f"role_{self.role_profile.role.value}")
        )
        
        stats['role_specific_items'] = role_processed_items
        
        return stats