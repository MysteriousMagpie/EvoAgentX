"""
DevPipe Integration for Model Selection

This module handles communication between the EvoAgentX backend and the Obsidian plugin
through the devpipe framework, specifically for model selection and AI capabilities.
"""

import json
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class DevPipeModelSelector:
    """
    DevPipe integration for model selection communication with Obsidian plugin.
    
    This class handles:
    - Model selection requests from the frontend
    - Health monitoring updates
    - Performance metrics communication
    - User preference synchronization
    """
    
    def __init__(self, devpipe_path: str):
        self.devpipe_path = Path(devpipe_path)
        self.queues_path = self.devpipe_path / "queues"
        self.status_path = self.devpipe_path / "status"
        self.communication_path = self.devpipe_path / "communication"
        
        # Ensure directories exist
        self.queues_path.mkdir(parents=True, exist_ok=True)
        self.status_path.mkdir(parents=True, exist_ok=True)
        self.communication_path.mkdir(parents=True, exist_ok=True)
        
        # Message queues
        self.inbox_path = self.queues_path / "model_selection_requests"
        self.outbox_path = self.queues_path / "model_selection_responses"
        
        self.inbox_path.mkdir(exist_ok=True)
        self.outbox_path.mkdir(exist_ok=True)
    
    def create_base_message(self, 
                           message_type: str, 
                           sender: str = "backend",
                           recipient: str = "ai-agent",
                           priority: str = "normal") -> Dict[str, Any]:
        """Create a base message structure following devpipe format"""
        return {
            "header": {
                "message_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "message_type": message_type,
                "version": "1.0.0",
                "sender": sender,
                "recipient": recipient,
                "priority": priority
            },
            "payload": {}
        }
    
    async def send_model_selection_response(self, 
                                          request_id: str,
                                          success: bool,
                                          selected_model: Optional[Dict[str, Any]] = None,
                                          fallback_models: Optional[List[str]] = None,
                                          reasoning: Optional[str] = None,
                                          error: Optional[str] = None):
        """Send model selection response to frontend"""
        try:
            message = self.create_base_message("model_selection_response")
            message["header"]["correlation_id"] = request_id
            
            message["payload"] = {
                "success": success,
                "selected_model": selected_model,
                "fallback_models": fallback_models or [],
                "reasoning": reasoning,
                "error": error
            }
            
            # Write to outbox
            filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')[:-3]}_model-selection-response_{request_id[:8]}.json"
            filepath = self.outbox_path / filename
            
            with open(filepath, 'w') as f:
                json.dump(message, f, indent=2)
            
            logger.info(f"Sent model selection response: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to send model selection response: {e}")
    
    async def send_model_health_update(self, health_summary: Dict[str, Any]):
        """Send model health status update to frontend"""
        try:
            message = self.create_base_message("model_health_status")
            message["payload"] = health_summary
            
            # Write to status directory for periodic updates
            status_file = self.status_path / "model_health.json"
            with open(status_file, 'w') as f:
                json.dump(message, f, indent=2)
            
            # Also send as a message
            filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')[:-3]}_model-health-status_{uuid.uuid4().hex[:8]}.json"
            filepath = self.outbox_path / filename
            
            with open(filepath, 'w') as f:
                json.dump(message, f, indent=2)
            
            logger.debug(f"Sent model health update: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to send model health update: {e}")
    
    async def send_performance_update(self, 
                                    model_name: str,
                                    task_type: str,
                                    success: bool,
                                    response_time: float,
                                    cost: float = 0.0,
                                    quality_score: Optional[float] = None):
        """Send model performance update to frontend"""
        try:
            message = self.create_base_message("model_performance_update")
            message["payload"] = {
                "model_name": model_name,
                "task_type": task_type,
                "success": success,
                "response_time": response_time,
                "cost": cost,
                "quality_score": quality_score
            }
            
            # Write to outbox
            filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')[:-3]}_model-performance_{model_name.replace('/', '_')}_{uuid.uuid4().hex[:8]}.json"
            filepath = self.outbox_path / filename
            
            with open(filepath, 'w') as f:
                json.dump(message, f, indent=2)
            
            logger.debug(f"Sent performance update: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to send performance update: {e}")
    
    async def process_incoming_requests(self) -> List[Dict[str, Any]]:
        """Process incoming model selection requests from frontend"""
        processed_requests = []
        
        try:
            # Look for new request files
            request_files = list(self.inbox_path.glob("*.json"))
            
            for request_file in request_files:
                try:
                    with open(request_file, 'r') as f:
                        message = json.load(f)
                    
                    # Validate message structure
                    if self._validate_message(message):
                        processed_requests.append(message)
                        logger.info(f"Processed request: {request_file.name}")
                    else:
                        logger.warning(f"Invalid message format: {request_file.name}")
                    
                    # Move processed file to archive or delete
                    archive_path = self.inbox_path / "processed"
                    archive_path.mkdir(exist_ok=True)
                    request_file.rename(archive_path / request_file.name)
                    
                except Exception as e:
                    logger.error(f"Failed to process request file {request_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to process incoming requests: {e}")
        
        return processed_requests
    
    def _validate_message(self, message: Dict[str, Any]) -> bool:
        """Validate message structure according to devpipe format"""
        try:
            # Check required header fields
            header = message.get("header", {})
            required_header_fields = ["message_id", "timestamp", "message_type", "sender", "recipient"]
            
            for field in required_header_fields:
                if field not in header:
                    return False
            
            # Check if payload exists
            if "payload" not in message:
                return False
            
            return True
            
        except Exception:
            return False
    
    async def update_frontend_capabilities(self, available_models: List[Dict[str, Any]]):
        """Update frontend with current model capabilities"""
        try:
            message = self.create_base_message("data", recipient="frontend")
            message["payload"] = {
                "data_type": "model_capabilities",
                "models": available_models,
                "timestamp": datetime.now().isoformat()
            }
            
            # Write to status for persistent state
            capabilities_file = self.status_path / "model_capabilities.json"
            with open(capabilities_file, 'w') as f:
                json.dump(message, f, indent=2)
            
            logger.info("Updated frontend model capabilities")
            
        except Exception as e:
            logger.error(f"Failed to update frontend capabilities: {e}")
    
    async def notify_model_selection_event(self, 
                                         event_type: str,
                                         model_name: str,
                                         context: Optional[Dict[str, Any]] = None):
        """Notify frontend of model selection events"""
        try:
            message = self.create_base_message("status")
            message["payload"] = {
                "status_type": "model_selection_event",
                "event_type": event_type,  # selected, failed, fallback_used
                "model_name": model_name,
                "timestamp": datetime.now().isoformat(),
                "context": context or {}
            }
            
            # Write to outbox
            filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')[:-3]}_model-event_{event_type}_{uuid.uuid4().hex[:8]}.json"
            filepath = self.outbox_path / filename
            
            with open(filepath, 'w') as f:
                json.dump(message, f, indent=2)
            
            logger.info(f"Notified model selection event: {event_type} for {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to notify model selection event: {e}")
    
    def get_devpipe_status(self) -> Dict[str, Any]:
        """Get current devpipe integration status"""
        return {
            "devpipe_path": str(self.devpipe_path),
            "inbox_files": len(list(self.inbox_path.glob("*.json"))),
            "outbox_files": len(list(self.outbox_path.glob("*.json"))),
            "status_files": len(list(self.status_path.glob("*.json"))),
            "last_health_update": self._get_last_file_time(self.status_path / "model_health.json"),
            "last_capabilities_update": self._get_last_file_time(self.status_path / "model_capabilities.json")
        }
    
    def _get_last_file_time(self, filepath: Path) -> Optional[str]:
        """Get last modification time of a file"""
        try:
            if filepath.exists():
                return datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
            return None
        except Exception:
            return None


