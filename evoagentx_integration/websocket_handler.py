"""
WebSocket Handler for VaultPilot Real-time Communication

This file manages WebSocket connections for real-time features like:
- Live chat updates
- Workflow progress notifications
- Copilot suggestions
- Vault synchronization events
"""

from typing import Dict, List, Set, Optional
import json
import asyncio
from datetime import datetime


class WebSocketManager:
    """
    Manages WebSocket connections for VaultPilot clients
    
    Features:
    - Connection management per vault/user
    - Message broadcasting
    - Real-time event handling
    - Connection cleanup
    """
    
    def __init__(self):
        # Store active connections by vault_id
        self.connections: Dict[str, Set] = {}
        # Store user sessions
        self.user_sessions: Dict[str, str] = {}
        
    async def connect(self, websocket, vault_id: str = "default", user_id: Optional[str] = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Initialize vault connections if needed
        if vault_id not in self.connections:
            self.connections[vault_id] = set()
            
        # Add connection to vault group
        self.connections[vault_id].add(websocket)
        
        # Track user session if provided
        if user_id:
            self.user_sessions[user_id] = vault_id
            
        print(f"VaultPilot WebSocket connected: vault={vault_id}, user={user_id}")
        
        # Send welcome message
        await self.send_to_connection(websocket, {
            "type": "connection",
            "data": {
                "status": "connected",
                "vault_id": vault_id,
                "timestamp": datetime.now().isoformat()
            }
        })
        
    async def disconnect(self, websocket, vault_id: str = "default", user_id: Optional[str] = None):
        """Handle WebSocket disconnection"""
        # Remove from vault connections
        if vault_id in self.connections:
            self.connections[vault_id].discard(websocket)
            
            # Clean up empty vault groups
            if not self.connections[vault_id]:
                del self.connections[vault_id]
                
        # Clean up user session
        if user_id and user_id in self.user_sessions:
            del self.user_sessions[user_id]
            
        print(f"VaultPilot WebSocket disconnected: vault={vault_id}, user={user_id}")
        
    async def send_to_connection(self, websocket, message: dict):
        """Send message to a specific connection"""
        try:
            formatted_message = {
                "type": message.get("type", "message"),
                "data": message.get("data", {}),
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_text(json.dumps(formatted_message))
        except Exception as e:
            print(f"Failed to send message to connection: {e}")
            
    async def broadcast_to_vault(self, vault_id: str, message: dict):
        """Broadcast message to all connections in a vault"""
        if vault_id not in self.connections:
            return
            
        # Create list of connections to avoid modification during iteration
        connections = list(self.connections[vault_id])
        
        # Send to all connections
        for websocket in connections:
            try:
                await self.send_to_connection(websocket, message)
            except Exception as e:
                print(f"Failed to send to connection, removing: {e}")
                # Remove failed connection
                self.connections[vault_id].discard(websocket)
                
    async def broadcast_to_user(self, user_id: str, message: dict):
        """Send message to a specific user"""
        if user_id not in self.user_sessions:
            return
            
        vault_id = self.user_sessions[user_id]
        await self.broadcast_to_vault(vault_id, message)
        
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected clients"""
        for vault_id in list(self.connections.keys()):
            await self.broadcast_to_vault(vault_id, message)
            
    # Event-specific broadcasting methods
    
    async def send_chat_update(self, vault_id: str, chat_data: dict):
        """Send real-time chat update"""
        await self.broadcast_to_vault(vault_id, {
            "type": "chat",
            "data": chat_data
        })
        
    async def send_workflow_progress(self, vault_id: str, progress_data: dict):
        """Send workflow progress update"""
        await self.broadcast_to_vault(vault_id, {
            "type": "workflow_progress", 
            "data": progress_data
        })
        
    async def send_copilot_suggestion(self, vault_id: str, suggestion_data: dict):
        """Send copilot suggestion"""
        await self.broadcast_to_vault(vault_id, {
            "type": "copilot",
            "data": suggestion_data
        })
        
    async def send_vault_sync(self, vault_id: str, sync_data: dict):
        """Send vault synchronization update"""
        await self.broadcast_to_vault(vault_id, {
            "type": "vault_sync",
            "data": sync_data
        })
        
    async def send_intent_debug(self, vault_id: str, debug_data: dict):
        """Send intent classification debug info"""
        await self.broadcast_to_vault(vault_id, {
            "type": "intent_debug",
            "data": debug_data
        })
        
    async def send_error(self, vault_id: str, error_message: str):
        """Send error notification"""
        await self.broadcast_to_vault(vault_id, {
            "type": "error",
            "data": {
                "message": error_message,
                "timestamp": datetime.now().isoformat()
            }
        })
        
    def get_connection_count(self, vault_id: Optional[str] = None) -> int:
        """Get number of active connections"""
        if vault_id:
            return len(self.connections.get(vault_id, set()))
        else:
            return sum(len(connections) for connections in self.connections.values())
            
    def get_active_vaults(self) -> List[str]:
        """Get list of vaults with active connections"""
        return list(self.connections.keys())


# Global WebSocket manager instance
websocket_manager = WebSocketManager()


# FastAPI WebSocket route
async def websocket_endpoint(websocket, vault_id: str = "default"):
    """
    Main WebSocket endpoint for VaultPilot
    
    Add this to your FastAPI app:
    
    @app.websocket("/ws/obsidian")
    async def websocket_obsidian(websocket: WebSocket, vault_id: str = "default"):
        await websocket_endpoint(websocket, vault_id)
    """
    
    await websocket_manager.connect(websocket, vault_id)
    
    try:
        while True:
            # Listen for messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_client_message(websocket, vault_id, message)
            except json.JSONDecodeError:
                await websocket_manager.send_error(vault_id, "Invalid JSON message")
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket_manager.disconnect(websocket, vault_id)


async def handle_client_message(websocket, vault_id: str, message: dict):
    """
    Handle incoming messages from VaultPilot clients
    
    You can extend this to handle client-to-server communication.
    """
    message_type = message.get("type", "unknown")
    data = message.get("data", {})
    
    if message_type == "ping":
        # Respond to ping with pong
        await websocket_manager.send_to_connection(websocket, {
            "type": "pong",
            "data": {"timestamp": datetime.now().isoformat()}
        })
        
    elif message_type == "vault_update":
        # Handle vault content updates
        await websocket_manager.send_vault_sync(vault_id, {
            "action": "content_updated",
            "files": data.get("files", []),
            "timestamp": datetime.now().isoformat()
        })
        
    elif message_type == "request_status":
        # Send status information
        await websocket_manager.send_to_connection(websocket, {
            "type": "status",
            "data": {
                "vault_id": vault_id,
                "connections": websocket_manager.get_connection_count(vault_id),
                "timestamp": datetime.now().isoformat()
            }
        })
        
    else:
        print(f"Unknown message type: {message_type}")


# Helper functions for integration with your AI systems

async def notify_workflow_started(vault_id: str, workflow_id: str, goal: str):
    """Notify clients that a workflow has started"""
    await websocket_manager.send_workflow_progress(vault_id, {
        "workflow_id": workflow_id,
        "step": "Starting workflow execution",
        "progress": 0.0,
        "status": "running",
        "goal": goal
    })


async def notify_workflow_step(vault_id: str, workflow_id: str, step: str, progress: float):
    """Notify clients of workflow progress"""
    await websocket_manager.send_workflow_progress(vault_id, {
        "workflow_id": workflow_id,
        "step": step,
        "progress": progress,
        "status": "running"
    })


async def notify_workflow_completed(vault_id: str, workflow_id: str, result: str):
    """Notify clients that a workflow completed"""
    await websocket_manager.send_workflow_progress(vault_id, {
        "workflow_id": workflow_id,
        "step": "Workflow completed successfully",
        "progress": 1.0,
        "status": "completed",
        "result": result
    })


async def notify_chat_response(vault_id: str, conversation_id: str, response: str, agent: str):
    """Notify clients of new chat responses"""
    await websocket_manager.send_chat_update(vault_id, {
        "conversation_id": conversation_id,
        "response": response,
        "agent": agent,
        "timestamp": datetime.now().isoformat()
    })


# Usage example for your AI processing:
"""
# In your chat processing:
async def process_chat(message, vault_id, conversation_id):
    # ... your chat logic ...
    
    # Notify clients of the response
    await notify_chat_response(vault_id, conversation_id, response, agent_name)
    
    return response

# In your workflow processing:
async def execute_workflow(goal, vault_id):
    workflow_id = str(uuid.uuid4())
    
    # Notify start
    await notify_workflow_started(vault_id, workflow_id, goal)
    
    # Process workflow with progress updates
    for step_num, step in enumerate(workflow_steps):
        progress = step_num / len(workflow_steps)
        await notify_workflow_step(vault_id, workflow_id, step, progress)
        
        # ... execute step ...
        
    # Notify completion
    await notify_workflow_completed(vault_id, workflow_id, final_result)
    
    return final_result
"""
