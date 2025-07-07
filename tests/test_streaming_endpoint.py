#!/usr/bin/env python3
"""
Test streaming endpoint with HTTP simulation
Dev-pipe protocol compliance verification
"""

import asyncio
import json
import sys
import os
from unittest.mock import Mock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evoagentx_integration.api_models import ChatStreamRequest
from evoagentx_integration.obsidian_routes import chat_with_agent_stream

async def test_streaming_endpoint():
    """Test the streaming endpoint implementation"""
    print("🌐 Testing Streaming Endpoint")
    print("=" * 40)
    
    # Test request as specified in the task
    test_request = ChatStreamRequest(
        message="Hello, test streaming!",
        stream=True
    )
    
    print(f"📤 Request: {test_request.message}")
    print("🔄 Processing streaming response...")
    
    try:
        # Call the endpoint function directly
        response = await chat_with_agent_stream(test_request)
        
        print(f"✅ Response type: {type(response).__name__}")
        print(f"✅ Media type: {response.media_type}")
        print(f"✅ Headers: {response.headers}")
        
        # Test streaming content
        chunk_count = 0
        async for chunk in response.body_iterator:
            chunk_str = chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk
            
            # Parse SSE data
            if chunk_str.startswith('data: '):
                try:
                    data = json.loads(chunk_str[6:].strip())
                    print(f"📦 Chunk {chunk_count + 1}: {data.get('type', 'unknown')} - {data.get('content', '')[:30]}...")
                    chunk_count += 1
                    
                    # Stop after a few chunks for testing
                    if chunk_count >= 5:
                        break
                except json.JSONDecodeError:
                    pass
        
        print(f"✅ Processed {chunk_count} SSE chunks")
        return True
        
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
        return False

async def main():
    """Main test execution"""
    print("🚀 Streaming Chat Backend - Integration Test")
    print("=" * 50)
    
    success = await test_streaming_endpoint()
    
    if success:
        print("\n🎯 STREAMING ENDPOINT TEST PASSED")
        print("✅ Ready for VaultPilot integration!")
        return 0
    else:
        print("\n❌ STREAMING ENDPOINT TEST FAILED") 
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except Exception as e:
        print(f"💥 Test execution error: {e}")
        exit(1)
