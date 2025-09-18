"""
Video model - Phase 1 手動動画管理システム
T025: Minimal implementation to pass tests
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Video(BaseModel):
    """
    Video entity for Phase 1
    Minimal implementation to satisfy TDD tests
    """
    id: str
    title: str
    file_path: str
    file_size: int
    duration: float
    format: str = "mp4"
    resolution: Optional[str] = None
    thumbnail_path: Optional[str] = None
    upload_timestamp: datetime
    last_played: Optional[datetime] = None
    play_count: int = 0
    status: str = "processing"
    
    class Config:
        # Allow datetime objects to be serialized
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VideoCreate(BaseModel):
    """Video creation model for API requests"""
    title: str
    file_path: str
    file_size: int
    duration: float = 0.0
    format: str = "mp4"
    resolution: Optional[str] = None
    status: str = "processing"


class VideoResponse(BaseModel):
    """Video response model for API responses"""
    id: str
    title: str
    file_path: str
    file_size: int
    duration: float
    format: str
    resolution: Optional[str]
    upload_timestamp: str  # ISO format string
    status: str
    play_count: int