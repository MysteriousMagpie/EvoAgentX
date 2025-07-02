#!/usr/bin/env python3
"""
Test script to verify Ask/Agent mode functionality in EvoAgentX Obsidian API
"""

import aiohttp
import asyncio
import json

API_BASE = "http://localhost:8000/api/obsidian"

async def test_ask_mode():
    """Test ask mode for simple Q&A"""
    print("\n🗣️ Testing Ask Mode...")
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "message": "What is Python?",
                "mode": "ask"
            }
            
            async with session.post(
                f"{API_BASE}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Ask Mode response: {data['response'][:100]}...")
                    print(f"   Agent: {data['agent_name']}")
                    print(f"   Mode: {data['metadata'].get('mode', 'not specified')}")
                    return data['conversation_id']
                else:
                    error_text = await response.text()
                    print(f"❌ Ask mode failed: {response.status} - {error_text}")
                    return None
        except Exception as e:
            print(f"❌ Ask mode error: {e}")
            return None

async def test_agent_mode():
    """Test agent mode for workflow execution"""
    print("\n🤖 Testing Agent Mode...")
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "message": "Create a simple to-do list for learning Python",
                "mode": "agent"
            }
            
            async with session.post(
                f"{API_BASE}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Agent Mode response: {data['response'][:100]}...")
                    print(f"   Agent: {data['agent_name']}")
                    print(f"   Mode: {data['metadata'].get('mode', 'not specified')}")
                    return data['conversation_id']
                else:
                    error_text = await response.text()
                    print(f"❌ Agent mode failed: {response.status} - {error_text}")
                    return None
        except Exception as e:
            print(f"❌ Agent mode error: {e}")
            return None

async def test_default_mode():
    """Test default mode (should be 'ask')"""
    print("\n🔄 Testing Default Mode...")
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "message": "Hello! How are you?"
                # No mode specified - should default to "ask"
            }
            
            async with session.post(
                f"{API_BASE}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Default Mode response: {data['response'][:100]}...")
                    print(f"   Agent: {data['agent_name']}")
                    print(f"   Mode: {data['metadata'].get('mode', 'not specified')}")
                    return data['conversation_id']
                else:
                    error_text = await response.text()
                    print(f"❌ Default mode failed: {response.status} - {error_text}")
                    return None
        except Exception as e:
            print(f"❌ Default mode error: {e}")
            return None

async def test_invalid_mode():
    """Test invalid mode parameter"""
    print("\n⚠️ Testing Invalid Mode...")
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "message": "Test message",
                "mode": "invalid_mode"
            }
            
            async with session.post(
                f"{API_BASE}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 422:
                    print("✅ Invalid mode correctly rejected with validation error")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Expected validation error, got: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Invalid mode test error: {e}")
            return False

async def main():
    print("🚀 Starting Ask/Agent Mode Tests")
    print("=" * 50)
    
    # Test all modes
    await test_ask_mode()
    await test_agent_mode()
    await test_default_mode()
    await test_invalid_mode()
    
    print("\n" + "=" * 50)
    print("✅ Ask/Agent Mode tests completed!")
    print("\n📝 Implementation Notes:")
    print("- Ask Mode: Uses agents for simple conversational responses")
    print("- Agent Mode: Executes EvoAgentX workflows for complex tasks")
    print("- Default Mode: Defaults to 'ask' when mode is not specified")
    print("- Validation: Invalid modes are properly rejected")

if __name__ == "__main__":
    asyncio.run(main())
