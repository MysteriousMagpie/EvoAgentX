#!/usr/bin/env python3
"""
VaultPilot WebSocket Reconnection Helper

Use this script to reconnect to the EvoAgentX WebSocket when you get disconnected.
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime


async def quick_reconnect(vault_id="default"):
    """Quick reconnection test"""
    url = f"ws://127.0.0.1:8000/ws/obsidian?vault_id={vault_id}"
    
    try:
        print(f"🔌 Attempting to reconnect to vault: {vault_id}")
        
        async with websockets.connect(url) as websocket:
            print("✅ WebSocket reconnected successfully!")
            
            # Send a test message
            test_msg = {
                "type": "ping",
                "data": {"reconnect_test": True},
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(test_msg))
            print("📤 Sent reconnection test ping")
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            data = json.loads(response)
            print(f"📥 Server responded: {data.get('type', 'unknown')}")
            
            # Keep connection alive for a few seconds
            print("🔄 Testing connection stability...")
            await asyncio.sleep(3)
            
            print("✅ Connection test completed successfully!")
            return True
            
    except ConnectionRefusedError:
        print("❌ Connection refused - is the server running?")
        print("💡 Try: python run_server.py --dev")
        return False
        
    except asyncio.TimeoutError:
        print("⏰ Connection timeout - server may be overloaded")
        return False
        
    except Exception as e:
        print(f"❌ Reconnection failed: {e}")
        return False


async def interactive_reconnect():
    """Interactive reconnection with user input"""
    print("🚀 VaultPilot WebSocket Reconnection Helper")
    print("=" * 50)
    
    # Get vault ID from user
    vault_id = input("Enter vault ID (press Enter for 'default'): ").strip()
    if not vault_id:
        vault_id = "default"
    
    print(f"\n🔌 Attempting to reconnect to vault: '{vault_id}'")
    
    success = await quick_reconnect(vault_id)
    
    if success:
        print("\n✅ Reconnection successful!")
        print("📋 Connection Details:")
        print(f"   • Vault ID: {vault_id}")
        print(f"   • WebSocket URL: ws://127.0.0.1:8000/ws/obsidian")
        print(f"   • Server Status: http://127.0.0.1:8000/ws/status")
        
        # Ask if user wants to keep testing
        if input("\nKeep connection alive for testing? (y/N): ").lower().startswith('y'):
            print("🔄 Keeping connection alive... (Press Ctrl+C to stop)")
            try:
                url = f"ws://127.0.0.1:8000/ws/obsidian?vault_id={vault_id}"
                async with websockets.connect(url) as websocket:
                    while True:
                        await asyncio.sleep(10)
                        # Send periodic pings
                        ping_msg = {
                            "type": "ping",
                            "data": {"keepalive": True},
                            "timestamp": datetime.now().isoformat()
                        }
                        await websocket.send(json.dumps(ping_msg))
                        print("💓 Sent keepalive ping")
                        
            except KeyboardInterrupt:
                print("\n🛑 Connection test stopped by user")
    else:
        print("\n❌ Reconnection failed!")
        print("🔧 Troubleshooting tips:")
        print("   1. Check if EvoAgentX server is running:")
        print("      python run_server.py --dev")
        print("   2. Check server status:")
        print("      curl http://127.0.0.1:8000/status")
        print("   3. Check WebSocket status:")
        print("      curl http://127.0.0.1:8000/ws/status")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command line vault ID
        vault_id = sys.argv[1]
        asyncio.run(quick_reconnect(vault_id))
    else:
        # Interactive mode
        asyncio.run(interactive_reconnect())
