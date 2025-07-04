"""
Enhanced Intelligence Parser for VaultPilot

Advanced content intelligence and parsing capabilities leveraging
EvoAgentX's intelligence parser for sophisticated content analysis.
"""

import re
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

from .api_models import IntelligenceParseRequest, IntelligenceParseResponse, Entity, ContextInfo


class ContentType(Enum):
    DAILY_NOTE = "daily_note"
    PROJECT_NOTE = "project_note"
    LITERATURE_NOTE = "literature_note"
    PERMANENT_NOTE = "permanent_note"
    MOC = "map_of_content"
    MEETING_NOTE = "meeting_note"
    RESEARCH_NOTE = "research_note"
    CREATIVE_WRITING = "creative_writing"
    UNKNOWN = "unknown"


class IntentType(Enum):
    QUESTION = "question"
    TASK_REQUEST = "task_request"
    INFORMATION_SEEKING = "information_seeking"
    CREATIVE_REQUEST = "creative_request"
    ANALYSIS_REQUEST = "analysis_request"
    ORGANIZATION_REQUEST = "organization_request"
    PLANNING_REQUEST = "planning_request"
    GENERAL_CHAT = "general_chat"


class EnhancedIntelligenceParser:
    """
    Advanced intelligence parser for VaultPilot content analysis.
    
    Provides sophisticated parsing, intent classification, and content
    intelligence for Obsidian vault content and user interactions.
    """
    
    def __init__(self):
        self.entity_patterns = self._init_entity_patterns()
        self.intent_classifiers = self._init_intent_classifiers()
        self.content_analyzers = self._init_content_analyzers()
        
    def _init_entity_patterns(self) -> Dict[str, str]:
        """Initialize regex patterns for entity extraction"""
        return {
            'date': r'\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{4}\b',
            'time': r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'url': r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w)*)?)?',
            'hashtag': r'#\w+',
            'mention': r'@\w+',
            'wiki_link': r'\[\[([^\]]+)\]\]',
            'external_link': r'\[([^\]]+)\]\(([^)]+)\)',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            'priority': r'\b(?:high|medium|low)\s+priority\b',
            'status': r'\b(?:todo|doing|done|pending|completed|in[_\s]progress)\b',
            'deadline': r'\b(?:due|deadline|by)\s+(?:on\s+)?(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})\b'
        }
    
    def _init_intent_classifiers(self) -> Dict[str, List[str]]:
        """Initialize intent classification patterns"""
        return {
            'question': [
                r'^(?:what|how|when|where|why|who|which|can|could|would|should|is|are|do|does|did)',
                r'\?',
                r'\b(?:explain|clarify|help me understand|tell me about)\b'
            ],
            'task_request': [
                r'\b(?:create|generate|make|build|write|draft|plan|organize|structure)\b',
                r'\b(?:please|can you|could you|would you)\b.*\b(?:create|generate|make|build)\b',
                r'^(?:let\'s|i need to|i want to|i should)\b'
            ],
            'information_seeking': [
                r'\b(?:find|search|look up|research|investigate|explore)\b',
                r'\b(?:information about|details on|more about)\b',
                r'\b(?:what do you know about|tell me about)\b'
            ],
            'creative_request': [
                r'\b(?:creative|imaginative|story|poem|narrative|character|plot)\b',
                r'\b(?:brainstorm|ideate|inspire|innovative)\b',
                r'\b(?:write a|create a).*(?:story|poem|article|essay)\b'
            ],
            'analysis_request': [
                r'\b(?:analyze|examine|evaluate|assess|review|critique)\b',
                r'\b(?:insights|patterns|trends|conclusions|findings)\b',
                r'\b(?:what does this mean|interpret|understand)\b'
            ],
            'organization_request': [
                r'\b(?:organize|structure|categorize|group|sort|arrange)\b',
                r'\b(?:clean up|tidy|reorganize|restructure)\b',
                r'\b(?:folder|category|tag|label|system)\b'
            ],
            'planning_request': [
                r'\b(?:plan|schedule|timeline|roadmap|strategy|agenda)\b',
                r'\b(?:next steps|action items|milestones|goals)\b',
                r'\b(?:how should i|what should i do)\b'
            ]
        }
    
    def _init_content_analyzers(self) -> Dict[str, Any]:
        """Initialize content type analyzers"""
        return {
            'daily_note': self._analyze_daily_note,
            'project_note': self._analyze_project_note,
            'literature_note': self._analyze_literature_note,
            'meeting_note': self._analyze_meeting_note,
            'research_note': self._analyze_research_note
        }
    
    async def parse_content(self, request: IntelligenceParseRequest) -> IntelligenceParseResponse:
        """
        Parse content with advanced intelligence
        
        Args:
            request: Content parsing request
            
        Returns:
            Comprehensive parsing response with entities, intent, and context
        """
        try:
            text = request.text
            parse_types = [request.parse_type] if request.parse_type != "all" else ["intent", "entities", "context"]
            
            # Initialize results
            intent = "general_chat"
            entities = []
            context_info = ContextInfo(domain="general", sentiment="neutral", topics=[], keywords=[])
            overall_confidence = 0.0
            
            # Parse based on requested types
            if "intent" in parse_types:
                intent, intent_confidence = await self._classify_intent(text)
                overall_confidence += intent_confidence * 0.4
            
            if "entities" in parse_types:
                entities = await self._extract_entities(text)
                entity_confidence = self._calculate_entity_confidence(entities)
                overall_confidence += entity_confidence * 0.3
            
            if "context" in parse_types:
                context_info = await self._analyze_context(text)
                context_confidence = self._calculate_context_confidence(context_info)
                overall_confidence += context_confidence * 0.3
            
            # Normalize confidence if not all types were parsed
            if len(parse_types) < 3:
                overall_confidence = overall_confidence / (len(parse_types) / 3)
            
            return IntelligenceParseResponse(
                intent=intent,
                entities=entities,
                context=context_info,
                confidence=min(1.0, overall_confidence)
            )
            
        except Exception as e:
            # Return basic fallback response
            return IntelligenceParseResponse(
                intent="general_chat",
                entities=[],
                context=ContextInfo(domain="general", sentiment="neutral", topics=[], keywords=[]),
                confidence=0.1
            )
    
    async def _classify_intent(self, text: str) -> Tuple[str, float]:
        """Classify user intent from text"""
        text_lower = text.lower()
        intent_scores = {}
        
        # Calculate scores for each intent type
        for intent_type, patterns in self.intent_classifiers.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                score += len(matches) * (1.0 / len(patterns))
            
            if score > 0:
                intent_scores[intent_type] = score
        
        if not intent_scores:
            return "general_chat", 0.5
        
        # Get highest scoring intent
        best_intent = max(intent_scores.keys(), key=lambda k: intent_scores[k])
        confidence = min(1.0, intent_scores[best_intent])
        
        return best_intent, confidence
    
    async def _extract_entities(self, text: str) -> List[Entity]:
        """Extract entities from text using pattern matching"""
        entities = []
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                entity = Entity(
                    type=entity_type,
                    value=match.group(0),
                    confidence=self._calculate_pattern_confidence(entity_type, match.group(0)),
                    start=match.start(),
                    end=match.end()
                )
                entities.append(entity)
        
        # Add custom entity detection
        entities.extend(await self._extract_vault_specific_entities(text))
        
        return entities
    
    async def _extract_vault_specific_entities(self, text: str) -> List[Entity]:
        """Extract Obsidian/vault-specific entities"""
        entities = []
        
        # Extract note titles from wiki links
        wiki_links = re.finditer(r'\[\[([^\]]+)\]\]', text)
        for match in wiki_links:
            entities.append(Entity(
                type="note_reference",
                value=match.group(1),
                confidence=0.95,
                start=match.start(),
                end=match.end()
            ))
        
        # Extract task items
        task_items = re.finditer(r'- \[[ x]\] (.+)', text)
        for match in task_items:
            status = "completed" if "x" in match.group(0) else "pending"
            entities.append(Entity(
                type="task_item",
                value=match.group(1),
                confidence=0.9,
                start=match.start(),
                end=match.end()
            ))
        
        # Extract YAML frontmatter
        frontmatter = re.search(r'^---\n(.*?)\n---', text, re.DOTALL)
        if frontmatter:
            entities.append(Entity(
                type="frontmatter",
                value=frontmatter.group(1),
                confidence=1.0,
                start=frontmatter.start(),
                end=frontmatter.end()
            ))
        
        return entities
    
    async def _analyze_context(self, text: str) -> ContextInfo:
        """Analyze content context and metadata"""
        
        # Detect content domain
        domain = await self._detect_domain(text)
        
        # Analyze sentiment
        sentiment = await self._analyze_sentiment(text)
        
        # Extract topics
        topics = await self._extract_topics(text)
        
        # Extract keywords
        keywords = await self._extract_keywords(text)
        
        return ContextInfo(
            domain=domain,
            sentiment=sentiment,
            topics=topics,
            keywords=keywords
        )
    
    async def _detect_domain(self, text: str) -> str:
        """Detect content domain/category"""
        text_lower = text.lower()
        
        domain_indicators = {
            'technology': ['code', 'programming', 'software', 'api', 'database', 'algorithm'],
            'academic': ['research', 'study', 'thesis', 'paper', 'academic', 'university'],
            'business': ['meeting', 'project', 'strategy', 'revenue', 'market', 'customer'],
            'personal': ['daily', 'journal', 'reflection', 'thoughts', 'feelings', 'personal'],
            'creative': ['story', 'creative', 'art', 'design', 'inspiration', 'imagination'],
            'health': ['health', 'fitness', 'exercise', 'nutrition', 'medical', 'wellness'],
            'finance': ['money', 'budget', 'investment', 'financial', 'expenses', 'income']
        }
        
        domain_scores = {}
        for domain, indicators in domain_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores.keys(), key=lambda k: domain_scores[k])
        return "general"
    
    async def _analyze_sentiment(self, text: str) -> str:
        """Analyze text sentiment"""
        text_lower = text.lower()
        
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'success', 'happy', 'love', 'like']
        negative_words = ['bad', 'terrible', 'awful', 'failed', 'problem', 'issue', 'sad', 'hate', 'dislike']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    async def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text"""
        # Simple topic extraction based on frequent meaningful words
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Filter out common words
        stop_words = {'that', 'this', 'with', 'have', 'will', 'from', 'they', 'been', 'were', 'said', 'each', 'which', 'their', 'time', 'about', 'would', 'there', 'could', 'other', 'more', 'very', 'what', 'know', 'just', 'first', 'into', 'over', 'think', 'also', 'your', 'work', 'life', 'only', 'can', 'still', 'should', 'after', 'being', 'now', 'made', 'before', 'here', 'through', 'when', 'where', 'much', 'some', 'these', 'many', 'then', 'them', 'well', 'were'}
        
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 4]
        
        # Count frequency and return top topics
        word_freq = {}
        for word in meaningful_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top 5 topics
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:5] if freq > 1]
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Extract capitalized words (likely proper nouns)
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', text)
        
        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', text)
        
        # Extract quoted phrases
        quoted = re.findall(r'"([^"]+)"', text)
        
        # Combine and deduplicate
        keywords = list(set(capitalized + hashtags + quoted))
        
        return keywords[:10]  # Return top 10 keywords
    
    def _calculate_pattern_confidence(self, entity_type: str, value: str) -> float:
        """Calculate confidence score for pattern-matched entities"""
        
        # Base confidence by entity type
        base_confidence = {
            'date': 0.95,
            'time': 0.9,
            'email': 0.98,
            'url': 0.95,
            'hashtag': 1.0,
            'wiki_link': 1.0,
            'phone': 0.85,
            'priority': 0.8,
            'status': 0.75
        }
        
        confidence = base_confidence.get(entity_type, 0.7)
        
        # Adjust based on value characteristics
        if entity_type == 'date':
            # Higher confidence for ISO format dates
            if re.match(r'\d{4}-\d{2}-\d{2}', value):
                confidence = 0.98
        
        elif entity_type == 'time':
            # Higher confidence for times with AM/PM
            if re.search(r'(AM|PM|am|pm)', value):
                confidence = 0.95
        
        return confidence
    
    def _calculate_entity_confidence(self, entities: List[Entity]) -> float:
        """Calculate overall confidence for entity extraction"""
        if not entities:
            return 0.5
        
        total_confidence = sum(entity.confidence for entity in entities)
        return min(1.0, total_confidence / len(entities))
    
    def _calculate_context_confidence(self, context: ContextInfo) -> float:
        """Calculate confidence for context analysis"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on detected elements
        if context.domain != "general":
            confidence += 0.2
        
        if context.topics:
            confidence += 0.1 * min(1.0, len(context.topics) / 3)
        
        if context.keywords:
            confidence += 0.1 * min(1.0, len(context.keywords) / 5)
        
        if context.sentiment != "neutral":
            confidence += 0.1
        
        return min(1.0, confidence)
    
    # Content type analyzers
    async def _analyze_daily_note(self, text: str) -> Dict[str, Any]:
        """Analyze daily note structure and content"""
        analysis = {
            'type': 'daily_note',
            'has_date': bool(re.search(r'\d{4}-\d{2}-\d{2}', text)),
            'has_tasks': bool(re.search(r'- \[[ x]\]', text)),
            'has_reflection': bool(re.search(r'reflection|thoughts|learned', text, re.IGNORECASE)),
            'has_planning': bool(re.search(r'tomorrow|next|plan|goals', text, re.IGNORECASE))
        }
        
        return analysis
    
    async def _analyze_project_note(self, text: str) -> Dict[str, Any]:
        """Analyze project note structure"""
        analysis = {
            'type': 'project_note',
            'has_objectives': bool(re.search(r'objective|goal|aim', text, re.IGNORECASE)),
            'has_timeline': bool(re.search(r'deadline|timeline|schedule', text, re.IGNORECASE)),
            'has_tasks': bool(re.search(r'- \[[ x]\]', text)),
            'has_status': bool(re.search(r'status|progress|completed', text, re.IGNORECASE))
        }
        
        return analysis
    
    async def _analyze_literature_note(self, text: str) -> Dict[str, Any]:
        """Analyze literature/research note"""
        analysis = {
            'type': 'literature_note',
            'has_citation': bool(re.search(r'author|published|journal|doi', text, re.IGNORECASE)),
            'has_summary': bool(re.search(r'summary|abstract|tldr', text, re.IGNORECASE)),
            'has_quotes': bool(re.search(r'"[^"]{20,}"', text)),
            'has_analysis': bool(re.search(r'analysis|insight|conclusion', text, re.IGNORECASE))
        }
        
        return analysis
    
    async def _analyze_meeting_note(self, text: str) -> Dict[str, Any]:
        """Analyze meeting note structure"""
        analysis = {
            'type': 'meeting_note',
            'has_attendees': bool(re.search(r'attendees|participants|present', text, re.IGNORECASE)),
            'has_agenda': bool(re.search(r'agenda|topics|discussion', text, re.IGNORECASE)),
            'has_action_items': bool(re.search(r'action|todo|follow[- ]up', text, re.IGNORECASE)),
            'has_decisions': bool(re.search(r'decision|agreed|resolved', text, re.IGNORECASE))
        }
        
        return analysis
    
    async def _analyze_research_note(self, text: str) -> Dict[str, Any]:
        """Analyze research note content"""
        analysis = {
            'type': 'research_note',
            'has_hypothesis': bool(re.search(r'hypothesis|theory|assumption', text, re.IGNORECASE)),
            'has_methodology': bool(re.search(r'method|approach|process', text, re.IGNORECASE)),
            'has_findings': bool(re.search(r'finding|result|discovery', text, re.IGNORECASE)),
            'has_references': bool(re.search(r'\[\[|\]\]|@\w+', text))
        }
        
        return analysis
