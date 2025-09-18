"""
Contract test for SystemStatus model
T028: This test MUST FAIL initially (TDD Red phase)
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

# This import will FAIL because the model doesn't exist yet
from src.models.system_status import SystemStatus, SystemStatusCreate


class TestSystemStatusModelContract:
    """Contract tests for SystemStatus model structure and validation"""
    
    def test_system_status_model_required_fields(self):
        """
        SystemStatus model must have all required fields
        Expected to FAIL: model doesn't exist yet
        """
        # Contract: Required fields validation
        status_data = {
            "cpu_usage": 25.5,
            "memory_usage": 60.2,
            "disk_usage": 45.8,
            "uptime": 3600,
            "active_sessions": 2,
            "total_videos": 10,
            "m5stack_status": "online",
            "display_status": "active",
            "api_status": "healthy",
            "timestamp": datetime.now()
        }
        
        status = SystemStatus(**status_data)
        
        # Contract: All required fields present
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
    
    def test_percentage_validation(self):
        """
        CPU, memory, and disk usage should be validated as 0-100%
        """
        # Valid percentages should work
        valid_status = SystemStatusCreate(
            cpu_usage=50.0,
            memory_usage=75.5,
            disk_usage=25.0,
            uptime=3600,
            active_sessions=1,
            total_videos=5,
            m5stack_status="online",
            display_status="active",
            api_status="healthy"
        )
        assert valid_status.cpu_usage == 50.0
        assert valid_status.memory_usage == 75.5
        assert valid_status.disk_usage == 25.0
        
        # Edge cases: 0% and 100% should be valid
        edge_status = SystemStatusCreate(
            cpu_usage=0.0,
            memory_usage=100.0,
            disk_usage=0.0,
            uptime=0,
            active_sessions=0,
            total_videos=0,
            m5stack_status="offline",
            display_status="idle",
            api_status="healthy"
        )
        assert edge_status.cpu_usage == 0.0
        assert edge_status.memory_usage == 100.0
        
        # Invalid percentages should fail
        invalid_values = [-1.0, 100.1, 150.0, -50.0]
        
        for invalid_val in invalid_values:
            with pytest.raises(ValidationError):
                SystemStatusCreate(
                    cpu_usage=invalid_val,
                    memory_usage=50.0,
                    disk_usage=50.0,
                    uptime=3600,
                    active_sessions=1,
                    total_videos=5,
                    m5stack_status="online",
                    display_status="active",
                    api_status="healthy"
                )
    
    def test_status_enum_validation(self):
        """
        Status fields should validate against allowed enum values
        """
        # Valid status values
        valid_status = SystemStatusCreate(
            cpu_usage=25.0,
            memory_usage=50.0,
            disk_usage=75.0,
            uptime=3600,
            active_sessions=2,
            total_videos=10,
            m5stack_status="online",
            display_status="active", 
            api_status="healthy"
        )
        assert valid_status.m5stack_status == "online"
        assert valid_status.display_status == "active"
        assert valid_status.api_status == "healthy"
        
        # Test all valid enum values
        m5stack_values = ["online", "offline", "error"]
        display_values = ["active", "idle", "error"]
        api_values = ["healthy", "degraded", "error"]
        
        for m5_val in m5stack_values:
            for disp_val in display_values:
                for api_val in api_values:
                    status = SystemStatusCreate(
                        cpu_usage=25.0,
                        memory_usage=50.0,
                        disk_usage=75.0,
                        uptime=3600,
                        active_sessions=1,
                        total_videos=5,
                        m5stack_status=m5_val,
                        display_status=disp_val,
                        api_status=api_val
                    )
                    assert status.m5stack_status == m5_val
                    assert status.display_status == disp_val
                    assert status.api_status == api_val
        
        # Invalid status values should fail
        with pytest.raises(ValidationError):
            SystemStatusCreate(
                cpu_usage=25.0,
                memory_usage=50.0,
                disk_usage=75.0,
                uptime=3600,
                active_sessions=1,
                total_videos=5,
                m5stack_status="invalid_status",
                display_status="active",
                api_status="healthy"
            )
    
    def test_count_validation(self):
        """
        Count fields (uptime, active_sessions, total_videos) should be non-negative
        """
        # Valid counts should work
        valid_status = SystemStatusCreate(
            cpu_usage=25.0,
            memory_usage=50.0,
            disk_usage=75.0,
            uptime=7200,
            active_sessions=5,
            total_videos=50,
            m5stack_status="online",
            display_status="active",
            api_status="healthy"
        )
        assert valid_status.uptime == 7200
        assert valid_status.active_sessions == 5
        assert valid_status.total_videos == 50
        
        # Zero should be valid
        zero_status = SystemStatusCreate(
            cpu_usage=0.0,
            memory_usage=0.0,
            disk_usage=0.0,
            uptime=0,
            active_sessions=0,
            total_videos=0,
            m5stack_status="offline",
            display_status="idle",
            api_status="degraded"
        )
        assert zero_status.uptime == 0
        assert zero_status.active_sessions == 0
        assert zero_status.total_videos == 0
        
        # Negative values should fail
        negative_values = [-1, -100, -3600]
        
        for neg_val in negative_values:
            with pytest.raises(ValidationError):
                SystemStatusCreate(
                    cpu_usage=25.0,
                    memory_usage=50.0,
                    disk_usage=75.0,
                    uptime=neg_val,  # Negative uptime
                    active_sessions=1,
                    total_videos=5,
                    m5stack_status="online",
                    display_status="active",
                    api_status="healthy"
                )
    
    def test_system_status_defaults(self):
        """
        SystemStatus should have appropriate default values
        """
        # Minimal creation with defaults
        status = SystemStatusCreate(
            cpu_usage=25.0,
            memory_usage=50.0,
            disk_usage=75.0
            # Other fields should use defaults
        )
        
        # Contract: Default values
        assert status.uptime >= 0  # Should have default
        assert status.active_sessions >= 0  # Should have default
        assert status.total_videos >= 0  # Should have default
        assert status.m5stack_status in ["online", "offline", "error"]
        assert status.display_status in ["active", "idle", "error"]
        assert status.api_status in ["healthy", "degraded", "error"]
        assert status.timestamp is not None  # Should auto-set to current time
    
    def test_system_status_create_vs_full_model(self):
        """
        SystemStatusCreate should not have id, SystemStatus should have UUID id
        """
        # Create model should not have id
        create_data = SystemStatusCreate(
            cpu_usage=30.0,
            memory_usage=40.0,
            disk_usage=50.0,
            uptime=1800,
            active_sessions=3,
            total_videos=15,
            m5stack_status="online",
            display_status="active",
            api_status="healthy"
        )
        assert not hasattr(create_data, 'id')
        
        # Full model should have id (UUID string)
        full_status = SystemStatus(
            id="123e4567-e89b-12d3-a456-426614174000",
            cpu_usage=30.0,
            memory_usage=40.0,
            disk_usage=50.0,
            uptime=1800,
            active_sessions=3,
            total_videos=15,
            m5stack_status="online",
            display_status="active",
            api_status="healthy",
            timestamp=datetime.now()
        )
        assert full_status.id == "123e4567-e89b-12d3-a456-426614174000"