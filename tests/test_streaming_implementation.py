#!/usr/bin/env python3
"""
Test streaming chat endpoint implementation
Following dev-pipe protocol testing requirements
"""

import asyncio
import json
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evoagentx_integration.api_models import ChatStreamRequest, ChatStreamChunk
from evoagentx_integration.agent_manager import AgentManager

async def test_streaming_components():
    """Test that streaming components work correctly"""
    print("🧪 Testing Streaming Chat Components")
    print("=" * 50)
    
    # Test 1: Model Creation
    print("1. Testing ChatStreamRequest model...")
    try:
        request = ChatStreamRequest(
            message="Hello, test streaming!",
            stream=True
        )
        print(f"   ✅ Request created: {request.message}")
    except Exception as e:
        print(f"   ❌ Request creation failed: {e}")
        return False
    
    # Test 2: Agent Manager Streaming
    print("2. Testing AgentManager streaming method...")
    try:
        agent_manager = AgentManager()
        
        # Check if method exists
        if hasattr(agent_manager, 'process_chat_stream'):
            print("   ✅ process_chat_stream method exists")
            
            # Test streaming (limited test)
            chunks_received = 0
            async for chunk in agent_manager.process_chat_stream(request):
                chunks_received += 1
                print(f"   📦 Chunk {chunks_received}: {chunk.content[:50]}...")
                if chunks_received >= 3:  # Limit test to 3 chunks
                    break
            
            print(f"   ✅ Received {chunks_received} chunks successfully")
        else:
            print("   ❌ process_chat_stream method not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Agent manager streaming failed: {e}")
        return False
    
    # Test 3: StreamChunk Model
    print("3. Testing ChatStreamChunk model...")
    try:
        chunk = ChatStreamChunk(
            content="Test chunk content",
            is_complete=False
        )
        print(f"   ✅ Chunk created with ID: {chunk.id}")
    except Exception as e:
        print(f"   ❌ Chunk creation failed: {e}")
        return False
    
    print("\n🎯 All streaming components test PASSED!")
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_streaming_components())
        if result:
            print("\n✅ STREAMING IMPLEMENTATION VERIFIED")
            exit(0)
        else:
            print("\n❌ STREAMING IMPLEMENTATION FAILED")
            exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        exit(1)
