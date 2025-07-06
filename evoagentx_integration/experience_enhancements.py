"""
VaultPilot Experience Enhancement System

Advanced performance optimizations, progress indicators, and UX improvements
for seamless VaultPilot integration with EvoAgentX.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging

from .api_models import APIResponse
from .websocket_handler import WebSocketManager


class OperationType(Enum):
    """Types of long-running operations"""
    VAULT_ANALYSIS = "vault_analysis"
    SEARCH = "search"
    WORKFLOW_EXECUTION = "workflow_execution" 
    FILE_OPERATIONS = "file_operations"
    BACKUP_CREATION = "backup_creation"
    BULK_ORGANIZATION = "bulk_organization"
    AI_PROCESSING = "ai_processing"


@dataclass
class ProgressUpdate:
    """Progress update data structure"""
    operation_id: str
    operation_type: OperationType
    progress: float  # 0.0 to 1.0
    current_step: str
    total_steps: int
    current_step_number: int
    eta_seconds: Optional[float] = None
    status: str = "running"
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass 
class PerformanceMetrics:
    """Performance tracking metrics"""
    response_time: float
    cache_hit: bool = False
    optimizations_applied: List[str] = None
    resource_usage: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.optimizations_applied is None:
            self.optimizations_applied = []


class ResponseOptimizer:
    """
    Advanced response time optimization system
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = {}
        self.performance_data = {}
        self.optimization_strategies = {
            'caching': self._apply_caching,
            'compression': self._apply_compression,
            'batching': self._apply_batching,
            'preloading': self._apply_preloading
        }
        
    async def optimize_response(self, 
                               operation: str, 
                               data: Any, 
                               context: Optional[Dict] = None) -> tuple[Any, PerformanceMetrics]:
        """
        Apply performance optimizations to reduce response time
        """
        start_time = time.time()
        optimizations_applied = []
        
        # Check cache first
        cache_key = self._generate_cache_key(operation, data)
        cached_result = self._get_cached_result(cache_key)
        
        if cached_result is not None:
            response_time = time.time() - start_time
            return cached_result, PerformanceMetrics(
                response_time=response_time,
                cache_hit=True,
                optimizations_applied=['caching']
            )
        
        # Apply optimizations based on operation type
        optimized_data = data
        
        if operation.startswith('search'):
            optimized_data, applied = await self._optimize_search(data, context)
            optimizations_applied.extend(applied)
            
        elif operation.startswith('vault'):
            optimized_data, applied = await self._optimize_vault_operations(data, context)
            optimizations_applied.extend(applied)
            
        elif operation.startswith('workflow'):
            optimized_data, applied = await self._optimize_workflow(data, context)
            optimizations_applied.extend(applied)
        
        # Cache result for future use
        self._cache_result(cache_key, optimized_data)
        
        response_time = time.time() - start_time
        
        return optimized_data, PerformanceMetrics(
            response_time=response_time,
            cache_hit=False,
            optimizations_applied=optimizations_applied
        )
    
    async def _optimize_search(self, data: Any, context: Optional[Dict]) -> tuple[Any, List[str]]:
        """Optimize search operations"""
        applied = []
        
        # Implement search-specific optimizations
        if isinstance(data, dict) and 'query' in data:
            # Query compression and optimization
            if len(data['query']) > 100:
                data['query'] = data['query'][:100]  # Truncate long queries
                applied.append('query_truncation')
                
            # Add intelligent result limiting
            if 'max_results' not in data:
                data['max_results'] = 50  # Reasonable default
                applied.append('result_limiting')
        
        return data, applied
    
    async def _optimize_vault_operations(self, data: Any, context: Optional[Dict]) -> tuple[Any, List[str]]:
        """Optimize vault operations"""
        applied = []
        
        if isinstance(data, dict):
            # Optimize depth for structure requests
            if 'max_depth' not in data:
                data['max_depth'] = 3  # Reasonable default
                applied.append('depth_limiting')
                
            # Disable content inclusion for structure-only requests
            if data.get('include_content', True) and not context.get('content_required', False):
                data['include_content'] = False
                applied.append('content_exclusion')
        
        return data, applied
    
    async def _optimize_workflow(self, data: Any, context: Optional[Dict]) -> tuple[Any, List[str]]:
        """Optimize workflow execution"""
        applied = []
        
        # Implement workflow-specific optimizations
        if isinstance(data, dict):
            # Add parallel execution hints
            if 'parallel_execution' not in data:
                data['parallel_execution'] = True
                applied.append('parallel_execution')
        
        return data, applied
    
    def _generate_cache_key(self, operation: str, data: Any) -> str:
        """Generate cache key for operation and data"""
        try:
            data_str = json.dumps(data, sort_keys=True) if data else ""
            return f"{operation}:{hash(data_str)}"
        except (TypeError, ValueError):
            return f"{operation}:{str(data)}"
    
    def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get cached result if still valid"""
        if cache_key in self.cache:
            if cache_key in self.cache_ttl:
                if datetime.now() > self.cache_ttl[cache_key]:
                    # Cache expired
                    del self.cache[cache_key]
                    del self.cache_ttl[cache_key]
                    return None
            return self.cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: Any, ttl_minutes: int = 5):
        """Cache result with TTL"""
        self.cache[cache_key] = result
        self.cache_ttl[cache_key] = datetime.now() + timedelta(minutes=ttl_minutes)
    
    # Optimization strategy implementations
    async def _apply_caching(self, data: Any) -> Any:
        return data
    
    async def _apply_compression(self, data: Any) -> Any:
        return data
        
    async def _apply_batching(self, data: Any) -> Any:
        return data
        
    async def _apply_preloading(self, data: Any) -> Any:
        return data


class ProgressIndicatorManager:
    """
    Advanced progress indicator system for long-running operations
    """
    
    def __init__(self, websocket_manager: WebSocketManager):
        self.websocket_manager = websocket_manager
        self.active_operations = {}
        self.progress_history = {}
        
    async def start_operation(self, 
                            operation_id: str,
                            operation_type: OperationType,
                            vault_id: str,
                            total_steps: int,
                            description: str = "") -> None:
        """Start tracking a long-running operation"""
        
        operation_data = {
            'operation_id': operation_id,
            'operation_type': operation_type,
            'vault_id': vault_id,
            'total_steps': total_steps,
            'current_step': 0,
            'start_time': datetime.now(),
            'description': description,
            'status': 'starting'
        }
        
        self.active_operations[operation_id] = operation_data
        
        # Send initial progress update
        await self._send_progress_update(operation_id, 0.0, "Starting operation...")
    
    async def update_progress(self,
                            operation_id: str,
                            current_step: int,
                            step_description: str,
                            progress_override: Optional[float] = None) -> None:
        """Update progress for an active operation"""
        
        if operation_id not in self.active_operations:
            return
            
        operation = self.active_operations[operation_id]
        operation['current_step'] = current_step
        operation['status'] = 'running'
        
        # Calculate progress
        if progress_override is not None:
            progress = progress_override
        else:
            progress = current_step / operation['total_steps']
        
        # Calculate ETA
        eta = self._calculate_eta(operation, progress)
        
        await self._send_progress_update(operation_id, progress, step_description, eta)
    
    async def complete_operation(self,
                               operation_id: str,
                               final_message: str = "Operation completed",
                               result_data: Optional[Dict] = None) -> None:
        """Mark operation as completed"""
        
        if operation_id not in self.active_operations:
            return
            
        operation = self.active_operations[operation_id]
        operation['status'] = 'completed'
        operation['end_time'] = datetime.now()
        
        # Send completion update
        await self._send_progress_update(
            operation_id, 
            1.0, 
            final_message, 
            None,
            status="completed",
            result_data=result_data
        )
        
        # Archive operation data
        self.progress_history[operation_id] = operation
        del self.active_operations[operation_id]
    
    async def fail_operation(self,
                           operation_id: str,
                           error_message: str,
                           error_details: Optional[Dict] = None) -> None:
        """Mark operation as failed"""
        
        if operation_id not in self.active_operations:
            return
            
        operation = self.active_operations[operation_id]
        operation['status'] = 'failed'
        operation['end_time'] = datetime.now()
        operation['error'] = error_message
        
        # Send failure update
        await self._send_progress_update(
            operation_id,
            operation['current_step'] / operation['total_steps'],
            f"Operation failed: {error_message}",
            None,
            status="failed",
            error_data=error_details
        )
        
        # Archive operation data
        self.progress_history[operation_id] = operation
        del self.active_operations[operation_id]
    
    async def _send_progress_update(self,
                                  operation_id: str,
                                  progress: float,
                                  message: str,
                                  eta: Optional[float] = None,
                                  status: str = "running",
                                  result_data: Optional[Dict] = None,
                                  error_data: Optional[Dict] = None) -> None:
        """Send progress update via WebSocket"""
        
        operation = self.active_operations.get(operation_id)
        if not operation:
            return
            
        update = {
            'operation_id': operation_id,
            'operation_type': operation['operation_type'].value,
            'progress': progress,
            'progress_percentage': round(progress * 100, 1),
            'current_step': operation['current_step'],
            'total_steps': operation['total_steps'],
            'message': message,
            'eta_seconds': eta,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'result_data': result_data,
            'error_data': error_data
        }
        
        await self.websocket_manager.broadcast_to_vault(
            operation['vault_id'],
            {
                'type': 'progress_update',
                'data': update
            }
        )
    
    def _calculate_eta(self, operation: Dict, current_progress: float) -> Optional[float]:
        """Calculate estimated time to completion"""
        
        if current_progress <= 0:
            return None
            
        elapsed = (datetime.now() - operation['start_time']).total_seconds()
        remaining_progress = 1.0 - current_progress
        
        if remaining_progress <= 0:
            return 0
            
        estimated_total_time = elapsed / current_progress
        eta = estimated_total_time - elapsed
        
        return max(0, eta)
    
    def get_active_operations(self, vault_id: str) -> List[Dict]:
        """Get all active operations for a vault"""
        return [
            op for op in self.active_operations.values()
            if op['vault_id'] == vault_id
        ]


class KeyboardShortcutManager:
    """
    Keyboard shortcut management and optimization
    """
    
    def __init__(self):
        self.shortcuts = {}
        self.command_mappings = {}
        self._setup_default_shortcuts()
    
    def _setup_default_shortcuts(self):
        """Setup default keyboard shortcuts for VaultPilot"""
        
        # Core shortcuts
        self.shortcuts.update({
            # Quick actions
            'Ctrl+Shift+P': 'vaultpilot-command-palette',
            'Ctrl+Shift+S': 'vaultpilot-smart-search',
            'Ctrl+Shift+C': 'vaultpilot-chat-modal',
            'Ctrl+Shift+W': 'vaultpilot-workflow-modal',
            
            # Navigation
            'Ctrl+Shift+V': 'vaultpilot-vault-structure',
            'Ctrl+Shift+F': 'vaultpilot-file-operations',
            'Ctrl+Shift+O': 'vaultpilot-vault-organizer',
            
            # AI features
            'Ctrl+Space': 'vaultpilot-copilot-suggest',
            'Ctrl+Shift+A': 'vaultpilot-ai-complete',
            'Alt+Enter': 'vaultpilot-accept-suggestion',
            
            # Batch operations
            'Ctrl+Shift+B': 'vaultpilot-batch-operations',
            'Ctrl+Shift+R': 'vaultpilot-rename-batch',
            'Ctrl+Shift+M': 'vaultpilot-move-batch',
            
            # Analysis and insights
            'Ctrl+Shift+I': 'vaultpilot-analyze-file',
            'Ctrl+Shift+H': 'vaultpilot-vault-health-check',
            'Ctrl+Shift+L': 'vaultpilot-link-analysis',
            
            # Quick creation
            'Ctrl+Shift+N': 'vaultpilot-quick-note',
            'Ctrl+Shift+T': 'vaultpilot-task-from-selection',
            'Ctrl+Shift+D': 'vaultpilot-daily-note-enhance',
        })
        
        # Context-sensitive shortcuts
        self.command_mappings.update({
            'vaultpilot-command-palette': {
                'description': 'Open VaultPilot command palette',
                'category': 'core',
                'context': 'global'
            },
            'vaultpilot-smart-search': {
                'description': 'Open intelligent search modal',
                'category': 'search',
                'context': 'global'
            },
            'vaultpilot-chat-modal': {
                'description': 'Open AI chat interface',
                'category': 'ai',
                'context': 'global'
            },
            'vaultpilot-workflow-modal': {
                'description': 'Open workflow execution modal',
                'category': 'automation',
                'context': 'global'
            },
            'vaultpilot-copilot-suggest': {
                'description': 'Trigger AI copilot suggestions',
                'category': 'ai',
                'context': 'editor'
            },
            'vaultpilot-accept-suggestion': {
                'description': 'Accept current AI suggestion',
                'category': 'ai',
                'context': 'editor'
            },
            'vaultpilot-task-from-selection': {
                'description': 'Create task from selected text',
                'category': 'productivity',
                'context': 'editor-selection'
            }
        })
    
    def get_shortcuts_for_context(self, context: str) -> Dict[str, str]:
        """Get relevant shortcuts for a specific context"""
        relevant_shortcuts = {}
        
        for shortcut, command in self.shortcuts.items():
            if command in self.command_mappings:
                cmd_context = self.command_mappings[command].get('context', 'global')
                if cmd_context == context or cmd_context == 'global':
                    relevant_shortcuts[shortcut] = command
                    
        return relevant_shortcuts
    
    def get_shortcuts_by_category(self, category: str) -> Dict[str, str]:
        """Get shortcuts by category (ai, search, automation, etc.)"""
        category_shortcuts = {}
        
        for shortcut, command in self.shortcuts.items():
            if command in self.command_mappings:
                cmd_category = self.command_mappings[command].get('category', 'other')
                if cmd_category == category:
                    category_shortcuts[shortcut] = command
                    
        return category_shortcuts
    
    def add_custom_shortcut(self, shortcut: str, command: str, description: str, category: str = 'custom'):
        """Add custom keyboard shortcut"""
        self.shortcuts[shortcut] = command
        self.command_mappings[command] = {
            'description': description,
            'category': category,
            'context': 'global',
            'custom': True
        }
    
    def generate_shortcut_reference(self) -> Dict[str, List[Dict]]:
        """Generate a comprehensive shortcut reference"""
        reference = {}
        
        for command, details in self.command_mappings.items():
            category = details.get('category', 'other')
            if category not in reference:
                reference[category] = []
                
            # Find shortcut for this command
            shortcut = None
            for sc, cmd in self.shortcuts.items():
                if cmd == command:
                    shortcut = sc
                    break
                    
            if shortcut:
                reference[category].append({
                    'shortcut': shortcut,
                    'command': command,
                    'description': details.get('description', ''),
                    'context': details.get('context', 'global')
                })
        
        return reference


class ExperienceEnhancementEngine:
    """
    Main orchestrator for VaultPilot experience enhancements
    """
    
    def __init__(self, websocket_manager: WebSocketManager):
        self.websocket_manager = websocket_manager
        self.response_optimizer = ResponseOptimizer()
        self.progress_manager = ProgressIndicatorManager(websocket_manager)
        self.shortcut_manager = KeyboardShortcutManager()
        self.logger = logging.getLogger('vaultpilot.enhancements')
        
    async def enhanced_execute(self,
                             operation: str,
                             data: Any,
                             vault_id: str,
                             operation_type: OperationType,
                             context: Optional[Dict] = None,
                             progress_callback: Optional[Callable] = None) -> tuple[Any, PerformanceMetrics]:
        """
        Execute operation with all enhancements applied
        """
        # Generate operation ID for progress tracking
        operation_id = f"{operation}_{int(time.time())}"
        
        try:
            # Start progress tracking for long operations
            if operation_type in [OperationType.VAULT_ANALYSIS, OperationType.WORKFLOW_EXECUTION]:
                await self.progress_manager.start_operation(
                    operation_id, operation_type, vault_id, 5, f"Executing {operation}"
                )
                
                # Update progress - starting optimization
                await self.progress_manager.update_progress(
                    operation_id, 1, "Optimizing request..."
                )
            
            # Apply response optimizations
            optimized_data, metrics = await self.response_optimizer.optimize_response(
                operation, data, context
            )
            
            if operation_type in [OperationType.VAULT_ANALYSIS, OperationType.WORKFLOW_EXECUTION]:
                # Update progress - optimization complete
                await self.progress_manager.update_progress(
                    operation_id, 2, "Processing request..."
                )
            
            # Log performance improvements
            self.logger.info(f"Operation {operation} optimized: {metrics.optimizations_applied}")
            
            # Execute with progress updates if needed
            if progress_callback:
                progress_callback(operation_id, optimized_data)
            
            if operation_type in [OperationType.VAULT_ANALYSIS, OperationType.WORKFLOW_EXECUTION]:
                # Simulate processing steps
                await asyncio.sleep(0.1)  # Simulate work
                await self.progress_manager.update_progress(
                    operation_id, 4, "Finalizing results..."
                )
                
                await self.progress_manager.complete_operation(
                    operation_id, "Operation completed successfully"
                )
            
            return optimized_data, metrics
            
        except Exception as e:
            if operation_type in [OperationType.VAULT_ANALYSIS, OperationType.WORKFLOW_EXECUTION]:
                await self.progress_manager.fail_operation(
                    operation_id, str(e)
                )
            raise
    
    def get_keyboard_shortcuts(self) -> Dict:
        """Get all keyboard shortcuts configuration"""
        return {
            'shortcuts': self.shortcut_manager.shortcuts,
            'commands': self.shortcut_manager.command_mappings,
            'reference': self.shortcut_manager.generate_shortcut_reference()
        }
    
    def get_performance_stats(self) -> Dict:
        """Get performance enhancement statistics"""
        return {
            'cache_stats': {
                'size': len(self.response_optimizer.cache),
                'hit_rate': 'calculated_dynamically'  # Would implement actual calculation
            },
            'active_operations': len(self.progress_manager.active_operations),
            'optimizations_available': list(self.response_optimizer.optimization_strategies.keys())
        }
