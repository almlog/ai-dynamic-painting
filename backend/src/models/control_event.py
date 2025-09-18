"""
ControlEvent model - Phase 1 手動動画管理システム
T029: Operation logging and event tracking
"""
import uuid
from datetime import datetime
from typing import Optional, Literal, Dict, Any, Union
from pydantic import BaseModel, Field


# Event type enumeration
EventType = Literal["play", "pause", "stop", "next", "previous", "volume", "upload"]


class ControlEventBase(BaseModel):
    """Base ControlEvent model with common fields"""
    session_id: Optional[str] = None  # Some events (upload) may not have session
    device_id: str  # Device that triggered the event
    event_type: EventType
    event_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ControlEventCreate(ControlEventBase):
    """ControlEvent creation model"""
    timestamp: datetime = Field(default_factory=datetime.now)


class ControlEventUpdate(BaseModel):
    """ControlEvent update model - mainly for success/error status updates"""
    success: Optional[bool] = None
    error_message: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None
    event_type: Optional[EventType] = None


class ControlEvent(ControlEventBase):
    """Complete ControlEvent model with all fields"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> dict:
        """Convert ControlEvent to dictionary"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "device_id": self.device_id,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "success": self.success,
            "error_message": self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ControlEvent':
        """Create ControlEvent from dictionary"""
        event_data = data.copy()
        
        # Parse datetime string if needed
        if isinstance(event_data.get("timestamp"), str):
            event_data["timestamp"] = datetime.fromisoformat(event_data["timestamp"].replace("Z", "+00:00"))
        
        return cls(**event_data)
    
    def update_timestamp(self, timestamp: Optional[datetime] = None):
        """Update timestamp to current or specified time"""
        self.timestamp = timestamp if timestamp else datetime.now()
    
    def mark_as_failed(self, error_message: str):
        """Mark event as failed with error message"""
        self.success = False
        self.error_message = error_message
    
    def mark_as_successful(self):
        """Mark event as successful and clear error message"""
        self.success = True
        self.error_message = None
    
    def add_data(self, additional_data: Dict[str, Any]):
        """Add or update event_data with additional information"""
        if self.event_data is None:
            self.event_data = {}
        self.event_data.update(additional_data)