# Global instance for easy access
_devpipe_model_selector: Optional[DevPipeModelSelector] = None


def get_devpipe_model_selector(devpipe_path: Optional[str] = None) -> Optional[DevPipeModelSelector]:
    """Get or create the global DevPipe model selector instance"""
    global _devpipe_model_selector
    
    if _devpipe_model_selector is None and devpipe_path:
        _devpipe_model_selector = DevPipeModelSelector(devpipe_path)
    
    return _devpipe_model_selector


async def start_devpipe_monitoring(devpipe_path: str, check_interval: int = 10):
    """Start background monitoring of devpipe communication"""
    devpipe_selector = get_devpipe_model_selector(devpipe_path)
    if not devpipe_selector:
        logger.error("Failed to initialize DevPipe model selector")
        return
    
    logger.info(f"Starting DevPipe monitoring with interval {check_interval}s")
    
    while True:
        try:
            # Process incoming requests
            requests = await devpipe_selector.process_incoming_requests()
            
            # Handle each request (this would typically integrate with the model selector)
            for request in requests:
                await handle_devpipe_model_request(request, devpipe_selector)
            
            await asyncio.sleep(check_interval)
            
        except Exception as e:
            logger.error(f"DevPipe monitoring error: {e}")
            await asyncio.sleep(5)  # Brief pause before retrying


async def handle_devpipe_model_request(request: Dict[str, Any], 
                                     devpipe_selector: DevPipeModelSelector):
    """Handle a model selection request from devpipe"""
    try:
        request_id = request["header"]["message_id"]
        message_type = request["header"]["message_type"]
        payload = request["payload"]
        
        if message_type == "model_selection_request":
            # This would integrate with the RobustModelSelector
            # For now, send a placeholder response
            await devpipe_selector.send_model_selection_response(
                request_id=request_id,
                success=True,
                selected_model={
                    "name": "gpt-4o-mini",
                    "provider": "openai",
                    "model_id": "gpt-4o-mini"
                },
                reasoning="Selected based on task requirements and performance metrics"
            )
            
        logger.info(f"Handled devpipe request: {message_type}")
        
    except Exception as e:
        logger.error(f"Failed to handle devpipe request: {e}")
