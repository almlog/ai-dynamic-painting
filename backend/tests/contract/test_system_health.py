"""
Contract test for GET /api/system/health endpoint
T044: This test MUST FAIL initially (TDD Red phase)
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app


class TestSystemHealthContract:
    """Contract tests for GET /api/system/health endpoint"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_health_endpoint_returns_200(self):
        """
        GET /api/system/health should return 200 OK
        """
        response = self.client.get("/api/system/health")
        
        assert response.status_code == 200
        health_data = response.json()
        
        # Contract: Health response must include status
        assert "status" in health_data
        assert health_data["status"] == "healthy"
    
    def test_health_includes_system_info(self):
        """
        GET /api/system/health should include system information
        """
        response = self.client.get("/api/system/health")
        
        assert response.status_code == 200
        health_data = response.json()
        
        # Contract: Health response must include system info
        assert "timestamp" in health_data
        assert "version" in health_data
        assert "uptime_seconds" in health_data
        
        # Contract: Values should be reasonable
        assert isinstance(health_data["uptime_seconds"], (int, float))
        assert health_data["uptime_seconds"] >= 0
        assert health_data["version"] is not None
    
    def test_health_includes_database_status(self):
        """
        GET /api/system/health should include database connectivity
        """
        response = self.client.get("/api/system/health")
        
        assert response.status_code == 200
        health_data = response.json()
        
        # Contract: Health response must include database status
        assert "database" in health_data
        db_status = health_data["database"]
        
        assert "connected" in db_status
        assert isinstance(db_status["connected"], bool)
        
        # If connected, should have additional info
        if db_status["connected"]:
            assert "tables_count" in db_status
            assert isinstance(db_status["tables_count"], int)
            assert db_status["tables_count"] >= 0
    
    def test_health_includes_storage_status(self):
        """
        GET /api/system/health should include storage information
        """
        response = self.client.get("/api/system/health")
        
        assert response.status_code == 200
        health_data = response.json()
        
        # Contract: Health response must include storage status
        assert "storage" in health_data
        storage_status = health_data["storage"]
        
        assert "videos_directory_exists" in storage_status
        assert isinstance(storage_status["videos_directory_exists"], bool)
        
        if storage_status["videos_directory_exists"]:
            assert "free_space_mb" in storage_status
            assert isinstance(storage_status["free_space_mb"], (int, float))
            assert storage_status["free_space_mb"] >= 0