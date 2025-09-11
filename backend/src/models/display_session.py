"""
DisplaySession model - Phase 1 手動動画管理システム
T026: Minimal implementation to pass tests
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DisplaySession(BaseModel):
    """
    DisplaySession entity for Phase 1
    Minimal implementation to satisfy TDD tests
    """
    id: str
    video_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    session_type: str = "manual"
    current_position: float = 0.0
    playback_status: str = "stopped"
    display_mode: str = "fullscreen"
    loop_enabled: bool = False
    created_by: str = "web"
    
    class Config:
        # Allow datetime objects to be serialized
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }