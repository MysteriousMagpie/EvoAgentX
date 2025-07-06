"""
Dev-Pipe Integration Service for VaultPilot Vault Management

This service provides proper dev-pipe protocol integration for all vault management
operations, ensuring structured communication, monitoring, and error handling.
"""

import json
import uuid
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import aiofiles

class DevPipeIntegration:
    """Handles dev-pipe protocol communication for VaultPilot operations"""
    
    def __init__(self, devpipe_root: str = "/Users/malachiledbetter/Documents/GitHub/EvoAgentX/dev-pipe"):
        self.devpipe_root = Path(devpipe_root)
        self.queues_dir = self.devpipe_root / "queues"
        self.tasks_dir = self.devpipe_root / "tasks" 
        self.status_dir = self.devpipe_root / "status"
        self.logs_dir = self.devpipe_root / "logs"
        
        # Ensure directories exist
        for dir_path in [self.queues_dir, self.tasks_dir, self.status_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            for subdir in ["incoming", "outgoing", "processing", "archive"]:
                if dir_path.name == "queues":
                    (dir_path / subdir).mkdir(exist_ok=True)
            for subdir in ["active", "pending", "completed", "failed"]:
                if dir_path.name == "tasks":
                    (dir_path / subdir).mkdir(exist_ok=True)
    
    def generate_message_id(self) -> str:
        """Generate unique message ID"""
        return str(uuid.uuid4())
    
    def get_timestamp(self) -> str:
        """Get ISO 8601 timestamp"""
        return datetime.now().isoformat()
    
    def create_filename(self, message_type: str, message_id: str) -> str:
        """Create standardized filename for dev-pipe messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        return f"{timestamp}_{message_type}_{message_id}.json"
    
    async def create_message(self, message_type: str, payload: Dict[str, Any], 
                           sender: str = "vault-manager", recipient: str = "ai-agent",
                           priority: str = "normal", correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a standardized dev-pipe message"""
        message_id = self.generate_message_id()
        
        message = {
            "header": {
                "message_id": message_id,
                "timestamp": self.get_timestamp(),
                "message_type": message_type,
                "version": "1.0.0",
                "sender": sender,
                "recipient": recipient,
                "priority": priority,
                "correlation_id": correlation_id or message_id
            },
            "payload": payload
        }
        
        return message
    
    async def send_message(self, message: Dict[str, Any], queue_type: str = "outgoing") -> str:
        """Send message through dev-pipe"""
        message_id = message["header"]["message_id"]
        message_type = message["header"]["message_type"]
        filename = self.create_filename(message_type, message_id)
        
        queue_path = self.queues_dir / queue_type / filename
        
        async with aiofiles.open(queue_path, 'w') as f:
            await f.write(json.dumps(message, indent=2))
        
        # Log the message
        await self.log_message("info", f"Message sent: {message_type} ({message_id})")
        
        return message_id
    
    async def receive_message(self, message_id: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """Wait for and receive response message"""
        for _ in range(timeout):
            incoming_files = list((self.queues_dir / "incoming").glob(f"*_{message_id}.json"))
            if incoming_files:
                async with aiofiles.open(incoming_files[0], 'r') as f:
                    content = await f.read()
                    message = json.loads(content)
                
                # Move to archive
                archive_path = self.queues_dir / "archive" / incoming_files[0].name
                incoming_files[0].rename(archive_path)
                
                return message
            
            await asyncio.sleep(1)
        
        return None
    
    async def create_task(self, task_type: str, operation: str, parameters: Dict[str, Any], 
                         priority: str = "normal") -> str:
        """Create a new task in dev-pipe task system"""
        task_id = self.generate_message_id()
        
        task = {
            "task_id": task_id,
            "task_type": task_type,
            "operation": operation,
            "status": "pending",
            "created_at": self.get_timestamp(),
            "priority": priority,
            "parameters": parameters,
            "progress": 0,
            "estimated_duration": None,
            "actual_duration": None,
            "result": None,
            "errors": []
        }
        
        filename = self.create_filename("task", task_id)
        task_path = self.tasks_dir / "pending" / filename
        
        async with aiofiles.open(task_path, 'w') as f:
            await f.write(json.dumps(task, indent=2))
        
        await self.log_message("info", f"Task created: {task_type} - {operation} ({task_id})")
        
        return task_id
    
    async def update_task_status(self, task_id: str, status: str, progress: Optional[int] = None, 
                               result: Any = None, errors: Optional[List[str]] = None):
        """Update task status and move between directories"""
        # Find current task file
        task_file = None
        current_dir = None
        
        for dir_name in ["pending", "active", "completed", "failed"]:
            task_dir = self.tasks_dir / dir_name
            for file_path in task_dir.glob(f"*_{task_id}.json"):
                task_file = file_path
                current_dir = dir_name
                break
            if task_file:
                break
        
        if not task_file:
            await self.log_message("error", f"Task not found: {task_id}")
            return
        
        # Load and update task
        async with aiofiles.open(task_file, 'r') as f:
            task = json.loads(await f.read())
        
        task["status"] = status
        task["updated_at"] = self.get_timestamp()
        
        if progress is not None:
            task["progress"] = progress
        if result is not None:
            task["result"] = result
        if errors is not None:
            task["errors"].extend(errors)
        
        # Determine target directory
        target_dir = {
            "pending": "pending",
            "active": "active", 
            "completed": "completed",
            "failed": "failed",
            "cancelled": "failed"
        }.get(status, current_dir or "failed")  # Default to "failed" if current_dir is None
        
        # Move task file if directory changed
        if target_dir and target_dir != current_dir:
            new_path = self.tasks_dir / target_dir / task_file.name
            task_file.unlink()  # Remove old file
        else:
            new_path = task_file
        
        # Save updated task
        async with aiofiles.open(new_path, 'w') as f:
            await f.write(json.dumps(task, indent=2))
        
        await self.log_message("info", f"Task updated: {task_id} -> {status}")
    
    async def log_message(self, level: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Log message to dev-pipe logs"""
        log_entry = {
            "timestamp": self.get_timestamp(),
            "level": level.upper(),
            "component": "vault-management",
            "message": message,
            "details": details or {}
        }
        
        log_dir = self.logs_dir / level
        log_dir.mkdir(exist_ok=True)
        
        log_filename = f"{datetime.now().strftime('%Y-%m-%d')}_vault-management.log"
        log_path = log_dir / log_filename
        
        async with aiofiles.open(log_path, 'a') as f:
            await f.write(json.dumps(log_entry) + "\n")
    
    async def update_system_status(self, component: str, status: Dict[str, Any]):
        """Update system status in dev-pipe"""
        status_data = {
            "component": component,
            "timestamp": self.get_timestamp(),
            "status": status
        }
        
        status_file = self.status_dir / f"{component}-status.json"
        
        async with aiofiles.open(status_file, 'w') as f:
            await f.write(json.dumps(status_data, indent=2))
    
    async def notify_progress(self, task_id: str, operation: str, progress: int, 
                            eta: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Send progress notification through dev-pipe"""
        progress_message = await self.create_message(
            message_type="progress",
            payload={
                "task_id": task_id,
                "operation": operation,
                "progress_percentage": progress,
                "estimated_completion": eta,
                "details": details or {}
            },
            sender="vault-manager",
            recipient="ai-agent",
            priority="normal"
        )
        
        await self.send_message(progress_message)
        await self.update_task_status(task_id, "active", progress=progress)
    
    async def handle_error(self, task_id: str, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Handle errors through dev-pipe protocol"""
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "timestamp": self.get_timestamp()
        }
        
        # Log error
        await self.log_message("error", f"Task error: {task_id}", error_details)
        
        # Update task status
        await self.update_task_status(task_id, "failed", errors=[str(error)])
        
        # Send error notification
        error_message = await self.create_message(
            message_type="error",
            payload={
                "task_id": task_id,
                "error": error_details
            },
            sender="vault-manager",
            recipient="ai-agent",
            priority="high"
        )
        
        await self.send_message(error_message)
    
    async def send_completion_notification(self, task_id: str, operation: str, 
                                         result: Dict[str, Any], duration: Optional[float] = None):
        """Send task completion notification"""
        completion_message = await self.create_message(
            message_type="completion",
            payload={
                "task_id": task_id,
                "operation": operation,
                "result": result,
                "duration_seconds": duration,
                "completed_at": self.get_timestamp()
            },
            sender="vault-manager",
            recipient="ai-agent",
            priority="normal"
        )
        
        await self.send_message(completion_message)
        await self.update_task_status(task_id, "completed", progress=100, result=result)
        
        # Update system status
        await self.update_system_status("vault-manager", {
            "last_operation": operation,
            "last_completion": self.get_timestamp(),
            "status": "ready"
        })


# Global dev-pipe integration instance
dev_pipe = DevPipeIntegration()
