"""
Robust Model Selection System for EvoAgentX

This module provides intelligent model selection with fallback mechanisms,
performance monitoring, and cost optimization. It integrates with the 
dev-pipe framework for communication and monitoring.
"""

import asyncio
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field
from ..core.logging import logger
from ..core.registry import MODEL_REGISTRY
from .model_configs import LLMConfig
from .base_model import BaseLLM
from .model_utils import Cost, create_llm_instance


class ModelStatus(Enum):
    """Model availability status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


class TaskType(Enum):
    """Types of tasks for performance tracking"""
    CODE_GENERATION = "code_generation"
    QA = "qa"
    REASONING = "reasoning"
    TEXT_GENERATION = "text_generation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    GENERAL = "general"


@dataclass
class ModelPerformanceMetrics:
    """Performance metrics for a model"""
    model_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    total_cost: float = 0.0
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    task_performance: Dict[str, float] = None  # task_type -> success_rate
    
    def __post_init__(self):
        if self.task_performance is None:
            self.task_performance = {}
    
    @property
    def success_rate(self) -> float:
        """Calculate overall success rate"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def cost_per_success(self) -> float:
        """Calculate cost per successful request"""
        if self.successful_requests == 0:
            return float('inf')
        return self.total_cost / self.successful_requests
    
    @property
    def is_healthy(self) -> bool:
        """Determine if model is considered healthy"""
        # Consider healthy if success rate > 80% and recent activity
        recent_threshold = datetime.now() - timedelta(hours=1)
        has_recent_success = (
            self.last_success_time and 
            self.last_success_time > recent_threshold
        )
        return self.success_rate > 0.8 and (has_recent_success or self.total_requests == 0)


@dataclass
class ModelSelectionCriteria:
    """Criteria for model selection"""
    task_type: TaskType = TaskType.GENERAL
    priority_order: List[str] = None  # preferred model order
    max_cost_per_request: Optional[float] = None
    min_success_rate: float = 0.7
    max_response_time: Optional[float] = None
    require_healthy_status: bool = True
    fallback_enabled: bool = True
    
    def __post_init__(self):
        if self.priority_order is None:
            self.priority_order = []


