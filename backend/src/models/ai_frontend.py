"""
AI frontend models for managing dashboard components and user interfaces.
Supports real-time monitoring, interactive controls, and responsive layouts.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON, Float
from sqlalchemy.orm import declarative_base
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from enum import Enum

Base = declarative_base()


class ComponentType(str, Enum):
    """Enumeration of AI dashboard component types"""
    GENERATION_MONITOR = "generation_monitor"
    AI_METRICS_MONITOR = "ai_metrics_monitor"
    GENERATION_QUEUE = "generation_queue"
    AI_CONTROL_PANEL = "ai_control_panel"
    USER_PREFERENCES = "user_preferences"
    GENERATION_TIMELINE = "generation_timeline"
    MODEL_PERFORMANCE = "model_performance_comparison"
    SATISFACTION_HEATMAP = "user_satisfaction_heatmap"
    COST_ANALYSIS = "cost_analysis"
    RESPONSIVE_LAYOUT = "responsive_ai_layout"


class ComponentStatus(str, Enum):
    """Enumeration of component status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    LOADING = "loading"
    UPDATING = "updating"


class AlertLevel(str, Enum):
    """Enumeration of alert levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    SUCCESS = "success"


class AIDashboardComponent(Base):
    """SQLAlchemy model for AI dashboard components"""
    __tablename__ = "ai_dashboard_components"
    
    id = Column(Integer, primary_key=True)
    component_id = Column(String(255), nullable=False, unique=True, index=True)
    component_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Configuration
    config = Column(JSON)  # Component-specific configuration
    data_sources = Column(JSON)  # List of data sources
    layout_config = Column(JSON)  # Layout and positioning
    styling_config = Column(JSON)  # Styling and theme
    
    # State and status
    status = Column(String(20), default="active")
    last_updated = Column(DateTime, default=datetime.now)
    data_cache = Column(JSON)  # Cached component data
    error_message = Column(Text)
    
    # User and permissions
    owner_id = Column(String(255), nullable=False, index=True)
    shared_with = Column(JSON)  # List of user IDs with access
    permissions = Column(JSON)  # Permission configuration
    
    # Metrics and analytics
    view_count = Column(Integer, default=0)
    interaction_count = Column(Integer, default=0)
    last_viewed = Column(DateTime)
    last_interacted = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __init__(self, component_id: str, component_type: str, title: str,
                 config: Dict[str, Any] = None, data_sources: List[str] = None,
                 layout_config: Dict[str, Any] = None, owner_id: str = "system"):
        self.component_id = component_id
        self.component_type = component_type
        self.title = title
        self.config = config or {}
        self.data_sources = data_sources or []
        self.layout_config = layout_config or {}
        self.styling_config = {}
        self.owner_id = owner_id
        self.status = ComponentStatus.ACTIVE.value
        self.shared_with = []
        self.permissions = {}
        self.data_cache = {}
        self.view_count = 0
        self.interaction_count = 0
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.last_updated = datetime.now()
    
    def update_data_cache(self, data: Dict[str, Any]):
        """Update component data cache"""
        self.data_cache = data
        self.last_updated = datetime.now()
        self.updated_at = datetime.now()
    
    def record_view(self):
        """Record a component view"""
        self.view_count += 1
        self.last_viewed = datetime.now()
        self.updated_at = datetime.now()
    
    def record_interaction(self):
        """Record a component interaction"""
        self.interaction_count += 1
        self.last_interacted = datetime.now()
        self.updated_at = datetime.now()
    
    def set_error(self, error_message: str):
        """Set component error state"""
        self.status = ComponentStatus.ERROR.value
        self.error_message = error_message
        self.updated_at = datetime.now()
    
    def clear_error(self):
        """Clear component error state"""
        if self.status == ComponentStatus.ERROR.value:
            self.status = ComponentStatus.ACTIVE.value
            self.error_message = None
            self.updated_at = datetime.now()


class AIMetric(Base):
    """SQLAlchemy model for AI metrics"""
    __tablename__ = "ai_metrics"
    
    id = Column(Integer, primary_key=True)
    metric_id = Column(String(255), nullable=False, unique=True, index=True)
    metric_name = Column(String(255), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50), nullable=False)  # percentage, duration, count, etc.
    
    # Context
    component = Column(String(100), nullable=False, index=True)
    user_id = Column(String(255), index=True)
    session_id = Column(String(255), index=True)
    
    # Additional data
    tags = Column(JSON)  # Additional metadata
    threshold_config = Column(JSON)  # Alert thresholds
    
    # Timestamps
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)
    
    def __init__(self, metric_id: str, metric_name: str, metric_value: float,
                 metric_type: str, component: str, timestamp: datetime = None,
                 user_id: str = None, tags: Dict[str, Any] = None):
        self.metric_id = metric_id
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.metric_type = metric_type
        self.component = component
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
        self.tags = tags or {}
        self.threshold_config = {}
        self.created_at = datetime.now()


class AIGenerationJob(Base):
    """SQLAlchemy model for AI generation jobs"""
    __tablename__ = "ai_generation_jobs"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(String(255), nullable=False, unique=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    
    # Job configuration
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    quality_setting = Column(String(20), default="standard")
    model_name = Column(String(100), default="veo-1")
    generation_config = Column(JSON)  # Model-specific configuration
    
    # Status and progress
    status = Column(String(30), default="pending")  # pending, processing, completed, failed
    progress_percentage = Column(Float, default=0.0)
    error_message = Column(Text)
    
    # Timing
    created_at = Column(DateTime, default=datetime.now)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    estimated_completion = Column(DateTime)
    
    # Results
    output_file_path = Column(String(500))
    output_metadata = Column(JSON)
    quality_score = Column(Float)
    user_rating = Column(Integer)  # 1-5 stars
    
    def __init__(self, job_id: str, user_id: str, prompt: str,
                 priority: str = "medium", quality_setting: str = "standard",
                 estimated_completion: datetime = None):
        self.job_id = job_id
        self.user_id = user_id
        self.prompt = prompt
        self.priority = priority
        self.quality_setting = quality_setting
        self.model_name = "veo-1"
        self.generation_config = {}
        self.status = "pending"
        self.progress_percentage = 0.0
        self.created_at = datetime.now()
        self.estimated_completion = estimated_completion or (datetime.now() + timedelta(minutes=10))
        self.output_metadata = {}
    
    def start_processing(self):
        """Mark job as started"""
        self.status = "processing"
        self.started_at = datetime.now()
    
    def update_progress(self, percentage: float):
        """Update job progress"""
        self.progress_percentage = min(100.0, max(0.0, percentage))
    
    def complete_job(self, output_file_path: str, quality_score: float = None):
        """Mark job as completed"""
        self.status = "completed"
        self.progress_percentage = 100.0
        self.completed_at = datetime.now()
        self.output_file_path = output_file_path
        self.quality_score = quality_score
    
    def fail_job(self, error_message: str):
        """Mark job as failed"""
        self.status = "failed"
        self.error_message = error_message
        self.completed_at = datetime.now()


class AIAlert(Base):
    """SQLAlchemy model for AI system alerts"""
    __tablename__ = "ai_alerts"
    
    id = Column(Integer, primary_key=True)
    alert_id = Column(String(255), nullable=False, unique=True, index=True)
    component_id = Column(String(255), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)
    level = Column(String(20), nullable=False)  # info, warning, critical, success
    
    # Alert content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(JSON)  # Additional alert details
    
    # Status and resolution
    status = Column(String(20), default="active")  # active, acknowledged, resolved, dismissed
    acknowledged_by = Column(String(255))
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Timestamps
    triggered_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)
    
    def __init__(self, alert_id: str, component_id: str, alert_type: str,
                 level: str, title: str, message: str, details: Dict[str, Any] = None):
        self.alert_id = alert_id
        self.component_id = component_id
        self.alert_type = alert_type
        self.level = level
        self.title = title
        self.message = message
        self.details = details or {}
        self.status = "active"
        self.triggered_at = datetime.now()
        # Auto-expire info alerts after 1 hour, warnings after 24 hours
        if level == "info":
            self.expires_at = datetime.now() + timedelta(hours=1)
        elif level == "warning":
            self.expires_at = datetime.now() + timedelta(hours=24)
        # Critical alerts don't auto-expire
    
    def acknowledge(self, user_id: str):
        """Acknowledge the alert"""
        self.status = "acknowledged"
        self.acknowledged_by = user_id
        self.acknowledged_at = datetime.now()
    
    def resolve(self, user_id: str, notes: str = None):
        """Resolve the alert"""
        self.status = "resolved"
        self.resolved_at = datetime.now()
        self.resolution_notes = notes


class UserPreference(Base):
    """SQLAlchemy model for user AI preferences"""
    __tablename__ = "user_ai_preferences"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    component_id = Column(String(255), nullable=False, index=True)
    preference_key = Column(String(255), nullable=False)
    preference_value = Column(JSON, nullable=False)
    
    # Learning and adaptation
    confidence_score = Column(Float, default=0.5)  # How confident we are in this preference
    interaction_count = Column(Integer, default=0)  # How many times this preference was used
    last_confirmed = Column(DateTime)  # Last time user confirmed this preference
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __init__(self, user_id: str, component_id: str, preference_key: str,
                 preference_value: Any, confidence_score: float = 0.5):
        self.user_id = user_id
        self.component_id = component_id
        self.preference_key = preference_key
        self.preference_value = preference_value
        self.confidence_score = confidence_score
        self.interaction_count = 0
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update_preference(self, new_value: Any, increase_confidence: bool = True):
        """Update preference value and confidence"""
        self.preference_value = new_value
        self.interaction_count += 1
        if increase_confidence:
            self.confidence_score = min(1.0, self.confidence_score + 0.1)
        self.last_confirmed = datetime.now()
        self.updated_at = datetime.now()


class ResponsiveLayout(Base):
    """SQLAlchemy model for responsive layouts"""
    __tablename__ = "responsive_layouts"
    
    id = Column(Integer, primary_key=True)
    layout_id = Column(String(255), nullable=False, unique=True, index=True)
    layout_name = Column(String(255), nullable=False)
    layout_type = Column(String(50), default="dashboard")
    
    # Layout configuration
    breakpoints = Column(JSON, nullable=False)  # Screen size breakpoints
    components = Column(JSON, nullable=False)  # Component configurations
    grid_config = Column(JSON)  # Grid system configuration
    
    # User customizations
    user_customizations = Column(JSON)  # User-specific layout modifications
    
    # Metadata
    created_by = Column(String(255), nullable=False)
    is_public = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __init__(self, layout_id: str, layout_name: str, breakpoints: Dict[str, Any],
                 components: List[Dict[str, Any]], created_by: str):
        self.layout_id = layout_id
        self.layout_name = layout_name
        self.breakpoints = breakpoints
        self.components = components
        self.created_by = created_by
        self.grid_config = {}
        self.user_customizations = {}
        self.is_public = False
        self.is_template = False
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


# Pydantic models for API and data validation

class ComponentConfig(BaseModel):
    """Pydantic model for component configuration"""
    type: ComponentType = Field(..., description="Component type")
    title: str = Field(..., description="Component title")
    data_sources: List[str] = Field([], description="Data sources")
    refresh_interval: int = Field(5000, description="Refresh interval in milliseconds")
    auto_refresh: bool = Field(True, description="Enable auto refresh")
    styling: Dict[str, Any] = Field({}, description="Styling configuration")
    permissions: Dict[str, Any] = Field({}, description="Permission configuration")
    
    class Config:
        from_attributes = True


class MetricData(BaseModel):
    """Pydantic model for metric data"""
    metric_name: str = Field(..., description="Metric name")
    metric_value: float = Field(..., description="Metric value")
    metric_type: str = Field(..., description="Metric type")
    component: str = Field(..., description="Source component")
    timestamp: Optional[datetime] = Field(None, description="Metric timestamp")
    tags: Dict[str, Any] = Field({}, description="Additional tags")
    
    class Config:
        from_attributes = True


class GenerationJobData(BaseModel):
    """Pydantic model for generation job data"""
    job_id: str = Field(..., description="Job ID")
    user_id: str = Field(..., description="User ID")
    prompt: str = Field(..., description="Generation prompt")
    priority: str = Field("medium", description="Job priority")
    status: str = Field("pending", description="Job status")
    created_at: datetime = Field(..., description="Creation timestamp")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    
    class Config:
        from_attributes = True


class AlertData(BaseModel):
    """Pydantic model for alert data"""
    alert_id: str = Field(..., description="Alert ID")
    component_id: str = Field(..., description="Component ID")
    level: AlertLevel = Field(..., description="Alert level")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    status: str = Field("active", description="Alert status")
    triggered_at: datetime = Field(..., description="Alert trigger time")
    
    class Config:
        from_attributes = True


class UserPreferenceData(BaseModel):
    """Pydantic model for user preference data"""
    user_id: str = Field(..., description="User ID")
    component_id: str = Field(..., description="Component ID")
    preferences: Dict[str, Any] = Field(..., description="User preferences")
    confidence_scores: Dict[str, float] = Field({}, description="Confidence scores")
    
    class Config:
        from_attributes = True


class LayoutConfig(BaseModel):
    """Pydantic model for layout configuration"""
    layout_name: str = Field(..., description="Layout name")
    breakpoints: Dict[str, Dict[str, Any]] = Field(..., description="Responsive breakpoints")
    components: List[Dict[str, Any]] = Field(..., description="Component configurations")
    auto_arrange: bool = Field(True, description="Enable auto arrangement")
    save_user_layout: bool = Field(True, description="Save user customizations")
    
    class Config:
        from_attributes = True


class ComponentData(BaseModel):
    """Pydantic model for component data response"""
    component_id: str
    type: str
    title: str
    data: Dict[str, Any]
    last_updated: datetime
    status: str
    
    class Config:
        from_attributes = True