"""
Integration test M5STACK communication - T019
Phase 1 手動動画管理システム - M5STACK通信統合テスト
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import time
from src.main import app


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


class TestM5StackIntegration:
    """M5STACK communication integration tests"""

    def test_m5stack_control_endpoint(self, client):
        """Test M5STACK control API endpoint"""
        # Test button press simulation
        control_data = {
            "action": "button_press",
            "button": "A",
            "device_id": "m5stack-test"
        }
        
        response = client.post("/api/m5stack/control", json=control_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "processed" in data["message"]

    def test_m5stack_sensor_data_endpoint(self, client):
        """Test M5STACK sensor data retrieval"""
        response = client.get("/api/m5stack/sensors")
        assert response.status_code == 200
        
        data = response.json()
        assert "temperature" in data
        assert "humidity" in data
        assert "light_level" in data
        assert isinstance(data["temperature"], (int, float))

    @patch('src.services.m5stack_service.requests')
    def test_m5stack_communication_flow(self, mock_requests, client):
        """Test complete M5STACK communication workflow"""
        # Mock M5STACK HTTP responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "sensors": {
                "temperature": 25.5,
                "humidity": 60.0,
                "light_level": 300
            }
        }
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response
        
        # 1. Send control command to M5STACK
        control_response = client.post("/api/m5stack/control", json={
            "action": "display_message",
            "message": "Hello from API",
            "device_id": "m5stack-001"
        })
        assert control_response.status_code == 200
        
        # 2. Get sensor data from M5STACK
        sensor_response = client.get("/api/m5stack/sensors")
        assert sensor_response.status_code == 200
        sensor_data = sensor_response.json()
        assert sensor_data["temperature"] == 25.5
        
        # 3. Verify M5STACK service was called
        mock_requests.post.assert_called()
        mock_requests.get.assert_called()

    def test_m5stack_button_integration_with_display(self, client):
        """Test M5STACK button press integration with display control"""
        # Simulate button press that should trigger display action
        button_data = {
            "action": "button_press",
            "button": "A",  # Play button
            "device_id": "m5stack-001"
        }
        
        response = client.post("/api/m5stack/control", json=button_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        # Should indicate that display action was triggered
        assert "display" in data["message"].lower() or "triggered" in data["message"].lower()

    def test_m5stack_invalid_action(self, client):
        """Test invalid M5STACK action handling"""
        invalid_data = {
            "action": "invalid_action",
            "device_id": "m5stack-001"
        }
        
        response = client.post("/api/m5stack/control", json=invalid_data)
        assert response.status_code == 400
        
        error_data = response.json()
        assert "invalid" in error_data["detail"].lower()

    def test_m5stack_missing_device_id(self, client):
        """Test missing device_id parameter"""
        incomplete_data = {
            "action": "button_press",
            "button": "A"
        }
        
        response = client.post("/api/m5stack/control", json=incomplete_data)
        assert response.status_code == 422
        
        error_data = response.json()
        assert "device_id" in str(error_data)

    @patch('src.services.m5stack_service.requests')
    def test_m5stack_connection_error_handling(self, mock_requests, client):
        """Test M5STACK connection error handling"""
        # Mock connection failure
        mock_requests.RequestException = Exception
        mock_requests.get.side_effect = Exception("Connection failed")
        
        response = client.get("/api/m5stack/sensors")
        assert response.status_code == 503  # Service Unavailable
        
        error_data = response.json()
        assert "connection" in error_data["detail"].lower()

    def test_m5stack_response_time_requirements(self, client):
        """Test M5STACK response time <1s requirement"""
        start_time = time.time()
        
        response = client.post("/api/m5stack/control", json={
            "action": "button_press",
            "button": "A",
            "device_id": "m5stack-test"
        })
        
        elapsed_time = time.time() - start_time
        
        # M5STACK operations should complete within 1 second
        assert elapsed_time < 1.0, f"M5STACK operation took {elapsed_time:.2f}s"
        assert response.status_code == 200

    def test_m5stack_multiple_devices(self, client):
        """Test handling multiple M5STACK devices"""
        devices = ["m5stack-001", "m5stack-002", "m5stack-003"]
        
        for device_id in devices:
            response = client.post("/api/m5stack/control", json={
                "action": "ping",
                "device_id": device_id
            })
            assert response.status_code == 200
            
            data = response.json()
            assert data["device_id"] == device_id

    @patch('src.services.m5stack_service.requests')
    def test_m5stack_sensor_data_validation(self, mock_requests, client):
        """Test M5STACK sensor data validation"""
        # Mock sensor data response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "temperature": 25.5,
            "humidity": 60.0,
            "light_level": 300,
            "timestamp": "2025-09-12T10:00:00Z"
        }
        mock_requests.get.return_value = mock_response
        
        response = client.get("/api/m5stack/sensors")
        assert response.status_code == 200
        
        data = response.json()
        
        # Validate sensor data ranges
        assert -40 <= data["temperature"] <= 80  # Reasonable temperature range
        assert 0 <= data["humidity"] <= 100      # Humidity percentage
        assert 0 <= data["light_level"] <= 4095  # Light sensor range

    def test_m5stack_concurrent_requests(self, client):
        """Test handling concurrent M5STACK requests"""
        import threading
        import concurrent.futures
        
        def send_request(device_id):
            response = client.post("/api/m5stack/control", json={
                "action": "ping",
                "device_id": f"m5stack-{device_id}"
            })
            return response.status_code == 200
        
        # Send 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(send_request, i) for i in range(5)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        assert all(results), "Some concurrent M5STACK requests failed"

    def test_m5stack_device_registration_flow(self, client):
        """Test M5STACK device registration workflow"""
        # 1. Register new device
        registration_data = {
            "device_id": "m5stack-new",
            "device_name": "New M5STACK Core2",
            "ip_address": "192.168.1.150"
        }
        
        response = client.post("/api/m5stack/register", json=registration_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert data["device_id"] == "m5stack-new"
        
        # 2. Verify device can be controlled after registration
        control_response = client.post("/api/m5stack/control", json={
            "action": "ping",
            "device_id": "m5stack-new"
        })
        assert control_response.status_code == 200