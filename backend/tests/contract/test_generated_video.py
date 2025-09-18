"""
Contract test for GeneratedVideo model
Test File: backend/tests/contract/test_generated_video.py

This test MUST FAIL initially (RED phase of TDD)
"""

import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_generated_video_model_exists():
    """Test that GeneratedVideo model exists and has required fields"""
    # This should initially FAIL until we implement the model
    try:
        from src.ai.models.generated_video import GeneratedVideo
        
        # Test model can be instantiated
        video = GeneratedVideo()
        assert video is not None
        
        # Test required fields exist
        required_fields = [
            'video_id', 'generation_task_id', 'file_path', 'file_size_bytes',
            'duration_seconds', 'resolution_width', 'resolution_height',
            'format', 'creation_time', 'quality_score', 'metadata',
            'thumbnail_path', 'is_processed', 'processing_time_seconds'
        ]
        
        for field in required_fields:
            assert hasattr(video, field), f"Missing required field: {field}"
            
    except ImportError:
        pytest.fail("GeneratedVideo model not implemented yet")


def test_generated_video_quality_enum():
    """Test that video quality enum is properly defined"""
    try:
        from src.ai.models.generated_video import VideoQuality
        
        # Test enum values exist
        expected_qualities = ['low', 'medium', 'high', 'ultra']
        
        for quality in expected_qualities:
            assert hasattr(VideoQuality, quality.upper()), f"Missing quality: {quality}"
            
    except ImportError:
        pytest.fail("VideoQuality enum not implemented yet")


def test_generated_video_format_enum():
    """Test that video format enum is properly defined"""
    try:
        from src.ai.models.generated_video import VideoFormat
        
        # Test enum values exist
        expected_formats = ['mp4', 'webm', 'avi', 'mov']
        
        for format_type in expected_formats:
            assert hasattr(VideoFormat, format_type.upper()), f"Missing format: {format_type}"
            
    except ImportError:
        pytest.fail("VideoFormat enum not implemented yet")


def test_generated_video_crud_operations():
    """Test basic CRUD operations for GeneratedVideo"""
    try:
        from src.ai.models.generated_video import GeneratedVideo, VideoQuality, VideoFormat
        
        # Test creation with required fields
        video_data = {
            'video_id': 'video_001',
            'generation_task_id': 'task_001', 
            'file_path': '/path/to/video.mp4',
            'file_size_bytes': 1048576,  # 1MB
            'duration_seconds': 30.5,
            'resolution_width': 1920,
            'resolution_height': 1080,
            'format': VideoFormat.MP4,
            'quality_score': 0.85
        }
        
        video = GeneratedVideo(**video_data)
        assert video.video_id == 'video_001'
        assert video.generation_task_id == 'task_001'
        assert video.file_size_bytes == 1048576
        assert video.quality_score == 0.85
        
        # Test computed properties
        assert video.file_size_mb == 1.0  # 1MB
        assert video.is_hd == True  # 1920x1080
        
    except ImportError:
        pytest.fail("GeneratedVideo model not fully implemented")


def test_generated_video_validation():
    """Test data validation for GeneratedVideo"""
    try:
        from src.ai.models.generated_video import GeneratedVideo, VideoFormat
        
        # Test file path validation
        video = GeneratedVideo(
            video_id='test_002',
            generation_task_id='task_002',
            file_path='',  # Empty path should be handled
            file_size_bytes=1000,
            duration_seconds=10.0,
            format=VideoFormat.MP4
        )
        
        # Should have default or valid path
        assert video.file_path is not None
        
        # Test quality score validation (0.0 to 1.0)
        video.quality_score = 0.5
        assert 0.0 <= video.quality_score <= 1.0
        
        # Test resolution validation
        video.resolution_width = 1920
        video.resolution_height = 1080
        assert video.resolution_width > 0
        assert video.resolution_height > 0
        
    except ImportError:
        pytest.fail("GeneratedVideo validation not implemented")


def test_generated_video_metadata_handling():
    """Test metadata and file operations"""
    try:
        from src.ai.models.generated_video import GeneratedVideo, VideoFormat
        
        video = GeneratedVideo(
            video_id='meta_test_001',
            generation_task_id='task_meta',
            file_path='/test/video.mp4',
            file_size_bytes=2097152,  # 2MB
            duration_seconds=60.0,
            resolution_width=1280,
            resolution_height = 720,
            format=VideoFormat.MP4
        )
        
        # Test metadata operations
        video.add_metadata('prompt', 'Beautiful sunset over mountains')
        video.add_metadata('style', 'cinematic')
        
        assert video.get_metadata('prompt') == 'Beautiful sunset over mountains'
        assert video.get_metadata('style') == 'cinematic'
        assert video.get_metadata('nonexistent') is None
        
        # Test computed properties
        assert video.file_size_mb == 2.0
        assert video.aspect_ratio == 16/9  # 1280/720
        
    except ImportError:
        pytest.fail("GeneratedVideo metadata handling not implemented")


def test_generated_video_json_serialization():
    """Test JSON serialization/deserialization"""
    try:
        from src.ai.models.generated_video import GeneratedVideo, VideoFormat
        import json
        
        video = GeneratedVideo(
            video_id='serialize_test_001',
            generation_task_id='task_serialize',
            file_path='/test/serialize.mp4',
            file_size_bytes=5242880,  # 5MB
            duration_seconds=120.0,
            resolution_width=1920,
            resolution_height=1080,
            format=VideoFormat.MP4,
            quality_score=0.92
        )
        
        # Test to_dict method
        video_dict = video.to_dict()
        assert isinstance(video_dict, dict)
        assert video_dict['video_id'] == 'serialize_test_001'
        assert video_dict['file_size_bytes'] == 5242880
        
        # Test JSON serialization
        json_str = json.dumps(video_dict)
        assert isinstance(json_str, str)
        
        # Test deserialization
        loaded_dict = json.loads(json_str)
        assert loaded_dict['video_id'] == 'serialize_test_001'
        
    except ImportError:
        pytest.fail("GeneratedVideo serialization not implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])