class ModelHealthMonitor:
    """Monitors model health and performance"""
    
    def __init__(self, devpipe_path: Optional[str] = None):
        self.metrics: Dict[str, ModelPerformanceMetrics] = {}
        self.status_cache: Dict[str, Tuple[ModelStatus, datetime]] = {}
        self.devpipe_path = devpipe_path
        self._lock = threading.Lock()
    
    def record_request(self, model_name: str, task_type: TaskType, 
                      success: bool, response_time: float, cost: float = 0.0):
        """Record a model request result"""
        with self._lock:
            if model_name not in self.metrics:
                self.metrics[model_name] = ModelPerformanceMetrics(model_name)
            
            metrics = self.metrics[model_name]
            metrics.total_requests += 1
            metrics.total_cost += cost
            
            if success:
                metrics.successful_requests += 1
                metrics.last_success_time = datetime.now()
                
                # Update task-specific performance
                task_key = task_type.value
                if task_key not in metrics.task_performance:
                    metrics.task_performance[task_key] = 0.0
                
                # Exponential moving average for task performance
                current_rate = metrics.task_performance[task_key]
                metrics.task_performance[task_key] = 0.9 * current_rate + 0.1 * 1.0
            else:
                metrics.failed_requests += 1
                metrics.last_failure_time = datetime.now()
                
                # Update task-specific performance
                task_key = task_type.value
                if task_key not in metrics.task_performance:
                    metrics.task_performance[task_key] = 1.0
                
                current_rate = metrics.task_performance[task_key]
                metrics.task_performance[task_key] = 0.9 * current_rate + 0.1 * 0.0
            
            # Update average response time
            total_time = metrics.average_response_time * (metrics.total_requests - 1) + response_time
            metrics.average_response_time = total_time / metrics.total_requests
            
            # Update status cache
            status = self._determine_status(metrics)
            self.status_cache[model_name] = (status, datetime.now())
            
            # Log to devpipe if available
            self._log_to_devpipe(model_name, success, response_time, cost, task_type)
    
    def _determine_status(self, metrics: ModelPerformanceMetrics) -> ModelStatus:
        """Determine model status based on metrics"""
        if metrics.total_requests < 5:
            return ModelStatus.UNKNOWN
        
        success_rate = metrics.success_rate
        if success_rate >= 0.9:
            return ModelStatus.HEALTHY
        elif success_rate >= 0.7:
            return ModelStatus.DEGRADED
        else:
            return ModelStatus.FAILED
    
    def get_model_status(self, model_name: str) -> ModelStatus:
        """Get current model status"""
        if model_name in self.status_cache:
            status, timestamp = self.status_cache[model_name]
            # Invalidate cache after 10 minutes
            if datetime.now() - timestamp < timedelta(minutes=10):
                return status
        
        if model_name in self.metrics:
            status = self._determine_status(self.metrics[model_name])
            self.status_cache[model_name] = (status, datetime.now())
            return status
        
        return ModelStatus.UNKNOWN
    
    def get_performance_metrics(self, model_name: str) -> Optional[ModelPerformanceMetrics]:
        """Get performance metrics for a model"""
        return self.metrics.get(model_name)
    
    def get_best_models_for_task(self, task_type: TaskType, limit: int = 5) -> List[str]:
        """Get best performing models for a specific task type"""
        task_key = task_type.value
        candidates = []
        
        for model_name, metrics in self.metrics.items():
            if task_key in metrics.task_performance:
                performance = metrics.task_performance[task_key]
                candidates.append((model_name, performance, metrics.cost_per_success))
        
        # Sort by performance (descending) then by cost (ascending)
        candidates.sort(key=lambda x: (-x[1], x[2]))
        return [model_name for model_name, _, _ in candidates[:limit]]
    
    def _log_to_devpipe(self, model_name: str, success: bool, response_time: float, 
                       cost: float, task_type: TaskType):
        """Log metrics to devpipe communication framework"""
        if not self.devpipe_path:
            return
        
        try:
            devpipe_logs = Path(self.devpipe_path) / "logs" / "info"
            devpipe_logs.mkdir(parents=True, exist_ok=True)
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "model_performance",
                "model_name": model_name,
                "success": success,
                "response_time": response_time,
                "cost": cost,
                "task_type": task_type.value
            }
            
            log_file = devpipe_logs / f"model_performance_{datetime.now().strftime('%Y-%m-%d')}.log"
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
                
        except Exception as e:
            logger.warning(f"Failed to log to devpipe: {e}")


