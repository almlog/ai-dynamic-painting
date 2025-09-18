"""Prompt Template model for AI generation."""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum
import json
import uuid
import re

Base = declarative_base()


class PromptCategory(Enum):
    """Enumeration for prompt template categories"""
    SCENIC = "scenic"
    ARTISTIC = "artistic"
    WEATHER = "weather"
    SEASONAL = "seasonal"
    MOOD = "mood"
    ABSTRACT = "abstract"
    CUSTOM = "custom"


class PromptTemplate:
    """Simple PromptTemplate class for contract test compatibility"""
    
    def __init__(self, template_id=None, name=None, prompt_text=None, 
                 category=None, variables=None, description=None, 
                 creation_time=None, usage_count=0, effectiveness_score=0.0,
                 is_active=True, creator_user_id=None, last_updated=None, tags=None):
        
        # Allow default constructor for testing
        if template_id is None and name is None:
            name = "default_template"
            
        self.template_id = template_id or f"tpl_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.prompt_text = prompt_text or ""
        self.category = category or PromptCategory.CUSTOM
        self.variables = variables or []
        self.description = description or ""
        self.creation_time = creation_time or datetime.now()
        self.usage_count = max(0, usage_count)
        self.effectiveness_score = max(0.0, min(1.0, effectiveness_score))  # Clamp to 0.0-1.0
        self.is_active = is_active
        self.creator_user_id = creator_user_id
        self.last_updated = last_updated or datetime.now()
        self.tags = tags or []
    
    def extract_variables(self):
        """Extract variables from prompt text using {variable} pattern"""
        if not self.prompt_text:
            return []
        
        # Find all {variable} patterns
        pattern = r'\{(\w+)\}'
        variables = re.findall(pattern, self.prompt_text)
        return list(set(variables))  # Remove duplicates
    
    def render_prompt(self, values):
        """Render prompt by substituting variables with values"""
        if not self.prompt_text:
            return ""
        
        rendered = self.prompt_text
        for key, value in values.items():
            placeholder = f"{{{key}}}"
            rendered = rendered.replace(placeholder, str(value))
        
        return rendered
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
        self.last_updated = datetime.now()
    
    def update_effectiveness(self, score):
        """Update effectiveness score"""
        self.effectiveness_score = max(0.0, min(1.0, score))
        self.last_updated = datetime.now()
    
    def calculate_popularity(self):
        """Calculate popularity based on usage and effectiveness"""
        if self.usage_count == 0:
            return 0.0
        
        # Simple popularity calculation: usage * effectiveness
        return float(self.usage_count * self.effectiveness_score / 100.0)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'template_id': self.template_id,
            'name': self.name,
            'prompt_text': self.prompt_text,
            'category': self.category.value if isinstance(self.category, PromptCategory) else str(self.category),
            'variables': self.variables,
            'description': self.description,
            'creation_time': self.creation_time.isoformat() if self.creation_time else None,
            'usage_count': self.usage_count,
            'effectiveness_score': self.effectiveness_score,
            'is_active': self.is_active,
            'creator_user_id': self.creator_user_id,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'tags': self.tags,
            'popularity': self.calculate_popularity()
        }


class PromptTemplateDB(Base):
    """SQLAlchemy model for prompt templates."""
    
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    template_text = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # morning, afternoon, evening, night, custom
    context_variables = Column(Text, nullable=True)  # JSON array of variable names
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    average_rating = Column(Float, nullable=True)
    is_active = Column(String, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PromptTemplateResponse(BaseModel):
    """Response model for prompt templates."""
    
    id: int
    name: str
    template_text: str
    category: str
    context_variables: List[str] = []
    usage_count: int = 0
    success_rate: float = 0.0
    average_rating: Optional[float] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True