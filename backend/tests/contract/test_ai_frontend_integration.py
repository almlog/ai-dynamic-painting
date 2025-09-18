"""
Contract tests for AI frontend integration - T261-T265.
Tests MUST fail initially (RED phase), then pass after implementation (GREEN phase).
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestAIFrontendIntegrationContract:
    """Contract tests for T261-T265: AI Frontend Integration"""
    
    def test_ai_dashboard_component_exists(self):
        """Test that AIDashboardComponent model exists"""
        from src.models.ai_frontend import AIDashboardComponent
        
        # Test component creation
        component = AIDashboardComponent(
            component_id="ai_dash_123",
            component_type="generation_monitor",
            title="AI Video Generation Monitor",
            config={
                "refresh_interval": 5000,
                "show_metrics": True,
                "show_queue": True,
                "show_errors": True
            },
            data_sources=["ai_metrics", "generation_queue", "error_logs"],
            layout_config={
                "position": {"x": 0, "y": 0},
                "size": {"width": 6, "height": 4},
                "responsive": True
            }
        )
        
        assert component.component_id == "ai_dash_123"
        assert component.component_type == "generation_monitor"
        assert component.title == "AI Video Generation Monitor"
        assert len(component.data_sources) == 3
        assert component.config["refresh_interval"] == 5000
    
    @pytest.mark.asyncio
    async def test_ai_frontend_service_exists(self):
        """Test that AIFrontendService exists and works"""
        from src.ai.services.ai_frontend_service import AIFrontendService
        
        # Create AI frontend service
        service = AIFrontendService()
        
        # Test dashboard component registration
        component_config = {
            "type": "generation_status",
            "title": "Video Generation Status",
            "data_sources": ["veo_api", "generation_queue"],
            "refresh_interval": 3000,
            "auto_refresh": True,
            "styling": {
                "theme": "dark",
                "show_animations": True
            }
        }
        
        component_id = await service.register_component(component_config)
        assert component_id is not None
        assert isinstance(component_id, str)
        assert component_id.startswith("ai_comp_")
        
        # Test component data generation
        component_data = await service.get_component_data(component_id)
        assert component_data is not None
        assert "component_id" in component_data
        assert "data" in component_data
        assert "last_updated" in component_data
    
    @pytest.mark.asyncio
    async def test_real_time_ai_monitoring(self):
        """Test real-time AI monitoring dashboard"""
        from src.ai.services.ai_frontend_service import AIFrontendService
        
        service = AIFrontendService()
        
        # Test AI metrics monitoring component
        monitor_config = {
            "type": "ai_metrics_monitor",
            "title": "AI Performance Monitor",
            "metrics": [
                {"name": "generation_success_rate", "display": "Success Rate", "format": "percentage"},
                {"name": "avg_generation_time", "display": "Avg Generation Time", "format": "duration"},
                {"name": "queue_length", "display": "Queue Length", "format": "number"},
                {"name": "error_rate", "display": "Error Rate", "format": "percentage"}
            ],
            "thresholds": {
                "success_rate": {"warning": 0.9, "critical": 0.8},
                "generation_time": {"warning": 30, "critical": 60},
                "error_rate": {"warning": 0.05, "critical": 0.1}
            },
            "alerts": {
                "enabled": True,
                "sound": True,
                "notifications": True
            }
        }
        
        component_id = await service.register_component(monitor_config)
        
        # Test real-time data updates
        for i in range(3):
            # Simulate metric updates
            await service.update_ai_metrics({
                "generation_success_rate": 0.95 - (i * 0.02),
                "avg_generation_time": 25 + (i * 5),
                "queue_length": 10 + i,
                "error_rate": 0.02 + (i * 0.01)
            })
            
            # Get updated component data
            data = await service.get_component_data(component_id)
            assert data["data"]["metrics"]["generation_success_rate"] == 0.95 - (i * 0.02)
            
            await asyncio.sleep(0.1)
        
        # Test alert generation
        alerts = await service.get_active_alerts(component_id)
        assert alerts is not None
        assert isinstance(alerts, list)
    
    @pytest.mark.asyncio
    async def test_generation_queue_visualization(self):
        """Test AI generation queue visualization"""
        from src.ai.services.ai_frontend_service import AIFrontendService
        
        service = AIFrontendService()
        
        # Test queue visualization component
        queue_config = {
            "type": "generation_queue",
            "title": "AI Generation Queue",
            "display_mode": "timeline",
            "show_details": True,
            "max_items": 50,
            "grouping": {
                "by": "priority",
                "show_groups": True
            },
            "filters": {
                "status": ["pending", "processing", "completed", "failed"],
                "priority": ["low", "medium", "high", "urgent"],
                "user_id": "all"
            }
        }
        
        component_id = await service.register_component(queue_config)
        
        # Add sample queue items
        queue_items = [
            {
                "job_id": "job_001",
                "user_id": "user_123",
                "prompt": "A beautiful sunset over mountains",
                "priority": "high",
                "status": "processing",
                "created_at": datetime.now() - timedelta(minutes=5),
                "estimated_completion": datetime.now() + timedelta(minutes=2)
            },
            {
                "job_id": "job_002",
                "user_id": "user_456",
                "prompt": "Futuristic city with flying cars",
                "priority": "medium",
                "status": "pending",
                "created_at": datetime.now() - timedelta(minutes=3),
                "estimated_completion": datetime.now() + timedelta(minutes=8)
            },
            {
                "job_id": "job_003",
                "user_id": "user_789",
                "prompt": "Underwater coral reef scene",
                "priority": "urgent",
                "status": "pending",
                "created_at": datetime.now() - timedelta(minutes=1),
                "estimated_completion": datetime.now() + timedelta(minutes=5)
            }
        ]
        
        for item in queue_items:
            await service.add_queue_item(item)
        
        # Test queue data retrieval
        queue_data = await service.get_component_data(component_id)
        assert queue_data["data"]["total_items"] >= 3
        assert "items" in queue_data["data"]
        assert "grouped_items" in queue_data["data"]
        
        # Test queue filtering
        filtered_data = await service.get_filtered_queue_data(
            component_id,
            filters={"status": ["pending"], "priority": ["urgent", "high"]}
        )
        assert filtered_data is not None
        assert len(filtered_data["items"]) >= 2
    
    @pytest.mark.asyncio
    async def test_interactive_ai_controls(self):
        """Test interactive AI control interface"""
        from src.ai.services.ai_frontend_service import AIFrontendService
        
        service = AIFrontendService()
        
        # Test AI control panel component
        control_config = {
            "type": "ai_control_panel",
            "title": "AI Generation Controls",
            "controls": [
                {
                    "id": "generation_enabled",
                    "type": "toggle",
                    "label": "Enable AI Generation",
                    "default": True
                },
                {
                    "id": "batch_size",
                    "type": "slider",
                    "label": "Batch Size",
                    "min": 1,
                    "max": 10,
                    "default": 3
                },
                {
                    "id": "quality_preset",
                    "type": "select",
                    "label": "Quality Preset",
                    "options": ["draft", "standard", "high", "ultra"],
                    "default": "standard"
                },
                {
                    "id": "emergency_stop",
                    "type": "button",
                    "label": "Emergency Stop",
                    "style": "danger",
                    "confirmation": True
                }
            ],
            "permissions": {
                "required_role": "admin",
                "emergency_override": True
            }
        }
        
        component_id = await service.register_component(control_config)
        
        # Test control interactions
        control_updates = [
            {"control_id": "generation_enabled", "value": False},
            {"control_id": "batch_size", "value": 5},
            {"control_id": "quality_preset", "value": "high"}
        ]
        
        for update in control_updates:
            result = await service.update_control_value(component_id, update)
            assert result["success"] == True
            assert result["updated_value"] == update["value"]
        
        # Test emergency stop
        emergency_result = await service.trigger_emergency_stop(component_id, user_role="admin")
        assert emergency_result["success"] == True
        assert emergency_result["action"] == "emergency_stop_triggered"
        
        # Test permission enforcement
        try:
            await service.update_control_value(component_id, 
                {"control_id": "generation_enabled", "value": True}, 
                user_role="viewer")
            pytest.fail("Expected permission error for viewer role")
        except Exception as e:
            assert "permission" in str(e).lower() or "unauthorized" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_ai_analytics_widgets(self):
        """Test AI-specific analytics widgets"""
        from src.ai.services.ai_frontend_service import AIFrontendService
        
        service = AIFrontendService()
        
        # Test AI analytics widget types
        widget_configs = [
            {
                "type": "generation_timeline",
                "title": "Generation Timeline",
                "time_range": "24h",
                "granularity": "1h",
                "metrics": ["successful_generations", "failed_generations", "avg_time"]
            },
            {
                "type": "model_performance_comparison",
                "title": "Model Performance Comparison",
                "models": ["veo-1", "veo-2", "stable-diffusion"],
                "metrics": ["quality_score", "generation_time", "success_rate"]
            },
            {
                "type": "user_satisfaction_heatmap",
                "title": "User Satisfaction Heatmap",
                "dimensions": ["time_of_day", "prompt_category"],
                "metric": "satisfaction_score"
            },
            {
                "type": "cost_analysis",
                "title": "AI Generation Cost Analysis",
                "breakdown": ["by_model", "by_user", "by_quality"],
                "time_period": "monthly"
            }
        ]
        
        widget_ids = []
        for config in widget_configs:
            widget_id = await service.register_component(config)
            widget_ids.append(widget_id)
            
            # Test widget data generation
            widget_data = await service.get_component_data(widget_id)
            assert widget_data is not None
            assert widget_data["type"] == config["type"]
            assert "data" in widget_data
        
        assert len(widget_ids) == 4
        
        # Test widget data aggregation
        combined_data = await service.get_combined_widget_data(widget_ids)
        assert combined_data is not None
        assert "widgets" in combined_data
        assert len(combined_data["widgets"]) == 4
    
    @pytest.mark.asyncio
    async def test_user_preference_interface(self):
        """Test user preference configuration interface"""
        from src.ai.services.ai_frontend_service import AIFrontendService
        
        service = AIFrontendService()
        
        # Test preference interface component
        preference_config = {
            "type": "user_preferences",
            "title": "AI Generation Preferences",
            "categories": [
                {
                    "id": "quality",
                    "title": "Quality Settings",
                    "preferences": [
                        {
                            "id": "default_quality",
                            "type": "select",
                            "label": "Default Quality",
                            "options": ["draft", "standard", "high", "ultra"],
                            "default": "standard"
                        },
                        {
                            "id": "auto_enhance",
                            "type": "toggle",
                            "label": "Auto Enhance Prompts",
                            "default": True
                        }
                    ]
                },
                {
                    "id": "notifications",
                    "title": "Notification Settings",
                    "preferences": [
                        {
                            "id": "completion_notifications",
                            "type": "toggle",
                            "label": "Generation Completion Notifications",
                            "default": True
                        },
                        {
                            "id": "notification_sound",
                            "type": "toggle",
                            "label": "Play Notification Sound",
                            "default": False
                        }
                    ]
                }
            ],
            "personalization": {
                "learn_from_interactions": True,
                "adaptive_suggestions": True
            }
        }
        
        component_id = await service.register_component(preference_config)
        
        # Test preference updates
        preference_updates = {
            "quality.default_quality": "high",
            "quality.auto_enhance": False,
            "notifications.completion_notifications": True,
            "notifications.notification_sound": True
        }
        
        update_result = await service.update_user_preferences(
            component_id, 
            "user_123", 
            preference_updates
        )
        assert update_result["success"] == True
        assert update_result["updated_count"] == 4
        
        # Test preference retrieval
        user_prefs = await service.get_user_preferences(component_id, "user_123")
        assert user_prefs["quality"]["default_quality"] == "high"
        assert user_prefs["quality"]["auto_enhance"] == False
        assert user_prefs["notifications"]["completion_notifications"] == True
        
        # Test preference learning
        interaction_data = {
            "user_id": "user_123",
            "action": "quality_upgrade",
            "context": {"original_quality": "standard", "chosen_quality": "high"},
            "timestamp": datetime.now()
        }
        
        learning_result = await service.record_preference_interaction(interaction_data)
        assert learning_result["recorded"] == True
        assert "learned_preferences" in learning_result
    
    @pytest.mark.asyncio
    async def test_responsive_ai_layout(self):
        """Test responsive layout system for AI components"""
        from src.ai.services.ai_frontend_service import AIFrontendService
        
        service = AIFrontendService()
        
        # Test responsive layout configuration
        layout_config = {
            "type": "responsive_ai_layout",
            "title": "AI Dashboard Layout",
            "breakpoints": {
                "mobile": {"max_width": 768, "columns": 1},
                "tablet": {"max_width": 1024, "columns": 2},
                "desktop": {"min_width": 1025, "columns": 3}
            },
            "components": [
                {
                    "id": "generation_status",
                    "type": "ai_metrics_monitor",
                    "priority": 1,
                    "responsive_sizing": {
                        "mobile": {"span": 1, "height": "auto"},
                        "tablet": {"span": 2, "height": "300px"},
                        "desktop": {"span": 1, "height": "250px"}
                    }
                },
                {
                    "id": "queue_viewer",
                    "type": "generation_queue",
                    "priority": 2,
                    "responsive_sizing": {
                        "mobile": {"span": 1, "height": "400px"},
                        "tablet": {"span": 1, "height": "350px"},
                        "desktop": {"span": 2, "height": "300px"}
                    }
                }
            ],
            "auto_arrange": True,
            "save_user_layout": True
        }
        
        layout_id = await service.create_responsive_layout(layout_config)
        assert layout_id is not None
        
        # Test layout rendering for different screen sizes
        screen_sizes = ["mobile", "tablet", "desktop"]
        
        for size in screen_sizes:
            layout_data = await service.render_layout_for_screen(layout_id, size)
            assert layout_data is not None
            assert layout_data["screen_size"] == size
            assert "components" in layout_data
            assert "grid_config" in layout_data
            
            # Verify responsive behavior
            if size == "mobile":
                assert layout_data["grid_config"]["columns"] == 1
            elif size == "tablet":
                assert layout_data["grid_config"]["columns"] == 2
            elif size == "desktop":
                assert layout_data["grid_config"]["columns"] == 3
        
        # Test layout customization
        custom_layout = {
            "user_id": "user_123",
            "screen_size": "desktop",
            "component_positions": {
                "generation_status": {"x": 0, "y": 0, "w": 1, "h": 2},
                "queue_viewer": {"x": 1, "y": 0, "w": 2, "h": 2}
            }
        }
        
        save_result = await service.save_user_layout(layout_id, custom_layout)
        assert save_result["success"] == True
        
        # Test layout retrieval with user customizations
        user_layout = await service.get_user_layout(layout_id, "user_123", "desktop")
        assert user_layout is not None
        assert user_layout["customized"] == True
        assert "generation_status" in user_layout["component_positions"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])