"""User Preference model for AI learning system."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum
import json
import uuid

Base = declarative_base()


class PreferenceType(Enum):
    """Enumeration for preference types"""
    STYLE = "style"
    COLOR = "color"
    MOOD = "mood"
    TIME_OF_DAY = "time_of_day"
    WEATHER = "weather"
    SEASON = "season"
    THEME = "theme"
    CONTENT_TYPE = "content_type"


class LearningSource(Enum):
    """Enumeration for learning sources"""
    EXPLICIT = "explicit"      # User directly told us
    IMPLICIT = "implicit"      # Learned from behavior
    SYSTEM = "system"          # System inferred
    EXTERNAL = "external"      # From external sources


class UserPreference:
    """Simple UserPreference class for contract test compatibility"""
    
    def __init__(self, preference_id=None, user_id=None, preference_type=None, 
                 preference_value=None, context=None, weight=0.5, 
                 confidence_score=0.5, learning_source=None, creation_time=None,
                 last_updated=None, usage_count=0, effectiveness_score=0.0,
                 is_active=True, metadata=None, tags=None):
        
        # Allow default constructor for testing
        if preference_id is None and user_id is None:
            user_id = "default_user"
            
        self.preference_id = preference_id or f"pref_{uuid.uuid4().hex[:8]}"
        self.user_id = user_id
        self.preference_type = preference_type or PreferenceType.STYLE
        self.preference_value = preference_value or ""
        self.context = context or {}
        self.weight = max(0.0, min(1.0, weight))  # Clamp to 0.0-1.0
        self.confidence_score = max(0.0, min(1.0, confidence_score))  # Clamp to 0.0-1.0
        self.learning_source = learning_source or LearningSource.SYSTEM
        self.creation_time = creation_time or datetime.now()
        self.last_updated = last_updated or datetime.now()
        self.usage_count = max(0, usage_count)
        self.effectiveness_score = max(0.0, min(1.0, effectiveness_score))
        self.is_active = is_active
        self.metadata = metadata or {}
        self.tags = tags or []
    
    def get_context_value(self, key):
        """Get a value from the context dictionary"""
        return self.context.get(key)
    
    def set_context_value(self, key, value):
        """Set a value in the context dictionary"""
        self.context[key] = value
        self.last_updated = datetime.now()
    
    def apply_positive_feedback(self, boost=0.1):
        """Apply positive feedback to increase weight and confidence"""
        self.weight = min(1.0, self.weight + boost)
        self.confidence_score = min(1.0, self.confidence_score + boost * 0.5)
        self.effectiveness_score = min(1.0, self.effectiveness_score + boost * 0.3)
        self.last_updated = datetime.now()
    
    def apply_negative_feedback(self, reduction=0.05):
        """Apply negative feedback to decrease weight"""
        self.weight = max(0.0, self.weight - reduction)
        self.confidence_score = max(0.0, self.confidence_score - reduction * 0.3)
        self.last_updated = datetime.now()
    
    def record_usage(self):
        """Record that this preference was used"""
        self.usage_count += 1
        self.last_updated = datetime.now()
    
    def calculate_similarity(self, other_preference):
        """Calculate similarity with another preference (0.0 to 1.0)"""
        if not isinstance(other_preference, UserPreference):
            return 0.0
        
        # Same type and value = high similarity
        if (self.preference_type == other_preference.preference_type and
            self.preference_value == other_preference.preference_value):
            
            # Calculate context similarity
            common_keys = set(self.context.keys()) & set(other_preference.context.keys())
            if not common_keys:
                return 0.8  # High similarity for same type/value, no context overlap
            
            context_matches = sum(1 for key in common_keys 
                                if self.context[key] == other_preference.context[key])
            context_similarity = context_matches / len(common_keys)
            
            # Weight the final similarity
            return 0.8 + (0.2 * context_similarity)
        
        # Different type or value
        return 0.1
    
    def matches_context(self, context_filter):
        """Check if this preference matches the given context filter"""
        if not context_filter:
            return True
        
        for key, value in context_filter.items():
            if key in self.context and self.context[key] == value:
                continue
            elif key not in self.context:
                continue  # Missing context key doesn't automatically disqualify
            else:
                return False  # Explicit mismatch
        
        return True
    
    @staticmethod
    def rank_by_weight(preferences):
        """Rank preferences by weight (highest first)"""
        return sorted(preferences, key=lambda p: p.weight, reverse=True)
    
    @staticmethod
    def rank_by_effectiveness(preferences):
        """Rank preferences by effectiveness score (highest first)"""
        return sorted(preferences, key=lambda p: p.effectiveness_score, reverse=True)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'preference_id': self.preference_id,
            'user_id': self.user_id,
            'preference_type': self.preference_type.value if isinstance(self.preference_type, PreferenceType) else str(self.preference_type),
            'preference_value': self.preference_value,
            'context': self.context,
            'weight': self.weight,
            'confidence_score': self.confidence_score,
            'learning_source': self.learning_source.value if isinstance(self.learning_source, LearningSource) else str(self.learning_source),
            'creation_time': self.creation_time.isoformat() if self.creation_time else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'usage_count': self.usage_count,
            'effectiveness_score': self.effectiveness_score,
            'is_active': self.is_active,
            'metadata': self.metadata,
            'tags': self.tags
        }


class UserPreferenceDB(Base):
    """SQLAlchemy model for user preferences."""
    
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    preference_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Preference details
    preference_type = Column(String, nullable=False)  # style, color, mood, etc.
    preference_value = Column(String, nullable=False)  # specific value
    context = Column(Text, nullable=True)  # JSON object for context
    
    # Learning metrics
    weight = Column(Float, default=0.5)  # 0.0 to 1.0
    confidence_score = Column(Float, default=0.5)  # 0.0 to 1.0
    learning_source = Column(String, nullable=False)  # explicit, implicit, system
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    effectiveness_score = Column(Float, default=0.0)
    last_used_at = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    preference_metadata = Column(Text, nullable=True)  # JSON object
    tags = Column(Text, nullable=True)  # JSON array
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserPreferenceCreate(BaseModel):
    """Pydantic model for creating user preferences."""
    
    user_id: str = Field(..., min_length=1, description="User identifier")
    preference_type: str = Field(..., description="Type of preference")
    preference_value: str = Field(..., min_length=1, description="Preference value")
    context: Optional[Dict[str, Any]] = Field(None, description="Context information")
    weight: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Preference weight")
    confidence_score: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Confidence score")
    learning_source: str = Field(..., description="Source of learning")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    tags: Optional[List[str]] = Field(default=[], description="Tags")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserPreferenceUpdate(BaseModel):
    """Pydantic model for updating user preferences."""
    
    preference_value: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    effectiveness_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserPreferenceResponse(BaseModel):
    """Pydantic model for user preference responses."""
    
    id: int
    preference_id: str
    user_id: str
    preference_type: str
    preference_value: str
    context: Optional[Dict[str, Any]] = None
    weight: float = 0.5
    confidence_score: float = 0.5
    learning_source: str
    usage_count: int = 0
    effectiveness_score: float = 0.0
    last_used_at: Optional[datetime] = None
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
    
    # Calculated properties
    strength: float = 0.0  # Combined weight * confidence
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def from_db(cls, db_preference: UserPreferenceDB) -> "UserPreferenceResponse":
        """Create response model from database model."""
        
        # Parse context
        context = None
        if db_preference.context:
            try:
                context = json.loads(db_preference.context)
            except json.JSONDecodeError:
                context = None
        
        # Parse metadata
        metadata = None
        if db_preference.preference_metadata:
            try:
                metadata = json.loads(db_preference.preference_metadata)
            except json.JSONDecodeError:
                metadata = None
        
        # Parse tags
        tags = []
        if db_preference.tags:
            try:
                tags = json.loads(db_preference.tags)
            except json.JSONDecodeError:
                tags = []
        
        # Calculate strength
        strength = db_preference.weight * db_preference.confidence_score
        
        return cls(
            id=db_preference.id,
            preference_id=db_preference.preference_id,
            user_id=db_preference.user_id,
            preference_type=db_preference.preference_type,
            preference_value=db_preference.preference_value,
            context=context,
            weight=db_preference.weight,
            confidence_score=db_preference.confidence_score,
            learning_source=db_preference.learning_source,
            usage_count=db_preference.usage_count,
            effectiveness_score=db_preference.effectiveness_score,
            last_used_at=db_preference.last_used_at,
            is_active=db_preference.is_active,
            metadata=metadata,
            tags=tags,
            created_at=db_preference.created_at,
            updated_at=db_preference.updated_at,
            strength=strength
        )


class UserPreferenceStats(BaseModel):
    """Statistics for user preferences."""
    
    total_preferences: int = 0
    active_preferences: int = 0
    inactive_preferences: int = 0
    
    # Type distribution
    style_preferences: int = 0
    color_preferences: int = 0
    mood_preferences: int = 0
    theme_preferences: int = 0
    other_preferences: int = 0
    
    # Learning source distribution
    explicit_count: int = 0
    implicit_count: int = 0
    system_count: int = 0
    external_count: int = 0
    
    # Quality metrics
    average_weight: float = 0.0
    average_confidence: float = 0.0
    average_effectiveness: float = 0.0
    total_usage: int = 0
    
    class Config:
        json_encoders = {
            float: lambda v: round(v, 4)
        }