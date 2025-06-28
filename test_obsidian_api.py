#!/usr/bin/env python3
"""
Test script for EvoAgentX Obsidian API integration.
Run this script to test the various endpoints and functionality.
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/obsidian"

async def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_BASE}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed: {data}")
                    return True
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

async def test_chat():
    """Test the chat endpoint"""
    print("\n💬 Testing chat endpoint...")
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "message": "Hello! Can you help me organize my notes about machine learning?",
                "context": {"test_mode": True}
            }
            
            async with session.post(
                f"{API_BASE}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Chat response: {data['response'][:100]}...")
                    print(f"   Conversation ID: {data['conversation_id']}")
                    return data['conversation_id']
                else:
                    error_text = await response.text()
                    print(f"❌ Chat failed: {response.status} - {error_text}")
                    return None
        except Exception as e:
            print(f"❌ Chat error: {e}")
            return None

async def test_copilot():
    """Test the copilot completion endpoint"""
    print("\n🤖 Testing copilot completion...")
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "text": "The main advantages of machine learning are",
                "cursor_position": 40,
                "file_type": "markdown",
                "context": "academic notes"
            }
            
            async with session.post(
                f"{API_BASE}/copilot/complete",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Copilot completion: {data['completion'][:100]}...")
                    print(f"   Confidence: {data['confidence']}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Copilot failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Copilot error: {e}")
            return False

async def test_workflow():
    """Test the workflow execution endpoint"""
    print("\n⚙️ Testing workflow execution...")
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "goal": "Create a simple learning plan for understanding neural networks",
                "context": {"time_available": "1 week", "level": "beginner"}
            }
            
            async with session.post(
                f"{API_BASE}/workflow",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Workflow completed: {data['output'][:150]}...")
                    print(f"   Execution ID: {data['execution_id']}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Workflow failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Workflow error: {e}")
            return False

async def test_agents():
    """Test agent listing and creation"""
    print("\n👥 Testing agent management...")
    async with aiohttp.ClientSession() as session:
        try:
            # List agents
            async with session.get(f"{API_BASE}/agents") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Found {len(data['agents'])} agents")
                    for agent in data['agents']:
                        print(f"   - {agent['name']}: {agent['description'][:50]}...")
                else:
                    print(f"❌ Agent listing failed: {response.status}")
                    return False
            
            # Create a custom agent
            agent_data = {
                "name": "TestAgent",
                "description": "A test agent for API validation",
                "system_prompt": "You are a helpful test assistant.",
                "prompt": "Respond to this test query: {query}"
            }
            
            async with session.post(
                f"{API_BASE}/agents/create",
                data=agent_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Created agent: {data['agent_name']}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Agent creation failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Agent management error: {e}")
            return False

async def test_vault_context():
    """Test vault context analysis"""
    print("\n📚 Testing vault context analysis...")
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "file_paths": [
                    "Notes/Machine Learning.md",
                    "Projects/NLP Study.md",
                    "Resources/AI Papers.md"
                ],
                "content_snippets": {
                    "Machine Learning.md": "Neural networks are computational models inspired by biological neural networks...",
                    "NLP Study.md": "Natural language processing involves teaching computers to understand human language..."
                }
            }
            
            async with session.post(
                f"{API_BASE}/vault/context",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Context summary: {data['context_summary'][:100]}...")
                    print(f"   Relevant notes: {len(data['relevant_notes'])}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Context analysis failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Context analysis error: {e}")
            return False

async def test_conversation_history(conversation_id):
    """Test conversation history retrieval"""
    if not conversation_id:
        print("\n⏭️ Skipping conversation history test (no conversation ID)")
        return True
        
    print("\n📜 Testing conversation history...")
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "conversation_id": conversation_id,
                "limit": 10
            }
            
            async with session.post(
                f"{API_BASE}/conversation/history",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Retrieved {len(data['messages'])} messages")
                    print(f"   Total count: {data['total_count']}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ History retrieval failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ History retrieval error: {e}")
            return False

async def main():
    """Run all tests"""
    print("🚀 Starting EvoAgentX Obsidian API Tests")
    print("=" * 50)
    
    # Check if server is running
    if not await test_health():
        print("\n❌ Server not available. Please start the EvoAgentX server:")
        print("   cd server && python -m uvicorn main:sio_app --host 0.0.0.0 --port 8000")
        return False
    
    # Run tests
    conversation_id = await test_chat()
    await test_copilot()
    
    # Skip workflow test if OpenAI key not available
    if os.getenv("OPENAI_API_KEY"):
        await test_workflow()
    else:
        print("\n⏭️ Skipping workflow test (OPENAI_API_KEY not set)")
    
    await test_agents()
    await test_vault_context()
    await test_conversation_history(conversation_id)
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\nNext steps:")
    print("1. Check the API documentation at http://localhost:8000/docs")
    print("2. Build your Obsidian plugin using the provided examples")
    print("3. Test WebSocket connections for real-time features")
    
    return True

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
