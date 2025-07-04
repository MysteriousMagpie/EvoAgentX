"""
EvoAgentX Agent Marketplace Integration for VaultPilot

This module integrates VaultPilot with EvoAgentX's agent marketplace,
enabling users to discover, install, and customize specialized agents
for their knowledge management workflows.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from .api_models import APIResponse
from .agent_evolution_system import AgentDNA, AgentEvolutionEngine


class AgentCategory(Enum):
    WRITING_ASSISTANT = "writing_assistant"
    RESEARCH_HELPER = "research_helper"
    PROJECT_MANAGER = "project_manager"
    CREATIVE_COMPANION = "creative_companion"
    KNOWLEDGE_ORGANIZER = "knowledge_organizer"
    TASK_PLANNER = "task_planner"
    CODE_ASSISTANT = "code_assistant"
    LEARNING_TUTOR = "learning_tutor"
    BRAINSTORMING_PARTNER = "brainstorming_partner"
    DATA_ANALYST = "data_analyst"


class AgentComplexity(Enum):
    SIMPLE = "simple"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class MarketplaceAgent:
    """Marketplace agent information"""
    agent_id: str
    name: str
    description: str
    category: AgentCategory
    complexity: AgentComplexity
    rating: float
    downloads: int
    price: float  # 0.0 for free agents
    tags: List[str]
    capabilities: List[str]
    author: str
    version: str
    creation_date: datetime
    last_updated: datetime
    dna_signature: Optional[str] = None
    requirements: Optional[List[str]] = None
    compatible_workflows: Optional[List[str]] = None
    demo_available: bool = False
    certification_level: Optional[str] = None


@dataclass
class AgentReview:
    """Agent marketplace review"""
    review_id: str
    agent_id: str
    user_id: str
    rating: int  # 1-5 stars
    review_text: str
    pros: List[str]
    cons: List[str]
    use_case: str
    timestamp: datetime
    helpful_votes: int = 0


@dataclass
class UserInstallation:
    """User agent installation record"""
    installation_id: str
    user_id: str
    agent_id: str
    installed_date: datetime
    customizations: Dict[str, Any]
    usage_stats: Dict[str, Any]
    satisfaction_rating: Optional[float] = None
    active: bool = True


class EvoAgentXMarketplace:
    """
    Advanced agent marketplace integration for VaultPilot.
    
    Connects users to EvoAgentX's agent ecosystem, enabling
    discovery, installation, and customization of specialized
    AI agents for knowledge management tasks.
    """
    
    def __init__(self, evolution_engine: Optional[AgentEvolutionEngine] = None):
        self.evolution_engine = evolution_engine
        self.marketplace_agents: Dict[str, MarketplaceAgent] = {}
        self.user_installations: Dict[str, List[UserInstallation]] = {}
        self.agent_reviews: Dict[str, List[AgentReview]] = {}
        self.featured_agents: List[str] = []
        self.trending_agents: List[str] = []
        
        # Initialize with sample marketplace agents
        self._initialize_marketplace()
    
    async def discover_agents(self, 
                            category: Optional[AgentCategory] = None,
                            complexity: Optional[AgentComplexity] = None,
                            search_query: Optional[str] = None,
                            tags: Optional[List[str]] = None,
                            free_only: bool = False,
                            min_rating: float = 0.0,
                            sort_by: str = "rating") -> List[MarketplaceAgent]:
        """
        Discover agents in the marketplace based on criteria
        
        Args:
            category: Filter by agent category
            complexity: Filter by complexity level
            search_query: Text search in name/description
            tags: Filter by tags
            free_only: Show only free agents
            min_rating: Minimum rating threshold
            sort_by: Sort criteria (rating, downloads, recent, price)
            
        Returns:
            List of matching marketplace agents
        """
        agents = list(self.marketplace_agents.values())
        
        # Apply filters
        if category:
            agents = [a for a in agents if a.category == category]
        
        if complexity:
            agents = [a for a in agents if a.complexity == complexity]
        
        if search_query:
            query_lower = search_query.lower()
            agents = [a for a in agents if 
                     query_lower in a.name.lower() or 
                     query_lower in a.description.lower()]
        
        if tags:
            agents = [a for a in agents if any(tag in a.tags for tag in tags)]
        
        if free_only:
            agents = [a for a in agents if a.price == 0.0]
        
        if min_rating > 0.0:
            agents = [a for a in agents if a.rating >= min_rating]
        
        # Sort results
        if sort_by == "rating":
            agents.sort(key=lambda x: x.rating, reverse=True)
        elif sort_by == "downloads":
            agents.sort(key=lambda x: x.downloads, reverse=True)
        elif sort_by == "recent":
            agents.sort(key=lambda x: x.last_updated, reverse=True)
        elif sort_by == "price":
            agents.sort(key=lambda x: x.price)
        
        return agents
    
    async def get_agent_details(self, agent_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a marketplace agent
        
        Args:
            agent_id: ID of the agent to retrieve
            
        Returns:
            Detailed agent information including reviews and compatibility
        """
        if agent_id not in self.marketplace_agents:
            return {"error": "Agent not found"}
        
        agent = self.marketplace_agents[agent_id]
        reviews = self.agent_reviews.get(agent_id, [])
        
        # Calculate review statistics
        review_stats = await self._calculate_review_stats(reviews)
        
        # Check compatibility with user's vault
        compatibility = await self._check_agent_compatibility(agent)
        
        return {
            "agent": asdict(agent),
            "reviews": {
                "total_reviews": len(reviews),
                "statistics": review_stats,
                "recent_reviews": [asdict(r) for r in reviews[-5:]]  # Last 5 reviews
            },
            "compatibility": compatibility,
            "installation_info": {
                "requirements": agent.requirements or [],
                "estimated_setup_time": await self._estimate_setup_time(agent),
                "customization_options": await self._get_customization_options(agent)
            },
            "similar_agents": await self._find_similar_agents(agent_id)
        }
    
    async def install_agent(self, 
                          user_id: str, 
                          agent_id: str, 
                          customizations: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Install an agent for a user with optional customizations
        
        Args:
            user_id: ID of the user installing the agent
            agent_id: ID of the agent to install
            customizations: Custom configuration options
            
        Returns:
            Installation result and agent configuration
        """
        if agent_id not in self.marketplace_agents:
            return {"error": "Agent not found in marketplace"}
        
        agent = self.marketplace_agents[agent_id]
        
        # Check if user already has this agent installed
        user_installations = self.user_installations.get(user_id, [])
        existing = next((i for i in user_installations if i.agent_id == agent_id and i.active), None)
        
        if existing:
            return {"error": "Agent already installed", "installation_id": existing.installation_id}
        
        # Create installation record
        installation = UserInstallation(
            installation_id=f"{user_id}_{agent_id}_{datetime.now().timestamp()}",
            user_id=user_id,
            agent_id=agent_id,
            installed_date=datetime.now(),
            customizations=customizations or {},
            usage_stats={
                "total_interactions": 0,
                "avg_satisfaction": 0.0,
                "preferred_tasks": [],
                "last_used": None
            }
        )
        
        # Add to user installations
        if user_id not in self.user_installations:
            self.user_installations[user_id] = []
        self.user_installations[user_id].append(installation)
        
        # Update agent download count
        agent.downloads += 1
        
        # Generate agent configuration
        agent_config = await self._generate_agent_configuration(agent, customizations)
        
        # If evolution engine is available, create evolved version
        if self.evolution_engine and agent.dna_signature:
            evolved_config = await self._create_evolved_agent(agent, customizations)
            agent_config.update({"evolved_features": evolved_config})
        
        return {
            "success": True,
            "installation_id": installation.installation_id,
            "agent_configuration": agent_config,
            "setup_instructions": await self._generate_setup_instructions(agent),
            "quick_start_guide": await self._generate_quick_start_guide(agent)
        }
    
    async def customize_agent(self, 
                            user_id: str, 
                            installation_id: str, 
                            customizations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Customize an installed agent's behavior and parameters
        
        Args:
            user_id: ID of the user
            installation_id: ID of the agent installation
            customizations: New customization parameters
            
        Returns:
            Updated agent configuration
        """
        # Find the installation
        user_installations = self.user_installations.get(user_id, [])
        installation = next((i for i in user_installations if i.installation_id == installation_id), None)
        
        if not installation:
            return {"error": "Installation not found"}
        
        # Update customizations
        installation.customizations.update(customizations)
        
        # Get agent info
        agent = self.marketplace_agents[installation.agent_id]
        
        # Generate new configuration
        updated_config = await self._generate_agent_configuration(agent, installation.customizations)
        
        # If evolution engine is available, adapt based on user preferences
        if self.evolution_engine:
            adaptation = await self._adapt_agent_to_user(agent, installation, customizations)
            updated_config.update({"adaptations": adaptation})
        
        return {
            "success": True,
            "updated_configuration": updated_config,
            "customization_summary": await self._summarize_customizations(customizations),
            "recommended_tweaks": await self._suggest_additional_customizations(agent, installation)
        }
    
    async def submit_review(self, 
                          user_id: str, 
                          agent_id: str, 
                          rating: int, 
                          review_text: str,
                          pros: List[str],
                          cons: List[str],
                          use_case: str) -> Dict[str, Any]:
        """
        Submit a review for a marketplace agent
        
        Args:
            user_id: ID of the reviewing user
            agent_id: ID of the agent being reviewed
            rating: Rating from 1-5 stars
            review_text: Detailed review text
            pros: List of positive aspects
            cons: List of negative aspects
            use_case: How the user employed the agent
            
        Returns:
            Review submission result
        """
        if agent_id not in self.marketplace_agents:
            return {"error": "Agent not found"}
        
        if not (1 <= rating <= 5):
            return {"error": "Rating must be between 1 and 5"}
        
        # Check if user has this agent installed
        user_installations = self.user_installations.get(user_id, [])
        has_installation = any(i.agent_id == agent_id for i in user_installations)
        
        if not has_installation:
            return {"error": "Can only review installed agents"}
        
        # Create review
        review = AgentReview(
            review_id=f"{user_id}_{agent_id}_{datetime.now().timestamp()}",
            agent_id=agent_id,
            user_id=user_id,
            rating=rating,
            review_text=review_text,
            pros=pros,
            cons=cons,
            use_case=use_case,
            timestamp=datetime.now()
        )
        
        # Add to agent reviews
        if agent_id not in self.agent_reviews:
            self.agent_reviews[agent_id] = []
        self.agent_reviews[agent_id].append(review)
        
        # Update agent rating
        await self._update_agent_rating(agent_id)
        
        return {
            "success": True,
            "review_id": review.review_id,
            "updated_agent_rating": self.marketplace_agents[agent_id].rating,
            "review_impact": await self._calculate_review_impact(review)
        }
    
    async def get_personalized_recommendations(self, user_id: str) -> Dict[str, Any]:
        """
        Get personalized agent recommendations for a user
        
        Args:
            user_id: ID of the user to get recommendations for
            
        Returns:
            Personalized agent recommendations with explanations
        """
        user_installations = self.user_installations.get(user_id, [])
        
        if not user_installations:
            # New user - recommend popular agents
            return await self._get_popular_recommendations()
        
        # Analyze user preferences
        user_profile = await self._analyze_user_preferences(user_id)
        
        # Find compatible agents
        compatible_agents = await self._find_compatible_agents(user_profile)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(user_profile, compatible_agents)
        
        return {
            "user_profile": user_profile,
            "recommendations": recommendations,
            "trending_in_category": await self._get_trending_in_user_categories(user_profile),
            "similar_users_like": await self._get_collaborative_recommendations(user_id)
        }
    
    def _initialize_marketplace(self):
        """Initialize marketplace with sample agents"""
        sample_agents = [
            MarketplaceAgent(
                agent_id="zettelkasten_master",
                name="Zettelkasten Master",
                description="Advanced note-taking and knowledge linking specialist using Zettelkasten methodology",
                category=AgentCategory.KNOWLEDGE_ORGANIZER,
                complexity=AgentComplexity.ADVANCED,
                rating=4.8,
                downloads=15420,
                price=0.0,
                tags=["zettelkasten", "note-taking", "knowledge-graph", "linking"],
                capabilities=["smart_linking", "note_analysis", "knowledge_mapping"],
                author="EvoAgentX Research",
                version="2.1.0",
                creation_date=datetime(2024, 8, 15),
                last_updated=datetime(2024, 12, 1),
                demo_available=True,
                certification_level="Premium"
            ),
            MarketplaceAgent(
                agent_id="research_synthesizer",
                name="Research Synthesizer Pro",
                description="Synthesizes research from multiple sources and creates comprehensive literature reviews",
                category=AgentCategory.RESEARCH_HELPER,
                complexity=AgentComplexity.EXPERT,
                rating=4.9,
                downloads=8750,
                price=19.99,
                tags=["research", "synthesis", "literature-review", "academic"],
                capabilities=["source_analysis", "synthesis", "citation_management"],
                author="Academic AI Labs",
                version="3.0.2",
                creation_date=datetime(2024, 6, 10),
                last_updated=datetime(2024, 11, 28),
                demo_available=True,
                certification_level="Premium"
            ),
            MarketplaceAgent(
                agent_id="creative_muse",
                name="Creative Muse",
                description="Inspiring creative writing companion for storytelling and ideation",
                category=AgentCategory.CREATIVE_COMPANION,
                complexity=AgentComplexity.INTERMEDIATE,
                rating=4.6,
                downloads=22100,
                price=0.0,
                tags=["creative-writing", "storytelling", "ideation", "inspiration"],
                capabilities=["story_development", "character_creation", "plot_assistance"],
                author="Creative AI Collective",
                version="1.8.3",
                creation_date=datetime(2024, 9, 5),
                last_updated=datetime(2024, 12, 15),
                demo_available=True,
                certification_level="Standard"
            )
        ]
        
        for agent in sample_agents:
            self.marketplace_agents[agent.agent_id] = agent
        
        # Set featured and trending
        self.featured_agents = ["zettelkasten_master", "research_synthesizer"]
        self.trending_agents = ["creative_muse", "zettelkasten_master"]
    
    async def _calculate_review_stats(self, reviews: List[AgentReview]) -> Dict[str, Any]:
        """Calculate review statistics"""
        if not reviews:
            return {"average_rating": 0.0, "rating_distribution": {}}
        
        ratings = [r.rating for r in reviews]
        avg_rating = sum(ratings) / len(ratings)
        
        distribution = {i: ratings.count(i) for i in range(1, 6)}
        
        return {
            "average_rating": round(avg_rating, 2),
            "total_reviews": len(reviews),
            "rating_distribution": distribution,
            "most_common_pros": await self._extract_common_terms([r.pros for r in reviews]),
            "most_common_cons": await self._extract_common_terms([r.cons for r in reviews])
        }
    
    async def _extract_common_terms(self, term_lists: List[List[str]]) -> List[str]:
        """Extract most common terms from lists"""
        from collections import Counter
        all_terms = [term for sublist in term_lists for term in sublist]
        return [term for term, count in Counter(all_terms).most_common(5)]
    
    async def _check_agent_compatibility(self, agent: MarketplaceAgent) -> Dict[str, Any]:
        """Check agent compatibility with user setup"""
        return {
            "compatible": True,
            "requirements_met": True,
            "warnings": [],
            "recommendations": [
                "Enable WebSocket for real-time features",
                "Consider increasing context window for better performance"
            ]
        }
    
    async def _generate_agent_configuration(self, 
                                          agent: MarketplaceAgent, 
                                          customizations: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate agent configuration based on marketplace info and customizations"""
        base_config = {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "category": agent.category.value,
            "capabilities": agent.capabilities,
            "complexity_level": agent.complexity.value,
            "version": agent.version
        }
        
        if customizations:
            base_config.update({"customizations": customizations})
        
        return base_config
    
    async def _update_agent_rating(self, agent_id: str):
        """Update agent rating based on all reviews"""
        reviews = self.agent_reviews.get(agent_id, [])
        if reviews:
            ratings = [r.rating for r in reviews]
            new_rating = sum(ratings) / len(ratings)
            self.marketplace_agents[agent_id].rating = round(new_rating, 1)
    
    async def _analyze_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Analyze user preferences based on installation history"""
        installations = self.user_installations.get(user_id, [])
        
        if not installations:
            return {"categories": [], "complexity_preference": "intermediate", "price_sensitivity": "free"}
        
        # Analyze categories
        categories = [self.marketplace_agents[i.agent_id].category.value for i in installations]
        most_common_category = max(set(categories), key=categories.count)
        
        # Analyze complexity
        complexities = [self.marketplace_agents[i.agent_id].complexity.value for i in installations]
        preferred_complexity = max(set(complexities), key=complexities.count)
        
        return {
            "preferred_categories": list(set(categories)),
            "most_used_category": most_common_category,
            "complexity_preference": preferred_complexity,
            "total_installations": len(installations),
            "active_agents": len([i for i in installations if i.active])
        }
    
    async def _estimate_setup_time(self, agent: MarketplaceAgent) -> str:
        """Estimate setup time for an agent"""
        complexity_times = {
            AgentComplexity.SIMPLE: "2-5 minutes",
            AgentComplexity.INTERMEDIATE: "5-10 minutes", 
            AgentComplexity.ADVANCED: "10-15 minutes",
            AgentComplexity.EXPERT: "15-30 minutes"
        }
        return complexity_times.get(agent.complexity, "5-10 minutes")
    
    async def _get_customization_options(self, agent: MarketplaceAgent) -> List[Dict[str, Any]]:
        """Get available customization options for an agent"""
        base_options = [
            {"name": "response_style", "type": "select", "options": ["formal", "casual", "creative"]},
            {"name": "detail_level", "type": "slider", "range": [1, 10], "default": 5},
            {"name": "proactivity", "type": "slider", "range": [1, 10], "default": 7}
        ]
        
        category_options = {
            AgentCategory.WRITING_ASSISTANT: [
                {"name": "writing_tone", "type": "select", "options": ["academic", "business", "creative", "technical"]}
            ],
            AgentCategory.RESEARCH_HELPER: [
                {"name": "source_types", "type": "multiselect", "options": ["academic", "news", "books", "web"]}
            ]
        }
        
        return base_options + category_options.get(agent.category, [])
    
    async def _find_similar_agents(self, agent_id: str) -> List[str]:
        """Find agents similar to the given agent"""
        if agent_id not in self.marketplace_agents:
            return []
        
        target_agent = self.marketplace_agents[agent_id]
        similar = []
        
        for aid, agent in self.marketplace_agents.items():
            if aid == agent_id:
                continue
            
            # Same category gets priority
            if agent.category == target_agent.category:
                similar.append(aid)
            # Similar tags
            elif any(tag in agent.tags for tag in target_agent.tags):
                similar.append(aid)
        
        return similar[:5]  # Return top 5
    
    async def _create_evolved_agent(self, agent: MarketplaceAgent, customizations: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create an evolved version of an agent using the evolution engine"""
        if not self.evolution_engine:
            return {}
        
        # Create base DNA for the agent
        await self.evolution_engine._initialize_agent_dna(agent.agent_id)
        
        # Apply customizations as evolutionary pressure
        if customizations:
            # Simulate feedback based on customizations
            from .agent_evolution_system import InteractionFeedback
            feedback = InteractionFeedback(
                agent_id=agent.agent_id,
                session_id="marketplace_install",
                interaction_type="customization",
                user_satisfaction=0.8,
                response_quality=0.8,
                task_completion=0.8,
                context_relevance=0.8,
                timestamp=datetime.now()
            )
            
            result = await self.evolution_engine.evolve_agent_from_feedback(agent.agent_id, feedback)
            return result
        
        return {}
    
    async def _generate_setup_instructions(self, agent: MarketplaceAgent) -> List[str]:
        """Generate setup instructions for an agent"""
        base_instructions = [
            "1. Agent will be automatically configured with default settings",
            "2. Test the agent with a simple query to verify functionality",
            "3. Customize agent parameters in the settings panel if needed"
        ]
        
        category_instructions = {
            AgentCategory.RESEARCH_HELPER: [
                "4. Configure preferred research databases and sources",
                "5. Set up citation format preferences"
            ],
            AgentCategory.WRITING_ASSISTANT: [
                "4. Select your preferred writing style and tone",
                "5. Configure grammar and style checking preferences"
            ]
        }
        
        return base_instructions + category_instructions.get(agent.category, [])
    
    async def _generate_quick_start_guide(self, agent: MarketplaceAgent) -> Dict[str, Any]:
        """Generate a quick start guide for an agent"""
        return {
            "title": f"Quick Start with {agent.name}",
            "description": f"Get up and running with {agent.name} in minutes",
            "steps": [
                {"step": 1, "action": "Open VaultPilot chat", "description": "Click the chat icon in Obsidian"},
                {"step": 2, "action": f"Select {agent.name}", "description": "Choose your new agent from the dropdown"},
                {"step": 3, "action": "Start with a test query", "description": "Try asking a simple question to test functionality"},
                {"step": 4, "action": "Explore capabilities", "description": f"Try the agent's specialized features: {', '.join(agent.capabilities[:3])}"}
            ],
            "example_queries": await self._get_example_queries(agent),
            "tips": [
                "Be specific in your requests for better results",
                "Use the agent's specialized capabilities for best performance",
                "Provide context about your current work for more relevant suggestions"
            ]
        }
    
    async def _get_example_queries(self, agent: MarketplaceAgent) -> List[str]:
        """Get example queries for an agent based on its category"""
        examples = {
            AgentCategory.WRITING_ASSISTANT: [
                "Help me improve this paragraph's clarity",
                "Suggest a better conclusion for my essay",
                "What's a more engaging way to start this section?"
            ],
            AgentCategory.RESEARCH_HELPER: [
                "Find recent papers about machine learning ethics",
                "Summarize the key findings from these research notes",
                "What are the main arguments in this literature?"
            ],
            AgentCategory.KNOWLEDGE_ORGANIZER: [
                "Suggest how to link these related notes",
                "Help me organize my project notes better",
                "What connections am I missing in my knowledge graph?"
            ]
        }
        return examples.get(agent.category, ["How can you help me with my work?"])
    
    async def _adapt_agent_to_user(self, agent: MarketplaceAgent, installation: UserInstallation, customizations: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt agent behavior based on user preferences and usage patterns"""
        adaptations = {
            "behavioral_adjustments": {},
            "preference_learning": {},
            "performance_optimizations": {}
        }
        
        # Analyze usage patterns if available
        if installation.usage_stats.get("total_interactions", 0) > 10:
            adaptations["behavioral_adjustments"] = {
                "response_length": "optimized_for_user_preferences",
                "formality_level": "adapted_to_user_style"
            }
        
        # Apply customizations
        if customizations:
            adaptations["preference_learning"] = {
                "custom_settings_applied": list(customizations.keys()),
                "learning_status": "active"
            }
        
        return adaptations
    
    async def _summarize_customizations(self, customizations: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize the customizations applied to an agent"""
        return {
            "total_customizations": len(customizations),
            "categories": list(customizations.keys()),
            "impact_level": "moderate" if len(customizations) < 5 else "significant",
            "summary": f"Applied {len(customizations)} customizations to personalize the agent behavior"
        }
    
    async def _suggest_additional_customizations(self, agent: MarketplaceAgent, installation: UserInstallation) -> List[Dict[str, Any]]:
        """Suggest additional customizations based on agent capabilities and user patterns"""
        suggestions = []
        
        # Based on agent category
        if agent.category == AgentCategory.WRITING_ASSISTANT:
            suggestions.append({
                "setting": "grammar_strictness",
                "reason": "Fine-tune grammar checking sensitivity",
                "impact": "Better writing assistance"
            })
        
        # Based on usage patterns
        if installation.usage_stats.get("total_interactions", 0) > 50:
            suggestions.append({
                "setting": "advanced_features",
                "reason": "You're a power user - unlock advanced capabilities",
                "impact": "Enhanced functionality"
            })
        
        return suggestions
    
    async def _calculate_review_impact(self, review: AgentReview) -> Dict[str, Any]:
        """Calculate the impact of a review on the agent's standing"""
        return {
            "rating_impact": "positive" if review.rating >= 4 else "neutral" if review.rating == 3 else "negative",
            "visibility_boost": review.rating >= 4,
            "estimated_download_impact": f"+{review.rating * 10}%" if review.rating >= 4 else "neutral"
        }
    
    async def _get_popular_recommendations(self) -> Dict[str, Any]:
        """Get popular agent recommendations for new users"""
        popular_agents = sorted(self.marketplace_agents.values(), key=lambda x: x.downloads, reverse=True)[:5]
        
        return {
            "user_profile": {"type": "new_user", "preferences": "unknown"},
            "recommendations": [
                {
                    "agent": asdict(agent),
                    "reason": "Popular choice with high user satisfaction",
                    "confidence": 0.8
                } for agent in popular_agents
            ]
        }
    
    async def _find_compatible_agents(self, user_profile: Dict[str, Any]) -> List[MarketplaceAgent]:
        """Find agents compatible with user preferences"""
        compatible = []
        preferred_categories = user_profile.get("preferred_categories", [])
        
        for agent in self.marketplace_agents.values():
            if agent.category.value in preferred_categories:
                compatible.append(agent)
        
        return compatible
    
    async def _generate_recommendations(self, user_profile: Dict[str, Any], compatible_agents: List[MarketplaceAgent]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        recommendations = []
        
        for agent in compatible_agents[:3]:  # Top 3 recommendations
            recommendations.append({
                "agent": asdict(agent),
                "reason": f"Matches your preference for {agent.category.value} agents",
                "confidence": 0.85,
                "personalization_factors": ["category_match", "rating_high"]
            })
        
        return recommendations
    
    async def _get_trending_in_user_categories(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get trending agents in user's preferred categories"""
        preferred_categories = user_profile.get("preferred_categories", [])
        trending = []
        
        for agent_id in self.trending_agents:
            agent = self.marketplace_agents[agent_id]
            if agent.category.value in preferred_categories:
                trending.append({
                    "agent": asdict(agent),
                    "trend_reason": "Rapidly gaining popularity"
                })
        
        return trending
    
    async def _get_collaborative_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get recommendations based on similar users"""
        # Simplified collaborative filtering
        return [
            {
                "agent": asdict(list(self.marketplace_agents.values())[0]),
                "reason": "Users with similar preferences also use this agent",
                "similarity_score": 0.75
            }
        ]
