"""Generated Video model for AI-created videos."""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
import json
import uuid

Base = declarative_base()


class VideoQuality(Enum):
    """Enumeration for video quality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


class VideoFormat(Enum):
    """Enumeration for video formats"""
    MP4 = "mp4"
    WEBM = "webm"
    AVI = "avi"
    MOV = "mov"


class GeneratedVideo:
    """Simple GeneratedVideo class for contract test compatibility"""
    
    def __init__(self, video_id=None, generation_task_id=None, file_path=None,
                 file_size_bytes=0, duration_seconds=0.0, resolution_width=1920,
                 resolution_height=1080, format=VideoFormat.MP4, creation_time=None,
                 quality_score=0.0, metadata=None, thumbnail_path=None,
                 is_processed=False, processing_time_seconds=None):
        
        # Allow default constructor for testing
        if video_id is None and generation_task_id is None:
            generation_task_id = "default_task"
            
        self.video_id = video_id or f"video_{uuid.uuid4().hex[:8]}"
        self.generation_task_id = generation_task_id
        self.file_path = file_path or "/default/path.mp4"
        self.file_size_bytes = file_size_bytes
        self.duration_seconds = duration_seconds
        self.resolution_width = resolution_width
        self.resolution_height = resolution_height
        self.format = format
        self.creation_time = creation_time or datetime.now()
        self.quality_score = max(0.0, min(1.0, quality_score))  # Clamp to 0.0-1.0
        self.metadata = metadata or {}
        self.thumbnail_path = thumbnail_path
        self.is_processed = is_processed
        self.processing_time_seconds = processing_time_seconds
    
    @property
    def file_size_mb(self):
        """File size in megabytes"""
        return self.file_size_bytes / (1024 * 1024)
    
    @property
    def is_hd(self):
        """Check if video is HD (1920x1080 or higher)"""
        return self.resolution_width >= 1920 and self.resolution_height >= 1080
    
    @property
    def aspect_ratio(self):
        """Calculate aspect ratio"""
        if self.resolution_height == 0:
            return 0.0
        return self.resolution_width / self.resolution_height
    
    def add_metadata(self, key, value):
        """Add metadata key-value pair"""
        self.metadata[key] = value
    
    def get_metadata(self, key):
        """Get metadata value by key"""
        return self.metadata.get(key)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'video_id': self.video_id,
            'generation_task_id': self.generation_task_id,
            'file_path': self.file_path,
            'file_size_bytes': self.file_size_bytes,
            'duration_seconds': self.duration_seconds,
            'resolution_width': self.resolution_width,
            'resolution_height': self.resolution_height,
            'format': self.format.value if isinstance(self.format, VideoFormat) else str(self.format),
            'creation_time': self.creation_time.isoformat() if self.creation_time else None,
            'quality_score': self.quality_score,
            'metadata': self.metadata,
            'thumbnail_path': self.thumbnail_path,
            'is_processed': self.is_processed,
            'processing_time_seconds': self.processing_time_seconds,
            'file_size_mb': self.file_size_mb,
            'is_hd': self.is_hd,
            'aspect_ratio': self.aspect_ratio
        }


class GeneratedVideoDB(Base):
    """SQLAlchemy model for AI-generated videos."""
    
    __tablename__ = "generated_videos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    generation_task_id = Column(Integer, ForeignKey("ai_generation_tasks.id"), nullable=False)
    
    # VEO API specific fields
    veo_video_id = Column(String, nullable=True, unique=True)
    veo_status = Column(String, nullable=True)  # VEO API status
    
    # Generation metadata
    prompt_used = Column(Text, nullable=False)
    context_data = Column(Text, nullable=True)  # JSON string
    generation_params = Column(Text, nullable=True)  # JSON string
    
    # Quality metrics
    quality_score = Column(Float, nullable=True)
    user_rating = Column(Float, nullable=True)
    
    # Processing info
    generation_duration_seconds = Column(Float, nullable=True)
    processing_cost_usd = Column(Float, nullable=True)
    
    # File information
    video_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    resolution = Column(String, nullable=True)  # e.g., "1920x1080"
    fps = Column(Integer, nullable=True)
    
    # Status flags
    is_downloaded = Column(Boolean, default=False)
    is_processed = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # video = relationship("Video", back_populates="generated_video")
    # generation_task = relationship("AIGenerationTaskDB", back_populates="generated_video")


class GeneratedVideoCreate(BaseModel):
    """Pydantic model for creating generated video records."""
    
    video_id: int = Field(..., description="Associated video ID")
    generation_task_id: int = Field(..., description="Generation task ID")
    veo_video_id: Optional[str] = Field(None, description="VEO API video ID")
    prompt_used: str = Field(..., min_length=1, description="Prompt used for generation")
    context_data: Optional[Dict[str, Any]] = Field(None, description="Context data used")
    generation_params: Optional[Dict[str, Any]] = Field(None, description="Generation parameters")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GeneratedVideoUpdate(BaseModel):
    """Pydantic model for updating generated video records."""
    
    veo_status: Optional[str] = None
    quality_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    user_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    generation_duration_seconds: Optional[float] = None
    processing_cost_usd: Optional[float] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None
    resolution: Optional[str] = None
    fps: Optional[int] = None
    is_downloaded: Optional[bool] = None
    is_processed: Optional[bool] = None
    is_available: Optional[bool] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GeneratedVideoResponse(BaseModel):
    """Pydantic model for generated video responses."""
    
    id: int
    video_id: int
    generation_task_id: int
    veo_video_id: Optional[str] = None
    veo_status: Optional[str] = None
    
    prompt_used: str
    context_data: Optional[Dict[str, Any]] = None
    generation_params: Optional[Dict[str, Any]] = None
    
    quality_score: Optional[float] = None
    user_rating: Optional[float] = None
    generation_duration_seconds: Optional[float] = None
    processing_cost_usd: Optional[float] = None
    
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None
    resolution: Optional[str] = None
    fps: Optional[int] = None
    
    is_downloaded: bool = False
    is_processed: bool = False
    is_available: bool = True
    
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    cost_per_second: Optional[float] = None
    quality_category: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def from_db(cls, db_video: GeneratedVideoDB) -> "GeneratedVideoResponse":
        """Create response model from database model."""
        
        # Parse JSON fields
        context_data = None
        if db_video.context_data:
            try:
                context_data = json.loads(db_video.context_data)
            except json.JSONDecodeError:
                context_data = None
        
        generation_params = None
        if db_video.generation_params:
            try:
                generation_params = json.loads(db_video.generation_params)
            except json.JSONDecodeError:
                generation_params = None
        
        # Calculate cost per second
        cost_per_second = None
        if db_video.processing_cost_usd and db_video.duration_seconds:
            cost_per_second = db_video.processing_cost_usd / db_video.duration_seconds
        
        # Determine quality category
        quality_category = None
        if db_video.quality_score is not None:
            if db_video.quality_score >= 8.0:
                quality_category = "excellent"
            elif db_video.quality_score >= 6.0:
                quality_category = "good"
            elif db_video.quality_score >= 4.0:
                quality_category = "fair"
            else:
                quality_category = "poor"
        
        return cls(
            id=db_video.id,
            video_id=db_video.video_id,
            generation_task_id=db_video.generation_task_id,
            veo_video_id=db_video.veo_video_id,
            veo_status=db_video.veo_status,
            prompt_used=db_video.prompt_used,
            context_data=context_data,
            generation_params=generation_params,
            quality_score=db_video.quality_score,
            user_rating=db_video.user_rating,
            generation_duration_seconds=db_video.generation_duration_seconds,
            processing_cost_usd=db_video.processing_cost_usd,
            video_url=db_video.video_url,
            thumbnail_url=db_video.thumbnail_url,
            file_size_bytes=db_video.file_size_bytes,
            duration_seconds=db_video.duration_seconds,
            resolution=db_video.resolution,
            fps=db_video.fps,
            is_downloaded=db_video.is_downloaded,
            is_processed=db_video.is_processed,
            is_available=db_video.is_available,
            created_at=db_video.created_at,
            updated_at=db_video.updated_at,
            cost_per_second=cost_per_second,
            quality_category=quality_category
        )


class GeneratedVideoStats(BaseModel):
    """Statistics for generated videos."""
    
    total_videos: int = 0
    total_duration_seconds: float = 0.0
    total_cost_usd: float = 0.0
    average_quality_score: Optional[float] = None
    average_user_rating: Optional[float] = None
    average_generation_time: Optional[float] = None
    
    # Quality distribution
    excellent_count: int = 0  # 8.0+
    good_count: int = 0       # 6.0-7.9
    fair_count: int = 0       # 4.0-5.9
    poor_count: int = 0       # <4.0
    
    # Status distribution
    available_count: int = 0
    processed_count: int = 0
    downloaded_count: int = 0
    
    class Config:
        json_encoders = {
            float: lambda v: round(v, 4)
        }