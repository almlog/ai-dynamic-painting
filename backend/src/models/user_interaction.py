"""
User interaction model for tracking user behavior with videos.
Used for learning user preferences from interaction patterns.
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

Base = declarative_base()


class UserInteraction(Base):
    """SQLAlchemy model for storing user interactions"""
    __tablename__ = "user_interactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    video_id = Column(String(255), nullable=False, index=True)
    interaction_type = Column(String(50), nullable=False)  # like, skip, watch, pause, repeat
    duration_seconds = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.now)
    prompt_style = Column(String(255))  # Style used in the prompt
    time_of_day = Column(String(50))  # morning, afternoon, evening, night
    weather = Column(String(50))  # sunny, rainy, cloudy, etc.
    context_data = Column(Text)  # JSON string for additional context
    
    def __init__(self, user_id: str, video_id: str, interaction_type: str, 
                 duration_seconds: int = 0, timestamp: Optional[datetime] = None,
                 prompt_style: Optional[str] = None, time_of_day: Optional[str] = None,
                 weather: Optional[str] = None, context_data: Optional[str] = None):
        self.user_id = user_id
        self.video_id = video_id
        self.interaction_type = interaction_type
        self.duration_seconds = duration_seconds
        self.timestamp = timestamp or datetime.now()
        self.prompt_style = prompt_style
        self.time_of_day = time_of_day
        self.weather = weather
        self.context_data = context_data
    
    def is_positive_interaction(self) -> bool:
        """Check if this interaction indicates positive preference"""
        positive_types = ["like", "watch", "repeat", "favorite"]
        long_watch = self.interaction_type == "watch" and self.duration_seconds > 60
        return self.interaction_type in positive_types or long_watch
    
    def is_negative_interaction(self) -> bool:
        """Check if this interaction indicates negative preference"""
        negative_types = ["skip", "dislike", "report"]
        short_watch = self.interaction_type == "watch" and self.duration_seconds < 10
        return self.interaction_type in negative_types or short_watch


class InteractionRequest(BaseModel):
    """Pydantic model for interaction API requests"""
    user_id: str = Field(..., description="User identifier")
    video_id: str = Field(..., description="Video identifier")
    interaction_type: str = Field(..., description="Type of interaction (like, skip, watch, etc.)")
    duration_seconds: Optional[int] = Field(0, ge=0, description="Duration of interaction in seconds")
    prompt_style: Optional[str] = Field(None, description="Style used in the video prompt")
    time_of_day: Optional[str] = Field(None, description="Time of day when interaction occurred")
    weather: Optional[str] = Field(None, description="Weather condition during interaction")
    context_data: Optional[Dict[str, Any]] = Field(None, description="Additional context data")


class InteractionResponse(BaseModel):
    """Pydantic model for interaction API responses"""
    id: int
    user_id: str
    video_id: str
    interaction_type: str
    duration_seconds: int
    timestamp: str
    prompt_style: Optional[str]
    time_of_day: Optional[str]
    weather: Optional[str]
    is_positive: bool
    
    class Config:
        from_attributes = True