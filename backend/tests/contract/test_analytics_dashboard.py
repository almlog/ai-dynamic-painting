"""
Contract tests for analytics dashboard system - T259.
Tests MUST fail initially (RED phase), then pass after implementation (GREEN phase).
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestAnalyticsDashboardContract:
    """Contract tests for T259: Analytics Dashboard System"""
    
    def test_analytics_dashboard_model_exists(self):
        """Test that AnalyticsDashboard model exists"""
        from src.models.analytics_dashboard import AnalyticsDashboard
        
        # Test model creation
        dashboard = AnalyticsDashboard(
            dashboard_id="dashboard_123",
            dashboard_name="AI Performance Dashboard",
            dashboard_type="performance",
            owner_id="user_123",
            dashboard_config={
                "refresh_interval": 300,
                "auto_refresh": True,
                "timezone": "UTC"
            },
            widgets=[
                {
                    "widget_id": "widget_1",
                    "widget_type": "metric_card",
                    "title": "Generation Success Rate",
                    "data_source": "ai_metrics",
                    "config": {"metric": "success_rate", "format": "percentage"}
                },
                {
                    "widget_id": "widget_2", 
                    "widget_type": "line_chart",
                    "title": "Response Time Trend",
                    "data_source": "performance_metrics",
                    "config": {"time_window": "24h", "granularity": "1h"}
                }
            ]
        )
        
        assert dashboard.dashboard_id == "dashboard_123"
        assert dashboard.dashboard_name == "AI Performance Dashboard"
        assert dashboard.dashboard_type == "performance"
        assert dashboard.owner_id == "user_123"
        assert len(dashboard.widgets) == 2
        assert dashboard.dashboard_config["refresh_interval"] == 300
    
    @pytest.mark.asyncio
    async def test_analytics_service_exists(self):
        """Test that AnalyticsService exists and works"""
        from src.ai.services.analytics_service import AnalyticsService
        
        # Create analytics service
        analytics_service = AnalyticsService()
        
        # Test metric collection
        metric_data = {
            "metric_name": "ai_generation_success",
            "metric_value": 0.95,
            "metric_type": "percentage",
            "component": "video_generation",
            "timestamp": datetime.now(),
            "tags": {"model": "veo", "quality": "standard"}
        }
        
        metric_id = await analytics_service.record_metric(**metric_data)
        assert metric_id is not None
        assert isinstance(metric_id, str)
        assert metric_id.startswith("metric_")
        
        # Test metric retrieval
        metrics = await analytics_service.get_metrics(
            metric_name="ai_generation_success",
            time_window="1h"
        )
        assert metrics is not None
        assert len(metrics) >= 1
        assert metrics[0]["metric_name"] == "ai_generation_success"
    
    @pytest.mark.asyncio
    async def test_dashboard_creation_and_management(self):
        """Test dashboard creation and management"""
        from src.ai.services.analytics_service import AnalyticsService
        
        analytics_service = AnalyticsService()
        
        # Test dashboard creation
        dashboard_config = {
            "name": "AI Performance Monitor",
            "type": "performance",
            "owner_id": "user_123",
            "widgets": [
                {
                    "type": "metric_card",
                    "title": "Success Rate",
                    "data_source": "ai_metrics",
                    "config": {"metric": "success_rate"}
                },
                {
                    "type": "time_series",
                    "title": "Response Times",
                    "data_source": "performance",
                    "config": {"window": "24h"}
                }
            ],
            "refresh_interval": 300,
            "auto_refresh": True
        }
        
        dashboard_id = await analytics_service.create_dashboard(dashboard_config)
        assert dashboard_id is not None
        assert isinstance(dashboard_id, str)
        
        # Test dashboard retrieval
        dashboard = await analytics_service.get_dashboard(dashboard_id)
        assert dashboard is not None
        assert dashboard["name"] == "AI Performance Monitor"
        assert dashboard["type"] == "performance"
        assert len(dashboard["widgets"]) == 2
        
        # Test dashboard listing
        dashboards = await analytics_service.list_dashboards("user_123")
        assert dashboards is not None
        assert len(dashboards) >= 1
        assert any(d["dashboard_id"] == dashboard_id for d in dashboards)
    
    @pytest.mark.asyncio
    async def test_real_time_metrics_collection(self):
        """Test real-time metrics collection and aggregation"""
        from src.ai.services.analytics_service import AnalyticsService
        
        analytics_service = AnalyticsService()
        
        # Simulate real-time metric collection
        metrics_data = [
            {
                "metric_name": "request_latency",
                "metric_value": 250.5,
                "metric_type": "duration_ms",
                "component": "api_gateway",
                "tags": {"endpoint": "/generate", "method": "POST"}
            },
            {
                "metric_name": "request_latency", 
                "metric_value": 180.2,
                "metric_type": "duration_ms",
                "component": "api_gateway",
                "tags": {"endpoint": "/generate", "method": "POST"}
            },
            {
                "metric_name": "memory_usage",
                "metric_value": 78.5,
                "metric_type": "percentage",
                "component": "ai_processor",
                "tags": {"process": "generation"}
            }
        ]
        
        # Record metrics
        metric_ids = []
        for metric in metrics_data:
            metric_id = await analytics_service.record_metric(**metric)
            metric_ids.append(metric_id)
        
        assert len(metric_ids) == 3
        
        # Test aggregated metrics
        latency_stats = await analytics_service.get_aggregated_metrics(
            metric_name="request_latency",
            aggregation="avg",
            time_window="1h",
            group_by=["component"]
        )
        
        assert latency_stats is not None
        assert "api_gateway" in latency_stats
        assert latency_stats["api_gateway"]["avg"] > 0
        
        # Test metric filtering
        filtered_metrics = await analytics_service.get_metrics(
            metric_name="request_latency",
            filters={"component": "api_gateway"},
            time_window="1h"
        )
        
        assert len(filtered_metrics) == 2
        assert all(m["component"] == "api_gateway" for m in filtered_metrics)
    
    @pytest.mark.asyncio
    async def test_custom_widget_types(self):
        """Test custom widget types and data visualization"""
        from src.ai.services.analytics_service import AnalyticsService
        
        analytics_service = AnalyticsService()
        
        # Test various widget types
        widget_configs = [
            {
                "type": "metric_card",
                "title": "Total Requests",
                "data_source": "api_metrics",
                "config": {
                    "metric": "request_count",
                    "aggregation": "sum",
                    "format": "number",
                    "threshold": {"warning": 1000, "critical": 5000}
                }
            },
            {
                "type": "gauge_chart",
                "title": "CPU Usage",
                "data_source": "system_metrics",
                "config": {
                    "metric": "cpu_usage",
                    "min_value": 0,
                    "max_value": 100,
                    "unit": "percentage",
                    "thresholds": [{"value": 80, "color": "orange"}, {"value": 90, "color": "red"}]
                }
            },
            {
                "type": "heatmap",
                "title": "Request Distribution",
                "data_source": "request_metrics",
                "config": {
                    "x_axis": "hour",
                    "y_axis": "endpoint", 
                    "value": "request_count",
                    "time_window": "7d"
                }
            },
            {
                "type": "pie_chart",
                "title": "Error Types Distribution",
                "data_source": "error_metrics",
                "config": {
                    "group_by": "error_type",
                    "value": "count",
                    "time_window": "24h"
                }
            }
        ]
        
        # Test widget data generation
        for widget_config in widget_configs:
            widget_data = await analytics_service.generate_widget_data(widget_config)
            assert widget_data is not None
            assert "widget_type" in widget_data
            assert "data" in widget_data
            assert widget_data["widget_type"] == widget_config["type"]
            
            # Verify data structure based on widget type
            if widget_config["type"] == "metric_card":
                assert "value" in widget_data["data"]
                assert "status" in widget_data["data"]
            elif widget_config["type"] == "gauge_chart":
                assert "current_value" in widget_data["data"]
                assert "max_value" in widget_data["data"]
            elif widget_config["type"] == "heatmap":
                assert "matrix" in widget_data["data"]
                assert "x_labels" in widget_data["data"]
                assert "y_labels" in widget_data["data"]
            elif widget_config["type"] == "pie_chart":
                assert "segments" in widget_data["data"]
                assert all("label" in seg and "value" in seg for seg in widget_data["data"]["segments"])
    
    @pytest.mark.asyncio
    async def test_alert_system_integration(self):
        """Test alert system integration with analytics"""
        from src.ai.services.analytics_service import AnalyticsService
        
        analytics_service = AnalyticsService()
        
        # Test alert rule creation
        alert_rule = {
            "rule_name": "High Error Rate Alert",
            "metric_name": "error_rate",
            "condition": "greater_than",
            "threshold": 0.05,  # 5% error rate
            "time_window": "5m",
            "severity": "warning",
            "notification_channels": ["email", "slack"],
            "cooldown_period": 300  # 5 minutes
        }
        
        rule_id = await analytics_service.create_alert_rule(alert_rule)
        assert rule_id is not None
        assert isinstance(rule_id, str)
        
        # Test alert triggering
        high_error_metrics = [
            {
                "metric_name": "error_rate",
                "metric_value": 0.08,  # 8% - above threshold
                "metric_type": "percentage",
                "component": "api_service"
            }
        ]
        
        for metric in high_error_metrics:
            await analytics_service.record_metric(**metric)
        
        # Check alert evaluation
        triggered_alerts = await analytics_service.evaluate_alert_rules()
        assert triggered_alerts is not None
        assert len(triggered_alerts) >= 1
        assert any(alert["rule_id"] == rule_id for alert in triggered_alerts)
        
        # Test alert notification
        for alert in triggered_alerts:
            notification_result = await analytics_service.send_alert_notification(alert)
            assert notification_result["sent"] == True
            assert "notification_id" in notification_result
    
    @pytest.mark.asyncio
    async def test_export_and_reporting(self):
        """Test data export and report generation"""
        from src.ai.services.analytics_service import AnalyticsService
        
        analytics_service = AnalyticsService()
        
        # Generate sample data for export
        sample_metrics = [
            {"metric_name": "response_time", "metric_value": 120.5, "component": "api"},
            {"metric_name": "throughput", "metric_value": 450, "component": "api"},
            {"metric_name": "error_count", "metric_value": 2, "component": "api"}
        ]
        
        for metric in sample_metrics:
            await analytics_service.record_metric(**metric)
        
        # Test data export
        export_config = {
            "format": "csv",
            "time_range": {"start": datetime.now() - timedelta(hours=1), "end": datetime.now()},
            "metrics": ["response_time", "throughput", "error_count"],
            "include_metadata": True
        }
        
        export_result = await analytics_service.export_data(export_config)
        assert export_result is not None
        assert "export_id" in export_result
        assert "download_url" in export_result
        assert export_result["format"] == "csv"
        
        # Test report generation
        report_config = {
            "report_type": "performance_summary",
            "time_period": "24h",
            "include_charts": True,
            "format": "pdf",
            "sections": ["overview", "trends", "alerts", "recommendations"]
        }
        
        report_result = await analytics_service.generate_report(report_config)
        assert report_result is not None
        assert "report_id" in report_result
        assert "download_url" in report_result
        assert report_result["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_dashboard_sharing_and_permissions(self):
        """Test dashboard sharing and permission management"""
        from src.ai.services.analytics_service import AnalyticsService
        
        analytics_service = AnalyticsService()
        
        # Create a dashboard
        dashboard_config = {
            "name": "Shared Performance Dashboard",
            "type": "performance",
            "owner_id": "user_123",
            "widgets": [{"type": "metric_card", "title": "Test Metric"}],
            "visibility": "private"
        }
        
        dashboard_id = await analytics_service.create_dashboard(dashboard_config)
        
        # Test sharing configuration
        sharing_config = {
            "dashboard_id": dashboard_id,
            "share_type": "link",
            "permissions": ["view"],
            "expiration": datetime.now() + timedelta(days=7),
            "password_protected": False,
            "allowed_users": ["user_456", "user_789"]
        }
        
        share_result = await analytics_service.share_dashboard(sharing_config)
        assert share_result is not None
        assert "share_id" in share_result
        assert "share_url" in share_result
        assert share_result["permissions"] == ["view"]
        
        # Test permission verification
        access_check = await analytics_service.check_dashboard_access(
            dashboard_id=dashboard_id,
            user_id="user_456",
            requested_permission="view"
        )
        assert access_check["allowed"] == True
        assert access_check["permission_level"] == "view"
        
        # Test unauthorized access
        unauthorized_check = await analytics_service.check_dashboard_access(
            dashboard_id=dashboard_id,
            user_id="user_999",
            requested_permission="view"
        )
        assert unauthorized_check["allowed"] == False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])