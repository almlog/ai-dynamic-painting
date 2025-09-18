"""Generation Schedule model for AI scheduling system."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum
import json
import uuid

Base = declarative_base()


class ScheduleType(Enum):
    """Enumeration for schedule types"""
    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CRON = "cron"
    EVENT_DRIVEN = "event_driven"


class ScheduleFrequency(Enum):
    """Enumeration for schedule frequencies"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    BURST = "burst"


class GenerationSchedule:
    """Simple GenerationSchedule class for contract test compatibility"""
    
    def __init__(self, schedule_id=None, name=None, is_active=True, 
                 schedule_type=None, frequency=None, start_time=None, 
                 end_time=None, creation_time=None, last_run_time=None,
                 next_run_time=None, run_count=0, success_count=0, 
                 failure_count=0, template_ids=None, context_preferences=None, 
                 priority_level=5):
        
        # Allow default constructor for testing
        if schedule_id is None and name is None:
            name = "default_schedule"
            
        self.schedule_id = schedule_id or f"sch_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.is_active = is_active
        self.schedule_type = schedule_type or ScheduleType.DAILY
        self.frequency = frequency or ScheduleFrequency.NORMAL
        self.start_time = start_time or datetime.now()
        self.end_time = end_time
        self.creation_time = creation_time or datetime.now()
        self.last_run_time = last_run_time
        self.next_run_time = next_run_time
        self.run_count = max(0, run_count)
        self.success_count = max(0, success_count)
        self.failure_count = max(0, failure_count)
        self.template_ids = template_ids or []
        self.context_preferences = context_preferences or {}
        self.priority_level = max(1, min(10, priority_level))  # Clamp to 1-10
    
    def add_template(self, template_id):
        """Add a template to the schedule"""
        if template_id not in self.template_ids:
            self.template_ids.append(template_id)
    
    def remove_template(self, template_id):
        """Remove a template from the schedule"""
        if template_id in self.template_ids:
            self.template_ids.remove(template_id)
    
    def is_active_at(self, check_time):
        """Check if schedule is active at given time"""
        if not self.is_active:
            return False
        
        if check_time < self.start_time:
            return False
        
        if self.end_time and check_time > self.end_time:
            return False
        
        return True
    
    def calculate_next_run_time(self, from_time):
        """Calculate next run time based on schedule type"""
        if self.schedule_type == ScheduleType.HOURLY:
            return from_time + timedelta(hours=1)
        elif self.schedule_type == ScheduleType.DAILY:
            return from_time + timedelta(days=1)
        elif self.schedule_type == ScheduleType.WEEKLY:
            return from_time + timedelta(weeks=1)
        elif self.schedule_type == ScheduleType.MONTHLY:
            return from_time + timedelta(days=30)  # Approximate
        elif self.schedule_type == ScheduleType.ONCE:
            return None  # No next run for one-time schedules
        else:
            # Default to daily for other types
            return from_time + timedelta(days=1)
    
    def record_successful_run(self):
        """Record a successful run"""
        self.run_count += 1
        self.success_count += 1
        self.last_run_time = datetime.now()
        
        # Calculate next run time
        next_run = self.calculate_next_run_time(self.last_run_time)
        if next_run:
            self.next_run_time = next_run
    
    def record_failed_run(self):
        """Record a failed run"""
        self.run_count += 1
        self.failure_count += 1
        self.last_run_time = datetime.now()
        
        # Calculate next run time even for failures
        next_run = self.calculate_next_run_time(self.last_run_time)
        if next_run:
            self.next_run_time = next_run
    
    def calculate_success_rate(self):
        """Calculate success rate as a percentage"""
        if self.run_count == 0:
            return 0.0
        
        return float(self.success_count / self.run_count)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'schedule_id': self.schedule_id,
            'name': self.name,
            'is_active': self.is_active,
            'schedule_type': self.schedule_type.value if isinstance(self.schedule_type, ScheduleType) else str(self.schedule_type),
            'frequency': self.frequency.value if isinstance(self.frequency, ScheduleFrequency) else str(self.frequency),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'creation_time': self.creation_time.isoformat() if self.creation_time else None,
            'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
            'next_run_time': self.next_run_time.isoformat() if self.next_run_time else None,
            'run_count': self.run_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'template_ids': self.template_ids,
            'context_preferences': self.context_preferences,
            'priority_level': self.priority_level,
            'success_rate': self.calculate_success_rate()
        }


