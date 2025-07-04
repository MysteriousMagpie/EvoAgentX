#!/usr/bin/env python3
"""
WebSocket Reconnection Test for VaultPilot

This script tests the WebSocket connection and demonstrates reconnection logic.
"""

import asyncio
import websockets
import json
import time
from datetime import datetime


class VaultPilotWebSocketClient:
    def __init__(self, url="ws://127.0.0.1:8000/ws/obsidian", vault_id="test"):
        self.url = f"{url}?vault_id={vault_id}"
        self.vault_id = vault_id
        self.websocket = None
        self.running = False
        self.reconnect_delay = 5  # seconds
        
    async def connect(self):
        """Connect to WebSocket with retry logic"""
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print(f"🔌 Connecting to WebSocket: {self.url}")
                self.websocket = await websockets.connect(self.url)
                print("✅ WebSocket connected successfully!")
                return True
                
            except Exception as e:
                retry_count += 1
                print(f"❌ Connection attempt {retry_count} failed: {e}")
                
                if retry_count < max_retries:
                    print(f"⏳ Retrying in {self.reconnect_delay} seconds...")
                    await asyncio.sleep(self.reconnect_delay)
                else:
                    print("🚫 Max retries reached. Connection failed.")
                    return False
                    
    async def send_message(self, message_type, data=None):
        """Send a message to the server"""
        if not self.websocket:
            print("❌ No WebSocket connection")
            return False
            
        try:
            message = {
                "type": message_type,
                "data": data or {},
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket.send(json.dumps(message))
            print(f"📤 Sent: {message_type}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return False
            
    async def listen(self):
        """Listen for messages from server"""
        try:
            while self.running and self.websocket:
                try:
                    message = await asyncio.wait_for(
                        self.websocket.recv(), 
                        timeout=30.0  # 30 second timeout
                    )
                    
                    data = json.loads(message)
                    print(f"📥 Received: {data.get('type', 'unknown')} - {data}")
                    
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    await self.send_message("ping", {"keepalive": True})
                    
                except websockets.exceptions.ConnectionClosed:
                    print("⚠️ WebSocket connection closed")
                    break
                    
        except Exception as e:
            print(f"❌ Listen error: {e}")
            
    async def start(self):
        """Start the WebSocket client with auto-reconnect"""
        self.running = True
        
        while self.running:
            if await self.connect():
                # Start listening for messages
                listen_task = asyncio.create_task(self.listen())
                
                # Send initial ping
                await self.send_message("ping", {"initial": True})
                
                # Wait for listening to complete (or fail)
                try:
                    await listen_task
                except Exception as e:
                    print(f"❌ Listening task failed: {e}")
                    
                # Close current connection
                if self.websocket:
                    await self.websocket.close()
                    self.websocket = None
                    
                # Attempt reconnection if still running
                if self.running:
                    print(f"🔄 Reconnecting in {self.reconnect_delay} seconds...")
                    await asyncio.sleep(self.reconnect_delay)
            else:
                print("🚫 Failed to establish connection. Exiting.")
                break
                
    async def stop(self):
        """Stop the WebSocket client"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        print("🛑 WebSocket client stopped")


async def main():
    """Test WebSocket connection and reconnection"""
    print("🚀 Starting VaultPilot WebSocket Test")
    print("=" * 50)
    
    client = VaultPilotWebSocketClient()
    
    try:
        # Start the client (this will run until stopped)
        client_task = asyncio.create_task(client.start())
        
        # Let it run for 30 seconds, then stop
        await asyncio.sleep(30)
        await client.stop()
        
        # Wait for client task to complete
        await client_task
        
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        await client.stop()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        await client.stop()
        
    print("✅ WebSocket test completed")


if __name__ == "__main__":
    asyncio.run(main())
