from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set, Optional
import json
import asyncio
import uuid
from datetime import datetime


class ObsidianWebSocketManager:
    """WebSocket manager specifically for Obsidian plugin connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict] = {}
        self.vault_connections: Dict[str, Set[str]] = {}  # vault_id -> set of connection_ids
        
    async def connect(self, websocket: WebSocket, vault_id: Optional[str] = None) -> str:
        """Connect a new Obsidian client"""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        
        self.active_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = {
            "vault_id": vault_id,
            "connected_at": datetime.now(),
            "last_activity": datetime.now()
        }
        
        if vault_id:
            if vault_id not in self.vault_connections:
                self.vault_connections[vault_id] = set()
            self.vault_connections[vault_id].add(connection_id)
        
        await self.send_to_connection(connection_id, {
            "type": "connection_established",
            "connection_id": connection_id,
            "vault_id": vault_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return connection_id
    
    def disconnect(self, connection_id: str):
        """Disconnect a client"""
        if connection_id in self.active_connections:
            metadata = self.connection_metadata.get(connection_id, {})
            vault_id = metadata.get("vault_id")
            
            # Remove from vault connections
            if vault_id and vault_id in self.vault_connections:
                self.vault_connections[vault_id].discard(connection_id)
                if not self.vault_connections[vault_id]:
                    del self.vault_connections[vault_id]
            
            # Clean up
            del self.active_connections[connection_id]
            if connection_id in self.connection_metadata:
                del self.connection_metadata[connection_id]
    
    async def send_to_connection(self, connection_id: str, message: dict):
        """Send message to a specific connection"""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_text(json.dumps(message))
                # Update last activity
                if connection_id in self.connection_metadata:
                    self.connection_metadata[connection_id]["last_activity"] = datetime.now()
            except Exception:
                # Connection is probably closed, remove it
                self.disconnect(connection_id)
    
    async def send_to_vault(self, vault_id: str, message: dict):
        """Send message to all connections from a specific vault"""
        if vault_id in self.vault_connections:
            tasks = []
            for connection_id in self.vault_connections[vault_id].copy():
                tasks.append(self.send_to_connection(connection_id, message))
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast(self, message: dict, exclude_connection: Optional[str] = None):
        """Broadcast message to all connected clients"""
        tasks = []
        for connection_id in list(self.active_connections.keys()):
            if connection_id != exclude_connection:
                tasks.append(self.send_to_connection(connection_id, message))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_workflow_progress(self, vault_id: str, workflow_id: str, progress_data: dict):
        """Send workflow execution progress to vault connections"""
        message = {
            "type": "workflow_progress",
            "workflow_id": workflow_id,
            "progress": progress_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_vault(vault_id, message)
    
    async def send_agent_response(self, connection_id: str, conversation_id: str, response: dict):
        """Send agent response to specific connection"""
        message = {
            "type": "agent_response",
            "conversation_id": conversation_id,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_connection(connection_id, message)
    
    async def send_copilot_suggestion(self, connection_id: str, suggestion: dict):
        """Send copilot suggestion to specific connection"""
        message = {
            "type": "copilot_suggestion",
            "suggestion": suggestion,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_connection(connection_id, message)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
    
    def get_vault_connections(self, vault_id: str) -> int:
        """Get number of connections for a specific vault"""
        return len(self.vault_connections.get(vault_id, set()))
    
    def get_connection_info(self, connection_id: str) -> dict:
        """Get information about a specific connection"""
        return self.connection_metadata.get(connection_id, {})


# Global instance
obsidian_ws_manager = ObsidianWebSocketManager()
