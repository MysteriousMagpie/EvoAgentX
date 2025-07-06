"""
Usage examples for the Persistent Memory Framework

This file demonstrates how to integrate persistent memory with different types of agents.
"""

from typing import Optional, Dict, Any, List
from evoagentx.memory.persistent_memory import (
    PersistentMemoryManager, 
    MemoryConfig, 
    MemoryCapableMixin,
    with_persistent_memory
)


# Example 1: Simple Agent with Memory Mixin
class ConversationalPlannerAgent(MemoryCapableMixin):
    """Example conversational planner with persistent memory"""
    
    def __init__(self, name: str = "planner", memory_config: Optional[MemoryConfig] = None):
        self.name = name
        self.agent_id = f"planner_{name}"
        super().__init__(memory_config=memory_config)
    
    def plan_day(self, user_input: str) -> str:
        """Plan a day based on user input with memory context"""
        # Remember the user's request
        self.remember(user_input, role="user", metadata={"action": "plan_request"})
        
        # Get relevant context from memory
        context = self.recall(query=user_input, include_summaries=True)
        
        # Generate plan (placeholder - would use LLM here)
        plan = self._generate_plan(user_input, context)
        
        # Remember the response
        self.remember(plan, role="assistant", metadata={"action": "plan_response"}, importance=0.8)
        
        return plan
    
    def _generate_plan(self, user_input: str, context: List[str]) -> str:
        """Generate a plan based on input and context"""
        # This would integrate with your LLM
        context_summary = f"Based on {len(context)} previous interactions" if context else "Starting fresh"
        return f"Daily Plan ({context_summary}):\n1. Process: {user_input}\n2. Review past context\n3. Create optimized schedule"
    
    def reflect_on_day(self, reflection: str) -> str:
        """Add a reflection to memory with high importance"""
        self.remember(
            reflection, 
            role="reflection", 
            metadata={"action": "daily_reflection"},
            importance=0.9  # High importance for reflections
        )
        return "Reflection recorded and will inform future planning."


# Example 2: Using the Decorator Approach
@with_persistent_memory(MemoryConfig(
    max_working_memory_tokens=1500,
    summarize_threshold=3,
    enable_vector_store=True
))
class ChatAgent:
    """Simple chat agent with memory via decorator"""
    
    def __init__(self, name: str):
        self.name = name
        self.agent_id = f"chat_{name}"
        # Note: The decorator adds memory capabilities automatically
    
    def chat(self, message: str) -> str:
        """Chat with memory"""
        # Remember user message
        self.remember(message, role="user")  # type: ignore
        
        # Get context for response
        context = self.recall(query=message)  # type: ignore
        
        # Generate response (placeholder)
        response = f"I understand: {message}. Context includes {len(context)} items."
        
        # Remember response
        self.remember(response, role="assistant")  # type: ignore
        
        return response


