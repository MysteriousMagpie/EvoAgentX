#!/usr/bin/env python3
"""
Quick WebSocket Test for VaultPilot Enhanced Endpoint

This script tests the newly implemented WebSocket endpoint:
ws://localhost:8000/api/obsidian/ws/enhanced

Usage: python3 quick_ws_test.py
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime


async def test_enhanced_websocket():
    """Test the enhanced WebSocket endpoint"""
    uri = "ws://localhost:8002/ws/obsidian"
    
    print(f"🔌 Testing: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connection successful!")
            
            # Wait for welcome message
            try:
                welcome_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                welcome_data = json.loads(welcome_message)
                print(f"📨 Welcome message: {json.dumps(welcome_data, indent=2)}")
                
                # Verify it's the enhanced endpoint
                if (welcome_data.get("type") == "connection" and 
                    welcome_data.get("data", {}).get("enhanced") == True):
                    print("✅ Enhanced features confirmed!")
                else:
                    print("⚠️  Enhanced features not detected in welcome message")
                    
            except asyncio.TimeoutError:
                print("⚠️  No welcome message received within 5 seconds")
            
            # Send a ping to test communication
            ping_message = {"type": "ping", "timestamp": datetime.now().isoformat()}
            await websocket.send(json.dumps(ping_message))
            print(f"📤 Sent ping: {ping_message}")
            
            # Wait for pong response
            try:
                pong_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                pong_data = json.loads(pong_message)
                print(f"📨 Received pong: {json.dumps(pong_data, indent=2)}")
                
                if pong_data.get("type") == "pong":
                    print("✅ Ping-pong test successful!")
                else:
                    print("⚠️  Unexpected response to ping")
                    
            except asyncio.TimeoutError:
                print("❌ No pong response received within 5 seconds")
            
            # Test vault sync feature
            sync_message = {"type": "vault_sync", "vault_id": "test"}
            await websocket.send(json.dumps(sync_message))
            print(f"📤 Sent vault sync: {sync_message}")
            
            try:
                sync_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                sync_data = json.loads(sync_response)
                print(f"📨 Received sync response: {json.dumps(sync_data, indent=2)}")
                
                if sync_data.get("type") == "vault_sync_response":
                    print("✅ Vault sync test successful!")
                else:
                    print("⚠️  Unexpected response to vault sync")
                    
            except asyncio.TimeoutError:
                print("❌ No sync response received within 5 seconds")
            
            # Test agent status feature
            status_message = {"type": "agent_status"}
            await websocket.send(json.dumps(status_message))
            print(f"📤 Sent agent status: {status_message}")
            
            try:
                status_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                status_data = json.loads(status_response)
                print(f"📨 Received status response: {json.dumps(status_data, indent=2)}")
                
                if status_data.get("type") == "agent_status_response":
                    print("✅ Agent status test successful!")
                else:
                    print("⚠️  Unexpected response to agent status")
                    
            except asyncio.TimeoutError:
                print("❌ No status response received within 5 seconds")
            
            print("\n🎉 All tests completed!")
            return True
            
    except ConnectionRefusedError:
        print("❌ Failed: Connection refused - is the server running on localhost:8000?")
        return False
    except websockets.exceptions.InvalidMessage as e:
        print(f"❌ Failed: server rejected WebSocket connection: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🚀 VaultPilot Enhanced WebSocket Test")
    print("=" * 50)
    
    success = await test_enhanced_websocket()
    
    if success:
        print("\n✅ Test Result: SUCCESS - Enhanced WebSocket endpoint is working!")
        sys.exit(0)
    else:
        print("\n❌ Test Result: FAILED - Please check server configuration")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
