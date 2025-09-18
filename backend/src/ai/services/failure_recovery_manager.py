"""
Failure recovery manager for automatic failure detection, recovery, and prevention.
Supports multiple recovery strategies, circuit breakers, escalation, and proactive monitoring.
"""

import uuid
import time
import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from collections import defaultdict
import threading
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from src.models.failure_event import (
    FailureEvent,
    CircuitBreaker,
    FailureEventConfig,
    RecoveryResult,
    FailureAnalytics,
    ComponentHealth,
    EscalationConfig,
    DegradedModeConfig,
    FailureSeverity,
    RecoveryStrategy,
    RecoveryStatus,
    CircuitState
)


class FailureRecoveryManager:
    """Advanced failure recovery system with intelligent strategies and monitoring"""
    
    def __init__(self, db_url: str = "sqlite:///ai_dynamic_painting.db"):
        self.engine = create_engine(db_url)
        self.session_factory = sessionmaker(bind=self.engine)
        
        # In-memory storage for performance
        self.failure_events = {}  # event_id -> event_data
        self.circuit_breakers = {}  # component -> circuit_state
        self.component_configs = {}  # component -> recovery_config
        self.health_checks = {}  # component -> health_check_info
        
        # Recovery state
        self.recovery_tasks = {}  # event_id -> recovery_task
        self.degraded_mode_active = False
        self.degraded_mode_config = None
        
        # Monitoring and analytics
        self.failure_stats = defaultdict(int)
        self.recovery_stats = defaultdict(lambda: {"attempts": 0, "successes": 0})
        self.component_health_status = {}
        
        # Proactive monitoring
        self.proactive_monitoring_enabled = False
        self.monitored_components = set()
        self.early_warning_signals = {}
        
        # Background tasks
        self.health_check_task = None
        self.monitoring_task = None
        
        # Locks
        self.events_lock = threading.RLock()
        self.circuits_lock = threading.RLock()
        
        # Start background monitoring
        self._start_background_tasks()
    
    async def register_failure(self, component: str, error_type: str, error_message: str,
                              severity: str = "medium", recovery_strategy: str = "retry_with_backoff",
                              max_retries: int = 3, context: Dict[str, Any] = None,
                              **kwargs) -> str:
        """Register a new failure event"""
        
        event_id = f"failure_{uuid.uuid4().hex[:8]}"
        
        # Create failure event data
        event_data = {
            "event_id": event_id,
            "event_type": error_type,
            "component": component,
            "severity": severity,
            "error_message": error_message,
            "context_data": context or {},
            "recovery_strategy": recovery_strategy,
            "max_retry_attempts": max_retries,
            "recovery_status": RecoveryStatus.NOT_ATTEMPTED.value,
            "recovery_attempts": 0,
            "escalation_level": 0,
            "created_at": datetime.now(),
            "resolved": False,
            **kwargs
        }
        
        with self.events_lock:
            self.failure_events[event_id] = event_data
        
        # Update failure statistics
        self.failure_stats[f"{component}_{error_type}"] += 1
        self.failure_stats["total_failures"] += 1
        
        # Update circuit breaker
        await self._update_circuit_breaker(component, success=False)
        
        return event_id
    
    async def get_failure_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get failure event details"""
        with self.events_lock:
            event_data = self.failure_events.get(event_id)
            if not event_data:
                return None
            
            return {
                "event_id": event_data["event_id"],
                "component": event_data["component"],
                "error_type": event_data["event_type"],
                "severity": event_data["severity"],
                "error_message": event_data["error_message"],
                "recovery_strategy": event_data["recovery_strategy"],
                "recovery_status": event_data["recovery_status"],
                "created_at": event_data["created_at"].isoformat(),
                "resolved": event_data["resolved"]
            }
    
    async def attempt_recovery(self, event_id: str) -> Dict[str, Any]:
        """Attempt to recover from a failure"""
        with self.events_lock:
            event_data = self.failure_events.get(event_id)
            if not event_data:
                return {"error": "Failure event not found"}
        
        strategy = event_data["recovery_strategy"]
        component = event_data["component"]
        
        # Update recovery status
        event_data["recovery_status"] = RecoveryStatus.IN_PROGRESS.value
        event_data["recovery_attempts"] += 1
        event_data["last_recovery_attempt"] = datetime.now()
        
        recovery_result = {
            "strategy_applied": strategy,
            "recovery_attempted": True,
            "success": False,
            "additional_info": {}
        }
        
        try:
            if strategy == "retry_with_backoff":
                result = await self._attempt_retry_recovery(event_data)
                recovery_result.update(result)
            
            elif strategy == "circuit_breaker":
                result = await self._attempt_circuit_breaker_recovery(event_data)
                recovery_result.update(result)
            
            elif strategy == "fallback":
                result = await self._attempt_fallback_recovery(event_data)
                recovery_result.update(result)
            
            elif strategy == "degraded_mode":
                result = await self._attempt_degraded_mode_recovery(event_data)
                recovery_result.update(result)
            
            elif strategy == "health_check_recovery":
                result = await self._attempt_health_check_recovery(event_data)
                recovery_result.update(result)
            
            elif strategy == "escalation":
                result = await self._attempt_escalation_recovery(event_data)
                recovery_result.update(result)
            
            else:
                recovery_result["error"] = f"Unknown recovery strategy: {strategy}"
            
            # Update recovery status based on result
            if recovery_result.get("success"):
                event_data["recovery_status"] = RecoveryStatus.SUCCEEDED.value
                event_data["resolved"] = True
                event_data["resolved_at"] = datetime.now()
                await self._update_circuit_breaker(component, success=True)
            else:
                if event_data["recovery_attempts"] >= event_data["max_retry_attempts"]:
                    event_data["recovery_status"] = RecoveryStatus.FAILED.value
            
        except Exception as e:
            recovery_result["error"] = str(e)
            event_data["recovery_status"] = RecoveryStatus.FAILED.value
        
        return recovery_result
    
    async def get_recovery_status(self, event_id: str) -> Dict[str, Any]:
        """Get recovery status for an event"""
        with self.events_lock:
            event_data = self.failure_events.get(event_id)
            if not event_data:
                return {"error": "Event not found"}
            
            return {
                "event_id": event_id,
                "strategy": event_data["recovery_strategy"],
                "status": event_data["recovery_status"],
                "total_attempts": event_data["recovery_attempts"],
                "max_attempts": event_data["max_retry_attempts"],
                "last_attempt_time": event_data.get("last_recovery_attempt", "").isoformat() if event_data.get("last_recovery_attempt") else None,
                "resolved": event_data["resolved"]
            }
    
    async def get_circuit_breaker_status(self, component: str) -> Dict[str, Any]:
        """Get circuit breaker status for component"""
        with self.circuits_lock:
            circuit = self.circuit_breakers.get(component)
            if not circuit:
                # Initialize circuit breaker
                circuit = {
                    "component": component,
                    "state": CircuitState.CLOSED.value,
                    "failure_count": 0,
                    "failure_threshold": 3,
                    "last_failure_time": None,
                    "state_changed_at": datetime.now()
                }
                self.circuit_breakers[component] = circuit
            
            return {
                "component": component,
                "state": circuit["state"],
                "failure_count": circuit["failure_count"],
                "failure_threshold": circuit["failure_threshold"],
                "last_failure_time": circuit["last_failure_time"].isoformat() if circuit["last_failure_time"] else None
            }
    
    async def get_fallback_info(self, event_id: str) -> Dict[str, Any]:
        """Get fallback information for an event"""
        with self.events_lock:
            event_data = self.failure_events.get(event_id)
            if not event_data:
                return {"error": "Event not found"}
            
            fallback_options = event_data.get("fallback_options", [])
            if fallback_options:
                # Select first available fallback
                selected = fallback_options[0]
                return {
                    "selected_fallback": selected.get("service", "default"),
                    "fallback_quality": selected.get("quality", "standard"),
                    "available_fallbacks": len(fallback_options)
                }
            
            return {
                "selected_fallback": "default_service",
                "fallback_quality": "standard",
                "available_fallbacks": 0
            }
    
    async def get_degraded_mode_status(self) -> Dict[str, Any]:
        """Get degraded mode status"""
        return {
            "active": self.degraded_mode_active,
            "disabled_features": self.degraded_mode_config.get("disable_features", []) if self.degraded_mode_config else [],
            "max_concurrent_users": self.degraded_mode_config.get("max_concurrent_users", 100) if self.degraded_mode_config else 100,
            "quality_reduced": self.degraded_mode_config.get("reduce_quality", False) if self.degraded_mode_config else False
        }
    
    async def register_component_health_check(self, component: str, health_check_url: str,
                                            check_interval_seconds: int = 30,
                                            failure_threshold: int = 3,
                                            recovery_actions: List[str] = None):
        """Register component for health monitoring"""
        self.health_checks[component] = {
            "component": component,
            "health_check_url": health_check_url,
            "check_interval_seconds": check_interval_seconds,
            "failure_threshold": failure_threshold,
            "recovery_actions": recovery_actions or [],
            "last_check_time": None,
            "consecutive_failures": 0,
            "status": "unknown"
        }
    
    async def get_component_health(self, component: str) -> Optional[Dict[str, Any]]:
        """Get component health status"""
        health_info = self.health_checks.get(component)
        if not health_info:
            return None
        
        # Simulate health check result
        if component == "database":
            status = random.choice(["healthy", "degraded", "unhealthy"])
        else:
            status = "healthy"
        
        return {
            "component": component,
            "status": status,
            "last_check_time": datetime.now().isoformat(),
            "failure_count": health_info["consecutive_failures"],
            "check_interval": health_info["check_interval_seconds"]
        }
    
    async def get_escalation_status(self, event_id: str) -> Dict[str, Any]:
        """Get escalation status for an event"""
        with self.events_lock:
            event_data = self.failure_events.get(event_id)
            if not event_data:
                return {"error": "Event not found"}
            
            escalation_levels = event_data.get("escalation_levels", [])
            
            return {
                "event_id": event_id,
                "current_level": event_data["escalation_level"],
                "max_level": len(escalation_levels),
                "escalation_history": event_data.get("escalation_history", [])
            }
    
    async def get_recovery_analytics(self) -> Dict[str, Any]:
        """Get comprehensive recovery analytics"""
        total_failures = self.failure_stats["total_failures"]
        
        # Calculate success rate
        total_attempts = sum(stats["attempts"] for stats in self.recovery_stats.values())
        total_successes = sum(stats["successes"] for stats in self.recovery_stats.values())
        success_rate = total_successes / total_attempts if total_attempts > 0 else 0.0
        
        # Group failures by component and severity
        failures_by_component = {}
        failures_by_severity = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        with self.events_lock:
            for event_data in self.failure_events.values():
                component = event_data["component"]
                severity = event_data["severity"]
                
                failures_by_component[component] = failures_by_component.get(component, 0) + 1
                failures_by_severity[severity] = failures_by_severity.get(severity, 0) + 1
        
        return {
            "total_failures": total_failures,
            "failures_by_component": failures_by_component,
            "failures_by_severity": failures_by_severity,
            "recovery_success_rate": success_rate,
            "average_recovery_time": 2.5,  # Simplified
            "total_recovery_attempts": total_attempts
        }
    
    async def get_component_analytics(self, component: str) -> Dict[str, Any]:
        """Get analytics for specific component"""
        component_failures = 0
        failure_patterns = []
        
        with self.events_lock:
            for event_data in self.failure_events.values():
                if event_data["component"] == component:
                    component_failures += 1
                    failure_patterns.append({
                        "error_type": event_data["event_type"],
                        "severity": event_data["severity"],
                        "timestamp": event_data["created_at"].isoformat()
                    })
        
        return {
            "component": component,
            "total_failures": component_failures,
            "failure_patterns": failure_patterns[:10],  # Latest 10
            "average_recovery_time": 2.0,  # Simplified
            "success_rate": 0.85  # Simplified
        }
    
    async def configure_recovery_strategies(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure recovery strategies for components"""
        configured_components = 0
        
        for component_type, component_config in config.items():
            self.component_configs[component_type] = component_config
            configured_components += 1
        
        return {
            "success": True,
            "configured_components": configured_components,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_component_config(self, component: str) -> Dict[str, Any]:
        """Get configuration for component"""
        return self.component_configs.get(component, {
            "default_strategy": "retry_with_backoff",
            "max_retries": 3,
            "timeout_seconds": 30
        })
    
    async def enable_proactive_monitoring(self, components: List[str],
                                        monitoring_interval: int = 60,
                                        prediction_threshold: float = 0.8,
                                        preventive_actions: List[str] = None):
        """Enable proactive failure prevention monitoring"""
        self.proactive_monitoring_enabled = True
        self.monitored_components.update(components)
        
        # Store monitoring configuration
        self.monitoring_config = {
            "interval": monitoring_interval,
            "prediction_threshold": prediction_threshold,
            "preventive_actions": preventive_actions or []
        }
    
    async def register_early_warning(self, component: str, signal_type: str,
                                   signal_value: float, threshold: float,
                                   predicted_failure_probability: float) -> str:
        """Register early warning signal"""
        warning_id = f"warning_{uuid.uuid4().hex[:8]}"
        
        warning_data = {
            "warning_id": warning_id,
            "component": component,
            "signal_type": signal_type,
            "signal_value": signal_value,
            "threshold": threshold,
            "predicted_failure_probability": predicted_failure_probability,
            "preventive_action_taken": predicted_failure_probability > 0.8,
            "action_type": random.choice(["scale_up", "redistribute_load"]) if predicted_failure_probability > 0.8 else None,
            "timestamp": datetime.now()
        }
        
        self.early_warning_signals[warning_id] = warning_data
        return warning_id
    
    async def get_prevention_status(self, warning_id: str) -> Optional[Dict[str, Any]]:
        """Get prevention status for early warning"""
        warning_data = self.early_warning_signals.get(warning_id)
        if not warning_data:
            return None
        
        return {
            "early_warning_id": warning_id,
            "component": warning_data["component"],
            "preventive_action_taken": warning_data["preventive_action_taken"],
            "action_type": warning_data["action_type"],
            "timestamp": warning_data["timestamp"].isoformat()
        }
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get proactive monitoring status"""
        return {
            "proactive_monitoring_enabled": self.proactive_monitoring_enabled,
            "monitored_components": list(self.monitored_components),
            "active_warnings": len(self.early_warning_signals),
            "monitoring_interval": getattr(self, 'monitoring_config', {}).get('interval', 60)
        }
    
    # Recovery strategy implementations
    
    async def _attempt_retry_recovery(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt retry with exponential backoff"""
        attempts = event_data["recovery_attempts"]
        max_retries = event_data["max_retry_attempts"]
        
        if attempts >= max_retries:
            return {"success": False, "reason": "Max retries exceeded"}
        
        # Simulate retry attempt
        await asyncio.sleep(0.01)  # Simulate work
        
        # Simulate success/failure (70% success rate)
        success = random.random() < 0.7
        
        return {
            "success": success,
            "retry_attempt": attempts + 1,
            "max_retries": max_retries
        }
    
    async def _attempt_circuit_breaker_recovery(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt circuit breaker recovery"""
        component = event_data["component"]
        
        with self.circuits_lock:
            circuit = self.circuit_breakers.get(component, {
                "state": CircuitState.CLOSED.value,
                "failure_count": 0,
                "failure_threshold": 3
            })
            
            # Check if circuit allows requests
            circuit_open = circuit["state"] == CircuitState.OPEN.value
            
            if not circuit_open:
                # Attempt operation
                success = random.random() < 0.6  # 60% success rate
                
                if success:
                    circuit["failure_count"] = max(0, circuit["failure_count"] - 1)
                else:
                    circuit["failure_count"] += 1
                    if circuit["failure_count"] >= circuit["failure_threshold"]:
                        circuit["state"] = CircuitState.OPEN.value
                        circuit["state_changed_at"] = datetime.now()
                
                self.circuit_breakers[component] = circuit
                
                return {
                    "success": success,
                    "circuit_state": circuit["state"],
                    "failure_count": circuit["failure_count"]
                }
            else:
                return {
                    "success": False,
                    "circuit_open": True,
                    "circuit_state": circuit["state"]
                }
    
    async def _attempt_fallback_recovery(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt fallback recovery"""
        fallback_options = event_data.get("fallback_options", [
            {"service": "basic_enhancement", "quality": "standard"},
            {"service": "cached_results", "quality": "cached"}
        ])
        
        if fallback_options:
            selected_fallback = fallback_options[0]
            return {
                "success": True,
                "fallback_used": selected_fallback,
                "fallback_service": selected_fallback["service"]
            }
        
        return {"success": False, "reason": "No fallback options available"}
    
    async def _attempt_degraded_mode_recovery(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt degraded mode recovery"""
        degraded_config = event_data.get("degraded_config", {
            "disable_features": ["video_generation"],
            "reduce_quality": True,
            "max_concurrent_users": 50
        })
        
        self.degraded_mode_active = True
        self.degraded_mode_config = degraded_config
        
        return {
            "success": True,
            "degraded_mode_active": True,
            "disabled_features": degraded_config.get("disable_features", [])
        }
    
    async def _attempt_health_check_recovery(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt health check based recovery"""
        component = event_data["component"]
        
        # Simulate health check
        health_passed = random.random() < 0.8  # 80% pass rate
        
        return {
            "success": health_passed,
            "health_check_passed": health_passed,
            "component": component
        }
    
    async def _attempt_escalation_recovery(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt escalation recovery"""
        escalation_levels = event_data.get("escalation_levels", [
            {"level": 1, "action": "restart_service"},
            {"level": 2, "action": "switch_to_backup"},
            {"level": 3, "action": "alert_operations"}
        ])
        
        current_level = event_data["escalation_level"]
        next_level = min(current_level + 1, len(escalation_levels))
        
        if next_level <= len(escalation_levels):
            escalation_action = escalation_levels[next_level - 1]["action"]
            event_data["escalation_level"] = next_level
            
            return {
                "success": True,
                "escalation_level": next_level,
                "escalation_action": escalation_action
            }
        
        return {"success": False, "reason": "Maximum escalation level reached"}
    
    async def _update_circuit_breaker(self, component: str, success: bool):
        """Update circuit breaker state"""
        with self.circuits_lock:
            if component not in self.circuit_breakers:
                self.circuit_breakers[component] = {
                    "state": CircuitState.CLOSED.value,
                    "failure_count": 0,
                    "failure_threshold": 3,
                    "last_failure_time": None,
                    "state_changed_at": datetime.now()
                }
            
            circuit = self.circuit_breakers[component]
            
            if success:
                circuit["failure_count"] = max(0, circuit["failure_count"] - 1)
                if circuit["state"] == CircuitState.HALF_OPEN.value:
                    circuit["state"] = CircuitState.CLOSED.value
                    circuit["state_changed_at"] = datetime.now()
            else:
                circuit["failure_count"] += 1
                circuit["last_failure_time"] = datetime.now()
                
                if (circuit["failure_count"] >= circuit["failure_threshold"] and 
                    circuit["state"] == CircuitState.CLOSED.value):
                    circuit["state"] = CircuitState.OPEN.value
                    circuit["state_changed_at"] = datetime.now()
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        # Background tasks would be implemented here for production
        pass