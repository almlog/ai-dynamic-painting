"""
Contract test for MonitoringService
T033: This test MUST FAIL initially (TDD Red phase)
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

# This import will FAIL because the service doesn't exist yet
from src.services.monitoring_service import MonitoringService
from src.models.system_status import SystemStatus


class TestMonitoringServiceContract:
    """Contract tests for MonitoringService system monitoring functionality"""
    
    def setup_method(self):
        """Setup test instance"""
        self.monitoring_service = MonitoringService()
    
    def test_monitoring_service_initialization(self):
        """
        MonitoringService should initialize properly
        Expected to FAIL: service doesn't exist yet
        """
        service = MonitoringService()
        
        # Contract: Service should be properly initialized
        assert service is not None
        assert hasattr(service, 'get_current_status')
        assert hasattr(service, 'record_system_status')
        assert hasattr(service, 'cleanup_old_logs')
        assert hasattr(service, 'get_status_history')
    
    def test_get_current_status_returns_system_status(self):
        """
        get_current_status() should return SystemStatus object with current metrics
        """
        status = self.monitoring_service.get_current_status()
        
        # Contract: Returns SystemStatus object
        assert isinstance(status, SystemStatus)
        
        # Contract: All required fields present with valid values
        assert hasattr(status, 'id')
        assert hasattr(status, 'timestamp')
        assert hasattr(status, 'cpu_usage')
        assert hasattr(status, 'memory_usage')
        assert hasattr(status, 'disk_usage')
        assert hasattr(status, 'uptime')
        assert hasattr(status, 'active_sessions')
        assert hasattr(status, 'total_videos')
        assert hasattr(status, 'm5stack_status')
        assert hasattr(status, 'display_status')
        assert hasattr(status, 'api_status')
        
        # Contract: Percentage values are valid (0-100)
        assert 0.0 <= status.cpu_usage <= 100.0
        assert 0.0 <= status.memory_usage <= 100.0
        assert 0.0 <= status.disk_usage <= 100.0
        
        # Contract: Counts are non-negative
        assert status.uptime >= 0
        assert status.active_sessions >= 0
        assert status.total_videos >= 0
        
        # Contract: Status enums are valid
        assert status.m5stack_status in ["online", "offline", "error"]
        assert status.display_status in ["active", "idle", "error"]
        assert status.api_status in ["healthy", "degraded", "error"]
    
    def test_record_system_status_saves_to_database(self):
        """
        record_system_status() should save current status to database
        """
        # Mock the current status
        mock_status = SystemStatus(
            cpu_usage=25.5,
            memory_usage=60.2,
            disk_usage=45.8,
            uptime=3600,
            active_sessions=2,
            total_videos=10,
            m5stack_status="online",
            display_status="active",
            api_status="healthy",
            timestamp=datetime.now()
        )
        
        with patch.object(self.monitoring_service, 'get_current_status', return_value=mock_status):
            result = self.monitoring_service.record_system_status()
        
        # Contract: Should return saved status
        assert isinstance(result, SystemStatus)
        assert result.cpu_usage == 25.5
        assert result.memory_usage == 60.2
        
        # Contract: Should have assigned ID and timestamp
        assert result.id is not None
        assert result.timestamp is not None
    
    def test_get_status_history_returns_recent_logs(self):
        """
        get_status_history() should return list of recent SystemStatus entries
        """
        # Test with default limit
        history = self.monitoring_service.get_status_history()
        
        # Contract: Returns list
        assert isinstance(history, list)
        
        # Contract: Each item is SystemStatus
        for status in history:
            assert isinstance(status, SystemStatus)
        
        # Test with custom limit
        limited_history = self.monitoring_service.get_status_history(limit=5)
        assert isinstance(limited_history, list)
        assert len(limited_history) <= 5
        
        # Test with hours filter
        recent_history = self.monitoring_service.get_status_history(hours=1)
        assert isinstance(recent_history, list)
        # All entries should be within last hour (tested by timestamp)
        now = datetime.now()
        for status in recent_history:
            time_diff = (now - status.timestamp).total_seconds()
            assert time_diff <= 3600  # 1 hour in seconds
    
    def test_cleanup_old_logs_removes_expired_entries(self):
        """
        cleanup_old_logs() should remove logs older than specified days
        """
        # Contract: Should return number of deleted entries
        deleted_count = self.monitoring_service.cleanup_old_logs(days=7)
        assert isinstance(deleted_count, int)
        assert deleted_count >= 0
        
        # Test with different day values
        deleted_1day = self.monitoring_service.cleanup_old_logs(days=1)
        assert isinstance(deleted_1day, int)
        assert deleted_1day >= 0
    
    def test_get_resource_usage_metrics(self):
        """
        Service should provide methods to get individual resource metrics
        """
        # CPU usage
        cpu = self.monitoring_service.get_cpu_usage()
        assert isinstance(cpu, float)
        assert 0.0 <= cpu <= 100.0
        
        # Memory usage
        memory = self.monitoring_service.get_memory_usage()
        assert isinstance(memory, float)
        assert 0.0 <= memory <= 100.0
        
        # Disk usage
        disk = self.monitoring_service.get_disk_usage()
        assert isinstance(disk, float)
        assert 0.0 <= disk <= 100.0
        
        # System uptime
        uptime = self.monitoring_service.get_uptime()
        assert isinstance(uptime, int)
        assert uptime >= 0
    
    def test_get_application_metrics(self):
        """
        Service should provide application-specific metrics
        """
        # Active sessions count
        sessions = self.monitoring_service.get_active_sessions_count()
        assert isinstance(sessions, int)
        assert sessions >= 0
        
        # Total videos count
        videos = self.monitoring_service.get_total_videos_count()
        assert isinstance(videos, int)
        assert videos >= 0
    
    def test_check_external_services_status(self):
        """
        Service should check status of external services (M5STACK, Display)
        """
        # M5STACK status check
        m5stack_status = self.monitoring_service.check_m5stack_status()
        assert m5stack_status in ["online", "offline", "error"]
        
        # Display status check  
        display_status = self.monitoring_service.check_display_status()
        assert display_status in ["active", "idle", "error"]
        
        # API health check
        api_status = self.monitoring_service.check_api_status()
        assert api_status in ["healthy", "degraded", "error"]
    
    def test_monitoring_service_handles_errors(self):
        """
        Service should handle errors gracefully and not crash
        """
        # Should not raise exceptions even if system calls fail
        try:
            status = self.monitoring_service.get_current_status()
            assert status is not None
        except Exception as e:
            pytest.fail(f"get_current_status should handle errors gracefully, got: {e}")
        
        try:
            history = self.monitoring_service.get_status_history()
            assert isinstance(history, list)
        except Exception as e:
            pytest.fail(f"get_status_history should handle errors gracefully, got: {e}")
    
    def test_monitoring_service_database_operations(self):
        """
        Service should handle database operations properly
        """
        # Should work with or without database connection
        # In minimal implementation, might use in-memory storage
        
        # Record status
        status1 = self.monitoring_service.record_system_status()
        assert isinstance(status1, SystemStatus)
        
        # Get history should include recorded status
        history = self.monitoring_service.get_status_history(limit=10)
        assert len(history) >= 1
        
        # Most recent entry should be the recorded status
        assert history[0].id == status1.id or any(s.id == status1.id for s in history)