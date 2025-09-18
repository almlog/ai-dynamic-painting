"""
AI Frontend service for managing dashboard components and user interfaces.
Provides real-time monitoring, interactive controls, and responsive layouts.
"""

import asyncio
import uuid
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from collections import defaultdict, deque
import threading
import statistics

# Import AI frontend models
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.ai_frontend import (
    AIDashboardComponent, AIMetric, AIGenerationJob, AIAlert, UserPreference, ResponsiveLayout,
    ComponentConfig, MetricData, GenerationJobData, AlertData, UserPreferenceData, LayoutConfig,
    ComponentType, ComponentStatus, AlertLevel
)


class AIFrontendService:
    """Advanced AI frontend service with real-time monitoring and interactive components"""
    
    def __init__(self):
        # In-memory storage for high-performance operations
        self.components: Dict[str, Dict[str, Any]] = {}
        self.metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.generation_queue: Dict[str, Dict[str, Any]] = {}
        self.alerts: Dict[str, Dict[str, Any]] = {}
        self.user_preferences: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
        self.layouts: Dict[str, Dict[str, Any]] = {}
        
        # Real-time data streams
        self.metric_streams: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.component_data_cache: Dict[str, Dict[str, Any]] = {}
        
        # Threading locks for thread safety
        self.components_lock = threading.RLock()
        self.metrics_lock = threading.RLock()
        self.queue_lock = threading.RLock()
        self.alerts_lock = threading.RLock()
        self.preferences_lock = threading.RLock()
        
        # Initialize sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize sample data for testing"""
        # Sample AI metrics
        self.current_ai_metrics = {
            "generation_success_rate": 0.95,
            "avg_generation_time": 25.5,
            "queue_length": 12,
            "error_rate": 0.02,
            "model_veo_performance": 0.92,
            "user_satisfaction": 4.3,
            "cost_per_generation": 0.05,
            "system_load": 0.78
        }
        
        # Sample generation queue items
        sample_jobs = [
            {
                "job_id": "job_001",
                "user_id": "user_123",
                "prompt": "A beautiful sunset over mountains",
                "priority": "high",
                "status": "processing",
                "created_at": datetime.now() - timedelta(minutes=5),
                "estimated_completion": datetime.now() + timedelta(minutes=2),
                "progress": 65
            },
            {
                "job_id": "job_002",
                "user_id": "user_456",
                "prompt": "Futuristic city with flying cars",
                "priority": "medium",
                "status": "pending",
                "created_at": datetime.now() - timedelta(minutes=3),
                "estimated_completion": datetime.now() + timedelta(minutes=8),
                "progress": 0
            },
            {
                "job_id": "job_003",
                "user_id": "user_789",
                "prompt": "Underwater coral reef scene",
                "priority": "urgent",
                "status": "pending",
                "created_at": datetime.now() - timedelta(minutes=1),
                "estimated_completion": datetime.now() + timedelta(minutes=5),
                "progress": 0
            }
        ]
        
        for job in sample_jobs:
            self.generation_queue[job["job_id"]] = job
    
    async def register_component(self, component_config: Dict[str, Any]) -> str:
        """Register a new AI dashboard component"""
        component_id = f"ai_comp_{uuid.uuid4().hex[:8]}"
        
        component_data = {
            "component_id": component_id,
            "type": component_config["type"],
            "title": component_config["title"],
            "data_sources": component_config.get("data_sources", []),
            "config": component_config,
            "status": "active",
            "created_at": datetime.now(),
            "last_updated": datetime.now(),
            "data_cache": {},
            "view_count": 0,
            "interaction_count": 0
        }
        
        with self.components_lock:
            self.components[component_id] = component_data
        
        # Initialize component data
        await self._update_component_data(component_id)
        
        return component_id
    
    async def get_component_data(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Get current data for a component"""
        with self.components_lock:
            component = self.components.get(component_id)
            
            if not component:
                return None
            
            # Record view
            component["view_count"] += 1
            component["last_viewed"] = datetime.now()
            
            # Update data if needed
            await self._update_component_data(component_id)
            
            return {
                "component_id": component_id,
                "type": component["type"],
                "title": component["title"],
                "data": component["data_cache"],
                "last_updated": component["last_updated"],
                "status": component["status"]
            }
    
    async def update_ai_metrics(self, metrics: Dict[str, Any]):
        """Update AI metrics data"""
        timestamp = datetime.now()
        
        with self.metrics_lock:
            for metric_name, value in metrics.items():
                # Update current metrics
                self.current_ai_metrics[metric_name] = value
                
                # Add to metrics history
                metric_entry = {
                    "metric_id": f"metric_{uuid.uuid4().hex[:8]}",
                    "metric_name": metric_name,
                    "metric_value": value,
                    "timestamp": timestamp,
                    "component": "ai_system"
                }
                
                self.metrics[metric_name].append(metric_entry)
                self.metric_streams[metric_name].append(metric_entry)
        
        # Update all components that depend on these metrics
        await self._refresh_metric_dependent_components()
    
    async def get_active_alerts(self, component_id: str) -> List[Dict[str, Any]]:
        """Get active alerts for a component"""
        with self.alerts_lock:
            component_alerts = []
            
            for alert in self.alerts.values():
                if (alert.get("component_id") == component_id and 
                    alert.get("status") == "active" and
                    (not alert.get("expires_at") or alert["expires_at"] > datetime.now())):
                    component_alerts.append(alert)
            
            return sorted(component_alerts, key=lambda x: x["triggered_at"], reverse=True)
    
    async def add_queue_item(self, job_data: Dict[str, Any]):
        """Add item to generation queue"""
        job_id = job_data.get("job_id", f"job_{uuid.uuid4().hex[:8]}")
        
        with self.queue_lock:
            self.generation_queue[job_id] = {
                **job_data,
                "job_id": job_id,
                "created_at": job_data.get("created_at", datetime.now()),
                "status": job_data.get("status", "pending"),
                "progress": job_data.get("progress", 0)
            }
        
        # Update queue-dependent components
        await self._refresh_queue_dependent_components()
    
    async def get_filtered_queue_data(self, component_id: str, 
                                    filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get filtered queue data for a component"""
        with self.queue_lock:
            queue_items = list(self.generation_queue.values())
        
        # Apply filters
        if filters:
            if "status" in filters:
                status_filter = filters["status"]
                if isinstance(status_filter, list):
                    queue_items = [item for item in queue_items if item["status"] in status_filter]
                else:
                    queue_items = [item for item in queue_items if item["status"] == status_filter]
            
            if "priority" in filters:
                priority_filter = filters["priority"]
                if isinstance(priority_filter, list):
                    queue_items = [item for item in queue_items if item["priority"] in priority_filter]
                else:
                    queue_items = [item for item in queue_items if item["priority"] == priority_filter]
        
        # Sort by priority and creation time
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        queue_items.sort(key=lambda x: (priority_order.get(x["priority"], 4), x["created_at"]))
        
        return {
            "items": queue_items,
            "total_count": len(queue_items),
            "filtered_count": len(queue_items)
        }
    
    async def update_control_value(self, component_id: str, control_update: Dict[str, Any],
                                 user_role: str = "user") -> Dict[str, Any]:
        """Update a control value in a control panel component"""
        
        with self.components_lock:
            component = self.components.get(component_id)
            
            if not component:
                raise ValueError(f"Component {component_id} not found")
            
            # Check permissions
            permissions = component["config"].get("permissions", {})
            required_role = permissions.get("required_role", "user")
            
            if required_role == "admin" and user_role != "admin":
                raise PermissionError("Admin role required for this control")
            
            # Update control value
            control_id = control_update["control_id"]
            new_value = control_update["value"]
            
            if "control_values" not in component["data_cache"]:
                component["data_cache"]["control_values"] = {}
            
            component["data_cache"]["control_values"][control_id] = new_value
            component["last_updated"] = datetime.now()
            component["interaction_count"] += 1
            
            return {
                "success": True,
                "control_id": control_id,
                "updated_value": new_value,
                "timestamp": datetime.now()
            }
    
    async def trigger_emergency_stop(self, component_id: str, user_role: str = "user") -> Dict[str, Any]:
        """Trigger emergency stop for AI generation"""
        
        if user_role != "admin":
            raise PermissionError("Admin role required for emergency stop")
        
        # Stop all processing jobs
        with self.queue_lock:
            for job_id, job in self.generation_queue.items():
                if job["status"] == "processing":
                    job["status"] = "cancelled"
                    job["error_message"] = "Emergency stop triggered"
                    job["completed_at"] = datetime.now()
        
        # Create alert
        alert_id = f"alert_{uuid.uuid4().hex[:8]}"
        alert_data = {
            "alert_id": alert_id,
            "component_id": component_id,
            "level": "critical",
            "title": "Emergency Stop Triggered",
            "message": "All AI generation processes have been stopped",
            "triggered_at": datetime.now(),
            "status": "active"
        }
        
        with self.alerts_lock:
            self.alerts[alert_id] = alert_data
        
        return {
            "success": True,
            "action": "emergency_stop_triggered",
            "stopped_jobs": len([j for j in self.generation_queue.values() if j["status"] == "cancelled"]),
            "timestamp": datetime.now()
        }
    
    async def update_user_preferences(self, component_id: str, user_id: str,
                                    preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences for a component"""
        
        with self.preferences_lock:
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = {}
            
            if component_id not in self.user_preferences[user_id]:
                self.user_preferences[user_id][component_id] = {}
            
            # Update preferences
            updated_count = 0
            for key, value in preferences.items():
                self.user_preferences[user_id][component_id][key] = {
                    "value": value,
                    "updated_at": datetime.now(),
                    "confidence": 0.8  # High confidence for user-set preferences
                }
                updated_count += 1
        
        return {
            "success": True,
            "user_id": user_id,
            "component_id": component_id,
            "updated_count": updated_count,
            "timestamp": datetime.now()
        }
    
    async def get_user_preferences(self, component_id: str, user_id: str) -> Dict[str, Any]:
        """Get user preferences for a component"""
        
        with self.preferences_lock:
            user_prefs = self.user_preferences.get(user_id, {}).get(component_id, {})
            
            # Convert to nested structure for easier access
            result = defaultdict(dict)
            for key, pref_data in user_prefs.items():
                if "." in key:
                    category, setting = key.split(".", 1)
                    result[category][setting] = pref_data["value"]
                else:
                    result["general"][key] = pref_data["value"]
            
            return dict(result)
    
    async def record_preference_interaction(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record a preference learning interaction"""
        
        user_id = interaction_data["user_id"]
        action = interaction_data["action"]
        context = interaction_data["context"]
        
        # Learn from the interaction
        learned_preferences = {}
        
        if action == "quality_upgrade":
            # User upgraded quality, learn their preference
            original = context["original_quality"]
            chosen = context["chosen_quality"]
            
            preference_key = "quality.preferred_level"
            learned_preferences[preference_key] = chosen
        
        # Record the learning
        component_id = "user_preferences"
        await self.update_user_preferences(component_id, user_id, learned_preferences)
        
        return {
            "recorded": True,
            "user_id": user_id,
            "action": action,
            "learned_preferences": learned_preferences,
            "timestamp": datetime.now()
        }
    
    async def create_responsive_layout(self, layout_config: Dict[str, Any]) -> str:
        """Create a responsive layout configuration"""
        layout_id = f"layout_{uuid.uuid4().hex[:8]}"
        
        layout_data = {
            "layout_id": layout_id,
            "title": layout_config["title"],
            "breakpoints": layout_config["breakpoints"],
            "components": layout_config["components"],
            "auto_arrange": layout_config.get("auto_arrange", True),
            "save_user_layout": layout_config.get("save_user_layout", True),
            "created_at": datetime.now(),
            "user_customizations": {}
        }
        
        with self.components_lock:
            self.layouts[layout_id] = layout_data
        
        return layout_id
    
    async def render_layout_for_screen(self, layout_id: str, screen_size: str) -> Dict[str, Any]:
        """Render layout for specific screen size"""
        
        layout = self.layouts.get(layout_id)
        if not layout:
            raise ValueError(f"Layout {layout_id} not found")
        
        breakpoints = layout["breakpoints"]
        if screen_size not in breakpoints:
            raise ValueError(f"Screen size {screen_size} not defined in layout")
        
        breakpoint_config = breakpoints[screen_size]
        
        # Generate grid configuration
        grid_config = {
            "columns": breakpoint_config.get("columns", 1),
            "max_width": breakpoint_config.get("max_width"),
            "min_width": breakpoint_config.get("min_width"),
            "gap": "16px",
            "padding": "16px"
        }
        
        # Arrange components for this screen size
        arranged_components = []
        for component in layout["components"]:
            responsive_sizing = component.get("responsive_sizing", {})
            size_config = responsive_sizing.get(screen_size, {})
            
            arranged_component = {
                "id": component["id"],
                "type": component["type"],
                "priority": component.get("priority", 1),
                "span": size_config.get("span", 1),
                "height": size_config.get("height", "auto"),
                "position": self._calculate_position(component, grid_config)
            }
            arranged_components.append(arranged_component)
        
        # Sort by priority
        arranged_components.sort(key=lambda x: x["priority"])
        
        return {
            "layout_id": layout_id,
            "screen_size": screen_size,
            "grid_config": grid_config,
            "components": arranged_components,
            "generated_at": datetime.now()
        }
    
    async def save_user_layout(self, layout_id: str, custom_layout: Dict[str, Any]) -> Dict[str, Any]:
        """Save user layout customizations"""
        
        layout = self.layouts.get(layout_id)
        if not layout:
            raise ValueError(f"Layout {layout_id} not found")
        
        user_id = custom_layout["user_id"]
        screen_size = custom_layout["screen_size"]
        
        # Save customizations
        customization_key = f"{user_id}_{screen_size}"
        layout["user_customizations"][customization_key] = {
            "user_id": user_id,
            "screen_size": screen_size,
            "component_positions": custom_layout["component_positions"],
            "saved_at": datetime.now()
        }
        
        return {
            "success": True,
            "layout_id": layout_id,
            "user_id": user_id,
            "screen_size": screen_size,
            "timestamp": datetime.now()
        }
    
    async def get_user_layout(self, layout_id: str, user_id: str, screen_size: str) -> Dict[str, Any]:
        """Get user layout with customizations"""
        
        # Get base layout
        base_layout = await self.render_layout_for_screen(layout_id, screen_size)
        
        # Check for user customizations
        layout = self.layouts.get(layout_id)
        if layout:
            customization_key = f"{user_id}_{screen_size}"
            customization = layout["user_customizations"].get(customization_key)
            
            if customization:
                base_layout["customized"] = True
                base_layout["component_positions"] = customization["component_positions"]
                base_layout["saved_at"] = customization["saved_at"]
            else:
                base_layout["customized"] = False
        
        return base_layout
    
    async def get_combined_widget_data(self, widget_ids: List[str]) -> Dict[str, Any]:
        """Get combined data from multiple widgets"""
        
        combined_data = {
            "widgets": [],
            "generated_at": datetime.now(),
            "total_widgets": len(widget_ids)
        }
        
        for widget_id in widget_ids:
            widget_data = await self.get_component_data(widget_id)
            if widget_data:
                combined_data["widgets"].append(widget_data)
        
        return combined_data
    
    # Helper methods
    
    async def _update_component_data(self, component_id: str):
        """Update component data based on its type"""
        
        component = self.components[component_id]
        component_type = component["type"]
        
        if component_type == "generation_status" or component_type == "ai_metrics_monitor":
            await self._update_metrics_component_data(component_id)
        elif component_type == "generation_queue":
            await self._update_queue_component_data(component_id)
        elif component_type == "ai_control_panel":
            await self._update_control_panel_data(component_id)
        elif component_type == "user_preferences":
            await self._update_preferences_component_data(component_id)
        else:
            await self._update_generic_component_data(component_id)
    
    async def _update_metrics_component_data(self, component_id: str):
        """Update metrics component data"""
        
        component = self.components[component_id]
        
        # Get current metrics
        metrics_data = {}
        for metric_name, value in self.current_ai_metrics.items():
            metrics_data[metric_name] = value
        
        # Check for alerts
        alerts = []
        config = component["config"]
        thresholds = config.get("thresholds", {})
        
        for metric_name, value in metrics_data.items():
            if metric_name in thresholds:
                threshold_config = thresholds[metric_name]
                
                if "critical" in threshold_config and value >= threshold_config["critical"]:
                    alert_id = f"alert_{uuid.uuid4().hex[:8]}"
                    alert = {
                        "alert_id": alert_id,
                        "level": "critical",
                        "metric": metric_name,
                        "value": value,
                        "threshold": threshold_config["critical"],
                        "message": f"{metric_name} is at critical level: {value}"
                    }
                    alerts.append(alert)
                    
                    # Store alert
                    with self.alerts_lock:
                        self.alerts[alert_id] = {
                            **alert,
                            "component_id": component_id,
                            "triggered_at": datetime.now(),
                            "status": "active"
                        }
                elif "warning" in threshold_config and value >= threshold_config["warning"]:
                    alert_id = f"alert_{uuid.uuid4().hex[:8]}"
                    alert = {
                        "alert_id": alert_id,
                        "level": "warning",
                        "metric": metric_name,
                        "value": value,
                        "threshold": threshold_config["warning"],
                        "message": f"{metric_name} is at warning level: {value}"
                    }
                    alerts.append(alert)
        
        component["data_cache"] = {
            "metrics": metrics_data,
            "alerts": alerts,
            "last_updated": datetime.now(),
            "status": "normal" if not alerts else "warning"
        }
        
        component["last_updated"] = datetime.now()
    
    async def _update_queue_component_data(self, component_id: str):
        """Update queue component data"""
        
        component = self.components[component_id]
        
        with self.queue_lock:
            queue_items = list(self.generation_queue.values())
        
        # Group by priority
        grouped_items = defaultdict(list)
        for item in queue_items:
            grouped_items[item["priority"]].append(item)
        
        # Sort each group by creation time
        for priority in grouped_items:
            grouped_items[priority].sort(key=lambda x: x["created_at"])
        
        component["data_cache"] = {
            "total_items": len(queue_items),
            "items": queue_items[:50],  # Limit to 50 for performance
            "grouped_items": dict(grouped_items),
            "status_counts": {
                "pending": len([i for i in queue_items if i["status"] == "pending"]),
                "processing": len([i for i in queue_items if i["status"] == "processing"]),
                "completed": len([i for i in queue_items if i["status"] == "completed"]),
                "failed": len([i for i in queue_items if i["status"] == "failed"])
            },
            "last_updated": datetime.now()
        }
        
        component["last_updated"] = datetime.now()
    
    async def _update_control_panel_data(self, component_id: str):
        """Update control panel component data"""
        
        component = self.components[component_id]
        config = component["config"]
        
        # Initialize control values if not exists
        if "control_values" not in component["data_cache"]:
            component["data_cache"]["control_values"] = {}
            
            # Set default values from config
            for control in config.get("controls", []):
                control_id = control["id"]
                default_value = control.get("default")
                if default_value is not None:
                    component["data_cache"]["control_values"][control_id] = default_value
        
        component["data_cache"]["controls_config"] = config.get("controls", [])
        component["data_cache"]["last_updated"] = datetime.now()
        
        component["last_updated"] = datetime.now()
    
    async def _update_preferences_component_data(self, component_id: str):
        """Update preferences component data"""
        
        component = self.components[component_id]
        config = component["config"]
        
        component["data_cache"] = {
            "categories": config.get("categories", []),
            "personalization": config.get("personalization", {}),
            "last_updated": datetime.now()
        }
        
        component["last_updated"] = datetime.now()
    
    async def _update_generic_component_data(self, component_id: str):
        """Update generic component data"""
        
        component = self.components[component_id]
        component_type = component["type"]
        
        # Generate sample data based on component type
        if "timeline" in component_type:
            data = await self._generate_timeline_data()
        elif "comparison" in component_type:
            data = await self._generate_comparison_data()
        elif "heatmap" in component_type:
            data = await self._generate_heatmap_data()
        elif "cost" in component_type:
            data = await self._generate_cost_data()
        else:
            data = {"message": "Generic component data", "timestamp": datetime.now()}
        
        component["data_cache"] = data
        component["last_updated"] = datetime.now()
    
    async def _refresh_metric_dependent_components(self):
        """Refresh all components that depend on metrics"""
        
        for component_id, component in self.components.items():
            if component["type"] in ["generation_status", "ai_metrics_monitor"]:
                await self._update_component_data(component_id)
    
    async def _refresh_queue_dependent_components(self):
        """Refresh all components that depend on queue data"""
        
        for component_id, component in self.components.items():
            if component["type"] == "generation_queue":
                await self._update_component_data(component_id)
    
    def _calculate_position(self, component: Dict[str, Any], grid_config: Dict[str, Any]) -> Dict[str, int]:
        """Calculate component position in grid"""
        
        # Simple auto-layout logic
        priority = component.get("priority", 1)
        
        # Higher priority components get better positions
        if priority == 1:
            return {"x": 0, "y": 0}
        elif priority == 2:
            return {"x": 1, "y": 0}
        else:
            return {"x": 0, "y": 1}
    
    async def _generate_timeline_data(self) -> Dict[str, Any]:
        """Generate timeline data"""
        
        # Generate sample timeline data
        timeline_data = []
        now = datetime.now()
        
        for i in range(24):
            timestamp = now - timedelta(hours=23-i)
            timeline_data.append({
                "timestamp": timestamp.isoformat(),
                "successful_generations": 45 + (i % 10),
                "failed_generations": 2 + (i % 3),
                "avg_time": 25 + (i % 15)
            })
        
        return {
            "timeline": timeline_data,
            "total_successful": sum(d["successful_generations"] for d in timeline_data),
            "total_failed": sum(d["failed_generations"] for d in timeline_data),
            "avg_generation_time": statistics.mean(d["avg_time"] for d in timeline_data)
        }
    
    async def _generate_comparison_data(self) -> Dict[str, Any]:
        """Generate model comparison data"""
        
        models = ["veo-1", "veo-2", "stable-diffusion"]
        comparison_data = []
        
        for model in models:
            comparison_data.append({
                "model": model,
                "quality_score": 0.8 + (hash(model) % 20) / 100,
                "generation_time": 20 + (hash(model) % 30),
                "success_rate": 0.85 + (hash(model) % 15) / 100
            })
        
        return {"models": comparison_data}
    
    async def _generate_heatmap_data(self) -> Dict[str, Any]:
        """Generate heatmap data"""
        
        hours = [f"{i:02d}:00" for i in range(24)]
        categories = ["landscape", "portrait", "abstract", "animals"]
        
        matrix = []
        for category in categories:
            row = [3.5 + (hash(f"{category}_{hour}") % 10) / 10 for hour in hours]
            matrix.append(row)
        
        return {
            "matrix": matrix,
            "x_labels": hours,
            "y_labels": categories,
            "value_range": [3.0, 5.0]
        }
    
    async def _generate_cost_data(self) -> Dict[str, Any]:
        """Generate cost analysis data"""
        
        return {
            "total_cost": 1250.75,
            "by_model": {
                "veo-1": 650.25,
                "veo-2": 450.50,
                "stable-diffusion": 150.00
            },
            "by_user": {
                "user_123": 425.30,
                "user_456": 380.45,
                "others": 445.00
            },
            "trend": "increasing",
            "monthly_estimate": 3750.00
        }