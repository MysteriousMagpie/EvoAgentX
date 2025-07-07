"""
Context Template Examples and Integration Guide

This module provides practical examples of how to use the enhanced context
templates in EvoAgentX, demonstrating integration patterns and best practices.
"""

from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass

from .base_context_template import ContextLayer, ContextConfig
from .dynamic_context import DynamicContextTemplate, DynamicContextConfig, ConversationPhase
from .hierarchical_context import HierarchicalContextTemplate, HierarchicalContextConfig, HierarchyLevel
from .role_based_context import RoleBasedContextTemplate, AgentRole, RoleProfile, ExpertiseDomain, InteractionStyle
from .task_specific_context import TaskSpecificContextTemplate, TaskType, TaskProfile, TaskComplexity, TaskDomain
from .utils import ContextTemplateFactory, ContextPresets, create_conversational_agent, create_code_assistant

from ...core.logging import logger


class ContextTemplateExamples:
    """Examples demonstrating different context template usage patterns"""
    
    @staticmethod
    def basic_dynamic_context_example():
        """Example: Basic dynamic context with conversation adaptation"""
        print("=== Dynamic Context Template Example ===")
        
        # Create a dynamic context template
        template = create_conversational_agent(
            instruction="You are a helpful AI assistant that adapts to conversation flow."
        )
        
        # Simulate conversation flow
        messages = [
            ("user", "Hi there! How are you?"),
            ("assistant", "Hello! I'm doing well, thank you for asking."),
            ("user", "I need help with Python programming. Can you explain functions?"),
            ("assistant", "I'd be happy to help with Python functions!"),
            ("user", "Actually, let me be more specific. How do I create a function that calculates factorial?"),
            ("assistant", "Great question! Here's how to create a factorial function...")
        ]
        
        # Process conversation and show context adaptation
        for role, message in messages:
            state = template.process_user_message(message, role)
            print(f"[{role}] {message}")
            
            if role == "user":
                # Get relevant context for response
                context = template.get_relevant_context(query=message)
                print(f"Context items: {len(context)}")
                print(f"Conversation phase: {state.phase.value}")
                print(f"Engagement level: {state.engagement_level.value}")
                print(f"Current topic: {state.get_current_topic()}")
                print("---")
        
        # Show conversation summary
        summary = template.get_conversation_summary()
        print(f"Final Summary: {summary}")
        print()
    
    @staticmethod
    def hierarchical_context_example():
        """Example: Hierarchical context with multi-level organization"""
        print("=== Hierarchical Context Template Example ===")
        
        # Create hierarchical context template
        config = HierarchicalContextConfig(
            enable_context_inheritance=True,
            enable_context_cascading=True
        )
        
        template = ContextTemplateFactory.create_hierarchical_template(
            instruction="You are an expert software architect with hierarchical knowledge organization.",
            config=config
        )
        
        # Add context at different hierarchy levels
        
        # System level - Core identity and capabilities
        template.add_hierarchical_context(
            content="I am an expert software architect with 15+ years of experience in distributed systems, microservices, and cloud architecture.",
            level=HierarchyLevel.SYSTEM,
            importance=0.9,
            source="system_identity"
        )
        
        # Domain level - Technical expertise
        template.add_hierarchical_context(
            content="I specialize in designing scalable web applications using modern frameworks like React, Node.js, and Python FastAPI.",
            level=HierarchyLevel.DOMAIN,
            importance=0.8,
            source="domain_expertise"
        )
        
        # Session level - Current conversation context
        template.add_hierarchical_context(
            content="The user is asking about building a real-time chat application with WebSocket support.",
            level=HierarchyLevel.SESSION,
            relevance_score=0.9,
            source="session_context"
        )
        
        # Task level - Specific current objective
        template.add_hierarchical_context(
            content="Need to design the backend architecture for handling 10,000+ concurrent WebSocket connections.",
            level=HierarchyLevel.TASK,
            relevance_score=1.0,
            importance=0.9,
            source="current_task"
        )
        
        # Interaction level - Immediate context
        template.add_hierarchical_context(
            content="User specifically mentioned Redis for session management and horizontal scaling requirements.",
            level=HierarchyLevel.INTERACTION,
            relevance_score=1.0,
            source="immediate_context"
        )
        
        # Get hierarchical context
        hierarchical_context = template.get_hierarchical_context(
            query="WebSocket architecture with Redis"
        )
        
        print("Hierarchical Context Organization:")
        for level, items in hierarchical_context.items():
            if items:
                print(f"\n{level.value.title()} Level:")
                for i, item in enumerate(items, 1):
                    relevance = item.get_weighted_relevance()
                    print(f"  {i}. {item.content[:80]}... (relevance: {relevance:.2f})")
        
        # Show hierarchy stats
        stats = template.get_hierarchy_stats()
        print(f"\nHierarchy Statistics: {stats}")
        print()
    
    @staticmethod
    def role_based_context_example():
        """Example: Role-based context for specialized agents"""
        print("=== Role-Based Context Template Example ===")
        
        # Create a research assistant with academic focus
        role_profile = RoleProfile(
            role=AgentRole.RESEARCH_ASSISTANT,
            expertise_domains=[ExpertiseDomain.SCIENCE, ExpertiseDomain.TECHNOLOGY],
            interaction_style=InteractionStyle.FORMAL,
            primary_capabilities=["literature_review", "data_analysis", "citation_management"],
            formality_level=0.8,
            detail_preference=0.9
        )
        
        template = ContextTemplateFactory.create_role_based_template(
            instruction="You are a research assistant specializing in scientific literature review and analysis.",
            role=AgentRole.RESEARCH_ASSISTANT,
            expertise_domains=[ExpertiseDomain.SCIENCE, ExpertiseDomain.TECHNOLOGY],
            interaction_style=InteractionStyle.FORMAL
        )
        
        # Add role-specific context
        template.add_role_specific_context(
            content="Recent study in Nature (2024) demonstrates breakthrough in quantum computing error correction using topological qubits.",
            context_type="evidence",
            relevance_score=0.9,
            domain_specific=True,
            metadata={"journal": "Nature", "year": 2024, "field": "quantum_computing"}
        )
        
        template.add_role_specific_context(
            content="Standard academic citation format: Author, A. (Year). Title. Journal, Volume(Issue), pages. DOI",
            context_type="best_practice",
            relevance_score=0.8,
            metadata={"category": "citation_standards"}
        )
        
        template.add_role_specific_context(
            content="When analyzing research papers, always evaluate: methodology, sample size, statistical significance, reproducibility, and peer review status.",
            context_type="methodology",
            relevance_score=0.9,
            importance=0.8
        )
        
        # Test context retrieval for research query
        query = "How do I evaluate the quality of quantum computing research papers?"
        relevant_context = template.get_relevant_context(query=query)
        
        print("Role-Based Context for Research Query:")
        print(f"Query: {query}")
        print(f"Retrieved {len(relevant_context)} context items:")
        
        for i, item in enumerate(relevant_context, 1):
            print(f"{i}. [{item.metadata.get('context_type', 'general')}] {item.content[:100]}...")
            print(f"   Relevance: {item.relevance_score:.2f}, Importance: {item.importance:.2f}")
        
        # Show role stats
        role_stats = template.get_role_stats()
        print(f"\nRole Statistics: {role_stats}")
        print()
    
    @staticmethod
    def task_specific_context_example():
        """Example: Task-specific context for code generation"""
        print("=== Task-Specific Context Template Example ===")
        
        # Create task profile for complex code generation
        task_profile = TaskProfile(
            task_type=TaskType.CODE_GENERATION,
            complexity=TaskComplexity.COMPLEX,
            domain=TaskDomain.WEB_DEVELOPMENT,
            requires_examples=True,
            requires_best_practices=True,
            requires_error_handling=True,
            technical_depth="advanced",
            key_concepts={"async", "websocket", "real-time", "scalability"},
            relevant_technologies={"fastapi", "websockets", "redis", "postgresql"}
        )
        
        template = ContextTemplateFactory.create_task_specific_template(
            instruction="Generate high-quality, production-ready code with proper error handling and documentation.",
            task_type=TaskType.CODE_GENERATION,
            complexity=TaskComplexity.COMPLEX,
            domain=TaskDomain.WEB_DEVELOPMENT
        )
        
        # Add task-specific context
        template.add_task_context(
            content="""
# FastAPI WebSocket Example with Error Handling
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import logging

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logging.error(f"Error sending message: {e}")
                await self.disconnect(connection)
            """,
            context_type="example",
            task_relevance=1.0,
            complexity_level=TaskComplexity.COMPLEX,
            domain_specific=True
        )
        
        template.add_task_context(
            content="Always implement proper WebSocket connection lifecycle management: connect, message handling, disconnect, and error recovery.",
            context_type="best_practice",
            task_relevance=0.9,
            importance=0.8
        )
        
        template.add_task_context(
            content="Use connection pooling and rate limiting for production WebSocket applications to prevent resource exhaustion.",
            context_type="best_practice",
            task_relevance=0.8,
            complexity_level=TaskComplexity.EXPERT
        )
        
        # Test automatic task classification
        query = "Create a WebSocket server that can handle real-time chat with Redis backend"
        classified_task, confidence = template.classify_task_from_query(query)
        
        print(f"Task Classification:")
        print(f"Query: {query}")
        print(f"Classified as: {classified_task.value} (confidence: {confidence:.2f})")
        
        # Get task-optimized context
        relevant_context = template.get_relevant_context(query=query)
        
        print(f"\nTask-Optimized Context ({len(relevant_context)} items):")
        for i, item in enumerate(relevant_context, 1):
            context_type = item.metadata.get('context_type', 'general')
            task_relevance = item.metadata.get('task_relevance', 0.5)
            print(f"{i}. [{context_type}] Relevance: {task_relevance:.2f}")
            print(f"   {item.content[:120]}...")
        
        # Show task progress tracking
        template.update_task_progress("Design WebSocket architecture", completed=True)
        template.update_task_progress("Implement connection management", completed=False)
        template.update_task_progress("Add error handling", completed=False)
        
        task_stats = template.get_task_stats()
        print(f"\nTask Statistics: {task_stats}")
        print()
    
    @staticmethod
    def integration_with_memory_example():
        """Example: Integrating context templates with existing memory system"""
        print("=== Integration with Memory System Example ===")
        
        # This would integrate with your existing memory framework
        try:
            from ...memory.persistent_memory import PersistentMemoryManager, MemoryConfig
            
            # Create memory-integrated context template
            memory_config = MemoryConfig(
                max_working_memory_tokens=2000,
                enable_vector_store=True,
                vector_similarity_threshold=0.7
            )
            
            template = create_conversational_agent(
                instruction="You are an AI assistant with persistent memory capabilities.",
                memory_config=memory_config
            )
            
            # Simulate adding memories that become context
            conversations = [
                "User prefers detailed technical explanations",
                "User is working on a Python web application project",
                "User has experience with FastAPI and PostgreSQL",
                "User asked about WebSocket implementation last week",
                "User mentioned scalability concerns for 10K+ users"
            ]
            
            for memory in conversations:
                template.add_context(
                    content=memory,
                    layer=ContextLayer.SESSION,
                    relevance_score=0.8,
                    source="memory_system",
                    metadata={"memory_type": "conversation_history"}
                )
            
            # Query with memory-informed context
            query = "How should I implement WebSocket scaling?"
            context = template.get_relevant_context(query=query)
            
            print("Memory-Informed Context:")
            for i, item in enumerate(context, 1):
                if item.source == "memory_system":
                    print(f"{i}. [MEMORY] {item.content}")
                else:
                    print(f"{i}. [CONTEXT] {item.content[:80]}...")
            
            print(f"Total context items: {len(context)}")
            
        except ImportError:
            print("Memory system not available for integration example")
        
        print()
    
    @staticmethod
    def performance_monitoring_example():
        """Example: Monitoring and optimizing context template performance"""
        print("=== Performance Monitoring Example ===")
        
        from .utils import ContextMetrics, ContextAnalyzer
        
        # Create a template and metrics tracker
        template = create_code_assistant(
            instruction="You are a code assistant focused on Python development."
        )
        
        metrics = ContextMetrics()
        
        # Simulate some context retrievals with varying quality
        test_queries = [
            ("How do I create a Python function?", 0.8),
            ("Explain async/await in Python", 0.9),
            ("Debug this code snippet", 0.7),
            ("Best practices for error handling", 0.85),
            ("Performance optimization techniques", 0.75)
        ]
        
        for query, quality in test_queries:
            # Add some context for the query
            template.add_context(
                content=f"Context for: {query}",
                layer=ContextLayer.TASK,
                relevance_score=0.8,
                source="test_data"
            )
            
            # Retrieve context
            context_items = template.get_relevant_context(query=query)
            
            # Record metrics
            metrics.record_context_retrieval(
                template=template,
                query=query,
                retrieved_items=context_items,
                response_quality=quality
            )
        
        # Analyze performance
        performance_summary = metrics.get_performance_summary()
        print("Performance Summary:")
        for key, value in performance_summary.items():
            print(f"  {key}: {value}")
        
        # Get efficiency analysis
        efficiency_analysis = ContextAnalyzer.analyze_context_efficiency(template)
        print(f"\nEfficiency Analysis:")
        print(f"  Efficiency Score: {efficiency_analysis['efficiency_score']:.2f}")
        print(f"  Token Utilization: {efficiency_analysis['token_utilization']:.2f}")
        print(f"  Recommendations: {efficiency_analysis['recommendations']}")
        
        print()


