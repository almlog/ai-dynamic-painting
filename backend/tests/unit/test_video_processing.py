"""
Unit tests for video processing - T058
Phase 1 手動動画管理システム - 動画処理ユニットテスト
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os
from pathlib import Path
import hashlib
from src.services.video_service import VideoService, VideoProcessingError
from src.models.video import Video


@pytest.fixture
def video_service():
    """Video service fixture"""
    return VideoService()


@pytest.fixture
def sample_video_data():
    """Sample video data for testing"""
    return {
        'id': 'test-video-123',
        'title': 'Test Video',
        'file_path': '/uploads/test_video.mp4',
        'file_size': 1024 * 1024,  # 1MB
        'duration': 120.5,
        'format': 'mp4',
        'upload_timestamp': '2025-09-12T10:00:00Z',
        'status': 'active'
    }


class TestVideoProcessing:
    """Video processing unit tests"""

    def test_video_file_validation(self, video_service):
        """Test video file validation logic"""
        # Valid video files
        valid_files = [
            ('video.mp4', 'video/mp4'),
            ('movie.avi', 'video/x-msvideo'),
            ('clip.mov', 'video/quicktime'),
            ('film.mkv', 'video/x-matroska')
        ]
        
        for filename, mime_type in valid_files:
            assert video_service.validate_file_type(filename, mime_type) == True
        
        # Invalid video files
        invalid_files = [
            ('document.pdf', 'application/pdf'),
            ('image.jpg', 'image/jpeg'),
            ('audio.mp3', 'audio/mpeg'),
            ('script.py', 'text/plain')
        ]
        
        for filename, mime_type in invalid_files:
            assert video_service.validate_file_type(filename, mime_type) == False

    def test_video_file_size_validation(self, video_service):
        """Test video file size validation"""
        # Valid sizes (under 500MB)
        valid_sizes = [
            1024,  # 1KB
            1024 * 1024,  # 1MB
            100 * 1024 * 1024,  # 100MB
            499 * 1024 * 1024  # 499MB
        ]
        
        for size in valid_sizes:
            assert video_service.validate_file_size(size) == True
        
        # Invalid sizes (over 500MB)
        invalid_sizes = [
            501 * 1024 * 1024,  # 501MB
            1024 * 1024 * 1024,  # 1GB
            2 * 1024 * 1024 * 1024  # 2GB
        ]
        
        for size in invalid_sizes:
            assert video_service.validate_file_size(size) == False

    @patch('src.services.video_service.cv2')
    def test_video_metadata_extraction(self, mock_cv2, video_service):
        """Test video metadata extraction"""
        # Mock OpenCV video capture
        mock_cap = MagicMock()
        mock_cap.get.side_effect = lambda prop: {
            mock_cv2.CAP_PROP_FRAME_COUNT: 3000,  # 3000 frames
            mock_cv2.CAP_PROP_FPS: 25.0,  # 25 FPS
            mock_cv2.CAP_PROP_FRAME_WIDTH: 1920,
            mock_cv2.CAP_PROP_FRAME_HEIGHT: 1080
        }.get(prop, 0)
        mock_cap.isOpened.return_value = True
        mock_cv2.VideoCapture.return_value = mock_cap
        
        # Test metadata extraction
        metadata = video_service.extract_metadata('/test/video.mp4')
        
        assert metadata['duration'] == 120.0  # 3000 frames / 25 FPS
        assert metadata['fps'] == 25.0
        assert metadata['resolution'] == '1920x1080'
        assert metadata['width'] == 1920
        assert metadata['height'] == 1080

    @patch('src.services.video_service.cv2')
    def test_video_thumbnail_generation(self, mock_cv2, video_service):
        """Test video thumbnail generation"""
        # Mock video capture for thumbnail
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, MagicMock())  # Success, mock frame
        mock_cv2.VideoCapture.return_value = mock_cap
        mock_cv2.imwrite.return_value = True
        
        # Generate thumbnail
        thumbnail_path = video_service.generate_thumbnail('/test/video.mp4', '/test/thumb.jpg')
        
        assert thumbnail_path == '/test/thumb.jpg'
        mock_cv2.imwrite.assert_called_once()
        mock_cap.set.assert_called()  # Should set frame position

    def test_video_file_hash_calculation(self, video_service):
        """Test video file hash calculation for deduplication"""
        # Create temporary test file
        test_content = b"fake video content for testing"
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            # Calculate hash
            file_hash = video_service.calculate_file_hash(temp_file_path)
            
            # Verify hash is correct SHA-256
            expected_hash = hashlib.sha256(test_content).hexdigest()
            assert file_hash == expected_hash
            
        finally:
            # Cleanup
            os.unlink(temp_file_path)

    @patch('src.services.video_service.os.path.exists')
    def test_duplicate_video_detection(self, mock_exists, video_service):
        """Test duplicate video detection by hash"""
        mock_exists.return_value = True
        
        # Mock database to return existing video with same hash
        existing_hash = "abc123def456"
        
        with patch.object(video_service, 'get_video_by_hash') as mock_get:
            mock_get.return_value = {
                'id': 'existing-video',
                'title': 'Existing Video',
                'file_hash': existing_hash
            }
            
            # Test duplicate detection
            is_duplicate, existing_video = video_service.check_duplicate(existing_hash)
            
            assert is_duplicate == True
            assert existing_video['id'] == 'existing-video'

    def test_video_format_conversion_validation(self, video_service):
        """Test video format conversion validation"""
        # Test supported format conversions
        supported_conversions = [
            ('mp4', 'avi'),
            ('avi', 'mp4'),
            ('mov', 'mp4'),
            ('mkv', 'mp4')
        ]
        
        for source, target in supported_conversions:
            assert video_service.is_conversion_supported(source, target) == True
        
        # Test unsupported conversions
        unsupported_conversions = [
            ('mp4', 'pdf'),
            ('avi', 'jpg'),
            ('unknown', 'mp4')
        ]
        
        for source, target in unsupported_conversions:
            assert video_service.is_conversion_supported(source, target) == False

    def test_video_compression_settings(self, video_service):
        """Test video compression settings calculation"""
        # Test compression for different file sizes
        test_cases = [
            (10 * 1024 * 1024, 'low'),    # 10MB -> low compression
            (100 * 1024 * 1024, 'medium'),  # 100MB -> medium compression
            (400 * 1024 * 1024, 'high')   # 400MB -> high compression
        ]
        
        for file_size, expected_compression in test_cases:
            compression = video_service.get_compression_level(file_size)
            assert compression == expected_compression

    @patch('src.services.video_service.subprocess')
    def test_video_processing_pipeline(self, mock_subprocess, video_service):
        """Test complete video processing pipeline"""
        # Mock subprocess for video processing commands
        mock_subprocess.run.return_value = MagicMock(returncode=0)
        
        # Mock file operations
        with patch('src.services.video_service.os.path.exists', return_value=True), \
             patch.object(video_service, 'extract_metadata') as mock_metadata, \
             patch.object(video_service, 'generate_thumbnail') as mock_thumbnail:
            
            mock_metadata.return_value = {
                'duration': 120.0,
                'fps': 25.0,
                'resolution': '1920x1080'
            }
            mock_thumbnail.return_value = '/test/thumbnail.jpg'
            
            # Process video
            result = video_service.process_video('/test/input.mp4', '/test/output.mp4')
            
            assert result['status'] == 'success'
            assert result['metadata']['duration'] == 120.0
            assert result['thumbnail_path'] == '/test/thumbnail.jpg'

    def test_video_processing_error_handling(self, video_service):
        """Test video processing error handling"""
        # Test file not found error
        with pytest.raises(VideoProcessingError) as exc_info:
            video_service.process_nonexistent_file('/nonexistent/video.mp4')
        
        assert "not found" in str(exc_info.value).lower()

    @patch('src.services.video_service.cv2')
    def test_video_frame_extraction(self, mock_cv2, video_service):
        """Test extracting specific frames from video"""
        # Mock video capture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            mock_cv2.CAP_PROP_FRAME_COUNT: 1000,
            mock_cv2.CAP_PROP_FPS: 25.0
        }.get(prop, 0)
        
        # Mock frame reading
        mock_frame = MagicMock()
        mock_cap.read.return_value = (True, mock_frame)
        mock_cv2.VideoCapture.return_value = mock_cap
        mock_cv2.imwrite.return_value = True
        
        # Extract frame at 30 seconds
        frame_path = video_service.extract_frame('/test/video.mp4', 30.0, '/test/frame.jpg')
        
        assert frame_path == '/test/frame.jpg'
        # Should set frame position to 30 * 25 = 750th frame
        mock_cap.set.assert_called_with(mock_cv2.CAP_PROP_POS_FRAMES, 750)

    def test_video_duration_validation(self, video_service):
        """Test video duration validation"""
        # Valid durations (5 seconds to 30 minutes)
        valid_durations = [5.0, 60.0, 300.0, 1800.0]  # 5s, 1min, 5min, 30min
        
        for duration in valid_durations:
            assert video_service.validate_duration(duration) == True
        
        # Invalid durations
        invalid_durations = [2.0, 2000.0, -5.0]  # Too short, too long, negative
        
        for duration in invalid_durations:
            assert video_service.validate_duration(duration) == False

    def test_video_quality_assessment(self, video_service):
        """Test video quality assessment"""
        # Test different resolution quality ratings
        quality_tests = [
            ((1920, 1080), 'HD'),
            ((1280, 720), 'HD'),
            ((640, 480), 'SD'),
            ((3840, 2160), '4K')
        ]
        
        for (width, height), expected_quality in quality_tests:
            quality = video_service.assess_quality(width, height)
            assert quality == expected_quality

    def test_video_batch_processing(self, video_service):
        """Test processing multiple videos in batch"""
        video_files = [
            '/test/video1.mp4',
            '/test/video2.avi',
            '/test/video3.mov'
        ]
        
        with patch.object(video_service, 'process_video') as mock_process:
            mock_process.return_value = {'status': 'success'}
            
            # Process batch
            results = video_service.process_batch(video_files)
            
            assert len(results) == 3
            assert all(result['status'] == 'success' for result in results)
            assert mock_process.call_count == 3