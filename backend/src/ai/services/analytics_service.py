"""
Analytics service for managing dashboards, metrics collection, and reporting.
Provides real-time analytics, custom dashboards, and alert management.
"""

import asyncio
import uuid
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque
import threading
import statistics

# Import analytics dashboard models
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.analytics_dashboard import (
    AnalyticsDashboard, MetricEntry, AlertRule,
    DashboardConfig, WidgetConfig, MetricData, AlertRuleConfig,
    DashboardType, WidgetType, MetricType
)


class AnalyticsService:
    """Advanced analytics service with dashboard management and real-time metrics"""
    
    def __init__(self):
        # In-memory storage for high-performance operations
        self.dashboards: Dict[str, Dict[str, Any]] = {}
        self.metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.alert_states: Dict[str, Dict[str, Any]] = {}
        self.widget_cache: Dict[str, Dict[str, Any]] = {}
        
        # Real-time metric streams
        self.metric_streams: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.aggregation_cache: Dict[str, Dict[str, Any]] = {}
        
        # Threading locks for thread safety
        self.dashboards_lock = threading.RLock()
        self.metrics_lock = threading.RLock()
        self.alerts_lock = threading.RLock()
        
        # Configuration
        self.max_metric_retention = timedelta(days=30)
        self.aggregation_intervals = {
            "1m": timedelta(minutes=1),
            "5m": timedelta(minutes=5),
            "1h": timedelta(hours=1),
            "1d": timedelta(days=1)
        }
    
    async def record_metric(self, metric_name: str, metric_value: float,
                          metric_type: str, component: str,
                          timestamp: datetime = None, tags: Dict[str, Any] = None,
                          dimensions: Dict[str, Any] = None) -> str:
        """Record a new metric data point"""
        metric_id = f"metric_{uuid.uuid4().hex[:8]}"
        
        metric_data = {
            "metric_id": metric_id,
            "metric_name": metric_name,
            "metric_value": metric_value,
            "metric_type": metric_type,
            "component": component,
            "timestamp": timestamp or datetime.now(),
            "tags": tags or {},
            "dimensions": dimensions or {},
            "created_at": datetime.now()
        }
        
        with self.metrics_lock:
            # Store in metrics collection
            self.metrics[metric_name].append(metric_data)
            
            # Add to real-time stream
            self.metric_streams[metric_name].append(metric_data)
            
            # Trigger alert evaluation
            await self._evaluate_metric_alerts(metric_name, metric_data)
            
            # Update aggregation cache
            self._update_aggregation_cache(metric_name, metric_data)
        
        return metric_id
    
    async def get_metrics(self, metric_name: str, time_window: str = "1h",
                         filters: Dict[str, Any] = None,
                         limit: int = 1000) -> List[Dict[str, Any]]:
        """Retrieve metrics with filtering and time window"""
        time_delta = self._parse_time_window(time_window)
        cutoff_time = datetime.now() - time_delta
        
        with self.metrics_lock:
            metrics = self.metrics.get(metric_name, [])
            
            # Filter by time window
            filtered_metrics = [
                m for m in metrics
                if m["timestamp"] >= cutoff_time
            ]
            
            # Apply additional filters
            if filters:
                for key, value in filters.items():
                    if key == "component":
                        filtered_metrics = [m for m in filtered_metrics if m["component"] == value]
                    elif key in ["tags", "dimensions"]:
                        filtered_metrics = [
                            m for m in filtered_metrics
                            if key in m and value in m[key].values()
                        ]
            
            # Limit results
            return filtered_metrics[-limit:] if limit else filtered_metrics
    
    async def get_aggregated_metrics(self, metric_name: str, aggregation: str = "avg",
                                   time_window: str = "1h",
                                   group_by: List[str] = None) -> Dict[str, Any]:
        """Get aggregated metric data with grouping"""
        metrics = await self.get_metrics(metric_name, time_window)
        
        if not metrics:
            return {}
        
        # Group metrics if specified
        if group_by:
            grouped_metrics = defaultdict(list)
            for metric in metrics:
                group_key = []
                for field in group_by:
                    if field in metric:
                        group_key.append(str(metric[field]))
                    elif field in metric.get("tags", {}):
                        group_key.append(str(metric["tags"][field]))
                    elif field in metric.get("dimensions", {}):
                        group_key.append(str(metric["dimensions"][field]))
                
                key = "_".join(group_key) if group_key else "default"
                grouped_metrics[key].append(metric["metric_value"])
            
            # Apply aggregation to each group
            result = {}
            for group, values in grouped_metrics.items():
                result[group] = self._apply_aggregation(values, aggregation)
            
            return result
        else:
            # Apply aggregation to all values
            values = [m["metric_value"] for m in metrics]
            return {"value": self._apply_aggregation(values, aggregation)}
    
    async def create_dashboard(self, dashboard_config: Dict[str, Any]) -> str:
        """Create a new analytics dashboard"""
        dashboard_id = f"dashboard_{uuid.uuid4().hex[:8]}"
        
        dashboard_data = {
            "dashboard_id": dashboard_id,
            "name": dashboard_config["name"],
            "type": dashboard_config["type"],
            "owner_id": dashboard_config["owner_id"],
            "description": dashboard_config.get("description", ""),
            "widgets": dashboard_config.get("widgets", []),
            "config": {
                "refresh_interval": dashboard_config.get("refresh_interval", 300),
                "auto_refresh": dashboard_config.get("auto_refresh", True),
                "timezone": dashboard_config.get("timezone", "UTC")
            },
            "visibility": "private",
            "shared_with": [],
            "tags": dashboard_config.get("tags", []),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "view_count": 0,
            "is_favorite": False
        }
        
        # Assign widget IDs
        for i, widget in enumerate(dashboard_data["widgets"]):
            if "widget_id" not in widget:
                widget["widget_id"] = f"widget_{i+1}"
        
        with self.dashboards_lock:
            self.dashboards[dashboard_id] = dashboard_data
        
        return dashboard_id
    
    async def get_dashboard(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve dashboard configuration and data"""
        with self.dashboards_lock:
            dashboard = self.dashboards.get(dashboard_id)
            
            if dashboard:
                # Record view
                dashboard["view_count"] += 1
                dashboard["last_viewed_at"] = datetime.now()
                
                # Return copy to prevent external modification
                return dict(dashboard)
            
            return None
    
    async def list_dashboards(self, owner_id: str) -> List[Dict[str, Any]]:
        """List dashboards for a specific owner"""
        with self.dashboards_lock:
            owner_dashboards = []
            for dashboard in self.dashboards.values():
                if dashboard["owner_id"] == owner_id:
                    summary = {
                        "dashboard_id": dashboard["dashboard_id"],
                        "name": dashboard["name"],
                        "type": dashboard["type"],
                        "widget_count": len(dashboard["widgets"]),
                        "last_viewed_at": dashboard.get("last_viewed_at"),
                        "view_count": dashboard["view_count"],
                        "is_favorite": dashboard["is_favorite"],
                        "created_at": dashboard["created_at"]
                    }
                    owner_dashboards.append(summary)
            
            return sorted(owner_dashboards, key=lambda x: x["created_at"], reverse=True)
    
    async def generate_widget_data(self, widget_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for a specific widget"""
        widget_type = widget_config["type"]
        data_source = widget_config["data_source"]
        config = widget_config.get("config", {})
        
        widget_data = {
            "widget_type": widget_type,
            "title": widget_config.get("title", "Untitled Widget"),
            "data": {},
            "generated_at": datetime.now(),
            "status": "success"
        }
        
        try:
            if widget_type == "metric_card":
                widget_data["data"] = await self._generate_metric_card_data(data_source, config)
            elif widget_type == "gauge_chart":
                widget_data["data"] = await self._generate_gauge_chart_data(data_source, config)
            elif widget_type == "heatmap":
                widget_data["data"] = await self._generate_heatmap_data(data_source, config)
            elif widget_type == "pie_chart":
                widget_data["data"] = await self._generate_pie_chart_data(data_source, config)
            elif widget_type == "time_series":
                widget_data["data"] = await self._generate_time_series_data(data_source, config)
            else:
                widget_data["data"] = await self._generate_generic_chart_data(data_source, config)
        
        except Exception as e:
            widget_data["status"] = "error"
            widget_data["error"] = str(e)
            widget_data["data"] = {}
        
        return widget_data
    
    async def create_alert_rule(self, alert_rule: Dict[str, Any]) -> str:
        """Create a new alert rule"""
        rule_id = f"rule_{uuid.uuid4().hex[:8]}"
        
        rule_data = {
            "rule_id": rule_id,
            "rule_name": alert_rule["rule_name"],
            "metric_name": alert_rule["metric_name"],
            "condition": alert_rule["condition"],
            "threshold": alert_rule["threshold"],
            "time_window": alert_rule["time_window"],
            "severity": alert_rule["severity"],
            "notification_channels": alert_rule.get("notification_channels", []),
            "cooldown_period": alert_rule.get("cooldown_period", 300),
            "is_active": True,
            "created_at": datetime.now(),
            "trigger_count": 0,
            "last_triggered": None
        }
        
        with self.alerts_lock:
            self.alert_rules[rule_id] = rule_data
            self.alert_states[rule_id] = {
                "last_evaluation": datetime.now(),
                "triggered": False,
                "cooldown_until": None
            }
        
        return rule_id
    
    async def evaluate_alert_rules(self) -> List[Dict[str, Any]]:
        """Evaluate all active alert rules and return triggered alerts"""
        triggered_alerts = []
        
        with self.alerts_lock:
            for rule_id, rule in self.alert_rules.items():
                if not rule["is_active"]:
                    continue
                
                state = self.alert_states[rule_id]
                
                # Check cooldown period
                if state["cooldown_until"] and datetime.now() < state["cooldown_until"]:
                    continue
                
                # Evaluate rule condition
                try:
                    is_triggered = await self._evaluate_alert_condition(rule)
                    
                    if is_triggered and not state["triggered"]:
                        # New alert trigger
                        alert = {
                            "rule_id": rule_id,
                            "rule_name": rule["rule_name"],
                            "metric_name": rule["metric_name"],
                            "severity": rule["severity"],
                            "threshold": rule["threshold"],
                            "current_value": await self._get_current_metric_value(rule["metric_name"]),
                            "triggered_at": datetime.now(),
                            "notification_channels": rule["notification_channels"]
                        }
                        
                        triggered_alerts.append(alert)
                        
                        # Update rule state
                        rule["trigger_count"] += 1
                        rule["last_triggered"] = datetime.now()
                        state["triggered"] = True
                        state["cooldown_until"] = datetime.now() + timedelta(seconds=rule["cooldown_period"])
                    
                    elif not is_triggered and state["triggered"]:
                        # Alert resolved
                        state["triggered"] = False
                        state["cooldown_until"] = None
                    
                    state["last_evaluation"] = datetime.now()
                
                except Exception as e:
                    print(f"Error evaluating alert rule {rule_id}: {e}")
        
        return triggered_alerts
    
    async def send_alert_notification(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Send alert notification through configured channels"""
        notification_id = f"notification_{uuid.uuid4().hex[:8]}"
        
        # Simulate notification sending
        notification_result = {
            "notification_id": notification_id,
            "alert_id": alert.get("rule_id"),
            "channels": alert.get("notification_channels", []),
            "sent": True,
            "sent_at": datetime.now(),
            "delivery_status": {}
        }
        
        # Simulate channel-specific delivery
        for channel in alert.get("notification_channels", []):
            if channel in ["email", "slack", "webhook"]:
                notification_result["delivery_status"][channel] = "delivered"
            else:
                notification_result["delivery_status"][channel] = "failed"
        
        return notification_result
    
    async def export_data(self, export_config: Dict[str, Any]) -> Dict[str, Any]:
        """Export analytics data in specified format"""
        export_id = f"export_{uuid.uuid4().hex[:8]}"
        
        # Generate export data based on configuration
        export_data = []
        for metric_name in export_config.get("metrics", []):
            time_range = export_config.get("time_range", {})
            start_time = time_range.get("start", datetime.now() - timedelta(hours=24))
            end_time = time_range.get("end", datetime.now())
            
            metrics = await self.get_metrics(metric_name, "24h")
            filtered_metrics = [
                m for m in metrics
                if start_time <= m["timestamp"] <= end_time
            ]
            export_data.extend(filtered_metrics)
        
        # Create export result
        export_result = {
            "export_id": export_id,
            "format": export_config.get("format", "json"),
            "record_count": len(export_data),
            "file_size_bytes": len(json.dumps(export_data)),
            "download_url": f"/api/exports/{export_id}",
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=24)
        }
        
        return export_result
    
    async def generate_report(self, report_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analytics report"""
        report_id = f"report_{uuid.uuid4().hex[:8]}"
        
        # Generate report content based on configuration
        report_data = {
            "report_id": report_id,
            "report_type": report_config["report_type"],
            "time_period": report_config["time_period"],
            "generated_at": datetime.now(),
            "sections": report_config.get("sections", []),
            "format": report_config.get("format", "pdf"),
            "download_url": f"/api/reports/{report_id}",
            "status": "completed"
        }
        
        return report_data
    
    async def share_dashboard(self, sharing_config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure dashboard sharing"""
        share_id = f"share_{uuid.uuid4().hex[:8]}"
        dashboard_id = sharing_config["dashboard_id"]
        
        with self.dashboards_lock:
            dashboard = self.dashboards.get(dashboard_id)
            if not dashboard:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            # Update dashboard sharing settings
            dashboard["visibility"] = "shared"
            dashboard["shared_with"] = sharing_config.get("allowed_users", [])
            dashboard["share_settings"] = {
                "share_id": share_id,
                "share_type": sharing_config.get("share_type", "link"),
                "permissions": sharing_config.get("permissions", ["view"]),
                "expiration": sharing_config.get("expiration"),
                "password_protected": sharing_config.get("password_protected", False)
            }
        
        share_result = {
            "share_id": share_id,
            "dashboard_id": dashboard_id,
            "share_url": f"/shared/dashboard/{share_id}",
            "permissions": sharing_config.get("permissions", ["view"]),
            "expiration": sharing_config.get("expiration"),
            "created_at": datetime.now()
        }
        
        return share_result
    
    async def check_dashboard_access(self, dashboard_id: str, user_id: str,
                                   requested_permission: str) -> Dict[str, Any]:
        """Check if user has access to dashboard with specified permission"""
        with self.dashboards_lock:
            dashboard = self.dashboards.get(dashboard_id)
            
            if not dashboard:
                return {"allowed": False, "reason": "Dashboard not found"}
            
            # Check ownership
            if dashboard["owner_id"] == user_id:
                return {"allowed": True, "permission_level": "owner"}
            
            # Check shared access
            if user_id in dashboard.get("shared_with", []):
                share_settings = dashboard.get("share_settings", {})
                permissions = share_settings.get("permissions", [])
                
                if requested_permission in permissions:
                    return {"allowed": True, "permission_level": requested_permission}
            
            return {"allowed": False, "reason": "Access denied"}
    
    # Helper methods
    
    def _parse_time_window(self, time_window: str) -> timedelta:
        """Parse time window string to timedelta"""
        if time_window.endswith("m"):
            return timedelta(minutes=int(time_window[:-1]))
        elif time_window.endswith("h"):
            return timedelta(hours=int(time_window[:-1]))
        elif time_window.endswith("d"):
            return timedelta(days=int(time_window[:-1]))
        else:
            return timedelta(hours=1)  # Default to 1 hour
    
    def _apply_aggregation(self, values: List[float], aggregation: str) -> float:
        """Apply aggregation function to values"""
        if not values:
            return 0.0
        
        if aggregation == "avg":
            return statistics.mean(values)
        elif aggregation == "sum":
            return sum(values)
        elif aggregation == "min":
            return min(values)
        elif aggregation == "max":
            return max(values)
        elif aggregation == "count":
            return len(values)
        elif aggregation == "median":
            return statistics.median(values)
        else:
            return statistics.mean(values)  # Default to average
    
    async def _evaluate_metric_alerts(self, metric_name: str, metric_data: Dict[str, Any]):
        """Evaluate alerts for a specific metric"""
        # This would trigger alert evaluation in a real implementation
        pass
    
    def _update_aggregation_cache(self, metric_name: str, metric_data: Dict[str, Any]):
        """Update aggregation cache with new metric data"""
        # This would update cached aggregations for performance
        pass
    
    async def _evaluate_alert_condition(self, rule: Dict[str, Any]) -> bool:
        """Evaluate if alert condition is met"""
        metric_name = rule["metric_name"]
        condition = rule["condition"]
        threshold = rule["threshold"]
        time_window = rule["time_window"]
        
        # Get recent metrics
        metrics = await self.get_metrics(metric_name, time_window)
        
        if not metrics:
            return False
        
        # Get current value (latest metric)
        current_value = metrics[-1]["metric_value"]
        
        # Evaluate condition
        if condition == "greater_than":
            return current_value > threshold
        elif condition == "less_than":
            return current_value < threshold
        elif condition == "equals":
            return abs(current_value - threshold) < 0.001
        else:
            return False
    
    async def _get_current_metric_value(self, metric_name: str) -> float:
        """Get the most recent value for a metric"""
        metrics = await self.get_metrics(metric_name, "5m", limit=1)
        return metrics[0]["metric_value"] if metrics else 0.0
    
    async def _generate_metric_card_data(self, data_source: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for metric card widget"""
        metric_name = config.get("metric", "default_metric")
        
        # Get current metric value
        current_value = await self._get_current_metric_value(metric_name)
        
        # Determine status based on thresholds
        status = "normal"
        thresholds = config.get("threshold", {})
        if "critical" in thresholds and current_value >= thresholds["critical"]:
            status = "critical"
        elif "warning" in thresholds and current_value >= thresholds["warning"]:
            status = "warning"
        
        return {
            "value": current_value,
            "format": config.get("format", "number"),
            "status": status,
            "trend": "stable"  # Could calculate trend from recent values
        }
    
    async def _generate_gauge_chart_data(self, data_source: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for gauge chart widget"""
        metric_name = config.get("metric", "default_metric")
        current_value = await self._get_current_metric_value(metric_name)
        
        return {
            "current_value": current_value,
            "min_value": config.get("min_value", 0),
            "max_value": config.get("max_value", 100),
            "unit": config.get("unit", ""),
            "thresholds": config.get("thresholds", [])
        }
    
    async def _generate_heatmap_data(self, data_source: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for heatmap widget"""
        # Simulate heatmap data
        hours = [f"{i:02d}:00" for i in range(24)]
        endpoints = ["/api/generate", "/api/upload", "/api/status", "/api/health"]
        
        matrix = []
        for endpoint in endpoints:
            row = [int(abs(hash(f"{endpoint}_{hour}")) % 100) for hour in hours]
            matrix.append(row)
        
        return {
            "matrix": matrix,
            "x_labels": hours,
            "y_labels": endpoints,
            "value_range": [0, 100]
        }
    
    async def _generate_pie_chart_data(self, data_source: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for pie chart widget"""
        # Simulate pie chart data
        segments = [
            {"label": "Success", "value": 85, "color": "#28a745"},
            {"label": "Warning", "value": 10, "color": "#ffc107"},
            {"label": "Error", "value": 5, "color": "#dc3545"}
        ]
        
        return {"segments": segments}
    
    async def _generate_time_series_data(self, data_source: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for time series widget"""
        # Simulate time series data
        now = datetime.now()
        timestamps = [(now - timedelta(minutes=i*5)).isoformat() for i in range(12, 0, -1)]
        values = [50 + i*2 + (i%3)*10 for i in range(12)]
        
        return {
            "timestamps": timestamps,
            "values": values,
            "unit": config.get("unit", ""),
            "label": config.get("label", "Metric")
        }
    
    async def _generate_generic_chart_data(self, data_source: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate generic chart data"""
        return {
            "data": [{"x": i, "y": i*2} for i in range(10)],
            "type": "line",
            "title": "Generic Chart"
        }