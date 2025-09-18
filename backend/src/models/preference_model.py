"""
Preference model for user preference learning system.
Tracks user preferences for various video generation parameters.
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

Base = declarative_base()


class PreferenceModel(Base):
    """SQLAlchemy model for storing user preferences"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    preference_type = Column(String(50), nullable=False)  # style, time, weather, etc.
    preference_value = Column(String(255), nullable=False)  # abstract, morning, rainy, etc.
    confidence_score = Column(Float, default=0.5)
    interaction_count = Column(Integer, default=1)
    last_updated = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    
    def __init__(self, user_id: str, preference_type: str, preference_value: str, 
                 confidence_score: float = 0.5, interaction_count: int = 1):
        self.user_id = user_id
        self.preference_type = preference_type
        self.preference_value = preference_value
        self.confidence_score = confidence_score
        self.interaction_count = interaction_count
        self.last_updated = datetime.now()
        self.created_at = datetime.now()
    
    def update_confidence(self, new_score: float):
        """Update confidence score and last_updated timestamp"""
        self.confidence_score = new_score
        self.last_updated = datetime.now()
    
    def increment_interaction(self):
        """Increment interaction count"""
        self.interaction_count += 1
        self.last_updated = datetime.now()


class PreferenceRequest(BaseModel):
    """Pydantic model for preference API requests"""
    user_id: str = Field(..., description="User identifier")
    preference_type: str = Field(..., description="Type of preference (style, time, weather)")
    preference_value: str = Field(..., description="Value of the preference")
    confidence_score: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Confidence score")


class PreferenceResponse(BaseModel):
    """Pydantic model for preference API responses"""
    user_id: str
    preference_type: str
    preference_value: str
    confidence_score: float
    interaction_count: int
    last_updated: str
    
    class Config:
        from_attributes = True