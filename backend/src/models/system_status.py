"""
SystemStatus model - Phase 1 手動動画管理システム
T028: System monitoring and health status
"""
import uuid
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, validator


# Status enumeration types
M5StackStatus = Literal["online", "offline", "error"]
DisplayStatus = Literal["active", "idle", "error"]
ApiStatus = Literal["healthy", "degraded", "error"]


class SystemStatusBase(BaseModel):
    """Base SystemStatus model with common fields"""
    cpu_usage: float = Field(..., ge=0.0, le=100.0)
    memory_usage: float = Field(..., ge=0.0, le=100.0)
    disk_usage: float = Field(..., ge=0.0, le=100.0)
    uptime: int = Field(default=0, ge=0)
    active_sessions: int = Field(default=0, ge=0)
    total_videos: int = Field(default=0, ge=0)
    m5stack_status: M5StackStatus = "offline"
    display_status: DisplayStatus = "idle"
    api_status: ApiStatus = "healthy"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SystemStatusCreate(SystemStatusBase):
    """SystemStatus creation model"""
    timestamp: datetime = Field(default_factory=datetime.now)


class SystemStatus(SystemStatusBase):
    """Complete SystemStatus model with all fields"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }