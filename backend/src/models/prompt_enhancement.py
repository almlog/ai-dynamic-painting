"""
Prompt enhancement model for tracking and managing dynamic prompt improvements.
Stores enhancement history, parameters, and quality metrics.
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

Base = declarative_base()


class PromptEnhancement(Base):
    """SQLAlchemy model for storing prompt enhancement data"""
    __tablename__ = "prompt_enhancements"
    
    id = Column(Integer, primary_key=True)
    enhancement_id = Column(String(255), nullable=False, unique=True, index=True)
    base_prompt = Column(Text, nullable=False)
    enhanced_prompt = Column(Text, nullable=False)
    enhancement_type = Column(String(100), nullable=False)  # style_injection, technical_optimization, etc.
    enhancement_params = Column(JSON)  # JSON field for enhancement parameters
    quality_score = Column(Float, default=0.0)
    user_satisfaction = Column(Float, default=0.0)
    technical_quality = Column(Float, default=0.0)
    style_accuracy = Column(Float, default=0.0)
    user_id = Column(String(255), index=True)  # User who requested enhancement
    processing_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __init__(self, enhancement_id: str, base_prompt: str, enhanced_prompt: str,
                 enhancement_type: str, enhancement_params: Dict[str, Any],
                 quality_score: float = 0.0, user_id: Optional[str] = None):
        self.enhancement_id = enhancement_id
        self.base_prompt = base_prompt
        self.enhanced_prompt = enhanced_prompt
        self.enhancement_type = enhancement_type
        self.enhancement_params = enhancement_params
        self.quality_score = quality_score
        self.user_id = user_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update_feedback(self, satisfaction: float = None, technical: float = None, 
                       style: float = None):
        """Update feedback scores"""
        if satisfaction is not None:
            self.user_satisfaction = satisfaction
        if technical is not None:
            self.technical_quality = technical
        if style is not None:
            self.style_accuracy = style
        
        # Recalculate overall quality score
        scores = [self.user_satisfaction, self.technical_quality, self.style_accuracy]
        non_zero_scores = [s for s in scores if s > 0]
        if non_zero_scores:
            self.quality_score = sum(non_zero_scores) / len(non_zero_scores)
        
        self.updated_at = datetime.now()


class EnhancementLayer(BaseModel):
    """Pydantic model for enhancement layer configuration"""
    layer: str = Field(..., description="Layer type (style, lighting, details, technical)")
    params: Dict[str, Any] = Field(..., description="Layer parameters")
    weight: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Layer application weight")


class EnhancementRequest(BaseModel):
    """Pydantic model for enhancement requests"""
    base_prompt: str = Field(..., min_length=1, description="Base prompt to enhance")
    enhancement_type: str = Field(..., description="Type of enhancement")
    target_style: Optional[str] = Field(None, description="Target artistic style")
    mood: Optional[str] = Field(None, description="Target mood or atmosphere")
    technical_quality: Optional[str] = Field(None, description="Technical quality level")
    artistic_elements: Optional[List[str]] = Field(None, description="Artistic elements to include")
    context: Optional[Dict[str, Any]] = Field(None, description="Contextual information")
    enhancement_layers: Optional[List[EnhancementLayer]] = Field(None, description="Multi-layer enhancements")
    user_id: Optional[str] = Field(None, description="User requesting enhancement")


class EnhancementResponse(BaseModel):
    """Pydantic model for enhancement responses"""
    enhancement_id: str
    base_prompt: str
    enhanced_prompt: str
    enhancement_type: str
    enhancement_params: Dict[str, Any]
    quality_score: float
    processing_time_ms: int
    improvement_factors: List[str]
    suggested_iterations: Optional[List[str]]
    created_at: str
    
    class Config:
        from_attributes = True


class EnhancementHistory(BaseModel):
    """Pydantic model for enhancement history"""
    enhancement_id: str
    base_prompt: str
    enhanced_prompt: str
    enhancement_type: str
    quality_score: float
    user_satisfaction: float
    timestamp: str
    
    class Config:
        from_attributes = True


class AdaptationMetrics(BaseModel):
    """Pydantic model for adaptation metrics"""
    learning_rate: float
    improvement_trend: float
    total_enhancements: int
    average_quality: float
    style_preferences: Dict[str, float]
    best_performing_techniques: List[str]
    adaptation_efficiency: float