class GenerationScheduleDB(Base):
    """SQLAlchemy model for generation schedules."""
    
    __tablename__ = "generation_schedules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    schedule_type = Column(String, nullable=False)  # hourly, daily, weekly, monthly
    frequency = Column(String, default="normal")    # low, normal, high, burst
    
    # Time configuration
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    next_run_time = Column(DateTime, nullable=True)
    last_run_time = Column(DateTime, nullable=True)
    
    # Statistics
    run_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Configuration
    template_ids = Column(Text, nullable=True)  # JSON array of template IDs
    context_preferences = Column(Text, nullable=True)  # JSON object
    priority_level = Column(Integer, default=5)  # 1-10
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GenerationScheduleCreate(BaseModel):
    """Pydantic model for creating generation schedules."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Schedule name")
    schedule_type: str = Field(..., description="Schedule type (hourly, daily, weekly, monthly)")
    frequency: Optional[str] = Field("normal", description="Schedule frequency")
    start_time: datetime = Field(..., description="Schedule start time")
    end_time: Optional[datetime] = Field(None, description="Schedule end time")
    template_ids: List[str] = Field(default=[], description="List of template IDs")
    context_preferences: Optional[Dict[str, Any]] = Field(None, description="Context preferences")
    priority_level: Optional[int] = Field(5, ge=1, le=10, description="Priority level (1-10)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GenerationScheduleUpdate(BaseModel):
    """Pydantic model for updating generation schedules."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    schedule_type: Optional[str] = None
    frequency: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    template_ids: Optional[List[str]] = None
    context_preferences: Optional[Dict[str, Any]] = None
    priority_level: Optional[int] = Field(None, ge=1, le=10)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GenerationScheduleResponse(BaseModel):
    """Pydantic model for generation schedule responses."""
    
    id: int
    schedule_id: str
    name: str
    is_active: bool
    schedule_type: str
    frequency: str
    start_time: datetime
    end_time: Optional[datetime] = None
    next_run_time: Optional[datetime] = None
    last_run_time: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    template_ids: List[str] = []
    context_preferences: Optional[Dict[str, Any]] = None
    priority_level: int = 5
    created_at: datetime
    updated_at: datetime
    
    # Calculated properties
    success_rate: float = 0.0
    is_due: bool = False
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def from_db(cls, db_schedule: GenerationScheduleDB) -> "GenerationScheduleResponse":
        """Create response model from database model."""
        
        # Parse template IDs
        template_ids = []
        if db_schedule.template_ids:
            try:
                template_ids = json.loads(db_schedule.template_ids)
            except json.JSONDecodeError:
                template_ids = []
        
        # Parse context preferences
        context_preferences = None
        if db_schedule.context_preferences:
            try:
                context_preferences = json.loads(db_schedule.context_preferences)
            except json.JSONDecodeError:
                context_preferences = None
        
        # Calculate success rate
        success_rate = 0.0
        if db_schedule.run_count > 0:
            success_rate = db_schedule.success_count / db_schedule.run_count
        
        # Check if schedule is due
        is_due = False
        if db_schedule.is_active and db_schedule.next_run_time:
            is_due = datetime.utcnow() >= db_schedule.next_run_time
        
        return cls(
            id=db_schedule.id,
            schedule_id=db_schedule.schedule_id,
            name=db_schedule.name,
            is_active=db_schedule.is_active,
            schedule_type=db_schedule.schedule_type,
            frequency=db_schedule.frequency,
            start_time=db_schedule.start_time,
            end_time=db_schedule.end_time,
            next_run_time=db_schedule.next_run_time,
            last_run_time=db_schedule.last_run_time,
            run_count=db_schedule.run_count,
            success_count=db_schedule.success_count,
            failure_count=db_schedule.failure_count,
            template_ids=template_ids,
            context_preferences=context_preferences,
            priority_level=db_schedule.priority_level,
            created_at=db_schedule.created_at,
            updated_at=db_schedule.updated_at,
            success_rate=success_rate,
            is_due=is_due
        )


class GenerationScheduleStats(BaseModel):
    """Statistics for generation schedules."""
    
    total_schedules: int = 0
    active_schedules: int = 0
    inactive_schedules: int = 0
    due_schedules: int = 0
    
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    overall_success_rate: float = 0.0
    
    # Schedule type distribution
    hourly_schedules: int = 0
    daily_schedules: int = 0
    weekly_schedules: int = 0
    monthly_schedules: int = 0
    
    class Config:
        json_encoders = {
            float: lambda v: round(v, 4)
        }