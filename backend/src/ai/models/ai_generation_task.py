"""AI Generation Task model for Phase 2 video generation."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import json
import uuid

Base = declarative_base()


class GenerationStatus(Enum):
    """Enumeration for AI generation task statuses"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AIGenerationTask:
    """Simple AIGenerationTask class for contract test compatibility"""
    
    def __init__(self, task_id=None, user_id=None, prompt_text=None, 
                 generation_status=None, creation_time=None, completion_time=None,
                 video_output_path=None, generation_params=None, error_message=None,
                 retry_count=0, priority_level=5, estimated_duration=None):
        
        # Allow default constructor for testing, but provide defaults
        if task_id is None and user_id is None:
            # Default values for testing
            user_id = "default_user"
            
        self.task_id = task_id or f"task_{uuid.uuid4().hex[:8]}"
        self.user_id = user_id
        self.prompt_text = prompt_text or ""
        self.generation_status = generation_status or GenerationStatus.PENDING
        self.creation_time = creation_time or datetime.now()
        self.completion_time = completion_time
        self.video_output_path = video_output_path
        self.generation_params = generation_params or {}
        self.error_message = error_message
        self.retry_count = retry_count
        self.priority_level = max(1, min(10, priority_level))  # Clamp to 1-10
        self.estimated_duration = estimated_duration
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'task_id': self.task_id,
            'user_id': self.user_id,
            'prompt_text': self.prompt_text,
            'generation_status': self.generation_status.value if isinstance(self.generation_status, GenerationStatus) else str(self.generation_status),
            'creation_time': self.creation_time.isoformat() if self.creation_time else None,
            'completion_time': self.completion_time.isoformat() if self.completion_time else None,
            'video_output_path': self.video_output_path,
            'generation_params': self.generation_params,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'priority_level': self.priority_level,
            'estimated_duration': self.estimated_duration
        }


class AIGenerationTaskDB(Base):
    """SQLAlchemy model for AI generation tasks."""
    
    __tablename__ = "ai_generation_tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, unique=True, nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending, processing, completed, failed
    scheduled_time = Column(DateTime, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=True)
    generation_params = Column(Text, nullable=True)  # JSON string
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    api_cost_usd = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to videos table
    # video = relationship("Video", back_populates="ai_generation_task")


class AIGenerationTaskCreate(BaseModel):
    """Pydantic model for creating AI generation tasks."""
    
    prompt: str = Field(..., min_length=1, max_length=1000, description="Generation prompt")
    scheduled_time: datetime = Field(..., description="When to execute the generation")
    generation_params: Optional[Dict[str, Any]] = Field(None, description="Additional generation parameters")
    priority: Optional[str] = Field("normal", description="Task priority")
    context: Optional[Dict[str, Any]] = Field(None, description="Context data for generation")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AIGenerationTaskUpdate(BaseModel):
    """Pydantic model for updating AI generation tasks."""
    
    status: Optional[str] = Field(None, pattern="^(pending|processing|completed|failed)$")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    video_id: Optional[int] = None
    error_message: Optional[str] = None
    retry_count: Optional[int] = None
    api_cost_usd: Optional[float] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AIGenerationTaskResponse(BaseModel):
    """Pydantic model for AI generation task responses."""
    
    id: int
    task_id: str
    prompt: str
    status: str
    scheduled_time: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    video_id: Optional[int] = None
    generation_params: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    api_cost_usd: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    # Calculated properties
    duration_seconds: Optional[float] = None
    is_completed: bool = False
    is_failed: bool = False
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def from_db(cls, db_task: AIGenerationTaskDB) -> "AIGenerationTaskResponse":
        """Create response model from database model."""
        
        # Parse generation params if present
        generation_params = None
        if db_task.generation_params:
            try:
                generation_params = json.loads(db_task.generation_params)
            except json.JSONDecodeError:
                generation_params = None
        
        # Calculate duration if task is completed
        duration_seconds = None
        if db_task.started_at and db_task.completed_at:
            duration_seconds = (db_task.completed_at - db_task.started_at).total_seconds()
        
        return cls(
            id=db_task.id,
            task_id=db_task.task_id,
            prompt=db_task.prompt,
            status=db_task.status,
            scheduled_time=db_task.scheduled_time,
            started_at=db_task.started_at,
            completed_at=db_task.completed_at,
            video_id=db_task.video_id,
            generation_params=generation_params,
            error_message=db_task.error_message,
            retry_count=db_task.retry_count,
            api_cost_usd=db_task.api_cost_usd,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at,
            duration_seconds=duration_seconds,
            is_completed=(db_task.status == "completed"),
            is_failed=(db_task.status == "failed")
        )


class AIGenerationTaskStats(BaseModel):
    """Statistics for AI generation tasks."""
    
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    pending_tasks: int = 0
    processing_tasks: int = 0
    
    success_rate: float = 0.0
    average_duration_seconds: Optional[float] = None
    total_cost_usd: float = 0.0
    
    class Config:
        json_encoders = {
            float: lambda v: round(v, 4)
        }