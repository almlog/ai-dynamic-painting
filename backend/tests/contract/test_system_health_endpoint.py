"""
Contract test for GET /api/system/health endpoint
T044: This test MUST FAIL initially (TDD Red phase)
"""
import pytest
from fastapi.testclient import TestClient

# This import will FAIL because the endpoint doesn't exist yet
from src.api.routes.system import router as system_router
from src.main import app


class TestSystemHealthEndpointContract:
    """Contract tests for GET /api/system/health endpoint"""
    
    def setup_method(self):
        """Setup test client"""
        app.include_router(system_router, prefix="/api")
        self.client = TestClient(app)
    
    def test_health_endpoint_returns_200(self):
        """
        GET /api/system/health should return 200 with system status
        Expected to FAIL: endpoint doesn't exist yet
        """
        response = self.client.get("/api/system/health")
        
        assert response.status_code == 200
        health_data = response.json()
        
        # Contract: Response must include health information
        assert "status" in health_data
        assert "timestamp" in health_data
        assert "system" in health_data
        assert "services" in health_data
        
        # Contract: Overall status should be valid
        assert health_data["status"] in ["healthy", "degraded", "unhealthy"]
    
    def test_health_response_system_metrics(self):
        """
        Health response should include system resource metrics
        """
        response = self.client.get("/api/system/health")
        
        assert response.status_code == 200
        health_data = response.json()
        
        # Contract: System metrics structure
        system = health_data["system"]
        assert "cpu_usage" in system
        assert "memory_usage" in system
        assert "disk_usage" in system
        assert "uptime" in system
        
        # Contract: Metrics should be valid ranges
        assert 0.0 <= system["cpu_usage"] <= 100.0
        assert 0.0 <= system["memory_usage"] <= 100.0
        assert 0.0 <= system["disk_usage"] <= 100.0
        assert system["uptime"] >= 0
    
    def test_health_response_service_status(self):
        """
        Health response should include external service status
        """
        response = self.client.get("/api/system/health")
        
        assert response.status_code == 200
        health_data = response.json()
        
        # Contract: Service status structure
        services = health_data["services"]
        assert "api" in services
        assert "m5stack" in services
        assert "display" in services
        
        # Contract: Each service should have status and details
        for service_name, service_info in services.items():
            assert "status" in service_info
            assert "message" in service_info
            assert service_info["status"] in ["healthy", "degraded", "unhealthy"]
            assert isinstance(service_info["message"], str)
    
    def test_health_response_application_metrics(self):
        """
        Health response should include application-specific metrics
        """
        response = self.client.get("/api/system/health")
        
        assert response.status_code == 200
        health_data = response.json()
        
        # Contract: Application metrics
        system = health_data["system"]
        assert "active_sessions" in system
        assert "total_videos" in system
        
        # Contract: Counts should be non-negative
        assert system["active_sessions"] >= 0
        assert system["total_videos"] >= 0
    
    def test_health_overall_status_logic(self):
        """
        Overall health status should reflect system and service conditions
        """
        response = self.client.get("/api/system/health")
        
        assert response.status_code == 200
        health_data = response.json()
        
        overall_status = health_data["status"]
        system = health_data["system"]
        services = health_data["services"]
        
        # Contract: Status logic validation
        # If any service is unhealthy, overall should not be healthy
        service_statuses = [s["status"] for s in services.values()]
        
        if "unhealthy" in service_statuses:
            assert overall_status in ["degraded", "unhealthy"]
        
        # If system resources are critical (>95%), status should reflect this
        if (system["cpu_usage"] > 95 or 
            system["memory_usage"] > 95 or 
            system["disk_usage"] > 95):
            assert overall_status in ["degraded", "unhealthy"]
    
    def test_health_response_format_consistency(self):
        """
        Health endpoint should return consistent JSON structure
        """
        response = self.client.get("/api/system/health")
        
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        
        health_data = response.json()
        
        # Contract: Required top-level fields
        required_fields = ["status", "timestamp", "system", "services"]
        for field in required_fields:
            assert field in health_data
        
        # Contract: Timestamp should be ISO format
        timestamp = health_data["timestamp"]
        assert isinstance(timestamp, str)
        # Should be parseable as ISO datetime
        from datetime import datetime
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    
    def test_health_endpoint_performance(self):
        """
        Health endpoint should respond quickly (< 5 seconds)
        """
        import time
        
        start_time = time.time()
        response = self.client.get("/api/system/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0  # Should respond within 5 seconds
    
    def test_health_endpoint_handles_service_failures(self):
        """
        Health endpoint should not crash even if some services fail
        """
        # Multiple requests to test resilience
        for i in range(3):
            response = self.client.get("/api/system/health")
            
            # Should always return 200, even if services are down
            assert response.status_code == 200
            health_data = response.json()
            
            # Should always have basic structure
            assert "status" in health_data
            assert "system" in health_data
            assert "services" in health_data
    
    def test_health_endpoint_caching_behavior(self):
        """
        Health endpoint should handle multiple rapid requests
        """
        responses = []
        
        # Make multiple rapid requests
        for i in range(5):
            response = self.client.get("/api/system/health")
            responses.append(response)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            health_data = response.json()
            assert "status" in health_data
    
    def test_health_response_detailed_service_info(self):
        """
        Each service should provide detailed status information
        """
        response = self.client.get("/api/system/health")
        
        assert response.status_code == 200
        health_data = response.json()
        
        services = health_data["services"]
        
        # API service details
        api_service = services["api"]
        assert api_service["status"] == "healthy"  # Should be healthy if responding
        assert "API operational" in api_service["message"] or "healthy" in api_service["message"].lower()
        
        # M5STACK service details
        m5stack_service = services["m5stack"]
        assert m5stack_service["status"] in ["healthy", "degraded", "unhealthy"]
        assert isinstance(m5stack_service["message"], str)
        assert len(m5stack_service["message"]) > 0
        
        # Display service details
        display_service = services["display"]
        assert display_service["status"] in ["healthy", "degraded", "unhealthy"]
        assert isinstance(display_service["message"], str)
        assert len(display_service["message"]) > 0