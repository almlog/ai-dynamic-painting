"""
Integration test display control flow - T018
Phase 1 手動動画管理システム - 表示制御フロー統合テスト
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import tempfile
import os
from src.main import app
from src.database.connection import DatabaseConnection, get_database_path


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def test_db():
    """Test database fixture with video data"""
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    # Initialize database
    db_conn = DatabaseConnection(db_path)
    db_conn.create_tables()
    
    # Insert test video
    with db_conn.get_session() as session:
        session.execute(text("""
            INSERT INTO videos (
                id, title, file_path, file_size, duration, format,
                upload_timestamp, status
            ) VALUES (
                'test-video-display',
                'Display Test Video',
                '/test/display_test.mp4',
                1024000,
                120.0,
                'mp4',
                datetime('now'),
                'active'
            )
        """))
        session.commit()
    
    yield db_conn, db_path
    
    # Cleanup
    os.unlink(db_path)


class TestDisplayControlFlow:
    """Display control integration tests"""

    def test_complete_display_flow(self, client, test_db):
        """Test complete display control workflow"""
        db_conn, db_path = test_db
        
        # Mock database path
        with patch('src.database.connection.get_database_path', return_value=db_path):
            # 1. Check initial display status
            response = client.get("/api/display/status")
            assert response.status_code == 200
            status_data = response.json()
            assert status_data["status"] == "stopped"
            assert status_data["current_video_id"] is None

            # 2. Start video playback
            play_response = client.post("/api/display/play", 
                json={"video_id": "test-video-display"})
            assert play_response.status_code == 200
            play_data = play_response.json()
            assert play_data["status"] == "success"
            assert play_data["message"] == "Video playback started"

            # 3. Check status after play
            status_response = client.get("/api/display/status")
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["status"] == "playing"
            assert status_data["current_video_id"] == "test-video-display"

            # 4. Pause video
            pause_response = client.post("/api/display/pause")
            assert pause_response.status_code == 200
            pause_data = pause_response.json()
            assert pause_data["status"] == "success"

            # 5. Check status after pause
            status_response = client.get("/api/display/status")
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["status"] == "paused"

            # 6. Resume video
            resume_response = client.post("/api/display/resume")
            assert resume_response.status_code == 200
            resume_data = resume_response.json()
            assert resume_data["status"] == "success"

            # 7. Check status after resume
            status_response = client.get("/api/display/status")
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["status"] == "playing"

            # 8. Stop video
            stop_response = client.post("/api/display/stop")
            assert stop_response.status_code == 200
            stop_data = stop_response.json()
            assert stop_data["status"] == "success"

            # 9. Check final status
            final_status = client.get("/api/display/status")
            assert final_status.status_code == 200
            final_data = final_status.json()
            assert final_data["status"] == "stopped"
            assert final_data["current_video_id"] is None

    def test_invalid_video_play(self, client, test_db):
        """Test playing non-existent video"""
        db_conn, db_path = test_db
        
        with patch('src.database.connection.get_database_path', return_value=db_path):
            response = client.post("/api/display/play",
                json={"video_id": "non-existent-video"})
            
            assert response.status_code == 404
            error_data = response.json()
            assert "not found" in error_data["detail"].lower()

    def test_pause_without_playing(self, client):
        """Test pausing when no video is playing"""
        response = client.post("/api/display/pause")
        assert response.status_code == 400
        error_data = response.json()
        assert "no video" in error_data["detail"].lower()

    def test_resume_without_paused(self, client):
        """Test resuming when no video is paused"""
        response = client.post("/api/display/resume")
        assert response.status_code == 400
        error_data = response.json()
        assert "no video" in error_data["detail"].lower()

    def test_concurrent_play_requests(self, client, test_db):
        """Test handling concurrent play requests"""
        db_conn, db_path = test_db
        
        with patch('src.database.connection.get_database_path', return_value=db_path):
            # Start first video
            response1 = client.post("/api/display/play",
                json={"video_id": "test-video-display"})
            assert response1.status_code == 200

            # Try to start second video (should replace first)
            response2 = client.post("/api/display/play", 
                json={"video_id": "test-video-display"})
            assert response2.status_code == 200

            # Check that only one video is playing
            status_response = client.get("/api/display/status")
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["status"] == "playing"
            assert status_data["current_video_id"] == "test-video-display"

    @patch('src.services.display_service.subprocess')
    def test_display_service_integration(self, mock_subprocess, client, test_db):
        """Test integration with display service subprocess calls"""
        db_conn, db_path = test_db
        mock_subprocess.run.return_value = MagicMock(returncode=0)
        
        with patch('src.database.connection.get_database_path', return_value=db_path):
            # Test that display service is called on play
            response = client.post("/api/display/play",
                json={"video_id": "test-video-display"})
            
            assert response.status_code == 200
            # Verify subprocess was called (would be actual video player)
            mock_subprocess.run.assert_called()

    def test_display_status_persistence(self, client, test_db):
        """Test that display status persists across requests"""
        db_conn, db_path = test_db
        
        with patch('src.database.connection.get_database_path', return_value=db_path):
            # Start playback
            client.post("/api/display/play",
                json={"video_id": "test-video-display"})
            
            # Check status multiple times
            for _ in range(3):
                response = client.get("/api/display/status")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "playing"
                assert data["current_video_id"] == "test-video-display"

    def test_error_handling_invalid_json(self, client):
        """Test error handling for invalid JSON requests"""
        # Invalid JSON
        response = client.post("/api/display/play",
            data="invalid json",
            headers={"Content-Type": "application/json"})
        assert response.status_code == 422

    def test_missing_video_id_parameter(self, client):
        """Test error handling for missing video_id parameter"""
        response = client.post("/api/display/play", json={})
        assert response.status_code == 422
        
        error_data = response.json()
        assert "video_id" in str(error_data)

    def test_display_control_response_times(self, client, test_db):
        """Test response times for display control operations"""
        import time
        
        db_conn, db_path = test_db
        
        with patch('src.database.connection.get_database_path', return_value=db_path):
            operations = [
                ("GET", "/api/display/status", None),
                ("POST", "/api/display/play", {"video_id": "test-video-display"}),
                ("POST", "/api/display/pause", None),
                ("POST", "/api/display/resume", None),
                ("POST", "/api/display/stop", None)
            ]
            
            for method, url, json_data in operations:
                start_time = time.time()
                
                if method == "GET":
                    response = client.get(url)
                else:
                    response = client.post(url, json=json_data)
                
                elapsed_time = time.time() - start_time
                
                # All operations should complete within 1 second
                assert elapsed_time < 1.0, f"{method} {url} took {elapsed_time:.2f}s"
                assert response.status_code in [200, 400]  # Allow expected errors