def run_all_examples():
    """Run all context template examples"""
    print("Running Enhanced Context Template Examples")
    print("=" * 50)
    
    examples = ContextTemplateExamples()
    
    examples.basic_dynamic_context_example()
    examples.hierarchical_context_example()
    examples.role_based_context_example()
    examples.task_specific_context_example()
    examples.integration_with_memory_example()
    examples.performance_monitoring_example()
    
    print("All examples completed successfully!")


class ContextTemplateIntegrationGuide:
    """Guide for integrating context templates with existing EvoAgentX agents"""
    
    @staticmethod
    def integrate_with_existing_agent():
        """Example of integrating context templates with existing agents"""
        
        # This is a pattern for integrating with your existing agent classes
        class EnhancedAgent:
            def __init__(self, agent_id: str, role: AgentRole = AgentRole.GENERAL_ASSISTANT):
                self.agent_id = agent_id
                
                # Choose appropriate context template based on role
                if role == AgentRole.CODE_ASSISTANT:
                    self.context_template = create_code_assistant(
                        instruction="You are a helpful coding assistant."
                    )
                elif role == AgentRole.RESEARCH_ASSISTANT:
                    self.context_template = create_research_assistant(
                        instruction="You are a research assistant focused on scientific literature."
                    )
                else:
                    self.context_template = create_conversational_agent(
                        instruction="You are a helpful AI assistant."
                    )
                
                # Initialize with agent identity context
                self.context_template.add_context(
                    content=f"I am agent {agent_id} with role {role.value}",
                    layer=ContextLayer.GLOBAL,
                    importance=0.9,
                    source="agent_identity"
                )
            
            def process_message(self, message: str, user_id: str = None) -> str:
                """Process a message using context-aware response generation"""
                
                # Add user message to context
                if hasattr(self.context_template, 'process_user_message'):
                    # Dynamic template with conversation tracking
                    self.context_template.process_user_message(message, "user")
                else:
                    # Standard context addition
                    self.context_template.add_context(
                        content=message,
                        layer=ContextLayer.DYNAMIC,
                        relevance_score=1.0,
                        source="user_message"
                    )
                
                # Get relevant context for response generation
                relevant_context = self.context_template.get_relevant_context(query=message)
                
                # Generate response (this would integrate with your LLM)
                context_summary = self._summarize_context(relevant_context)
                response = f"Based on context: {context_summary}, I respond to: {message}"
                
                # Add response to context
                self.context_template.add_context(
                    content=response,
                    layer=ContextLayer.DYNAMIC,
                    relevance_score=0.8,
                    source="agent_response"
                )
                
                return response
            
            def _summarize_context(self, context_items: List) -> str:
                """Summarize context items for response generation"""
                if not context_items:
                    return "no specific context"
                
                return f"{len(context_items)} relevant context items available"
            
            def get_agent_stats(self) -> Dict[str, Any]:
                """Get comprehensive agent statistics including context usage"""
                base_stats = {
                    'agent_id': self.agent_id,
                    'template_type': self.context_template.__class__.__name__
                }
                
                # Add context-specific stats
                if hasattr(self.context_template, 'get_conversation_summary'):
                    base_stats.update(self.context_template.get_conversation_summary())
                elif hasattr(self.context_template, 'get_role_stats'):
                    base_stats.update(self.context_template.get_role_stats())
                elif hasattr(self.context_template, 'get_task_stats'):
                    base_stats.update(self.context_template.get_task_stats())
                else:
                    base_stats.update(self.context_template.get_context_stats())
                
                return base_stats
        
        return EnhancedAgent
    
    @staticmethod
    def integration_patterns():
        """Common patterns for integrating context templates"""
        patterns = {
            "agent_initialization": """
            # Pattern 1: Initialize agent with context template
            def __init__(self, role_type: str):
                if role_type == "researcher":
                    self.context = create_research_assistant("Research instruction")
                elif role_type == "coder":
                    self.context = create_code_assistant("Coding instruction")
                else:
                    self.context = create_conversational_agent("General instruction")
            """,
            
            "message_processing": """
            # Pattern 2: Process messages with context awareness
            def process_message(self, message: str) -> str:
                # Update conversation state (for dynamic templates)
                if hasattr(self.context, 'process_user_message'):
                    self.context.process_user_message(message, "user")
                
                # Get relevant context
                context = self.context.get_relevant_context(query=message)
                
                # Generate context-aware response
                return self.generate_response(message, context)
            """,
            
            "context_management": """
            # Pattern 3: Manage context lifecycle
            def start_new_conversation(self):
                if hasattr(self.context, 'reset_conversation'):
                    self.context.reset_conversation()
                else:
                    self.context.clear_context_layer(ContextLayer.DYNAMIC)
            
            def add_domain_knowledge(self, knowledge: str):
                self.context.add_context(
                    content=knowledge,
                    layer=ContextLayer.GLOBAL,
                    importance=0.8,
                    source="domain_knowledge"
                )
            """,
            
            "performance_monitoring": """
            # Pattern 4: Monitor and optimize performance
            def monitor_context_performance(self):
                stats = self.context.get_context_stats()
                if stats['estimated_tokens'] > 4000:
                    self.context.clear_old_context(max_age_hours=6)
                
                efficiency = analyze_template_performance(self.context)
                if efficiency['efficiency_score'] < 0.5:
                    self.optimize_context_settings()
            """
        }
        
        return patterns


if __name__ == "__main__":
    # Run examples if script is executed directly
    run_all_examples()