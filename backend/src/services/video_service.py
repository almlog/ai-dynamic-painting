"""
VideoService - Phase 1 手動動画管理システム
T030: Minimal CRUD implementation to pass tests
"""
import uuid
from datetime import datetime
from typing import List, Optional
from src.models.video import Video, VideoCreate


class VideoService:
    """
    Video service for basic CRUD operations
    Minimal implementation to satisfy TDD tests
    """
    
    def __init__(self):
        # In-memory storage for minimal implementation
        # Real database integration will come later
        self._videos: dict[str, Video] = {}
        self._init_sample_data()
    
    def _init_sample_data(self) -> None:
        """Initialize with sample data for testing"""
        sample_video = Video(
            id="sample-video-123",
            title="Sample Test Video",
            file_path="/tmp/sample.mp4",
            file_size=1024000,
            duration=120.5,
            format="mp4",
            resolution="1920x1080",
            upload_timestamp=datetime.now(),
            status="active",
            play_count=0
        )
        self._videos[sample_video.id] = sample_video
    
    def get_all_videos(self, status: Optional[str] = None, limit: int = 20) -> List[Video]:
        """
        Get all videos with optional filtering
        Minimal implementation to pass contract tests
        """
        videos = list(self._videos.values())
        
        # Filter by status if provided
        if status:
            videos = [v for v in videos if v.status == status]
        
        # Apply limit
        return videos[:limit]
    
    def get_video_by_id(self, video_id: str) -> Optional[Video]:
        """
        Get video by ID
        Minimal implementation to pass tests
        """
        return self._videos.get(video_id)
    
    def create_video(self, video_data: VideoCreate) -> Video:
        """
        Create new video record
        Minimal implementation to pass upload tests
        """
        video_id = str(uuid.uuid4())
        
        video = Video(
            id=video_id,
            title=video_data.title,
            file_path=video_data.file_path,
            file_size=video_data.file_size,
            duration=video_data.duration,
            format=video_data.format,
            resolution=video_data.resolution,
            upload_timestamp=datetime.now(),
            status=video_data.status  # Use status from video_data
        )
        
        self._videos[video_id] = video
        return video
    
    def delete_video(self, video_id: str) -> bool:
        """
        Delete video by ID
        Minimal implementation to pass tests
        """
        if video_id in self._videos:
            del self._videos[video_id]
            return True
        return False
    
    def get_video_count(self) -> int:
        """Get total video count for API responses"""
        return len(self._videos)