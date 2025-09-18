"""Interaction Log model for user behavior tracking."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum
import json
import uuid

Base = declarative_base()


class InteractionType(Enum):
    """Enumeration for interaction types"""
    BUTTON_PRESS = "button_press"
    VIDEO_GENERATION = "video_generation"
    PREFERENCE_UPDATE = "preference_update"
    SCHEDULE_CHANGE = "schedule_change"
    API_CALL = "api_call"
    SYSTEM_EVENT = "system_event"


class InteractionLog:
    """Simple InteractionLog class for contract test compatibility"""
    
    def __init__(self, log_id=None, user_id=None, interaction_type=None, 
                 interaction_data=None, timestamp=None, session_id=None, 
                 device_info=None, response_time_ms=0, success=True, 
                 error_message=None, context=None, metadata=None, tags=None):
        
        # Allow default constructor for testing
        if log_id is None and user_id is None:
            user_id = "default_user"
            
        self.log_id = log_id or f"log_{uuid.uuid4().hex[:8]}"
        self.user_id = user_id
        self.interaction_type = interaction_type or InteractionType.SYSTEM_EVENT
        self.interaction_data = interaction_data or {}
        self.timestamp = timestamp or datetime.now()
        self.session_id = session_id or f"session_{uuid.uuid4().hex[:8]}"
        self.device_info = device_info or {}
        self.response_time_ms = max(0, response_time_ms)  # Clamp to non-negative
        self.success = success
        self.error_message = error_message
        self.context = context or {}
        self.metadata = metadata or {}
        self.tags = tags or []
    
    def get_interaction_value(self, key):
        """Get a value from the interaction data"""
        return self.interaction_data.get(key)
    
    def set_interaction_value(self, key, value):
        """Set a value in the interaction data"""
        self.interaction_data[key] = value
    
    def is_same_session(self, session_id):
        """Check if this log belongs to the given session"""
        return self.session_id == session_id
    
    def get_device_type(self):
        """Get the device type from device info"""
        return self.device_info.get('type', 'unknown')
    
    def get_device_info(self, key):
        """Get a specific device info value"""
        return self.device_info.get(key)
    
    def is_fast_response(self, threshold_ms=1000):
        """Check if response time is considered fast"""
        return self.response_time_ms < threshold_ms
    
    def is_slow_response(self, threshold_ms=2000):
        """Check if response time is considered slow"""
        return self.response_time_ms > threshold_ms
    
    def mark_successful(self, response_time_ms=None):
        """Mark this interaction as successful"""
        self.success = True
        self.error_message = None
        if response_time_ms is not None:
            self.response_time_ms = max(0, response_time_ms)
    
    def mark_failed(self, error_message, response_time_ms=None):
        """Mark this interaction as failed"""
        self.success = False
        self.error_message = error_message
        if response_time_ms is not None:
            self.response_time_ms = max(0, response_time_ms)
    
    def get_context_value(self, key):
        """Get a value from the context"""
        return self.context.get(key)
    
    def set_context_value(self, key, value):
        """Set a value in the context"""
        self.context[key] = value
    
    def get_metadata_value(self, key):
        """Get a value from the metadata"""
        return self.metadata.get(key)
    
    def set_metadata_value(self, key, value):
        """Set a value in the metadata"""
        self.metadata[key] = value
    
    def add_tag(self, tag):
        """Add a tag to this log entry"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    @staticmethod
    def calculate_success_rate(logs):
        """Calculate success rate for a list of logs"""
        if not logs:
            return 0.0
        
        successful_count = sum(1 for log in logs if log.success)
        return successful_count / len(logs)
    
    @staticmethod
    def calculate_average_response_time(logs):
        """Calculate average response time for a list of logs"""
        if not logs:
            return 0.0
        
        total_time = sum(log.response_time_ms for log in logs)
        return total_time / len(logs)
    
    @staticmethod
    def filter_successful(logs):
        """Filter logs to only successful ones"""
        return [log for log in logs if log.success]
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'interaction_type': self.interaction_type.value if isinstance(self.interaction_type, InteractionType) else str(self.interaction_type),
            'interaction_data': self.interaction_data,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'session_id': self.session_id,
            'device_info': self.device_info,
            'response_time_ms': self.response_time_ms,
            'success': self.success,
            'error_message': self.error_message,
            'context': self.context,
            'metadata': self.metadata,
            'tags': self.tags
        }


