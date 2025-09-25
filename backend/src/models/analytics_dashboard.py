"""
Analytics dashboard model for managing data visualization and reporting.
Supports real-time metrics, custom widgets, and dashboard sharing.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON, Float
from sqlalchemy.orm import declarative_base
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum

Base = declarative_base()


class DashboardType(str, Enum):
    """Enumeration of dashboard types"""
    PERFORMANCE = "performance"
    BUSINESS = "business" 
    SYSTEM = "system"
    CUSTOM = "custom"
    AI_METRICS = "ai_metrics"


class WidgetType(str, Enum):
    """Enumeration of widget types"""
    METRIC_CARD = "metric_card"
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    GAUGE_CHART = "gauge_chart"
    HEATMAP = "heatmap"
    TABLE = "table"
    TIME_SERIES = "time_series"


class MetricType(str, Enum):
    """Enumeration of metric types"""
    COUNT = "count"
    PERCENTAGE = "percentage"
    DURATION_MS = "duration_ms"
    BYTES = "bytes"
    RATE = "rate"
    GAUGE = "gauge"


class AnalyticsDashboard(Base):
    """SQLAlchemy model for storing analytics dashboards"""
    __tablename__ = "analytics_dashboards"
    
    id = Column(Integer, primary_key=True)
    dashboard_id = Column(String(255), nullable=False, unique=True, index=True)
    dashboard_name = Column(String(255), nullable=False)
    dashboard_type = Column(String(50), nullable=False)
    owner_id = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Dashboard configuration
    dashboard_config = Column(JSON)  # refresh_interval, auto_refresh, timezone, etc.
    widgets = Column(JSON)  # List of widget configurations
    layout = Column(JSON)  # Dashboard layout configuration
    
    # Sharing and permissions
    visibility = Column(String(20), default="private")  # private, public, shared
    shared_with = Column(JSON)  # List of user IDs with access
    share_settings = Column(JSON)  # Sharing configuration
    
    # Metadata
    tags = Column(JSON)  # Dashboard tags for organization
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_viewed_at = Column(DateTime)
    view_count = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_favorite = Column(Boolean, default=False)
    
    def __init__(self, dashboard_id: str, dashboard_name: str, dashboard_type: str,
                 owner_id: str, dashboard_config: Dict[str, Any] = None,
                 widgets: List[Dict[str, Any]] = None, description: str = None):
        self.dashboard_id = dashboard_id
        self.dashboard_name = dashboard_name
        self.dashboard_type = dashboard_type
        self.owner_id = owner_id
        self.description = description
        self.dashboard_config = dashboard_config or {}
        self.widgets = widgets or []
        self.layout = {}
        self.visibility = "private"
        self.shared_with = []
        self.share_settings = {}
        self.tags = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.view_count = 0
        self.is_active = True
        self.is_favorite = False
    
    def add_widget(self, widget_config: Dict[str, Any]):
        """Add a widget to the dashboard"""
        if not self.widgets:
            self.widgets = []
        self.widgets.append(widget_config)
        self.updated_at = datetime.now()
    
    def remove_widget(self, widget_id: str):
        """Remove a widget from the dashboard"""
        if self.widgets:
            self.widgets = [w for w in self.widgets if w.get("widget_id") != widget_id]
            self.updated_at = datetime.now()
    
    def update_widget(self, widget_id: str, widget_config: Dict[str, Any]):
        """Update a widget configuration"""
        if self.widgets:
            for i, widget in enumerate(self.widgets):
                if widget.get("widget_id") == widget_id:
                    self.widgets[i] = widget_config
                    self.updated_at = datetime.now()
                    break
    
    def record_view(self):
        """Record a dashboard view"""
        self.view_count += 1
        self.last_viewed_at = datetime.now()
        self.updated_at = datetime.now()


class MetricEntry(Base):
    """SQLAlchemy model for storing metrics data"""
    __tablename__ = "metric_entries"
    
    id = Column(Integer, primary_key=True)
    metric_id = Column(String(255), nullable=False, unique=True, index=True)
    metric_name = Column(String(255), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50), nullable=False)
    component = Column(String(100), nullable=False, index=True)
    
    # Context and metadata
    tags = Column(JSON)  # Additional metadata tags
    dimensions = Column(JSON)  # Dimensional data for grouping
    context_data = Column(JSON)  # Additional context information
    
    # Timestamps
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)
    
    def __init__(self, metric_id: str, metric_name: str, metric_value: float,
                 metric_type: str, component: str, timestamp: datetime = None,
                 tags: Dict[str, Any] = None, dimensions: Dict[str, Any] = None):
        self.metric_id = metric_id
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.metric_type = metric_type
        self.component = component
        self.timestamp = timestamp or datetime.now()
        self.tags = tags or {}
        self.dimensions = dimensions or {}
        self.context_data = {}
        self.created_at = datetime.now()


class AlertRule(Base):
    """SQLAlchemy model for storing alert rules"""
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True)
    rule_id = Column(String(255), nullable=False, unique=True, index=True)
    rule_name = Column(String(255), nullable=False)
    metric_name = Column(String(255), nullable=False, index=True)
    condition = Column(String(50), nullable=False)  # greater_than, less_than, equals, etc.
    threshold = Column(Float, nullable=False)
    time_window = Column(String(20), nullable=False)  # 5m, 1h, 24h, etc.
    severity = Column(String(20), nullable=False)  # info, warning, critical
    
    # Notification settings
    notification_channels = Column(JSON)  # email, slack, webhook, etc.
    notification_template = Column(Text)
    cooldown_period = Column(Integer, default=300)  # seconds
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime)
    trigger_count = Column(Integer, default=0)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __init__(self, rule_id: str, rule_name: str, metric_name: str,
                 condition: str, threshold: float, time_window: str,
                 severity: str, created_by: str, notification_channels: List[str] = None):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.metric_name = metric_name
        self.condition = condition
        self.threshold = threshold
        self.time_window = time_window
        self.severity = severity
        self.created_by = created_by
        self.notification_channels = notification_channels or []
        self.cooldown_period = 300
        self.is_active = True
        self.trigger_count = 0
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


# Pydantic models for API and data validation

class DashboardConfig(BaseModel):
    """Pydantic model for dashboard configuration"""
    name: str = Field(..., description="Dashboard name")
    type: DashboardType = Field(..., description="Dashboard type")
    owner_id: str = Field(..., description="Dashboard owner user ID")
    description: Optional[str] = Field(None, description="Dashboard description")
    widgets: List[Dict[str, Any]] = Field([], description="Widget configurations")
    refresh_interval: int = Field(300, description="Auto-refresh interval in seconds")
    auto_refresh: bool = Field(True, description="Enable auto-refresh")
    timezone: str = Field("UTC", description="Dashboard timezone")
    tags: List[str] = Field([], description="Dashboard tags")
    
    class Config:
        from_attributes = True


class WidgetConfig(BaseModel):
    """Pydantic model for widget configuration"""
    widget_id: str = Field(..., description="Unique widget identifier")
    widget_type: WidgetType = Field(..., description="Widget type")
    title: str = Field(..., description="Widget title")
    data_source: str = Field(..., description="Data source identifier")
    config: Dict[str, Any] = Field({}, description="Widget-specific configuration")
    position: Dict[str, int] = Field({}, description="Widget position and size")
    
    class Config:
        from_attributes = True


class MetricData(BaseModel):
    """Pydantic model for metric data"""
    metric_name: str = Field(..., description="Metric name")
    metric_value: float = Field(..., description="Metric value")
    metric_type: MetricType = Field(..., description="Metric type")
    component: str = Field(..., description="Component that generated the metric")
    timestamp: Optional[datetime] = Field(None, description="Metric timestamp")
    tags: Dict[str, Any] = Field({}, description="Metric tags")
    dimensions: Dict[str, Any] = Field({}, description="Metric dimensions")
    
    class Config:
        from_attributes = True


class AlertRuleConfig(BaseModel):
    """Pydantic model for alert rule configuration"""
    rule_name: str = Field(..., description="Alert rule name")
    metric_name: str = Field(..., description="Metric to monitor")
    condition: str = Field(..., description="Alert condition")
    threshold: float = Field(..., description="Alert threshold")
    time_window: str = Field(..., description="Time window for evaluation")
    severity: str = Field(..., description="Alert severity level")
    notification_channels: List[str] = Field([], description="Notification channels")
    cooldown_period: int = Field(300, description="Cooldown period in seconds")
    
    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    """Pydantic model for dashboard summary"""
    dashboard_id: str
    dashboard_name: str
    dashboard_type: str
    owner_id: str
    widget_count: int
    last_viewed_at: Optional[datetime]
    view_count: int
    is_favorite: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalyticsReport(BaseModel):
    """Pydantic model for analytics report"""
    report_id: str
    report_type: str
    time_period: str
    generated_at: datetime
    data_summary: Dict[str, Any]
    charts: List[Dict[str, Any]]
    insights: List[str]
    recommendations: List[str]
    
    class Config:
        from_attributes = True