# Example 3: Direct Memory Manager Usage
class CustomAgent:
    """Agent that directly manages its own memory"""
    
    def __init__(self, agent_id: str, memory_config: Optional[MemoryConfig] = None):
        self.agent_id = agent_id
        
        # Custom memory configuration
        if not memory_config:
            memory_config = MemoryConfig(
                max_working_memory_tokens=3000,  # Larger memory
                summarize_threshold=7,
                vector_similarity_threshold=0.6,  # More permissive similarity
                enable_vector_store=True,
                auto_cleanup_days=60  # Keep memories longer
            )
        
        self.memory = PersistentMemoryManager(agent_id, memory_config)
    
    def process_document(self, document: str, document_type: str) -> str:
        """Process a document and remember it with metadata"""
        # Add to memory with specific metadata
        self.memory.add_message(
            content=f"Processed {document_type}: {document[:200]}...",
            role="system",
            metadata={
                "document_type": document_type,
                "length": len(document),
                "processed_at": "2025-07-05"
            },
            importance=0.7
        )
        
        # Search for related documents
        related = self.memory.search_memory(f"{document_type} document")
        
        return f"Document processed. Found {len(related)} related documents in memory."
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in memory"""
        stats = self.memory.get_stats()
        recent_items = self.memory.backend.get_recent_items(self.agent_id, limit=20)
        
        # Analyze document types
        doc_types = {}
        for item in recent_items:
            doc_type = item.metadata.get("document_type", "unknown")
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        return {
            "memory_stats": stats,
            "document_types": doc_types,
            "total_processed": len(recent_items)
        }


# Example 4: Memory Configuration Presets
class MemoryPresets:
    """Predefined memory configurations for different use cases"""
    
    @staticmethod
    def lightweight() -> MemoryConfig:
        """Lightweight config for simple agents"""
        return MemoryConfig(
            max_working_memory_tokens=1000,
            max_working_memory_messages=10,
            summarize_threshold=3,
            enable_vector_store=False,
            auto_cleanup_days=7
        )
    
    @staticmethod
    def conversational() -> MemoryConfig:
        """Config optimized for conversational agents"""
        return MemoryConfig(
            max_working_memory_tokens=2500,
            max_working_memory_messages=25,
            summarize_threshold=5,
            enable_vector_store=True,
            vector_similarity_threshold=0.75,
            auto_cleanup_days=30
        )
    
    @staticmethod
    def research() -> MemoryConfig:
        """Config for research/analysis agents that need long-term memory"""
        return MemoryConfig(
            max_working_memory_tokens=5000,
            max_working_memory_messages=50,
            summarize_threshold=10,
            enable_vector_store=True,
            vector_similarity_threshold=0.6,
            max_retrieved_memories=5,
            auto_cleanup_days=90
        )
    
    @staticmethod
    def high_performance() -> MemoryConfig:
        """Config optimized for performance with minimal memory usage"""
        return MemoryConfig(
            max_working_memory_tokens=800,
            max_working_memory_messages=8,
            summarize_threshold=2,
            enable_vector_store=False,
            auto_summarize=True,
            auto_cleanup_days=3
        )


# Example Usage Functions
def demo_conversational_planner():
    """Demo the conversational planner with memory"""
    # Create agent with conversational memory config
    planner = ConversationalPlannerAgent(
        name="daily_planner",
        memory_config=MemoryPresets.conversational()
    )
    
    # Simulate a conversation
    print("=== Conversational Planner Demo ===")
    
    # Day 1
    response1 = planner.plan_day("I need to prepare for a presentation tomorrow")
    print(f"Day 1 Plan: {response1}")
    
    # Add reflection
    reflection1 = planner.reflect_on_day("Spent too much time on research, need better time management")
    print(f"Reflection: {reflection1}")
    
    # Day 2 - should have context from previous day
    response2 = planner.plan_day("I have that presentation today, plus need to review project proposals")
    print(f"Day 2 Plan: {response2}")
    
    # Show memory stats
    stats = planner.memory_stats()
    print(f"Memory Stats: {stats}")


def demo_memory_search():
    """Demo memory search capabilities"""
    agent = CustomAgent("research_agent", MemoryPresets.research())
    
    print("=== Memory Search Demo ===")
    
    # Process several documents
    agent.process_document("This is a research paper about AI agents", "research_paper")
    agent.process_document("Meeting notes about project planning", "meeting_notes")
    agent.process_document("Code review for the new feature", "code_review")
    agent.process_document("Another AI paper about memory systems", "research_paper")
    
    # Search for related content
    ai_docs = agent.memory.search_memory("AI research")
    print(f"Found {len(ai_docs)} documents about AI research")
    
    # Analyze patterns
    analysis = agent.analyze_patterns()
    print(f"Pattern Analysis: {analysis}")


def demo_session_management():
    """Demo session management and context persistence"""
    agent = ChatAgent("session_demo")
    
    print("=== Session Management Demo ===")
    
    # First session
    print("Session 1:")
    print(agent.chat("Hello, I'm working on a Python project"))
    print(agent.chat("I need help with error handling"))
    print(agent.chat("Specifically for API calls"))
    
    # Start new session
    new_session = agent.new_session()
    print(f"\nStarted new session: {new_session}")
    
    # New session should still have access to relevant past context
    print("Session 2:")
    print(agent.chat("Can you help me with the API error handling we discussed?"))
    
    # Show memory stats
    stats = agent.memory_stats()
    print(f"\nFinal Memory Stats: {stats}")


if __name__ == "__main__":
    # Run demos
    demo_conversational_planner()
    print("\n" + "="*50 + "\n")
    demo_memory_search()
    print("\n" + "="*50 + "\n")
    demo_session_management()
