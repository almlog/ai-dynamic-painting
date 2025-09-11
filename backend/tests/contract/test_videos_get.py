"""
Contract test for GET /api/videos endpoint
T009: This test MUST FAIL initially (TDD Red phase)
"""
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

# This import will FAIL because the endpoint doesn't exist yet
# This is CORRECT for TDD Red phase
from src.api.routes.videos import router as videos_router
from src.main import app


class TestVideosGetContract:
    """Contract tests for GET /api/videos endpoint"""
    
    def setup_method(self):
        """Setup test client"""
        app.include_router(videos_router, prefix="/api")
        self.client = TestClient(app)
    
    def test_get_videos_returns_200_with_valid_schema(self):
        """
        GET /api/videos should return 200 with valid video list schema
        Expected to FAIL: endpoint doesn't exist yet
        """
        response = self.client.get("/api/videos")
        
        assert response.status_code == 200
        data = response.json()
        
        # Contract: Response must have 'videos', 'total', 'page' fields
        assert "videos" in data
        assert "total" in data  
        assert "page" in data
        
        # Contract: videos must be a list
        assert isinstance(data["videos"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["page"], int)
    
    def test_get_videos_with_status_filter(self):
        """
        GET /api/videos?status=active should filter by status
        Expected to FAIL: endpoint doesn't exist yet
        """
        response = self.client.get("/api/videos?status=active")
        
        assert response.status_code == 200
        data = response.json()
        
        # Contract: All returned videos should have status='active'
        for video in data["videos"]:
            assert video["status"] == "active"
    
    def test_get_videos_with_limit(self):
        """
        GET /api/videos?limit=5 should limit results
        Expected to FAIL: endpoint doesn't exist yet
        """
        response = self.client.get("/api/videos?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        # Contract: Should respect limit parameter
        assert len(data["videos"]) <= 5
    
    def test_get_videos_invalid_status_returns_400(self):
        """
        GET /api/videos?status=invalid should return 400
        Expected to FAIL: endpoint doesn't exist yet
        """
        response = self.client.get("/api/videos?status=invalid")
        
        assert response.status_code == 400
        data = response.json()
        
        # Contract: Error response must have 'error' and 'message' fields
        assert "error" in data
        assert "message" in data