"""
VaultPilot Agent Manager Service

This service manages AI agents, their capabilities, and execution contexts
for the VaultPilot integration with EvoAgentX.
"""

import uuid
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from .api_models import (
    Agent, AgentCreateRequest, AgentExecuteRequest, 
    APIResponse, ChatRequest, ChatResponse
)


class AgentManager:
    """
    AI Agent management service for VaultPilot.
    
    Handles agent lifecycle, capability management, and execution coordination.
    """
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}
        self.execution_history: Dict[str, List[Dict]] = {}
        self._setup_default_agents()
    
    async def get_all_agents(self) -> List[Agent]:
        """Get list of all available agents"""
        return list(self.agents.values())
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get specific agent by ID"""
        return self.agents.get(agent_id)
    
    async def create_agent(self, request: AgentCreateRequest) -> Agent:
        """
        Create a new custom agent
        
        Args:
            request: AgentCreateRequest with agent configuration
            
        Returns:
            Created Agent instance
        """
        agent = Agent(
            name=request.name,
            description=request.description,
            capabilities=request.capabilities or [],
            system_prompt=request.system_prompt
        )
        
        self.agents[agent.id] = agent
        self.agent_capabilities[agent.id] = agent.capabilities
        self.execution_history[agent.id] = []
        
        return agent
    
    async def execute_agent_task(self, request: AgentExecuteRequest) -> ChatResponse:
        """
        Execute a task using a specific agent
        
        Args:
            request: AgentExecuteRequest with agent ID and task
            
        Returns:
            ChatResponse with agent's response
        """
        agent = self.agents.get(request.agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {request.agent_id}")
        
        if not agent.active:
            raise ValueError(f"Agent is inactive: {agent.name}")
        
        try:
            # Execute task using agent's capabilities
            response = await self._execute_agent_task_internal(agent, request)
            
            # Record execution history
            execution_record = {
                "timestamp": datetime.now().isoformat(),
                "task": request.task,
                "context": request.context,
                "response": response.response,
                "success": True
            }
            self.execution_history[agent.id].append(execution_record)
            
            return response
            
        except Exception as e:
            # Record failed execution
            execution_record = {
                "timestamp": datetime.now().isoformat(),
                "task": request.task,
                "context": request.context,
                "error": str(e),
                "success": False
            }
            self.execution_history[agent.id].append(execution_record)
            
            raise Exception(f"Agent execution failed: {str(e)}")
    
    async def auto_select_agent(self, task: str, context: Optional[str] = None) -> Optional[Agent]:
        """
        Automatically select the best agent for a given task
        
        Args:
            task: Task description
            context: Optional task context
            
        Returns:
            Best matching Agent or None if no suitable agent found
        """
        if not self.agents:
            return None
        
        # Analyze task to determine required capabilities
        required_capabilities = await self._analyze_task_requirements(task, context)
        
        # Score agents based on capability match
        agent_scores = []
        for agent in self.agents.values():
            if not agent.active:
                continue
                
            score = self._calculate_agent_score(agent, required_capabilities, task)
            agent_scores.append((score, agent))
        
        if not agent_scores:
            return None
        
        # Return agent with highest score
        agent_scores.sort(key=lambda x: x[0], reverse=True)
        return agent_scores[0][1] if agent_scores[0][0] > 0.3 else None
    
    async def get_agent_capabilities(self, agent_id: str) -> List[str]:
        """Get capabilities for specific agent"""
        return self.agent_capabilities.get(agent_id, [])
    
    async def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Agent:
        """Update agent configuration"""
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        # Update allowed fields
        if "name" in updates:
            agent.name = updates["name"]
        if "description" in updates:
            agent.description = updates["description"]
        if "capabilities" in updates:
            agent.capabilities = updates["capabilities"]
            self.agent_capabilities[agent_id] = agent.capabilities
        if "active" in updates:
            agent.active = updates["active"]
        if "system_prompt" in updates:
            agent.system_prompt = updates["system_prompt"]
        
        return agent
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent"""
        if agent_id not in self.agents:
            return False
        
        del self.agents[agent_id]
        if agent_id in self.agent_capabilities:
            del self.agent_capabilities[agent_id]
        if agent_id in self.execution_history:
            del self.execution_history[agent_id]
        
        return True
    
    async def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get usage statistics for an agent"""
        if agent_id not in self.execution_history:
            return {"total_executions": 0, "success_rate": 0.0, "last_used": None}
        
        history = self.execution_history[agent_id]
        total = len(history)
        successful = sum(1 for record in history if record.get("success", False))
        
        return {
            "total_executions": total,
            "success_rate": successful / total if total > 0 else 0.0,
            "last_used": history[-1]["timestamp"] if history else None,
            "recent_tasks": [record["task"] for record in history[-5:]]
        }
    
    def _setup_default_agents(self):
        """Setup default VaultPilot agents"""
        # VaultPilot Copilot Agent
        copilot_agent = Agent(
            name="VaultPilot Copilot",
            description="Intelligent writing assistant and knowledge management copilot",
            capabilities=[
                "auto_completion",
                "writing_assistance", 
                "note_linking",
                "content_analysis",
                "knowledge_synthesis"
            ],
            system_prompt=self._get_copilot_system_prompt()
        )
        self.agents[copilot_agent.id] = copilot_agent
        self.agent_capabilities[copilot_agent.id] = copilot_agent.capabilities
        self.execution_history[copilot_agent.id] = []
        
        # Research Assistant Agent
        research_agent = Agent(
            name="Research Assistant",
            description="Specialized agent for research tasks, literature review, and analysis",
            capabilities=[
                "research_synthesis",
                "literature_review",
                "source_analysis",
                "fact_checking",
                "citation_management"
            ],
            system_prompt=self._get_research_system_prompt()
        )
        self.agents[research_agent.id] = research_agent
        self.agent_capabilities[research_agent.id] = research_agent.capabilities
        self.execution_history[research_agent.id] = []
        
        # Organization Expert Agent
        organization_agent = Agent(
            name="Organization Expert", 
            description="Vault organization and structure optimization specialist",
            capabilities=[
                "vault_analysis",
                "structure_optimization",
                "template_creation",
                "workflow_design",
                "productivity_improvement"
            ],
            system_prompt=self._get_organization_system_prompt()
        )
        self.agents[organization_agent.id] = organization_agent
        self.agent_capabilities[organization_agent.id] = organization_agent.capabilities
        self.execution_history[organization_agent.id] = []
        
        # Creative Writing Agent
        creative_agent = Agent(
            name="Creative Writing Assistant",
            description="Specialized agent for creative writing, storytelling, and narrative development",
            capabilities=[
                "creative_writing",
                "story_development",
                "character_creation",
                "plot_assistance",
                "style_improvement"
            ],
            system_prompt=self._get_creative_system_prompt()
        )
        self.agents[creative_agent.id] = creative_agent
        self.agent_capabilities[creative_agent.id] = creative_agent.capabilities
        self.execution_history[creative_agent.id] = []
    
    async def _execute_agent_task_internal(self, agent: Agent, request: AgentExecuteRequest) -> ChatResponse:
        """Internal agent task execution"""
        # TODO: Implement actual agent execution
        # This should integrate with your main AI processing system
        
        # Create a chat request with agent-specific system prompt
        chat_request = ChatRequest(
            message=request.task,
            vault_context=request.context or "",
            agent_id=agent.id
        )
        
        # Simulate agent response (replace with actual AI call)
        response_text = await self._generate_agent_response(agent, chat_request)
        
        return ChatResponse(
            response=response_text,
            agent_used=agent.name,
            conversation_id=str(uuid.uuid4()),
            context_used=request.context or "",
            timestamp=datetime.now().isoformat(),
            metadata={
                "agent_id": agent.id,
                "agent_capabilities": agent.capabilities,
                "task_type": self._classify_task_type(request.task)
            }
        )
    
    async def _generate_agent_response(self, agent: Agent, request: ChatRequest) -> str:
        """Generate agent-specific response"""
        # TODO: Replace with actual AI generation
        # This should use the agent's system prompt and capabilities
        
        task_type = self._classify_task_type(request.message)
        context = request.vault_context or ""
        
        if "copilot" in agent.name.lower():
            return await self._generate_copilot_response(request.message, context)
        elif "research" in agent.name.lower():
            return await self._generate_research_response(request.message, context)
        elif "organization" in agent.name.lower():
            return await self._generate_organization_response(request.message, context)
        elif "creative" in agent.name.lower():
            return await self._generate_creative_response(request.message, context)
        else:
            return f"Agent {agent.name} processed your request: {request.message}"
    
    async def _analyze_task_requirements(self, task: str, context: Optional[str]) -> List[str]:
        """Analyze task to determine required capabilities"""
        requirements = []
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["write", "writing", "draft", "compose"]):
            requirements.extend(["writing_assistance", "creative_writing"])
        
        if any(word in task_lower for word in ["research", "analyze", "study", "investigate"]):
            requirements.extend(["research_synthesis", "source_analysis"])
        
        if any(word in task_lower for word in ["organize", "structure", "plan", "workflow"]):
            requirements.extend(["vault_analysis", "structure_optimization"])
        
        if any(word in task_lower for word in ["complete", "finish", "suggest", "help"]):
            requirements.extend(["auto_completion", "writing_assistance"])
        
        if any(word in task_lower for word in ["link", "connect", "relate", "reference"]):
            requirements.extend(["note_linking", "knowledge_synthesis"])
        
        return requirements
    
    def _calculate_agent_score(self, agent: Agent, required_capabilities: List[str], task: str) -> float:
        """Calculate agent suitability score for a task"""
        if not required_capabilities:
            return 0.5  # Neutral score if no specific requirements
        
        # Calculate capability overlap
        agent_caps = set(agent.capabilities)
        required_caps = set(required_capabilities)
        overlap = len(agent_caps & required_caps)
        
        if overlap == 0:
            return 0.0
        
        # Base score from capability overlap
        capability_score = overlap / len(required_caps)
        
        # Bonus for exact matches in agent name/description
        name_bonus = 0.0
        task_lower = task.lower()
        agent_name_lower = agent.name.lower()
        agent_desc_lower = agent.description.lower()
        
        if any(word in agent_name_lower for word in task_lower.split()):
            name_bonus += 0.2
        
        if any(word in agent_desc_lower for word in task_lower.split()):
            name_bonus += 0.1
        
        return min(1.0, capability_score + name_bonus)
    
    def _classify_task_type(self, task: str) -> str:
        """Classify task type for processing"""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["write", "writing", "draft", "compose"]):
            return "writing"
        elif any(word in task_lower for word in ["research", "analyze", "study"]):
            return "research"
        elif any(word in task_lower for word in ["organize", "structure", "plan"]):
            return "organization"
        elif any(word in task_lower for word in ["create", "story", "creative"]):
            return "creative"
        else:
            return "general"
    
    # Agent response generators (placeholder implementations)
    async def _generate_copilot_response(self, task: str, context: str) -> str:
        """Generate copilot agent response"""
        return f"As your VaultPilot Copilot, I'll help you with: {task}. Based on your vault context, I suggest focusing on the key concepts and connections in your notes."
    
    async def _generate_research_response(self, task: str, context: str) -> str:
        """Generate research agent response"""
        return f"For your research task '{task}', I recommend starting with a literature review and identifying key sources. I can help analyze the research landscape and synthesize findings."
    
    async def _generate_organization_response(self, task: str, context: str) -> str:
        """Generate organization agent response"""
        return f"To organize your vault for '{task}', I suggest creating a hierarchical structure with clear categories and using consistent naming conventions. Let me analyze your current structure first."
    
    async def _generate_creative_response(self, task: str, context: str) -> str:
        """Generate creative agent response"""
        return f"For your creative project '{task}', I can help with story development, character creation, and narrative structure. Let's start by exploring your creative vision and goals."
    
    # System prompts for different agent types
    def _get_copilot_system_prompt(self) -> str:
        """Get system prompt for copilot agent"""
        return """You are the VaultPilot Copilot, an intelligent writing assistant specialized in knowledge management and note-taking. 
        You help users with auto-completion, writing assistance, note linking, and knowledge synthesis. 
        Focus on improving productivity and creating connections between ideas."""
    
    def _get_research_system_prompt(self) -> str:
        """Get system prompt for research agent"""
        return """You are a Research Assistant specialized in academic research, literature review, and analysis.
        You help users synthesize research findings, analyze sources, check facts, and manage citations.
        Focus on maintaining academic rigor and providing evidence-based insights."""
    
    def _get_organization_system_prompt(self) -> str:
        """Get system prompt for organization agent"""
        return """You are an Organization Expert focused on vault structure optimization and productivity improvement.
        You help users organize their knowledge base, create efficient workflows, and design effective templates.
        Focus on creating sustainable organizational systems."""
    
    def _get_creative_system_prompt(self) -> str:
        """Get system prompt for creative agent"""
        return """You are a Creative Writing Assistant specialized in storytelling and narrative development.
        You help users with creative writing, story development, character creation, and plot assistance.
        Focus on enhancing creativity while maintaining narrative coherence."""
    
    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        """Process a chat request with an agent"""
        try:
            # Auto-select agent if not specified
            if request.agent_id:
                agent = await self.get_agent(request.agent_id)
                if not agent:
                    raise ValueError(f"Agent {request.agent_id} not found")
            else:
                # Auto-select the best agent for this task
                agent = await self.auto_select_agent(request.message, request.vault_context)
                if not agent:
                    # Default to the first available agent
                    agents = await self.get_all_agents()
                    agent = agents[0] if agents else None
                    
            if not agent:
                raise ValueError("No agents available")
            
            # Generate response
            response_text = await self._generate_agent_response(agent, request)
            
            return ChatResponse(
                response=response_text,
                conversation_id=request.conversation_id or str(uuid.uuid4()),
                agent_name=agent.name
            )
        except Exception as e:
            return ChatResponse(
                response=f"Sorry, I encountered an error: {str(e)}",
                conversation_id=request.conversation_id or str(uuid.uuid4()),
                agent_name="System"
            )

    async def get_conversation_history(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation history - placeholder implementation"""
        # TODO: Implement conversation history storage
        return {
            "conversation_id": conversation_id,
            "messages": []
        }

    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete conversation - placeholder implementation"""
        # TODO: Implement conversation deletion
        return True

    async def execute_agent(self, request: AgentExecuteRequest) -> Any:
        """Execute a specific agent with a task"""
        agent = await self.get_agent(request.agent_id)
        if not agent:
            raise ValueError(f"Agent {request.agent_id} not found")
        
        # Convert to chat request for processing
        chat_request = ChatRequest(
            message=request.task,
            agent_id=request.agent_id,
            vault_context=request.context
        )
        
        return await self.process_chat(chat_request)

    async def parse_intelligence(self, request: Any) -> Any:
        """Parse intelligence request - placeholder implementation"""
        # TODO: Implement intelligence parsing
        return {
            "intent": "general_assistance",
            "confidence": 0.8,
            "entities": [],
            "suggestions": []
        }

    async def update_memory(self, request: Any) -> None:
        """Update agent memory - placeholder implementation"""
        # TODO: Implement memory updates
        pass
