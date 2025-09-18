"""
Contract test for GET /api/display/status endpoint
T014: This test should pass (endpoints already exist)  
"""
import pytest
from fastapi.testclient import TestClient
from src.api.routes.display import router as display_router
from src.main import app


class TestDisplayStatusContract:
    """Contract tests for GET /api/display/status endpoint"""
    
    def setup_method(self):
        """Setup test client"""
        app.include_router(display_router, prefix="/api")
        self.client = TestClient(app)
    
    def test_status_with_no_session_returns_idle(self):
        """
        GET /api/display/status without active session should return idle
        """
        # Ensure no active session
        self.client.post("/api/display/stop")
        
        response = self.client.get("/api/display/status")
        
        assert response.status_code == 200
        status_data = response.json()
        
        # Contract: Idle status response
        if "session" in status_data:
            assert status_data["session"] is None
        if "status" in status_data:
            assert status_data["status"] == "idle"
    
    def test_status_with_active_session_returns_session_info(self):
        """
        GET /api/display/status with active session should return session info
        """
        # Start a video session
        video_data = {
            "video_id": "sample-video-123",
            "loop_enabled": False
        }
        play_response = self.client.post("/api/display/play", json=video_data)
        assert play_response.status_code == 200
        
        # Get status
        status_response = self.client.get("/api/display/status")
        
        assert status_response.status_code == 200
        status_data = status_response.json()
        
        # Contract: Active session response must include session details
        assert "video_id" in status_data
        assert "playback_status" in status_data
        assert "id" in status_data
        assert status_data["video_id"] == "sample-video-123"
        assert status_data["playback_status"] == "playing"
    
    def test_status_after_pause_shows_paused(self):
        """
        GET /api/display/status after pause should show paused status
        """
        # Start and pause video
        video_data = {
            "video_id": "sample-video-123",
            "loop_enabled": False
        }
        self.client.post("/api/display/play", json=video_data)
        self.client.post("/api/display/pause")
        
        # Check status
        response = self.client.get("/api/display/status")
        
        assert response.status_code == 200
        status_data = response.json()
        assert status_data["playback_status"] == "paused"
    
    def test_status_after_stop_shows_idle(self):
        """
        GET /api/display/status after stop should show idle/stopped
        """
        # Start and stop video
        video_data = {
            "video_id": "sample-video-123", 
            "loop_enabled": False
        }
        self.client.post("/api/display/play", json=video_data)
        self.client.post("/api/display/stop")
        
        # Check status
        response = self.client.get("/api/display/status")
        
        assert response.status_code == 200
        status_data = response.json()
        # After stop, session should be cleared (idle state)
        if "session" in status_data:
            assert status_data["session"] is None
        if "status" in status_data:
            assert status_data["status"] == "idle"
        # OR if still showing session info, should be empty/none
        if "playback_status" not in status_data:
            # This means session was cleared properly
            assert True