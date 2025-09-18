"""
Contract tests for export/import system - T260.
Tests MUST fail initially (RED phase), then pass after implementation (GREEN phase).
"""

import pytest
import asyncio
import json
import tempfile
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestExportImportContract:
    """Contract tests for T260: Export/Import Features"""
    
    def test_data_export_model_exists(self):
        """Test that DataExport model exists"""
        from src.models.data_export import DataExport
        
        # Test model creation
        export = DataExport(
            export_id="export_123",
            export_name="AI Metrics Export",
            export_type="analytics",
            data_sources=["metrics", "dashboards", "alerts"],
            export_format="json",
            file_path="/exports/ai_metrics_20250918.json",
            created_by="user_123",
            export_config={
                "include_metadata": True,
                "date_range": {
                    "start": "2025-09-01T00:00:00Z",
                    "end": "2025-09-18T23:59:59Z"
                },
                "compression": "gzip",
                "encryption": False
            }
        )
        
        assert export.export_id == "export_123"
        assert export.export_name == "AI Metrics Export"
        assert export.export_type == "analytics"
        assert len(export.data_sources) == 3
        assert export.export_format == "json"
        assert export.export_config["include_metadata"] == True
    
    @pytest.mark.asyncio
    async def test_export_import_service_exists(self):
        """Test that ExportImportService exists and works"""
        from src.ai.services.export_import_service import ExportImportService
        
        # Create export/import service
        service = ExportImportService()
        
        # Test data export initiation
        export_config = {
            "name": "Weekly AI Report",
            "type": "analytics",
            "format": "csv",
            "data_sources": ["ai_metrics", "performance_data"],
            "date_range": {
                "start": datetime.now() - timedelta(days=7),
                "end": datetime.now()
            },
            "include_metadata": True,
            "compression": True
        }
        
        export_id = await service.initiate_export(export_config)
        assert export_id is not None
        assert isinstance(export_id, str)
        assert export_id.startswith("export_")
        
        # Test export status check
        export_status = await service.get_export_status(export_id)
        assert export_status is not None
        assert export_status["export_id"] == export_id
        assert "status" in export_status
        assert "progress_percentage" in export_status
    
    @pytest.mark.asyncio
    async def test_multiple_export_formats(self):
        """Test export in multiple formats (JSON, CSV, Excel, XML)"""
        from src.ai.services.export_import_service import ExportImportService
        
        service = ExportImportService()
        
        formats = ["json", "csv", "excel", "xml"]
        export_ids = []
        
        for format_type in formats:
            export_config = {
                "name": f"Test Export {format_type.upper()}",
                "type": "system_data",
                "format": format_type,
                "data_sources": ["test_metrics"],
                "include_headers": True,
                "encoding": "utf-8"
            }
            
            export_id = await service.initiate_export(export_config)
            export_ids.append(export_id)
            
            # Verify export was created
            export_status = await service.get_export_status(export_id)
            assert export_status["format"] == format_type
            assert export_status["status"] in ["pending", "processing", "completed"]
        
        assert len(export_ids) == 4
        assert all(eid.startswith("export_") for eid in export_ids)
    
    @pytest.mark.asyncio
    async def test_filtered_data_export(self):
        """Test filtered data export with conditions"""
        from src.ai.services.export_import_service import ExportImportService
        
        service = ExportImportService()
        
        # Test export with filters
        export_config = {
            "name": "Filtered Metrics Export",
            "type": "metrics",
            "format": "json",
            "data_sources": ["ai_metrics"],
            "filters": {
                "component": ["video_generation", "prompt_enhancement"],
                "metric_type": "performance",
                "severity": ["medium", "high"],
                "date_range": {
                    "start": datetime.now() - timedelta(days=30),
                    "end": datetime.now()
                },
                "tags": {
                    "environment": "production",
                    "version": "2.0"
                }
            },
            "include_aggregations": True,
            "aggregation_periods": ["daily", "weekly"]
        }
        
        export_id = await service.initiate_export(export_config)
        
        # Verify filtered export
        export_details = await service.get_export_details(export_id)
        assert export_details is not None
        assert export_details["filters"]["component"] == ["video_generation", "prompt_enhancement"]
        assert export_details["include_aggregations"] == True
        assert "daily" in export_details["aggregation_periods"]
    
    @pytest.mark.asyncio
    async def test_large_dataset_export(self):
        """Test export of large datasets with pagination and streaming"""
        from src.ai.services.export_import_service import ExportImportService
        
        service = ExportImportService()
        
        # Test large dataset export
        export_config = {
            "name": "Large Dataset Export",
            "type": "bulk_data",
            "format": "csv",
            "data_sources": ["historical_metrics", "log_data", "user_interactions"],
            "streaming": True,
            "chunk_size": 1000,
            "compression": "gzip",
            "estimated_rows": 100000,
            "memory_limit_mb": 512
        }
        
        export_id = await service.initiate_export(export_config)
        
        # Monitor export progress
        max_attempts = 10
        attempts = 0
        
        while attempts < max_attempts:
            status = await service.get_export_status(export_id)
            
            if status["status"] == "completed":
                assert status["progress_percentage"] == 100
                assert "file_size_bytes" in status
                assert "total_rows" in status
                break
            elif status["status"] == "failed":
                pytest.fail(f"Export failed: {status.get('error_message')}")
            
            attempts += 1
            await asyncio.sleep(0.1)
        
        # Verify export completion
        final_status = await service.get_export_status(export_id)
        assert final_status["status"] in ["completed", "processing"]
    
    @pytest.mark.asyncio
    async def test_data_import_functionality(self):
        """Test data import from various sources"""
        from src.ai.services.export_import_service import ExportImportService
        
        service = ExportImportService()
        
        # Test import configuration
        import_config = {
            "name": "Metrics Data Import",
            "type": "analytics",
            "source_format": "json",
            "file_path": "/imports/external_metrics.json",
            "data_mapping": {
                "timestamp": "created_at",
                "value": "metric_value",
                "type": "metric_type",
                "source": "component"
            },
            "validation_rules": {
                "required_fields": ["timestamp", "value", "type"],
                "data_types": {
                    "timestamp": "datetime",
                    "value": "float",
                    "type": "string"
                },
                "value_ranges": {
                    "value": {"min": 0, "max": 1000}
                }
            },
            "conflict_resolution": "update_existing",
            "batch_size": 500
        }
        
        import_id = await service.initiate_import(import_config)
        assert import_id is not None
        assert isinstance(import_id, str)
        assert import_id.startswith("import_")
        
        # Test import status
        import_status = await service.get_import_status(import_id)
        assert import_status is not None
        assert import_status["import_id"] == import_id
        assert "status" in import_status
        assert "records_processed" in import_status
    
    @pytest.mark.asyncio
    async def test_data_validation_during_import(self):
        """Test data validation and error handling during import"""
        from src.ai.services.export_import_service import ExportImportService
        
        service = ExportImportService()
        
        # Test import with validation errors
        import_config = {
            "name": "Validation Test Import",
            "type": "test_data",
            "source_format": "csv",
            "file_content": [
                {"name": "metric1", "value": 100, "type": "performance"},  # Valid
                {"name": "metric2", "value": "invalid", "type": "performance"},  # Invalid value
                {"name": "", "value": 50, "type": "performance"},  # Missing name
                {"name": "metric3", "value": 200, "type": "unknown"}  # Invalid type
            ],
            "validation_rules": {
                "required_fields": ["name", "value", "type"],
                "data_types": {"value": "number"},
                "allowed_values": {"type": ["performance", "system", "business"]},
                "field_length": {"name": {"min": 1, "max": 50}}
            },
            "error_handling": "continue_on_error",
            "max_errors": 10
        }
        
        import_id = await service.initiate_import(import_config)
        
        # Wait for import completion and check validation results
        max_attempts = 10
        attempts = 0
        
        while attempts < max_attempts:
            status = await service.get_import_status(import_id)
            
            if status["status"] in ["completed", "completed_with_errors"]:
                assert "validation_errors" in status
                assert "records_processed" in status
                assert "records_failed" in status
                assert status["records_failed"] > 0  # Should have validation errors
                break
            
            attempts += 1
            await asyncio.sleep(0.1)
        
        # Get detailed validation report
        validation_report = await service.get_import_validation_report(import_id)
        assert validation_report is not None
        assert "error_summary" in validation_report
        assert "failed_records" in validation_report
    
    @pytest.mark.asyncio
    async def test_backup_and_restore_functionality(self):
        """Test system backup and restore capabilities"""
        from src.ai.services.export_import_service import ExportImportService
        
        service = ExportImportService()
        
        # Test full system backup
        backup_config = {
            "name": "Full System Backup",
            "type": "backup",
            "scope": "full_system",
            "include": [
                "dashboards",
                "metrics",
                "alert_rules",
                "user_preferences",
                "system_config"
            ],
            "compression": "lz4",
            "encryption": True,
            "encryption_key": "backup_key_123",
            "exclude_sensitive": False
        }
        
        backup_id = await service.create_backup(backup_config)
        assert backup_id is not None
        assert backup_id.startswith("backup_")
        
        # Test backup status
        backup_status = await service.get_backup_status(backup_id)
        assert backup_status["backup_id"] == backup_id
        assert backup_status["status"] in ["pending", "processing", "completed"]
        
        # Test restore preparation
        restore_config = {
            "backup_id": backup_id,
            "restore_scope": "selective",
            "include": ["dashboards", "metrics"],
            "conflict_resolution": "merge",
            "dry_run": True  # Test mode first
        }
        
        restore_id = await service.prepare_restore(restore_config)
        assert restore_id is not None
        assert restore_id.startswith("restore_")
        
        # Get restore preview
        restore_preview = await service.get_restore_preview(restore_id)
        assert restore_preview is not None
        assert "affected_entities" in restore_preview
        assert "potential_conflicts" in restore_preview
    
    @pytest.mark.asyncio
    async def test_scheduled_exports(self):
        """Test scheduled export functionality"""
        from src.ai.services.export_import_service import ExportImportService
        
        service = ExportImportService()
        
        # Test scheduled export creation
        schedule_config = {
            "name": "Daily Metrics Export",
            "export_config": {
                "type": "analytics",
                "format": "csv",
                "data_sources": ["daily_metrics"]
            },
            "schedule": {
                "frequency": "daily",
                "time": "02:00",
                "timezone": "UTC",
                "enabled": True
            },
            "retention": {
                "keep_count": 30,
                "cleanup_old": True
            },
            "notification": {
                "on_success": True,
                "on_failure": True,
                "recipients": ["admin@example.com"]
            }
        }
        
        schedule_id = await service.create_export_schedule(schedule_config)
        assert schedule_id is not None
        assert schedule_id.startswith("schedule_")
        
        # Test schedule management
        schedules = await service.list_export_schedules()
        assert any(s["schedule_id"] == schedule_id for s in schedules)
        
        # Test schedule execution simulation
        execution_result = await service.execute_scheduled_export(schedule_id)
        assert execution_result is not None
        assert "export_id" in execution_result
        assert "execution_time" in execution_result
    
    @pytest.mark.asyncio
    async def test_export_import_security(self):
        """Test security features for export/import operations"""
        from src.ai.services.export_import_service import ExportImportService
        
        service = ExportImportService()
        
        # Test access control
        export_config = {
            "name": "Secured Export",
            "type": "sensitive_data",
            "format": "json",
            "data_sources": ["user_data", "api_keys"],
            "security": {
                "encryption": True,
                "access_level": "admin_only",
                "audit_trail": True,
                "data_masking": {
                    "mask_fields": ["email", "api_key"],
                    "masking_pattern": "***"
                }
            }
        }
        
        # Test unauthorized access
        try:
            export_id = await service.initiate_export(export_config, user_role="viewer")
            # Should not reach here for unauthorized access
            pytest.fail("Expected authorization error for viewer role")
        except Exception as e:
            assert "unauthorized" in str(e).lower() or "permission" in str(e).lower()
        
        # Test authorized access
        export_id = await service.initiate_export(export_config, user_role="admin")
        assert export_id is not None
        
        # Verify audit trail creation
        audit_logs = await service.get_export_audit_trail(export_id)
        assert audit_logs is not None
        assert len(audit_logs) >= 1
        assert any("initiated" in log["action"] for log in audit_logs)
    
    @pytest.mark.asyncio
    async def test_template_management(self):
        """Test export/import template management"""
        from src.ai.services.export_import_service import ExportImportService
        
        service = ExportImportService()
        
        # Test template creation
        template_config = {
            "name": "Standard Analytics Export",
            "description": "Template for regular analytics data export",
            "type": "export",
            "template": {
                "format": "csv",
                "data_sources": ["metrics", "events"],
                "default_filters": {
                    "date_range": "last_30_days",
                    "include_metadata": True
                },
                "column_mapping": {
                    "timestamp": "Date",
                    "metric_value": "Value",
                    "component": "Source"
                }
            },
            "category": "analytics",
            "is_public": True
        }
        
        template_id = await service.create_template(template_config)
        assert template_id is not None
        assert template_id.startswith("template_")
        
        # Test template usage
        export_from_template = await service.create_export_from_template(
            template_id,
            overrides={
                "name": "Monthly Report Export",
                "date_range": "last_month"
            }
        )
        
        assert export_from_template is not None
        assert "export_id" in export_from_template
        
        # Test template listing
        templates = await service.list_templates(category="analytics")
        assert any(t["template_id"] == template_id for t in templates)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])