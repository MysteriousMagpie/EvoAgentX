"""
Simple test for the Persistent Memory Framework

This test verifies basic functionality without requiring external dependencies.
"""

import os
import tempfile
import shutil
from pathlib import Path

from evoagentx.memory.persistent_memory import (
    PersistentMemoryManager,
    MemoryConfig,
    MemoryCapableMixin
)


def test_basic_memory_functionality():
    """Test basic memory operations"""
    print("Testing basic memory functionality...")
    
    # Create temporary directory for test database
    test_dir = Path(tempfile.mkdtemp())
    test_db = test_dir / "test_memory.sqlite"
    
    try:
        # Create config without vector store to avoid dependencies
        config = MemoryConfig(
            db_path=str(test_db),
            enable_vector_store=False,
            max_working_memory_messages=5,
            summarize_threshold=3
        )
        
        # Create memory manager
        memory = PersistentMemoryManager("test_agent", config)
        
        # Test adding messages
        print("  Adding messages...")
        id1 = memory.add_message("Hello, I'm starting a conversation", "user")
        id2 = memory.add_message("Hi! How can I help you today?", "assistant")
        id3 = memory.add_message("I need help with planning my day", "user")
        
        assert id1 and id2 and id3, "Message IDs should be generated"
        
        # Test getting context
        print("  Testing context retrieval...")
        context = memory.get_context()
        assert len(context) >= 3, f"Should have at least 3 context items, got {len(context)}"
        
        # Test adding more messages to trigger summarization
        print("  Testing summarization...")
        for i in range(10):
            memory.add_message(f"Message {i} for testing summarization", "user")
        
        # Check that summarization occurred
        stats = memory.get_stats()
        print(f"  Memory stats after many messages: {stats}")
        assert stats['working_memory_items'] <= config.max_working_memory_messages, "Working memory should be limited"
        
        # Test memory search
        print("  Testing memory search...")
        search_results = memory.search_memory("planning")
        print(f"  Found {len(search_results)} results for 'planning'")
        
        # Test session management
        print("  Testing session management...")
        old_session = memory.current_session_id
        new_session = memory.start_new_session()
        assert new_session != old_session, "New session should have different ID"
        
        print("✅ Basic memory functionality test passed!")
        
    finally:
        # Clean up
        shutil.rmtree(test_dir, ignore_errors=True)


def test_memory_mixin():
    """Test the memory mixin functionality"""
    print("Testing memory mixin...")
    
    # Create temporary directory
    test_dir = Path(tempfile.mkdtemp())
    test_db = test_dir / "test_mixin.sqlite"
    
    try:
        # Create agent with memory mixin
        class TestAgent(MemoryCapableMixin):
            def __init__(self, name: str):
                self.name = name
                self.agent_id = f"test_{name}"
                config = MemoryConfig(
                    db_path=str(test_db),
                    enable_vector_store=False
                )
                super().__init__(memory_config=config)
            
            def process_input(self, user_input: str) -> str:
                # Remember user input
                self.remember(user_input, "user")
                
                # Get context
                context = self.recall()
                
                # Generate response
                response = f"Processed: {user_input}. Context has {len(context)} items."
                
                # Remember response
                self.remember(response, "assistant")
                
                return response
        
        # Test the agent
        agent = TestAgent("mixin_test")
        
        print("  Testing agent with mixin...")
        response1 = agent.process_input("What's the weather like?")
        response2 = agent.process_input("Can you help me plan my schedule?")
        
        assert "Processed:" in response1, "Response should contain processed input"
        assert "Context has" in response2, "Second response should have context"
        
        # Test memory stats
        stats = agent.memory_stats()
        assert stats['working_memory_items'] >= 4, "Should have at least 4 items (2 user + 2 assistant)"
        
        print("✅ Memory mixin test passed!")
        
    finally:
        # Clean up
        shutil.rmtree(test_dir, ignore_errors=True)


def test_memory_configuration():
    """Test different memory configurations"""
    print("Testing memory configurations...")
    
    # Test lightweight config
    lightweight_config = MemoryConfig(
        max_working_memory_messages=3,
        enable_vector_store=False,
        auto_summarize=False
    )
    
    # Test conversational config
    conversational_config = MemoryConfig(
        max_working_memory_messages=20,
        summarize_threshold=5,
        enable_vector_store=False  # Disabled for testing
    )
    
    assert lightweight_config.max_working_memory_messages == 3
    assert conversational_config.max_working_memory_messages == 20
    assert not lightweight_config.auto_summarize
    assert conversational_config.auto_summarize
    
    print("✅ Memory configuration test passed!")


def run_all_tests():
    """Run all tests"""
    print("Running Persistent Memory Framework Tests")
    print("=" * 50)
    
    try:
        test_basic_memory_functionality()
        print()
        test_memory_mixin()
        print()
        test_memory_configuration()
        print()
        print("🎉 All tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
