"""
Contract test for POST /api/m5stack/control endpoint
T016: This test MUST FAIL initially (TDD Red phase)
"""
import pytest
from fastapi.testclient import TestClient

# This import will FAIL because the endpoint doesn't exist yet
from src.api.routes.m5stack import router as m5stack_router
from src.main import app


class TestM5StackControlContract:
    """Contract tests for POST /api/m5stack/control endpoint"""
    
    def setup_method(self):
        """Setup test client"""
        app.include_router(m5stack_router, prefix="/api")
        self.client = TestClient(app)
    
    def test_m5stack_button_control_returns_200(self):
        """
        POST /api/m5stack/control with valid action should return 200
        Expected to FAIL: endpoint doesn't exist yet
        """
        request_data = {
            "action": "play_pause",
            "device_info": {
                "device_id": "m5stack-001",
                "ip_address": "192.168.1.200"
            }
        }
        
        response = self.client.post("/api/m5stack/control", json=request_data)
        
        assert response.status_code == 200
        result_data = response.json()
        
        # Contract: Response must include result and current_session
        assert "result" in result_data
        assert "current_session" in result_data
        assert isinstance(result_data["result"], str)
    
    def test_m5stack_invalid_action_returns_400(self):
        """
        POST /api/m5stack/control with invalid action should return 400
        Expected to FAIL: endpoint doesn't exist yet
        """
        request_data = {
            "action": "invalid_action",
            "device_info": {
                "device_id": "m5stack-001"
            }
        }
        
        response = self.client.post("/api/m5stack/control", json=request_data)
        
        assert response.status_code == 400
        error_data = response.json()
        
        # Contract: Error response format
        assert "error" in error_data
        assert "message" in error_data