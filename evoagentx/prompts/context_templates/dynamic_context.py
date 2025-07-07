"""
Dynamic Context Template

Provides intelligent context adaptation based on conversation flow and state.
This template automatically adjusts context relevance and selection based on:
- Conversation phase (greeting, task, conclusion)
- User engagement patterns
- Topic shifts and continuity
- Response quality feedback
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
import time
import re
from collections import deque, Counter

from .base_context_template import BaseContextTemplate, ContextItem, ContextLayer, ContextConfig
from ...core.logging import logger


class ConversationPhase(Enum):
    """Different phases of a conversation"""
    GREETING = "greeting"
    ORIENTATION = "orientation"  # Understanding user needs
    TASK_EXECUTION = "task_execution"
    REFINEMENT = "refinement"  # Iterating on solutions
    CONCLUSION = "conclusion"
    FOLLOW_UP = "follow_up"


class UserEngagementLevel(Enum):
    """User engagement patterns"""
    HIGH = "high"       # Detailed responses, asking questions
    MEDIUM = "medium"   # Standard responses
    LOW = "low"         # Short responses, disengaged
    CONFUSED = "confused"  # Asking for clarification


@dataclass
class ConversationState:
    """Tracks the current state of the conversation"""
    phase: ConversationPhase = ConversationPhase.GREETING
    engagement_level: UserEngagementLevel = UserEngagementLevel.MEDIUM
    topic_stack: deque = field(default_factory=lambda: deque(maxlen=5))
    turn_count: int = 0
    last_user_message_time: float = 0
    last_topic_shift_time: float = 0
    user_satisfaction_indicators: List[str] = field(default_factory=list)
    confusion_indicators: List[str] = field(default_factory=list)
    
    def update_turn(self):
        """Update conversation state after each turn"""
        self.turn_count += 1
        self.last_user_message_time = time.time()
    
    def add_topic(self, topic: str):
        """Add a new topic to the conversation"""
        if not self.topic_stack or self.topic_stack[-1] != topic:
            self.topic_stack.append(topic)
            self.last_topic_shift_time = time.time()
    
    def get_current_topic(self) -> Optional[str]:
        """Get the current topic being discussed"""
        return self.topic_stack[-1] if self.topic_stack else None
    
    def get_topic_history(self) -> List[str]:
        """Get recent topic history"""
        return list(self.topic_stack)


@dataclass
class DynamicContextConfig(ContextConfig):
    """Extended configuration for dynamic context behavior"""
    # Conversation analysis settings
    enable_phase_detection: bool = True
    enable_engagement_tracking: bool = True
    enable_topic_tracking: bool = True
    
    # Adaptation settings
    adapt_context_to_phase: bool = True
    adapt_context_to_engagement: bool = True
    boost_recent_context: bool = True
    
    # Feedback integration
    enable_satisfaction_tracking: bool = True
    enable_confusion_detection: bool = True
    
    # Context selection weights
    phase_weight: float = 0.3
    engagement_weight: float = 0.2
    topic_relevance_weight: float = 0.4
    recency_weight: float = 0.1


class DynamicContextTemplate(BaseContextTemplate):
    """
    Dynamic context template that adapts to conversation state.
    
    Features:
    - Automatic conversation phase detection
    - User engagement level tracking
    - Topic drift detection and adaptation
    - Context relevance adjustment based on conversation state
    - Feedback-driven context optimization
    """
    
    def __init__(
        self,
        instruction: str,
        context_config: Optional[DynamicContextConfig] = None,
        **kwargs
    ):
        # Use dynamic config or create default
        if context_config is None:
            context_config = DynamicContextConfig()
        
        super().__init__(instruction=instruction, context_config=context_config, **kwargs)
        
        # Conversation state tracking
        self.conversation_state = ConversationState()
        
        # Pattern matchers for conversation analysis
        self._setup_pattern_matchers()
        
        # Context adaptation rules
        self._setup_adaptation_rules()
        
        # Message history for analysis
        self.message_history: deque = deque(maxlen=50)
    
    def _setup_pattern_matchers(self):
        """Setup regex patterns for conversation analysis"""
        self.phase_patterns = {
            ConversationPhase.GREETING: [
                r'\b(hello|hi|hey|good morning|good afternoon|good evening)\b',
                r'\b(how are you|nice to meet you)\b'
            ],
            ConversationPhase.ORIENTATION: [
                r'\b(help me|i need|i want|can you|how do i)\b',
                r'\b(what is|explain|tell me about)\b'
            ],
            ConversationPhase.TASK_EXECUTION: [
                r'\b(let\'s|start|begin|proceed|continue)\b',
                r'\b(do this|implement|create|build|solve)\b'
            ],
            ConversationPhase.REFINEMENT: [
                r'\b(actually|instead|change|modify|adjust)\b',
                r'\b(not quite|try again|different|better)\b'
            ],
            ConversationPhase.CONCLUSION: [
                r'\b(thanks|thank you|that\'s all|perfect|great)\b',
                r'\b(done|finished|complete|good enough)\b'
            ]
        }
        
        self.engagement_patterns = {
            UserEngagementLevel.HIGH: [
                r'\b(interesting|fascinating|tell me more|why|how)\b',
                r'[?]{2,}',  # Multiple question marks
                r'\b(explain further|more details|elaborate)\b'
            ],
            UserEngagementLevel.LOW: [
                r'^\w{1,3}$',  # Very short responses
                r'\b(ok|fine|sure|yeah|k)\b$',
                r'^(yes|no)\.?$'
            ],
            UserEngagementLevel.CONFUSED: [
                r'\b(confused|don\'t understand|what do you mean|unclear)\b',
                r'\b(huh|what|sorry|come again)\b',
                r'[?]{3,}'  # Many question marks indicating confusion
            ]
        }
        
        self.satisfaction_patterns = [
            r'\b(perfect|excellent|exactly|great|awesome|love it)\b',
            r'\b(that\'s right|correct|good|nice|helpful)\b'
        ]
        
        self.confusion_patterns = [
            r'\b(confused|lost|don\'t get it|unclear|makes no sense)\b',
            r'\b(what|huh|sorry|come again|repeat)\b'
        ]
    
    def _setup_adaptation_rules(self):
        """Setup context adaptation rules for different conversation states"""
        self.phase_context_rules = {
            ConversationPhase.GREETING: {
                'boost_layers': [ContextLayer.GLOBAL],
                'context_focus': 'agent_introduction',
                'max_items': 5
            },
            ConversationPhase.ORIENTATION: {
                'boost_layers': [ContextLayer.GLOBAL, ContextLayer.SESSION],
                'context_focus': 'capabilities_and_examples',
                'max_items': 10
            },
            ConversationPhase.TASK_EXECUTION: {
                'boost_layers': [ContextLayer.TASK, ContextLayer.DYNAMIC],
                'context_focus': 'task_specific_knowledge',
                'max_items': 15
            },
            ConversationPhase.REFINEMENT: {
                'boost_layers': [ContextLayer.DYNAMIC, ContextLayer.TASK],
                'context_focus': 'recent_context_and_feedback',
                'max_items': 12
            },
            ConversationPhase.CONCLUSION: {
                'boost_layers': [ContextLayer.SESSION],
                'context_focus': 'summary_and_next_steps',
                'max_items': 8
            }
        }
        
        self.engagement_context_rules = {
            UserEngagementLevel.HIGH: {
                'include_detailed_context': True,
                'boost_educational_content': True,
                'max_items_multiplier': 1.2
            },
            UserEngagementLevel.MEDIUM: {
                'include_detailed_context': True,
                'boost_educational_content': False,
                'max_items_multiplier': 1.0
            },
            UserEngagementLevel.LOW: {
                'include_detailed_context': False,
                'boost_educational_content': False,
                'max_items_multiplier': 0.7,
                'prioritize_actionable_context': True
            },
            UserEngagementLevel.CONFUSED: {
                'include_detailed_context': False,
                'boost_clarification_context': True,
                'max_items_multiplier': 0.8,
                'prioritize_simple_explanations': True
            }
        }
    
    def process_user_message(self, message: str, role: str = "user") -> ConversationState:
        """
        Process a user message and update conversation state.
        
        Args:
            message: The user's message
            role: Role of the message sender
            
        Returns:
            Updated conversation state
        """
        if role == "user":
            # Add to message history
            self.message_history.append({
                'content': message,
                'role': role,
                'timestamp': time.time()
            })
            
            # Update conversation state
            self.conversation_state.update_turn()
            
            # Analyze message for conversation insights
            if self.context_config.enable_phase_detection:
                self._detect_conversation_phase(message)
            
            if self.context_config.enable_engagement_tracking:
                self._assess_engagement_level(message)
            
            if self.context_config.enable_topic_tracking:
                self._extract_and_track_topics(message)
            
            # Track satisfaction and confusion indicators
            if self.context_config.enable_satisfaction_tracking:
                self._track_satisfaction_indicators(message)
            
            if self.context_config.enable_confusion_detection:
                self._detect_confusion_indicators(message)
            
            # Add message as dynamic context
            self.add_context(
                content=message,
                layer=ContextLayer.DYNAMIC,
                relevance_score=1.0,  # Recent messages are highly relevant
                importance=0.7,
                source="user_message",
                metadata={
                    'phase': self.conversation_state.phase.value,
                    'engagement': self.conversation_state.engagement_level.value,
                    'turn': self.conversation_state.turn_count
                }
            )
        
        return self.conversation_state
    
    def get_relevant_context(
        self,
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        include_layers: Optional[List[ContextLayer]] = None
    ) -> List[ContextItem]:
        """
        Get context adapted to current conversation state.
        
        Overrides base method to apply dynamic adaptation rules.
        """
        # Get base context
        base_context = super().get_relevant_context(query, max_tokens, include_layers)
        
        # Apply conversation state adaptations
        if self.context_config.adapt_context_to_phase:
            base_context = self._adapt_context_for_phase(base_context)
        
        if self.context_config.adapt_context_to_engagement:
            base_context = self._adapt_context_for_engagement(base_context)
        
        # Boost context relevance based on topic alignment
        if self.context_config.enable_topic_tracking and query:
            base_context = self._boost_topic_relevant_context(base_context, query)
        
        # Apply recency boost if enabled
        if self.context_config.boost_recent_context:
            base_context = self._apply_recency_boost(base_context)
        
        return base_context
    
    def _detect_conversation_phase(self, message: str):
        """Detect the current conversation phase based on message content"""
        message_lower = message.lower()
        
        # Score each phase based on pattern matches
        phase_scores = {}
        for phase, patterns in self.phase_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, message_lower))
                score += matches
            phase_scores[phase] = score
        
        # Determine the most likely phase
        if any(score > 0 for score in phase_scores.values()):
            detected_phase = max(phase_scores.keys(), key=lambda p: phase_scores[p])
            
            # Only update if we have a strong signal or it's a natural progression
            if phase_scores[detected_phase] > 0:
                old_phase = self.conversation_state.phase
                self.conversation_state.phase = detected_phase
                
                if old_phase != detected_phase:
                    logger.debug(f"Conversation phase changed: {old_phase.value} -> {detected_phase.value}")
    
    def _assess_engagement_level(self, message: str):
        """Assess user engagement level based on message characteristics"""
        message_lower = message.lower()
        
        # Check for engagement patterns
        engagement_scores = {}
        for level, patterns in self.engagement_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, message_lower))
                score += matches
            engagement_scores[level] = score
        
        # Consider message length as an engagement indicator
        message_length = len(message.split())
        if message_length > 20:
            engagement_scores[UserEngagementLevel.HIGH] += 1
        elif message_length < 3:
            engagement_scores[UserEngagementLevel.LOW] += 1
        
        # Update engagement level if we have clear indicators
        if any(score > 0 for score in engagement_scores.values()):
            detected_level = max(engagement_scores.keys(), key=lambda l: engagement_scores[l])
            
            old_level = self.conversation_state.engagement_level
            self.conversation_state.engagement_level = detected_level
            
            if old_level != detected_level:
                logger.debug(f"Engagement level changed: {old_level.value} -> {detected_level.value}")
    
    def _extract_and_track_topics(self, message: str):
        """Extract and track topics from user messages"""
        # Simple topic extraction based on nouns and key phrases
        # In practice, this could use more sophisticated NLP
        
        # Extract potential topics (simplified approach)
        words = message.lower().split()
        
        # Look for topic-indicating patterns
        topic_indicators = [
            r'\babout (\w+)',
            r'\bregarding (\w+)',
            r'\bfor (\w+)',
            r'\bwith (\w+)',
            r'\busing (\w+)'
        ]
        
        topics = []
        for pattern in topic_indicators:
            matches = re.findall(pattern, message.lower())
            topics.extend(matches)
        
        # Add significant nouns as potential topics
        # This is a simplified approach - in practice you'd use NER or similar
        significant_words = [word for word in words if len(word) > 4 and word.isalpha()]
        topics.extend(significant_words[:3])  # Take up to 3 significant words
        
        # Update topic tracking
        for topic in topics:
            if topic and len(topic) > 2:
                self.conversation_state.add_topic(topic)
    
    def _track_satisfaction_indicators(self, message: str):
        """Track indicators of user satisfaction"""
        message_lower = message.lower()
        
        for pattern in self.satisfaction_patterns:
            if re.search(pattern, message_lower):
                self.conversation_state.user_satisfaction_indicators.append(pattern)
                # Keep only recent indicators
                if len(self.conversation_state.user_satisfaction_indicators) > 10:
                    self.conversation_state.user_satisfaction_indicators.pop(0)
    
    def _detect_confusion_indicators(self, message: str):
        """Detect indicators of user confusion"""
        message_lower = message.lower()
        
        for pattern in self.confusion_patterns:
            if re.search(pattern, message_lower):
                self.conversation_state.confusion_indicators.append(pattern)
                # Keep only recent indicators
                if len(self.conversation_state.confusion_indicators) > 10:
                    self.conversation_state.confusion_indicators.pop(0)
    
    def _adapt_context_for_phase(self, context_items: List[ContextItem]) -> List[ContextItem]:
        """Adapt context selection based on conversation phase"""
        current_phase = self.conversation_state.phase
        
        if current_phase not in self.phase_context_rules:
            return context_items
        
        rules = self.phase_context_rules[current_phase]
        
        # Boost relevance for preferred layers
        boost_layers = rules.get('boost_layers', [])
        for item in context_items:
            if item.layer in boost_layers:
                item.relevance_score = min(item.relevance_score + 0.2, 1.0)
        
        # Apply max items limit for phase
        max_items = rules.get('max_items', len(context_items))
        return context_items[:max_items]
    
    def _adapt_context_for_engagement(self, context_items: List[ContextItem]) -> List[ContextItem]:
        """Adapt context selection based on user engagement level"""
        current_engagement = self.conversation_state.engagement_level
        
        if current_engagement not in self.engagement_context_rules:
            return context_items
        
        rules = self.engagement_context_rules[current_engagement]
        
        # Apply multiplier to max items
        multiplier = rules.get('max_items_multiplier', 1.0)
        max_items = int(len(context_items) * multiplier)
        
        # Filter context based on engagement rules
        if not rules.get('include_detailed_context', True):
            # Prefer shorter, more actionable context
            context_items = [item for item in context_items if len(item.content) < 200]
        
        return context_items[:max_items]
    
    def _boost_topic_relevant_context(self, context_items: List[ContextItem], query: str) -> List[ContextItem]:
        """Boost context relevance based on topic alignment"""
        current_topics = self.conversation_state.get_topic_history()
        
        if not current_topics:
            return context_items
        
        # Boost items that mention current topics
        for item in context_items:
            for topic in current_topics:
                if topic.lower() in item.content.lower():
                    item.relevance_score = min(item.relevance_score + 0.15, 1.0)
        
        return context_items
    
    def _apply_recency_boost(self, context_items: List[ContextItem]) -> List[ContextItem]:
        """Apply recency boost to context items"""
        current_time = time.time()
        
        for item in context_items:
            # Boost items from the last 5 minutes significantly
            age_minutes = (current_time - item.timestamp) / 60
            if age_minutes < 5:
                item.relevance_score = min(item.relevance_score + 0.3, 1.0)
            elif age_minutes < 15:
                item.relevance_score = min(item.relevance_score + 0.1, 1.0)
        
        return context_items
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation state"""
        return {
            'phase': self.conversation_state.phase.value,
            'engagement': self.conversation_state.engagement_level.value,
            'turn_count': self.conversation_state.turn_count,
            'current_topic': self.conversation_state.get_current_topic(),
            'topic_history': self.conversation_state.get_topic_history(),
            'satisfaction_indicators': len(self.conversation_state.user_satisfaction_indicators),
            'confusion_indicators': len(self.conversation_state.confusion_indicators),
            'context_stats': self.get_context_stats()
        }
    
    def reset_conversation(self):
        """Reset conversation state for a new conversation"""
        self.conversation_state = ConversationState()
        self.message_history.clear()
        
        # Clear dynamic context but preserve other layers
        self.clear_context_layer(ContextLayer.DYNAMIC)
        
        logger.info("Conversation state reset for new session")