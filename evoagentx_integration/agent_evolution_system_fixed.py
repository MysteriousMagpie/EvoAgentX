"""
Advanced Agent Evolution System for VaultPilot

This module implements EvoAgentX's agent evolution capabilities,
allowing VaultPilot agents to learn and improve from user interactions.
"""

import asyncio
import json
import hashlib
import random
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from .api_models import APIResponse


def random_uniform(low: float, high: float) -> float:
    """Generate random float between low and high"""
    return random.uniform(low, high)


def random_normal(mean: float, std: float) -> float:
    """Generate random float from normal distribution"""
    return random.gauss(mean, std)


def clip_value(val: float, min_val: float, max_val: float) -> float:
    """Clip value to range"""
    return max(min_val, min(max_val, val))


def calculate_mean(values: List[float]) -> float:
    """Calculate mean of values"""
    return sum(values) / len(values) if values else 0.0


def calculate_std(values: List[float]) -> float:
    """Calculate standard deviation of values"""
    if not values:
        return 0.0
    mean = calculate_mean(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return math.sqrt(variance)


class EvolutionStrategy(Enum):
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    GENETIC_ALGORITHM = "genetic_algorithm"
    NEURAL_EVOLUTION = "neural_evolution"
    PROMPT_OPTIMIZATION = "prompt_optimization"
    HYBRID_APPROACH = "hybrid_approach"


@dataclass
class AgentDNA:
    """Agent genetic information for evolution"""
    agent_id: str
    generation: int
    prompt_genes: Dict[str, Any]
    behavior_genes: Dict[str, Any]
    performance_genes: Dict[str, Any]
    fitness_score: float = 0.0
    mutations: int = 0
    parent_ids: Optional[List[str]] = None
    creation_timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.creation_timestamp is None:
            self.creation_timestamp = datetime.now()
        if self.parent_ids is None:
            self.parent_ids = []


@dataclass
class InteractionFeedback:
    """User interaction feedback for agent evolution"""
    agent_id: str
    session_id: str
    interaction_type: str
    user_satisfaction: float  # 0.0 to 1.0
    response_quality: float   # 0.0 to 1.0
    task_completion: float    # 0.0 to 1.0
    context_relevance: float  # 0.0 to 1.0
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class AgentEvolutionEngine:
    """
    Advanced agent evolution system leveraging EvoAgentX's
    agent evolution and learning capabilities.
    
    Implements multiple evolution strategies to improve agent
    performance based on user feedback and task success.
    """
    
    def __init__(self, evolution_strategy: EvolutionStrategy = EvolutionStrategy.HYBRID_APPROACH):
        self.evolution_strategy = evolution_strategy
        self.agent_population: Dict[str, AgentDNA] = {}
        self.interaction_history: List[InteractionFeedback] = []
        self.evolution_cycles = 0
        self.fitness_threshold = 0.8
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        
        # Evolution parameters
        self.population_size = 20
        self.elite_percentage = 0.2
        self.diversity_weight = 0.3
        
    async def evolve_agent_from_feedback(self, 
                                       agent_id: str, 
                                       feedback: InteractionFeedback) -> Dict[str, Any]:
        """
        Evolve agent based on user feedback and performance metrics
        
        Args:
            agent_id: ID of the agent to evolve
            feedback: User interaction feedback
            
        Returns:
            Evolution results and new agent configuration
        """
        # Record feedback
        self.interaction_history.append(feedback)
        
        # Get current agent DNA
        if agent_id not in self.agent_population:
            await self._initialize_agent_dna(agent_id)
        
        current_dna = self.agent_population[agent_id]
        
        # Calculate fitness based on feedback
        fitness = await self._calculate_fitness(agent_id, feedback)
        current_dna.fitness_score = fitness
        
        # Determine if evolution is needed
        if fitness < self.fitness_threshold:
            evolved_dna = await self._evolve_agent_dna(current_dna, feedback)
            self.agent_population[agent_id] = evolved_dna
            
            return {
                "evolved": True,
                "generation": evolved_dna.generation,
                "fitness_improvement": evolved_dna.fitness_score - current_dna.fitness_score,
                "mutations": evolved_dna.mutations,
                "evolution_strategy": self.evolution_strategy.value,
                "new_configuration": await self._dna_to_configuration(evolved_dna)
            }
        
        return {
            "evolved": False,
            "current_fitness": fitness,
            "threshold": self.fitness_threshold,
            "recommendation": "Agent performing well, no evolution needed"
        }
    
    async def breed_specialized_agents(self, 
                                     parent_agents: List[str], 
                                     specialization_goal: str) -> Dict[str, Any]:
        """
        Create specialized agents by breeding top performers
        
        Args:
            parent_agents: List of parent agent IDs
            specialization_goal: Goal for the new specialized agent
            
        Returns:
            New specialized agent configuration
        """
        if len(parent_agents) < 2:
            raise ValueError("At least 2 parent agents required for breeding")
        
        # Get parent DNA
        parent_dnas = [self.agent_population[aid] for aid in parent_agents if aid in self.agent_population]
        
        if len(parent_dnas) < 2:
            raise ValueError("Parent agents not found in population")
        
        # Create hybrid DNA
        new_dna = await self._crossover_dna(parent_dnas, specialization_goal)
        
        # Generate new agent ID
        new_agent_id = f"specialized_{hashlib.md5(specialization_goal.encode()).hexdigest()[:8]}"
        
        # Store in population
        self.agent_population[new_agent_id] = new_dna
        
        return {
            "agent_id": new_agent_id,
            "specialization": specialization_goal,
            "parents": parent_agents,
            "generation": new_dna.generation,
            "configuration": await self._dna_to_configuration(new_dna),
            "expected_capabilities": await self._predict_capabilities(new_dna)
        }
    
    async def _initialize_agent_dna(self, agent_id: str):
        """Initialize DNA for a new agent"""
        dna = AgentDNA(
            agent_id=agent_id,
            generation=0,
            prompt_genes={
                "creativity": random_uniform(0.1, 0.9),
                "formality": random_uniform(0.1, 0.9),
                "detail_level": random_uniform(0.1, 0.9),
                "proactivity": random_uniform(0.1, 0.9),
                "empathy": random_uniform(0.1, 0.9)
            },
            behavior_genes={
                "response_length": random_uniform(0.1, 1.0),
                "question_frequency": random_uniform(0.0, 0.5),
                "suggestion_boldness": random_uniform(0.1, 0.9),
                "context_utilization": random_uniform(0.5, 1.0)
            },
            performance_genes={
                "learning_rate": random_uniform(0.01, 0.1),
                "adaptation_speed": random_uniform(0.1, 0.5),
                "memory_retention": random_uniform(0.7, 1.0),
                "specialization_focus": random_uniform(0.0, 1.0)
            }
        )
        self.agent_population[agent_id] = dna
    
    async def _calculate_fitness(self, agent_id: str, feedback: InteractionFeedback) -> float:
        """Calculate agent fitness based on feedback"""
        # Weighted combination of feedback metrics
        weights = {
            "satisfaction": 0.3,
            "quality": 0.25,
            "completion": 0.25,
            "relevance": 0.2
        }
        
        fitness = (
            weights["satisfaction"] * feedback.user_satisfaction +
            weights["quality"] * feedback.response_quality +
            weights["completion"] * feedback.task_completion +
            weights["relevance"] * feedback.context_relevance
        )
        
        return min(max(fitness, 0.0), 1.0)
    
    async def _evolve_agent_dna(self, current_dna: AgentDNA, feedback: InteractionFeedback) -> AgentDNA:
        """Evolve agent DNA based on feedback"""
        new_dna = AgentDNA(
            agent_id=current_dna.agent_id,
            generation=current_dna.generation + 1,
            prompt_genes=current_dna.prompt_genes.copy(),
            behavior_genes=current_dna.behavior_genes.copy(),
            performance_genes=current_dna.performance_genes.copy(),
            mutations=current_dna.mutations + 1,
            parent_ids=[current_dna.agent_id]
        )
        
        # Apply evolution based on feedback
        if feedback.user_satisfaction < 0.5:
            # Adjust empathy and formality
            new_dna.prompt_genes["empathy"] = min(0.9, new_dna.prompt_genes["empathy"] + 0.1)
            new_dna.prompt_genes["formality"] = max(0.1, new_dna.prompt_genes["formality"] - 0.1)
        
        if feedback.response_quality < 0.5:
            # Adjust detail level and context utilization
            new_dna.prompt_genes["detail_level"] = min(0.9, new_dna.prompt_genes["detail_level"] + 0.1)
            new_dna.behavior_genes["context_utilization"] = min(1.0, new_dna.behavior_genes["context_utilization"] + 0.1)
        
        if feedback.task_completion < 0.5:
            # Adjust proactivity and suggestion boldness
            new_dna.prompt_genes["proactivity"] = min(0.9, new_dna.prompt_genes["proactivity"] + 0.1)
            new_dna.behavior_genes["suggestion_boldness"] = min(0.9, new_dna.behavior_genes["suggestion_boldness"] + 0.1)
        
        # Apply random mutations
        new_dna = await self._mutate_dna(new_dna)
        
        return new_dna
    
    async def _crossover_dna(self, parent_dnas: List[AgentDNA], goal: Optional[str] = None) -> AgentDNA:
        """Create offspring DNA from parent agents"""
        if len(parent_dnas) < 2:
            raise ValueError("Need at least 2 parents for crossover")
        
        # Select best parents based on fitness
        parent_dnas.sort(key=lambda x: x.fitness_score, reverse=True)
        parent1, parent2 = parent_dnas[0], parent_dnas[1]
        
        # Create offspring DNA
        offspring = AgentDNA(
            agent_id=f"offspring_{datetime.now().timestamp()}",
            generation=max(parent1.generation, parent2.generation) + 1,
            prompt_genes={},
            behavior_genes={},
            performance_genes={},
            parent_ids=[parent1.agent_id, parent2.agent_id]
        )
        
        # Crossover prompt genes
        for gene in parent1.prompt_genes:
            if random.random() < self.crossover_rate:
                offspring.prompt_genes[gene] = parent1.prompt_genes[gene]
            else:
                offspring.prompt_genes[gene] = parent2.prompt_genes[gene]
        
        # Crossover behavior genes
        for gene in parent1.behavior_genes:
            if random.random() < self.crossover_rate:
                offspring.behavior_genes[gene] = parent1.behavior_genes[gene]
            else:
                offspring.behavior_genes[gene] = parent2.behavior_genes[gene]
        
        # Crossover performance genes
        for gene in parent1.performance_genes:
            if random.random() < self.crossover_rate:
                offspring.performance_genes[gene] = parent1.performance_genes[gene]
            else:
                offspring.performance_genes[gene] = parent2.performance_genes[gene]
        
        return offspring
    
    async def _mutate_dna(self, dna: AgentDNA) -> AgentDNA:
        """Apply random mutations to DNA"""
        mutation_strength = 0.05
        
        # Mutate prompt genes
        for gene in dna.prompt_genes:
            if random.random() < self.mutation_rate:
                mutation = random_normal(0, mutation_strength)
                dna.prompt_genes[gene] = clip_value(dna.prompt_genes[gene] + mutation, 0.0, 1.0)
        
        # Mutate behavior genes
        for gene in dna.behavior_genes:
            if random.random() < self.mutation_rate:
                mutation = random_normal(0, mutation_strength)
                dna.behavior_genes[gene] = clip_value(dna.behavior_genes[gene] + mutation, 0.0, 1.0)
        
        # Mutate performance genes
        for gene in dna.performance_genes:
            if random.random() < self.mutation_rate:
                mutation = random_normal(0, mutation_strength)
                dna.performance_genes[gene] = clip_value(dna.performance_genes[gene] + mutation, 0.0, 1.0)
        
        dna.mutations += 1
        return dna
    
    async def _dna_to_configuration(self, dna: AgentDNA) -> Dict[str, Any]:
        """Convert DNA to agent configuration"""
        return {
            "agent_id": dna.agent_id,
            "generation": dna.generation,
            "prompt_parameters": {
                "creativity_level": dna.prompt_genes.get("creativity", 0.5),
                "formality_level": dna.prompt_genes.get("formality", 0.5),
                "detail_preference": dna.prompt_genes.get("detail_level", 0.5),
                "proactive_suggestions": dna.prompt_genes.get("proactivity", 0.5),
                "empathy_factor": dna.prompt_genes.get("empathy", 0.5)
            },
            "behavior_settings": {
                "preferred_response_length": dna.behavior_genes.get("response_length", 0.5),
                "clarification_frequency": dna.behavior_genes.get("question_frequency", 0.2),
                "suggestion_confidence": dna.behavior_genes.get("suggestion_boldness", 0.5),
                "context_integration": dna.behavior_genes.get("context_utilization", 0.8)
            },
            "performance_metrics": {
                "adaptation_rate": dna.performance_genes.get("learning_rate", 0.05),
                "flexibility": dna.performance_genes.get("adaptation_speed", 0.3),
                "memory_strength": dna.performance_genes.get("memory_retention", 0.85),
                "specialization_degree": dna.performance_genes.get("specialization_focus", 0.5)
            },
            "fitness_score": dna.fitness_score,
            "generation_info": {
                "mutations": dna.mutations,
                "parents": dna.parent_ids,
                "created": dna.creation_timestamp.isoformat() if dna.creation_timestamp else None
            }
        }
    
    async def _predict_capabilities(self, dna: AgentDNA) -> List[str]:
        """Predict agent capabilities based on DNA"""
        capabilities = []
        
        if dna.prompt_genes.get("creativity", 0) > 0.7:
            capabilities.append("creative_writing")
        if dna.prompt_genes.get("detail_level", 0) > 0.7:
            capabilities.append("detailed_analysis")
        if dna.prompt_genes.get("proactivity", 0) > 0.7:
            capabilities.append("proactive_assistance")
        if dna.behavior_genes.get("context_utilization", 0) > 0.8:
            capabilities.append("context_mastery")
        if dna.performance_genes.get("specialization_focus", 0) > 0.7:
            capabilities.append("domain_expertise")
        
        return capabilities
    
    def get_evolution_statistics(self) -> Dict[str, Any]:
        """Get comprehensive evolution statistics"""
        if not self.agent_population:
            return {"error": "No agents in population"}
        
        fitness_scores = [dna.fitness_score for dna in self.agent_population.values()]
        generations = [dna.generation for dna in self.agent_population.values()]
        
        return {
            "population_size": len(self.agent_population),
            "evolution_cycles": self.evolution_cycles,
            "fitness_statistics": {
                "average": calculate_mean(fitness_scores),
                "best": max(fitness_scores),
                "worst": min(fitness_scores),
                "std_dev": calculate_std(fitness_scores)
            },
            "generation_statistics": {
                "average": calculate_mean([float(g) for g in generations]),
                "latest": max(generations),
                "oldest": min(generations)
            },
            "interaction_count": len(self.interaction_history),
            "evolution_strategy": self.evolution_strategy.value
        }
