"""
Contract test for POST /api/display/pause endpoint
T013: This test should pass (endpoints already exist)
"""
import pytest
from fastapi.testclient import TestClient
from src.api.routes.display import router as display_router
from src.main import app


class TestDisplayPauseContract:
    """Contract tests for POST /api/display/pause endpoint"""
    
    def setup_method(self):
        """Setup test client"""
        app.include_router(display_router, prefix="/api")
        self.client = TestClient(app)
    
    def test_pause_active_playback_returns_200(self):
        """
        POST /api/display/pause with active playback should return 200
        """
        # First start a video (need an active session)
        video_data = {
            "video_id": "sample-video-123",
            "loop_enabled": False
        }
        play_response = self.client.post("/api/display/play", json=video_data)
        assert play_response.status_code == 200
        
        # Now pause it
        pause_response = self.client.post("/api/display/pause")
        assert pause_response.status_code == 200
        
        pause_data = pause_response.json()
        # Contract: Response must include session info with paused status
        assert "playback_status" in pause_data
        assert pause_data["playback_status"] == "paused"
        assert "video_id" in pause_data
        assert "id" in pause_data
    
    def test_pause_without_active_playback_returns_409(self):
        """
        POST /api/display/pause without active playback should return 409
        """
        # Ensure no active session (global state)
        self.client.post("/api/display/stop")
        
        response = self.client.post("/api/display/pause")
        
        assert response.status_code == 409
        error_data = response.json()
        
        # Contract: Error response structure
        assert "detail" in error_data
        detail = error_data["detail"]
        assert "error" in detail
        assert "message" in detail
        assert "no active" in detail["message"].lower() or "no video" in detail["message"].lower()
    
    def test_pause_already_paused_video_returns_200(self):
        """
        POST /api/display/pause on already paused video should return 200
        """
        # Start video
        video_data = {
            "video_id": "sample-video-123",
            "loop_enabled": False
        }
        self.client.post("/api/display/play", json=video_data)
        
        # Pause once
        first_pause = self.client.post("/api/display/pause")
        assert first_pause.status_code == 200
        
        # Pause again (should still work)
        second_pause = self.client.post("/api/display/pause")
        assert second_pause.status_code == 200
        
        pause_data = second_pause.json()
        assert pause_data["playback_status"] == "paused"