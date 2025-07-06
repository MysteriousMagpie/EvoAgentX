#!/usr/bin/env python3
"""
VaultPilot WebSocket Test for Default Port

This script tests the WebSocket endpoint that VaultPilot expects:
ws://localhost:8000/api/obsidian/ws/enhanced

Run this after starting the server on the default port 8000.
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime


async def test_vaultpilot_endpoint():
    """Test the endpoint that VaultPilot actually uses"""
    uri = "ws://localhost:8000/api/obsidian/ws/enhanced"
    
    print(f"🔌 Testing VaultPilot endpoint: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connection successful - VaultPilot can now connect!")
            
            # Wait for welcome message
            try:
                welcome_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                welcome_data = json.loads(welcome_message)
                print(f"📨 Welcome message: {json.dumps(welcome_data, indent=2)}")
                
                # Verify enhanced features
                if (welcome_data.get("type") == "connection" and 
                    welcome_data.get("data", {}).get("enhanced") == True):
                    print("✅ Enhanced features are available!")
                    features = welcome_data.get("data", {}).get("features", [])
                    print(f"🚀 Available features: {', '.join(features)}")
                else:
                    print("⚠️  Enhanced features not properly configured")
                    
            except asyncio.TimeoutError:
                print("❌ No welcome message received")
                return False
            
            # Quick ping test
            ping_message = {"type": "ping"}
            await websocket.send(json.dumps(ping_message))
            
            try:
                pong_message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                pong_data = json.loads(pong_message)
                
                if (pong_data.get("type") == "pong" and 
                    pong_data.get("data", {}).get("enhanced") == True):
                    print("✅ Enhanced ping-pong working correctly!")
                    return True
                else:
                    print("⚠️  Ping response not enhanced")
                    return False
                    
            except asyncio.TimeoutError:
                print("❌ No pong response")
                return False
                
    except ConnectionRefusedError:
        print("❌ Connection refused")
        print("💡 Make sure to start the server with: python run_server.py")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


async def main():
    """Main test for VaultPilot compatibility"""
    print("🧪 VaultPilot WebSocket Compatibility Test")
    print("=" * 50)
    
    success = await test_vaultpilot_endpoint()
    
    if success:
        print("\n🎉 SUCCESS: VaultPilot WebSocket endpoint is ready!")
        print("📝 VaultPilot can now connect to: ws://localhost:8000/api/obsidian/ws/enhanced")
        print("✨ Enhanced features are working correctly")
    else:
        print("\n❌ FAILED: VaultPilot integration needs attention")
        print("🔧 Check server configuration and try again")


if __name__ == "__main__":
    asyncio.run(main())
