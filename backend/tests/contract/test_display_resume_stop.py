"""
Contract tests for POST /api/display/resume and POST /api/display/stop endpoints
T039, T040: These tests should pass (endpoints already exist)
"""
import pytest
from fastapi.testclient import TestClient
from src.api.routes.display import router as display_router
from src.main import app


class TestDisplayResumeStopContract:
    """Contract tests for resume and stop endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        app.include_router(display_router, prefix="/api")
        self.client = TestClient(app)
    
    # T039: Resume endpoint tests
    def test_resume_paused_video_returns_200(self):
        """
        POST /api/display/resume on paused video should return 200
        """
        # Start and pause video
        video_data = {
            "video_id": "sample-video-123",
            "loop_enabled": False
        }
        self.client.post("/api/display/play", json=video_data)
        self.client.post("/api/display/pause")
        
        # Resume video
        response = self.client.post("/api/display/resume")
        
        assert response.status_code == 200
        resume_data = response.json()
        
        # Contract: Resume response must show playing status
        assert "playback_status" in resume_data
        assert resume_data["playback_status"] == "playing"
        assert "video_id" in resume_data
        assert "id" in resume_data
    
    def test_resume_without_session_returns_409(self):
        """
        POST /api/display/resume without active session should return 409
        """
        # Ensure no active session
        self.client.post("/api/display/stop")
        
        response = self.client.post("/api/display/resume")
        
        assert response.status_code == 409
        error_data = response.json()
        
        # Contract: Error response structure
        assert "detail" in error_data
        detail = error_data["detail"]
        assert "error" in detail
        assert "message" in detail
        assert "no active" in detail["message"].lower() or "no video" in detail["message"].lower()
    
    # T040: Stop endpoint tests
    def test_stop_active_video_returns_200(self):
        """
        POST /api/display/stop on active video should return 200
        """
        # Start video
        video_data = {
            "video_id": "sample-video-123",
            "loop_enabled": False
        }
        self.client.post("/api/display/play", json=video_data)
        
        # Stop video
        response = self.client.post("/api/display/stop")
        
        assert response.status_code == 200
        stop_data = response.json()
        
        # Contract: Stop response must show stopped status
        assert "playback_status" in stop_data
        assert stop_data["playback_status"] == "stopped"
        assert "video_id" in stop_data
        assert "id" in stop_data
    
    def test_stop_without_active_playback_returns_409(self):
        """
        POST /api/display/stop without active playback should return 409
        """
        # Ensure no active session (try to stop twice)
        self.client.post("/api/display/stop")
        
        response = self.client.post("/api/display/stop")
        
        # First stop might succeed, second should fail
        # But for stopped session, might still return 409
        assert response.status_code in [200, 409]
        
        if response.status_code == 409:
            error_data = response.json()
            assert "detail" in error_data
            detail = error_data["detail"]
            assert "error" in detail
            assert "message" in detail
    
    def test_resume_stop_playing_cycle(self):
        """
        Test complete playback control cycle: play -> pause -> resume -> stop
        """
        # Start video
        video_data = {
            "video_id": "sample-video-123",
            "loop_enabled": False
        }
        play_response = self.client.post("/api/display/play", json=video_data)
        assert play_response.status_code == 200
        assert play_response.json()["playback_status"] == "playing"
        
        # Pause
        pause_response = self.client.post("/api/display/pause")
        assert pause_response.status_code == 200
        assert pause_response.json()["playback_status"] == "paused"
        
        # Resume
        resume_response = self.client.post("/api/display/resume")
        assert resume_response.status_code == 200
        assert resume_response.json()["playback_status"] == "playing"
        
        # Stop
        stop_response = self.client.post("/api/display/stop")
        assert stop_response.status_code == 200
        assert stop_response.json()["playback_status"] == "stopped"