class RobustModelSelector:
    """Intelligent model selector with fallback and performance optimization"""
    
    def __init__(self, devpipe_path: Optional[str] = None):
        self.health_monitor = ModelHealthMonitor(devpipe_path)
        self.model_cache: Dict[str, BaseLLM] = {}
        self.devpipe_path = devpipe_path
        self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Initialize default model configurations"""
        self.default_model_configs = {
            TaskType.CODE_GENERATION: [
                "gpt-4o-mini", "anthropic/claude-3-haiku-20240307", 
                "deepseek-ai/deepseek-coder-33b-instruct"
            ],
            TaskType.QA: [
                "gpt-4o-mini", "anthropic/claude-3-sonnet-20240229",
                "meta-llama/Llama-3.1-70B-Instruct"
            ],
            TaskType.REASONING: [
                "gpt-4o", "anthropic/claude-3-opus-20240229",
                "deepseek-ai/DeepSeek-R1"
            ],
            TaskType.GENERAL: [
                "gpt-4o-mini", "anthropic/claude-3-haiku-20240307",
                "meta-llama/Llama-3.1-8B-Instruct"
            ]
        }
    
    def select_model(self, criteria: ModelSelectionCriteria) -> Optional[BaseLLM]:
        """Select the best available model based on criteria"""
        candidates = self._get_candidate_models(criteria)
        
        for model_name in candidates:
            try:
                model = self._get_or_create_model(model_name)
                if model and self._validate_model(model, criteria):
                    logger.info(f"Selected model: {model_name}")
                    self._notify_devpipe_selection(model_name, criteria)
                    return model
            except Exception as e:
                logger.warning(f"Failed to create/validate model {model_name}: {e}")
                self.health_monitor.record_request(
                    model_name, criteria.task_type, False, 0.0, 0.0
                )
                continue
        
        logger.error("No suitable model found matching criteria")
        self._notify_devpipe_failure(criteria)
        return None
    
    def _get_candidate_models(self, criteria: ModelSelectionCriteria) -> List[str]:
        """Get list of candidate models in priority order"""
        candidates = []
        
        # First, add explicitly preferred models
        if criteria.priority_order:
            candidates.extend(criteria.priority_order)
        
        # Then add performance-based recommendations
        performance_models = self.health_monitor.get_best_models_for_task(
            criteria.task_type, limit=3
        )
        candidates.extend(performance_models)
        
        # Finally, add default models for the task type
        default_models = self.default_model_configs.get(criteria.task_type, [])
        candidates.extend(default_models)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for model in candidates:
            if model not in seen:
                seen.add(model)
                unique_candidates.append(model)
        
        return unique_candidates
    
    def _get_or_create_model(self, model_name: str) -> Optional[BaseLLM]:
        """Get existing model from cache or create new one"""
        if model_name in self.model_cache:
            return self.model_cache[model_name]
        
        try:
            # Determine model type and create appropriate config
            model_config = self._create_model_config(model_name)
            if not model_config:
                return None
            
            model = create_llm_instance(model_config)
            self.model_cache[model_name] = model
            return model
            
        except Exception as e:
            logger.error(f"Failed to create model {model_name}: {e}")
            return None
    
    def _create_model_config(self, model_name: str) -> Optional[LLMConfig]:
        """Create appropriate config for model name"""
        # This is a simplified version - in practice, you'd have more sophisticated
        # model type detection and configuration
        
        if model_name.startswith("gpt-") or model_name.startswith("o1-"):
            from .model_configs import OpenAILLMConfig
            return OpenAILLMConfig(
                model=model_name,
                temperature=0.7,
                max_tokens=2000
            )
        elif model_name.startswith("anthropic/"):
            from .model_configs import LiteLLMConfig
            return LiteLLMConfig(
                model=model_name,
                temperature=0.7,
                max_tokens=2000
            )
        elif "deepseek" in model_name.lower():
            from .model_configs import LiteLLMConfig
            return LiteLLMConfig(
                model=model_name,
                temperature=0.7,
                max_tokens=2000
            )
        elif "llama" in model_name.lower() or "meta-llama" in model_name:
            from .model_configs import LiteLLMConfig
            return LiteLLMConfig(
                model=model_name,
                temperature=0.7,
                max_tokens=2000
            )
        else:
            # Default to LiteLLM for unknown models
            from .model_configs import LiteLLMConfig
            return LiteLLMConfig(
                model=model_name,
                temperature=0.7,
                max_tokens=2000
            )
    
    def _validate_model(self, model: BaseLLM, criteria: ModelSelectionCriteria) -> bool:
        """Validate if model meets the selection criteria"""
        model_name = model.config.model
        
        # Check health status
        if criteria.require_healthy_status:
            status = self.health_monitor.get_model_status(model_name)
            if status == ModelStatus.FAILED:
                return False
        
        # Check performance metrics
        metrics = self.health_monitor.get_performance_metrics(model_name)
        if metrics:
            if metrics.success_rate < criteria.min_success_rate:
                return False
            
            if criteria.max_cost_per_request and metrics.cost_per_success > criteria.max_cost_per_request:
                return False
                
            if criteria.max_response_time and metrics.average_response_time > criteria.max_response_time:
                return False
        
        return True
    
    async def generate_with_fallback(self, messages: List[dict], 
                                   criteria: ModelSelectionCriteria,
                                   **kwargs) -> Optional[str]:
        """Generate text with automatic fallback to alternative models"""
        candidates = self._get_candidate_models(criteria)
        
        for model_name in candidates:
            start_time = time.time()
            success = False
            cost = 0.0
            
            try:
                model = self._get_or_create_model(model_name)
                if not model:
                    continue
                
                # Attempt generation
                if hasattr(model, 'single_generate_async'):
                    result = await model.single_generate_async(messages, **kwargs)
                else:
                    # Fallback to synchronous generation
                    result = model.single_generate(messages, **kwargs)
                
                success = True
                response_time = time.time() - start_time
                
                # Extract cost if available
                if hasattr(model, '_last_cost'):
                    cost = getattr(model._last_cost, 'total_cost', 0.0)
                
                # Record successful request
                self.health_monitor.record_request(
                    model_name, criteria.task_type, True, response_time, cost
                )
                
                logger.info(f"Successfully generated with {model_name} in {response_time:.2f}s")
                return result
                
            except Exception as e:
                success = False
                response_time = time.time() - start_time
                
                logger.warning(f"Model {model_name} failed: {e}")
                self.health_monitor.record_request(
                    model_name, criteria.task_type, False, response_time, cost
                )
                
                if not criteria.fallback_enabled:
                    break
                
                continue
        
        logger.error("All models failed to generate response")
        return None
    
    async def generate_with_devpipe_integration(self, 
                                               messages: List[dict], 
                                               criteria: ModelSelectionCriteria,
                                               devpipe_selector=None,
                                               **kwargs) -> Optional[str]:
        """Enhanced generation with devpipe communication"""
        candidates = self._get_candidate_models(criteria)
        
        # Notify devpipe of selection attempt
        if devpipe_selector:
            await devpipe_selector.notify_model_selection_event(
                "selection_started", 
                candidates[0] if candidates else "none",
                {"task_type": criteria.task_type.value, "candidates": candidates}
            )
        
        for i, model_name in enumerate(candidates):
            start_time = time.time()
            success = False
            cost = 0.0
            
            try:
                model = self._get_or_create_model(model_name)
                if not model:
                    continue
                
                # Notify devpipe of model attempt
                if devpipe_selector:
                    await devpipe_selector.notify_model_selection_event(
                        "attempting_model", 
                        model_name,
                        {"attempt": i + 1, "total_candidates": len(candidates)}
                    )
                
                # Attempt generation
                if hasattr(model, 'single_generate_async'):
                    result = await model.single_generate_async(messages, **kwargs)
                else:
                    result = model.single_generate(messages, **kwargs)
                
                success = True
                response_time = time.time() - start_time
                
                # Extract cost if available
                if hasattr(model, '_last_cost'):
                    cost = getattr(model._last_cost, 'total_cost', 0.0)
                
                # Record successful request
                self.health_monitor.record_request(
                    model_name, criteria.task_type, True, response_time, cost
                )
                
                # Notify devpipe of success
                if devpipe_selector:
                    await devpipe_selector.notify_model_selection_event(
                        "model_succeeded", 
                        model_name,
                        {"response_time": response_time, "cost": cost}
                    )
                    
                    await devpipe_selector.send_performance_update(
                        model_name=model_name,
                        task_type=criteria.task_type.value,
                        success=True,
                        response_time=response_time,
                        cost=cost
                    )
                
                logger.info(f"Successfully generated with {model_name} in {response_time:.2f}s")
                return result
                
            except Exception as e:
                success = False
                response_time = time.time() - start_time
                
                logger.warning(f"Model {model_name} failed: {e}")
                self.health_monitor.record_request(
                    model_name, criteria.task_type, False, response_time, cost
                )
                
                # Notify devpipe of failure
                if devpipe_selector:
                    await devpipe_selector.notify_model_selection_event(
                        "model_failed", 
                        model_name,
                        {"error": str(e), "response_time": response_time}
                    )
                    
                    await devpipe_selector.send_performance_update(
                        model_name=model_name,
                        task_type=criteria.task_type.value,
                        success=False,
                        response_time=response_time,
                        cost=cost
                    )
                
                if not criteria.fallback_enabled:
                    break
                
                continue
        
        # Notify devpipe of complete failure
        if devpipe_selector:
            await devpipe_selector.notify_model_selection_event(
                "all_models_failed", 
                "none",
                {"task_type": criteria.task_type.value, "candidates_tried": len(candidates)}
            )
        
        logger.error("All models failed to generate response")
        return None

    def enable_devpipe_integration(self):
        """Enable enhanced devpipe integration features"""
        if self.devpipe_path:
            try:
                from ..integration.devpipe_model_selector import get_devpipe_model_selector
                self.devpipe_integration = get_devpipe_model_selector(str(self.devpipe_path))
                logger.info("DevPipe integration enabled")
                return True
            except ImportError:
                logger.warning("DevPipe integration module not available")
                return False
        return False

    async def sync_health_to_devpipe(self):
        """Sync current health status to devpipe"""
        if hasattr(self, 'devpipe_integration') and self.devpipe_integration:
            try:
                health_summary = self.get_health_summary()
                await self.devpipe_integration.send_model_health_update(health_summary)
                logger.debug("Synced health status to devpipe")
            except Exception as e:
                logger.error(f"Failed to sync health to devpipe: {e}")

    async def sync_capabilities_to_devpipe(self):
        """Sync model capabilities to devpipe"""
        if hasattr(self, 'devpipe_integration') and self.devpipe_integration:
            try:
                available_models = []
                for task_type, models in self.default_model_configs.items():
                    for model_name in models:
                        model_info = {
                            "name": model_name,
                            "capabilities": [task_type.value],
                            "status": self.health_monitor.get_model_status(model_name).value
                        }
                        
                        # Check if we already have this model in the list
                        existing = next((m for m in available_models if m["name"] == model_name), None)
                        if existing:
                            existing["capabilities"].append(task_type.value)
                        else:
                            available_models.append(model_info)
                
                await self.devpipe_integration.update_frontend_capabilities(available_models)
                logger.debug("Synced capabilities to devpipe")
            except Exception as e:
                logger.error(f"Failed to sync capabilities to devpipe: {e}")
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary of all models"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_models": len(self.health_monitor.metrics),
            "healthy_models": 0,
            "degraded_models": 0,
            "failed_models": 0,
            "unknown_models": 0,
            "models": {}
        }
        
        for model_name, metrics in self.health_monitor.metrics.items():
            status = self.health_monitor.get_model_status(model_name)
            
            if status == ModelStatus.HEALTHY:
                summary["healthy_models"] += 1
            elif status == ModelStatus.DEGRADED:
                summary["degraded_models"] += 1
            elif status == ModelStatus.FAILED:
                summary["failed_models"] += 1
            else:
                summary["unknown_models"] += 1
            
            summary["models"][model_name] = {
                "status": status.value,
                "success_rate": metrics.success_rate,
                "total_requests": metrics.total_requests,
                "average_response_time": metrics.average_response_time,
                "cost_per_success": metrics.cost_per_success,
                "task_performance": metrics.task_performance
            }
        
        return summary


# Global instance for easy access
global_model_selector: Optional[RobustModelSelector] = None


def initialize_robust_model_selector(devpipe_path: Optional[str] = None) -> RobustModelSelector:
    """Initialize the global model selector"""
    global global_model_selector
    global_model_selector = RobustModelSelector(devpipe_path)
    return global_model_selector


def get_robust_model_selector() -> Optional[RobustModelSelector]:
    """Get the global model selector instance"""
    return global_model_selector
