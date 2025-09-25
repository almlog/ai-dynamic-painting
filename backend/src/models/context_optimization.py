"""
Context optimization model for tracking and managing context-based optimizations.
Stores optimization parameters and performance metrics.
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

Base = declarative_base()


class ContextOptimization(Base):
    """SQLAlchemy model for storing context optimization data"""
    __tablename__ = "context_optimizations"
    
    id = Column(Integer, primary_key=True)
    optimization_id = Column(String(255), nullable=False, unique=True, index=True)
    context_type = Column(String(100), nullable=False)  # environmental, temporal, user, etc.
    context_data = Column(JSON)  # JSON field for flexible context storage
    optimization_params = Column(JSON)  # JSON field for optimization parameters
    performance_score = Column(Float, default=0.0)
    user_satisfaction = Column(Float, default=0.0)
    generation_quality = Column(Float, default=0.0)
    cache_key = Column(String(255), index=True)  # For caching optimizations
    is_cached = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __init__(self, optimization_id: str, context_type: str, 
                 context_data: Dict[str, Any], optimization_params: Dict[str, Any],
                 performance_score: float = 0.0):
        self.optimization_id = optimization_id
        self.context_type = context_type
        self.context_data = context_data
        self.optimization_params = optimization_params
        self.performance_score = performance_score
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update_performance(self, score: float, satisfaction: float = None, quality: float = None):
        """Update performance metrics"""
        self.performance_score = score
        if satisfaction is not None:
            self.user_satisfaction = satisfaction
        if quality is not None:
            self.generation_quality = quality
        self.updated_at = datetime.now()
    
    def get_cache_key(self) -> str:
        """Generate cache key from context data"""
        import hashlib
        import json
        
        # Create deterministic string from context data
        context_str = json.dumps(self.context_data, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()


class ContextOptimizationRequest(BaseModel):
    """Pydantic model for context optimization requests"""
    context_type: str = Field(..., description="Type of context (environmental, temporal, user)")
    context_data: Dict[str, Any] = Field(..., description="Context data for optimization")
    base_prompt: Optional[str] = Field(None, description="Base prompt to optimize")
    optimization_goals: Optional[Dict[str, float]] = Field(None, description="Optimization goals and weights")


class ContextOptimizationResponse(BaseModel):
    """Pydantic model for context optimization responses"""
    optimization_id: str
    context_type: str
    optimized_params: Dict[str, Any]
    optimization_score: float
    style_suggestions: List[str]
    mood_adjustment: str
    color_palette: List[str]
    confidence: float
    cache_hit: bool
    processing_time_ms: int
    
    class Config:
        from_attributes = True


class OptimizationMetrics(BaseModel):
    """Pydantic model for optimization performance metrics"""
    total_optimizations: int
    average_satisfaction: float
    average_performance: float
    cache_hit_rate: float
    best_performing_contexts: List[Dict[str, Any]]
    optimization_trends: Dict[str, float]
    last_updated: str