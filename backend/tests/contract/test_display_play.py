"""
Contract test for POST /api/display/play endpoint
T012: This test MUST FAIL initially (TDD Red phase)
"""
import pytest
from fastapi.testclient import TestClient

# This import will FAIL because the endpoint doesn't exist yet
from src.api.routes.display import router as display_router
from src.main import app


class TestDisplayPlayContract:
    """Contract tests for POST /api/display/play endpoint"""
    
    def setup_method(self):
        """Setup test client"""
        app.include_router(display_router, prefix="/api")
        self.client = TestClient(app)
    
    def test_play_video_with_valid_id_returns_200(self):
        """
        POST /api/display/play with valid video_id should return 200
        Expected to FAIL: endpoint doesn't exist yet
        """
        request_data = {
            "video_id": "sample-video-123",  # Use existing sample video
            "loop_enabled": False,
            "start_position": 0
        }
        
        response = self.client.post("/api/display/play", json=request_data)
        
        assert response.status_code == 200
        session_data = response.json()
        
        # Contract: Response must include DisplaySession fields
        assert "id" in session_data
        assert "video_id" in session_data
        assert "playback_status" in session_data
        assert "start_time" in session_data
        
        # Contract: Validate field values
        assert session_data["video_id"] == "sample-video-123"
        assert session_data["playback_status"] == "playing"
    
    def test_play_nonexistent_video_returns_404(self):
        """
        POST /api/display/play with invalid video_id should return 404
        Expected to FAIL: endpoint doesn't exist yet
        """
        request_data = {
            "video_id": "nonexistent-video-id"
        }
        
        response = self.client.post("/api/display/play", json=request_data)
        
        assert response.status_code == 404
        error_data = response.json()
        
        # Contract: Error response format
        assert "error" in error_data
        assert "message" in error_data