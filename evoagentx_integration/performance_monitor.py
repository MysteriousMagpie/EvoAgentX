"""
Performance Monitoring and Analytics for VaultPilot Integration

Advanced monitoring, analytics, and performance optimization for
VaultPilot's integration with EvoAgentX.
"""

import time
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging

from .api_models import APIResponse


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    endpoint: str
    method: str
    duration: float
    status_code: int
    timestamp: datetime
    user_id: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class UsageMetric:
    """Usage analytics metric"""
    feature: str
    action: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class PerformanceMonitor:
    """
    Performance monitoring and analytics system for VaultPilot integration.
    
    Tracks API performance, user behavior, and system health metrics.
    """
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.performance_metrics = deque(maxlen=max_metrics)
        self.usage_metrics = deque(maxlen=max_metrics)
        self.error_metrics = deque(maxlen=max_metrics)
        
        # Real-time statistics
        self.endpoint_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'total_requests': 0,
            'total_duration': 0.0,
            'error_count': 0,
            'avg_duration': 0.0,
            'last_request': None
        })
        
        self.feature_usage: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'total_uses': 0,
            'unique_users': set(),
            'last_used': None,
            'popular_actions': defaultdict(int)
        })
        
        # Setup logging
        self.logger = logging.getLogger('vaultpilot.monitoring')
        
    async def track_api_performance(self, 
                                  endpoint: str, 
                                  method: str, 
                                  duration: float, 
                                  status_code: int,
                                  user_id: Optional[str] = None,
                                  error: Optional[str] = None,
                                  metadata: Optional[Dict[str, Any]] = None):
        """Track API endpoint performance"""
        
        metric = PerformanceMetric(
            endpoint=endpoint,
            method=method,
            duration=duration,
            status_code=status_code,
            timestamp=datetime.now(),
            user_id=user_id,
            error=error,
            metadata=metadata
        )
        
        self.performance_metrics.append(metric)
        await self._update_endpoint_stats(metric)
        
        # Log slow requests
        if duration > 2.0:  # Log requests taking more than 2 seconds
            self.logger.warning(f"Slow request: {method} {endpoint} took {duration:.2f}s")
        
        # Log errors
        if status_code >= 400:
            self.logger.error(f"API error: {method} {endpoint} returned {status_code} - {error}")
    
    async def track_feature_usage(self,
                                feature: str,
                                action: str,
                                user_id: Optional[str] = None,
                                session_id: Optional[str] = None,
                                metadata: Optional[Dict[str, Any]] = None):
        """Track feature usage analytics"""
        
        metric = UsageMetric(
            feature=feature,
            action=action,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata
        )
        
        self.usage_metrics.append(metric)
        await self._update_feature_stats(metric)
        
        self.logger.info(f"Feature usage: {feature}.{action} by user {user_id}")
    
    async def track_error(self,
                         error_type: str,
                         error_message: str,
                         context: Optional[Dict[str, Any]] = None,
                         user_id: Optional[str] = None):
        """Track application errors"""
        
        error_metric = {
            'error_type': error_type,
            'error_message': error_message,
            'context': context,
            'user_id': user_id,
            'timestamp': datetime.now()
        }
        
        self.error_metrics.append(error_metric)
        
        self.logger.error(f"Application error: {error_type} - {error_message}")
    
    async def _update_endpoint_stats(self, metric: PerformanceMetric):
        """Update real-time endpoint statistics"""
        key = f"{metric.method} {metric.endpoint}"
        stats = self.endpoint_stats[key]
        
        stats['total_requests'] += 1
        stats['total_duration'] += metric.duration
        stats['avg_duration'] = stats['total_duration'] / stats['total_requests']
        stats['last_request'] = metric.timestamp
        
        if metric.status_code >= 400:
            stats['error_count'] += 1
    
    async def _update_feature_stats(self, metric: UsageMetric):
        """Update real-time feature usage statistics"""
        stats = self.feature_usage[metric.feature]
        
        stats['total_uses'] += 1
        stats['last_used'] = metric.timestamp
        stats['popular_actions'][metric.action] += 1
        
        if metric.user_id:
            stats['unique_users'].add(metric.user_id)
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_metrics = [
            m for m in self.performance_metrics 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {'message': 'No recent metrics available'}
        
        # Calculate summary statistics
        total_requests = len(recent_metrics)
        avg_duration = sum(m.duration for m in recent_metrics) / total_requests
        error_rate = sum(1 for m in recent_metrics if m.status_code >= 400) / total_requests
        
        # Top endpoints by request count
        endpoint_counts = defaultdict(int)
        for metric in recent_metrics:
            endpoint_counts[f"{metric.method} {metric.endpoint}"] += 1
        
        top_endpoints = sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Slowest endpoints
        endpoint_durations = defaultdict(list)
        for metric in recent_metrics:
            endpoint_durations[f"{metric.method} {metric.endpoint}"].append(metric.duration)
        
        slowest_endpoints = []
        for endpoint, durations in endpoint_durations.items():
            avg_duration = sum(durations) / len(durations)
            slowest_endpoints.append((endpoint, avg_duration))
        
        slowest_endpoints = sorted(slowest_endpoints, key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'period_hours': hours,
            'total_requests': total_requests,
            'average_duration': round(avg_duration, 3),
            'error_rate': round(error_rate * 100, 2),
            'top_endpoints': top_endpoints,
            'slowest_endpoints': [(ep, round(dur, 3)) for ep, dur in slowest_endpoints],
            'timestamp': datetime.now().isoformat()
        }
    
    def get_usage_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Get usage analytics for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_usage = [
            m for m in self.usage_metrics 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_usage:
            return {'message': 'No recent usage data available'}
        
        # Feature usage summary
        feature_counts = defaultdict(int)
        action_counts = defaultdict(int)
        unique_users = set()
        
        for metric in recent_usage:
            feature_counts[metric.feature] += 1
            action_counts[f"{metric.feature}.{metric.action}"] += 1
            if metric.user_id:
                unique_users.add(metric.user_id)
        
        top_features = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'period_hours': hours,
            'total_interactions': len(recent_usage),
            'unique_users': len(unique_users),
            'top_features': top_features,
            'top_actions': top_actions,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_errors = [
            e for e in self.error_metrics 
            if e['timestamp'] >= cutoff_time
        ]
        
        if not recent_errors:
            return {'message': 'No recent errors', 'error_count': 0}
        
        error_types = defaultdict(int)
        for error in recent_errors:
            error_types[error['error_type']] += 1
        
        top_errors = sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'period_hours': hours,
            'total_errors': len(recent_errors),
            'error_types': top_errors,
            'recent_errors': [
                {
                    'type': e['error_type'],
                    'message': e['error_message'],
                    'timestamp': e['timestamp'].isoformat()
                }
                for e in recent_errors[-5:]  # Last 5 errors
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        
        # Recent performance metrics
        recent_perf = [m for m in self.performance_metrics if m.timestamp >= last_hour]
        recent_errors = [e for e in self.error_metrics if e['timestamp'] >= last_hour]
        
        # Calculate health scores
        performance_score = self._calculate_performance_score(recent_perf)
        error_score = self._calculate_error_score(recent_errors)
        usage_score = self._calculate_usage_score()
        
        overall_health = (performance_score + error_score + usage_score) / 3
        
        health_status = "healthy"
        if overall_health < 0.5:
            health_status = "critical"
        elif overall_health < 0.7:
            health_status = "warning"
        elif overall_health < 0.9:
            health_status = "degraded"
        
        return {
            'status': health_status,
            'overall_score': round(overall_health, 2),
            'performance_score': round(performance_score, 2),
            'error_score': round(error_score, 2),
            'usage_score': round(usage_score, 2),
            'metrics': {
                'requests_last_hour': len(recent_perf),
                'errors_last_hour': len(recent_errors),
                'avg_response_time': round(sum(m.duration for m in recent_perf) / len(recent_perf), 3) if recent_perf else 0,
                'active_endpoints': len(set(f"{m.method} {m.endpoint}" for m in recent_perf))
            },
            'timestamp': now.isoformat()
        }
    
    def _calculate_performance_score(self, recent_metrics: List[PerformanceMetric]) -> float:
        """Calculate performance health score (0-1)"""
        if not recent_metrics:
            return 1.0
        
        avg_duration = sum(m.duration for m in recent_metrics) / len(recent_metrics)
        error_rate = sum(1 for m in recent_metrics if m.status_code >= 400) / len(recent_metrics)
        
        # Score based on response time and error rate
        duration_score = max(0, 1 - (avg_duration - 0.5) / 2.0)  # Optimal: < 0.5s
        error_score = max(0, 1 - error_rate * 5)  # Penalize errors heavily
        
        return (duration_score + error_score) / 2
    
    def _calculate_error_score(self, recent_errors: List[Dict]) -> float:
        """Calculate error health score (0-1)"""
        if not recent_errors:
            return 1.0
        
        # Score based on error frequency
        error_count = len(recent_errors)
        if error_count == 0:
            return 1.0
        elif error_count <= 5:
            return 0.8
        elif error_count <= 10:
            return 0.6
        elif error_count <= 20:
            return 0.4
        else:
            return 0.2
    
    def _calculate_usage_score(self) -> float:
        """Calculate usage health score (0-1)"""
        # Score based on recent activity
        last_hour = datetime.now() - timedelta(hours=1)
        recent_usage = [m for m in self.usage_metrics if m.timestamp >= last_hour]
        
        if not recent_usage:
            return 0.5  # Neutral score for no usage
        
        # More usage generally indicates healthy system
        usage_count = len(recent_usage)
        if usage_count >= 50:
            return 1.0
        elif usage_count >= 20:
            return 0.8
        elif usage_count >= 10:
            return 0.6
        else:
            return 0.4
    
    async def generate_analytics_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        
        performance = self.get_performance_summary(hours)
        usage = self.get_usage_analytics(hours)
        errors = self.get_error_summary(hours)
        health = self.get_system_health()
        
        # Calculate trends (compare with previous period)
        previous_period_perf = self.get_performance_summary(hours * 2)
        
        trends = {}
        if previous_period_perf.get('total_requests'):
            current_requests = performance.get('total_requests', 0)
            previous_requests = previous_period_perf.get('total_requests', 0) - current_requests
            
            if previous_requests > 0:
                request_trend = (current_requests - previous_requests) / previous_requests * 100
                trends['request_trend'] = round(request_trend, 1)
        
        return {
            'report_period_hours': hours,
            'generated_at': datetime.now().isoformat(),
            'system_health': health,
            'performance': performance,
            'usage_analytics': usage,
            'error_analysis': errors,
            'trends': trends,
            'recommendations': self._generate_recommendations(performance, usage, errors)
        }
    
    def _generate_recommendations(self, 
                                performance: Dict[str, Any], 
                                usage: Dict[str, Any], 
                                errors: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on metrics"""
        
        recommendations = []
        
        # Performance recommendations
        avg_duration = performance.get('average_duration', 0)
        if avg_duration > 1.0:
            recommendations.append("Consider optimizing slow endpoints - average response time is high")
        
        error_rate = performance.get('error_rate', 0)
        if error_rate > 5:
            recommendations.append("High error rate detected - investigate failing endpoints")
        
        # Usage recommendations
        total_interactions = usage.get('total_interactions', 0)
        if total_interactions < 10:
            recommendations.append("Low user engagement - consider improving feature discoverability")
        
        # Error recommendations
        error_count = errors.get('total_errors', 0)
        if error_count > 10:
            recommendations.append("Multiple errors detected - review error patterns and implement fixes")
        
        # General recommendations
        if not recommendations:
            recommendations.append("System is performing well - maintain current practices")
        
        return recommendations
    
    def export_metrics(self, format: str = 'json') -> str:
        """Export metrics in specified format"""
        
        if format == 'json':
            export_data = {
                'performance_metrics': [asdict(m) for m in list(self.performance_metrics)],
                'usage_metrics': [asdict(m) for m in list(self.usage_metrics)],
                'error_metrics': list(self.error_metrics),
                'exported_at': datetime.now().isoformat()
            }
            
            # Convert datetime objects to strings for JSON serialization
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return obj
            
            return json.dumps(export_data, default=convert_datetime, indent=2)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global monitoring instance
performance_monitor = PerformanceMonitor()


# Decorator for automatic performance tracking
def track_performance(endpoint: str):
    """Decorator to automatically track endpoint performance"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            error = None
            status_code = 200
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                status_code = 500
                raise
            finally:
                duration = time.time() - start_time
                await performance_monitor.track_api_performance(
                    endpoint=endpoint,
                    method="API",
                    duration=duration,
                    status_code=status_code,
                    error=error
                )
        
        return wrapper
    return decorator


# Utility function for feature usage tracking
async def track_feature(feature: str, action: str, user_id: Optional[str] = None, **metadata):
    """Utility function to track feature usage"""
    await performance_monitor.track_feature_usage(
        feature=feature,
        action=action,
        user_id=user_id,
        metadata=metadata
    )
