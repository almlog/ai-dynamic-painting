"""
Integration test for video upload flow
T017: This test MUST FAIL initially (TDD Red phase)
"""
import pytest
import io
from fastapi.testclient import TestClient

# These imports will FAIL because the services don't exist yet
from src.services.video_service import VideoService
from src.models.video import Video
from src.main import app


class TestVideoUploadIntegration:
    """Integration tests for complete video upload flow"""
    
    def setup_method(self):
        """Setup test environment"""
        self.client = TestClient(app)
        self.video_service = VideoService()
    
    def test_complete_video_upload_flow(self):
        """
        Test complete flow: Upload → Store → Retrieve
        Expected to FAIL: services/models don't exist yet
        """
        # Step 1: Upload video via API
        mock_video_content = b"fake_mp4_content_for_integration_test"
        files = {
            "file": ("integration_test.mp4", io.BytesIO(mock_video_content), "video/mp4")
        }
        data = {
            "title": "Integration Test Video"
        }
        
        # This will fail because the endpoint doesn't exist
        upload_response = self.client.post("/api/videos", files=files, data=data)
        assert upload_response.status_code == 201
        
        uploaded_video = upload_response.json()
        video_id = uploaded_video["id"]
        
        # Step 2: Verify video is stored in database
        stored_video = self.video_service.get_video_by_id(video_id)
        assert stored_video is not None
        assert stored_video.title == "Integration Test Video"
        assert stored_video.status == "processing"
        
        # Step 3: Retrieve video via API
        get_response = self.client.get(f"/api/videos/{video_id}")
        assert get_response.status_code == 200
        
        retrieved_video = get_response.json()
        assert retrieved_video["id"] == video_id
        assert retrieved_video["title"] == "Integration Test Video"
    
    def test_video_upload_with_processing(self):
        """
        Test video upload triggers processing pipeline
        Expected to FAIL: processing pipeline doesn't exist yet
        """
        mock_video_content = b"fake_mp4_for_processing_test"
        files = {
            "file": ("processing_test.mp4", io.BytesIO(mock_video_content), "video/mp4")
        }
        
        # Upload video
        response = self.client.post("/api/videos", files=files)
        assert response.status_code == 201
        
        video_data = response.json()
        video_id = video_data["id"]
        
        # Verify processing was triggered
        # (This would normally involve checking background tasks)
        video = self.video_service.get_video_by_id(video_id)
        assert video.status in ["processing", "active"]