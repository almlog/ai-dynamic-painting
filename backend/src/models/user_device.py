"""
UserDevice model - Phase 1 手動動画管理システム
T027: Device tracking and management
"""
import uuid
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, validator
import ipaddress


# Device type enumeration
DeviceType = Literal["web_browser", "m5stack"]


class UserDeviceBase(BaseModel):
    """Base UserDevice model with common fields"""
    device_type: DeviceType
    device_name: str = Field(..., max_length=50)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_count: int = Field(default=0, ge=0)
    is_active: bool = True

    @validator('ip_address')
    def validate_ip_address(cls, v):
        if v is None:
            return v
        if v == "":
            raise ValueError("IP address cannot be empty string")
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid IP address format: {v}")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserDeviceCreate(UserDeviceBase):
    """UserDevice creation model"""
    last_seen: datetime = Field(default_factory=datetime.now)


class UserDeviceUpdate(BaseModel):
    """UserDevice update model - all fields optional"""
    device_type: Optional[DeviceType] = None
    device_name: Optional[str] = Field(None, max_length=50)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_count: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    last_seen: Optional[datetime] = None

    @validator('ip_address')
    def validate_ip_address(cls, v):
        if v is None or v == "":
            return v
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid IP address format: {v}")


class UserDevice(UserDeviceBase):
    """Complete UserDevice model with all fields"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    last_seen: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> dict:
        """Convert UserDevice to dictionary"""
        return {
            "id": self.id,
            "device_type": self.device_type,
            "device_name": self.device_name,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "last_seen": self.last_seen.isoformat() if isinstance(self.last_seen, datetime) else self.last_seen,
            "session_count": self.session_count,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserDevice':
        """Create UserDevice from dictionary"""
        device_data = data.copy()
        
        # Parse datetime string if needed
        if isinstance(device_data.get("last_seen"), str):
            device_data["last_seen"] = datetime.fromisoformat(device_data["last_seen"].replace("Z", "+00:00"))
        
        return cls(**device_data)
    
    def update_last_seen(self, timestamp: Optional[datetime] = None):
        """Update last_seen timestamp"""
        self.last_seen = timestamp if timestamp else datetime.now()
    
    def increment_session_count(self, increment: int = 1):
        """Increment session count"""
        self.session_count += increment