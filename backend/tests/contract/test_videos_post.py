"""
Contract test for POST /api/videos endpoint (video upload)
T010: This test MUST FAIL initially (TDD Red phase)
"""
import pytest
import io
from httpx import AsyncClient
from fastapi.testclient import TestClient

# This import will FAIL because the endpoint doesn't exist yet
# This is CORRECT for TDD Red phase
from src.api.routes.videos import router as videos_router
from src.main import app


class TestVideosPostContract:
    """Contract tests for POST /api/videos endpoint"""
    
    def setup_method(self):
        """Setup test client"""
        app.include_router(videos_router, prefix="/api")
        self.client = TestClient(app)
    
    def test_post_video_upload_returns_201_with_valid_schema(self):
        """
        POST /api/videos with valid MP4 file should return 201
        Expected to FAIL: endpoint doesn't exist yet
        """
        # Create mock MP4 file content
        mock_video_content = b"fake_mp4_content_for_testing"
        files = {
            "file": ("test_video.mp4", io.BytesIO(mock_video_content), "video/mp4")
        }
        data = {
            "title": "Test Video Upload"
        }
        
        response = self.client.post("/api/videos", files=files, data=data)
        
        assert response.status_code == 201
        video_data = response.json()
        
        # Contract: Response must include video object with required fields
        assert "id" in video_data
        assert "title" in video_data
        assert "file_path" in video_data
        assert "file_size" in video_data
        assert "status" in video_data
        assert "upload_timestamp" in video_data
        
        # Contract: Validate field types and values
        assert isinstance(video_data["id"], str)
        assert video_data["title"] == "Test Video Upload"
        assert video_data["status"] == "processing"
        assert isinstance(video_data["file_size"], int)
    
    def test_post_video_without_file_returns_400(self):
        """
        POST /api/videos without file should return 400
        Expected to FAIL: endpoint doesn't exist yet
        """
        data = {"title": "Test Video Without File"}
        
        response = self.client.post("/api/videos", data=data)
        
        assert response.status_code == 400
        error_data = response.json()
        
        # Contract: Error response must have 'error' and 'message' fields
        assert "error" in error_data
        assert "message" in error_data
        assert "file" in error_data["message"].lower()
    
    def test_post_video_large_file_returns_413(self):
        """
        POST /api/videos with file >500MB should return 413
        Expected to FAIL: endpoint doesn't exist yet
        """
        # Create mock large file content (simulate 500MB+ file)
        large_file_content = b"x" * (500 * 1024 * 1024 + 1)  # 500MB + 1 byte
        files = {
            "file": ("large_video.mp4", io.BytesIO(large_file_content), "video/mp4")
        }
        data = {
            "title": "Large Test Video"
        }
        
        response = self.client.post("/api/videos", files=files, data=data)
        
        assert response.status_code == 413
        error_data = response.json()
        
        # Contract: File too large error response
        assert "error" in error_data
        assert "size" in error_data["message"].lower()
    
    def test_post_video_invalid_format_returns_400(self):
        """
        POST /api/videos with non-MP4 file should return 400
        Expected to FAIL: endpoint doesn't exist yet
        """
        # Create mock invalid file content
        invalid_file_content = b"not_a_video_file_content"
        files = {
            "file": ("invalid.txt", io.BytesIO(invalid_file_content), "text/plain")
        }
        data = {
            "title": "Invalid File Format"
        }
        
        response = self.client.post("/api/videos", files=files, data=data)
        
        assert response.status_code == 400
        error_data = response.json()
        
        # Contract: Invalid format error response
        assert "error" in error_data
        assert "format" in error_data["message"].lower()
    
    def test_post_video_missing_title_uses_filename(self):
        """
        POST /api/videos without title should use filename
        Expected to FAIL: endpoint doesn't exist yet
        """
        mock_video_content = b"fake_mp4_content"
        files = {
            "file": ("auto_title_video.mp4", io.BytesIO(mock_video_content), "video/mp4")
        }
        # No title provided
        
        response = self.client.post("/api/videos", files=files)
        
        assert response.status_code == 201
        video_data = response.json()
        
        # Contract: Should use filename as title when title not provided
        assert "auto_title_video" in video_data["title"]