class InteractionLogDB(Base):
    """SQLAlchemy model for interaction logs."""
    
    __tablename__ = "interaction_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    log_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Interaction details
    interaction_type = Column(String, nullable=False)  # button_press, video_generation, etc.
    interaction_data = Column(Text, nullable=True)  # JSON object
    
    # Timing and session
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    session_id = Column(String, nullable=False, index=True)
    device_info = Column(Text, nullable=True)  # JSON object
    
    # Performance metrics
    response_time_ms = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    # Context and metadata
    context = Column(Text, nullable=True)  # JSON object
    log_metadata = Column(Text, nullable=True)  # JSON object (renamed to avoid SQLAlchemy conflict)
    tags = Column(Text, nullable=True)  # JSON array
    
    created_at = Column(DateTime, default=datetime.utcnow)


class InteractionLogCreate(BaseModel):
    """Pydantic model for creating interaction logs."""
    
    user_id: str = Field(..., min_length=1, description="User identifier")
    interaction_type: str = Field(..., description="Type of interaction")
    interaction_data: Optional[Dict[str, Any]] = Field(None, description="Interaction data")
    session_id: str = Field(..., min_length=1, description="Session identifier")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Device information")
    response_time_ms: Optional[int] = Field(0, ge=0, description="Response time in milliseconds")
    success: Optional[bool] = Field(True, description="Whether interaction was successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    context: Optional[Dict[str, Any]] = Field(None, description="Context information")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    tags: Optional[List[str]] = Field(default=[], description="Tags")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class InteractionLogUpdate(BaseModel):
    """Pydantic model for updating interaction logs."""
    
    interaction_data: Optional[Dict[str, Any]] = None
    response_time_ms: Optional[int] = Field(None, ge=0)
    success: Optional[bool] = None
    error_message: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class InteractionLogResponse(BaseModel):
    """Pydantic model for interaction log responses."""
    
    id: int
    log_id: str
    user_id: str
    interaction_type: str
    interaction_data: Optional[Dict[str, Any]] = None
    timestamp: datetime
    session_id: str
    device_info: Optional[Dict[str, Any]] = None
    response_time_ms: int = 0
    success: bool = True
    error_message: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: List[str] = []
    created_at: datetime
    
    # Calculated properties
    is_fast: bool = False  # < 1000ms
    is_slow: bool = False  # > 2000ms
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def from_db(cls, db_log: InteractionLogDB) -> "InteractionLogResponse":
        """Create response model from database model."""
        
        # Parse interaction data
        interaction_data = None
        if db_log.interaction_data:
            try:
                interaction_data = json.loads(db_log.interaction_data)
            except json.JSONDecodeError:
                interaction_data = None
        
        # Parse device info
        device_info = None
        if db_log.device_info:
            try:
                device_info = json.loads(db_log.device_info)
            except json.JSONDecodeError:
                device_info = None
        
        # Parse context
        context = None
        if db_log.context:
            try:
                context = json.loads(db_log.context)
            except json.JSONDecodeError:
                context = None
        
        # Parse metadata
        metadata = None
        if db_log.log_metadata:
            try:
                metadata = json.loads(db_log.log_metadata)
            except json.JSONDecodeError:
                metadata = None
        
        # Parse tags
        tags = []
        if db_log.tags:
            try:
                tags = json.loads(db_log.tags)
            except json.JSONDecodeError:
                tags = []
        
        # Calculate performance flags
        is_fast = db_log.response_time_ms < 1000
        is_slow = db_log.response_time_ms > 2000
        
        return cls(
            id=db_log.id,
            log_id=db_log.log_id,
            user_id=db_log.user_id,
            interaction_type=db_log.interaction_type,
            interaction_data=interaction_data,
            timestamp=db_log.timestamp,
            session_id=db_log.session_id,
            device_info=device_info,
            response_time_ms=db_log.response_time_ms,
            success=db_log.success,
            error_message=db_log.error_message,
            context=context,
            metadata=metadata,
            tags=tags,
            created_at=db_log.created_at,
            is_fast=is_fast,
            is_slow=is_slow
        )


class InteractionLogStats(BaseModel):
    """Statistics for interaction logs."""
    
    total_interactions: int = 0
    successful_interactions: int = 0
    failed_interactions: int = 0
    success_rate: float = 0.0
    
    # Performance metrics
    average_response_time_ms: float = 0.0
    fast_interactions: int = 0  # < 1000ms
    slow_interactions: int = 0  # > 2000ms
    
    # Interaction type distribution
    button_press_count: int = 0
    video_generation_count: int = 0
    preference_update_count: int = 0
    schedule_change_count: int = 0
    api_call_count: int = 0
    system_event_count: int = 0
    
    # Device distribution
    web_interactions: int = 0
    mobile_interactions: int = 0
    m5stack_interactions: int = 0
    raspberry_pi_interactions: int = 0
    other_device_interactions: int = 0
    
    # Session metrics
    unique_sessions: int = 0
    unique_users: int = 0
    
    class Config:
        json_encoders = {
            float: lambda v: round(v, 4)
        }