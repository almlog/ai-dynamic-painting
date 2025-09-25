"""
Data source model for multi-source integration.
Stores configuration and metadata for various data sources.
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum

Base = declarative_base()


class SourceType(str, Enum):
    """Enumeration of supported data source types"""
    WEATHER_API = "weather_api"
    TIME_API = "time_api"
    SENSOR_DEVICE = "sensor_device"
    M5STACK = "m5stack"
    CALENDAR_API = "calendar_api"
    USER_INPUT = "user_input"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"


class AuthType(str, Enum):
    """Enumeration of authentication types"""
    NONE = "none"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    CUSTOM = "custom"


class DataSource(Base):
    """SQLAlchemy model for storing data source configurations"""
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True)
    source_id = Column(String(255), nullable=False, unique=True, index=True)
    source_type = Column(String(50), nullable=False)  # weather_api, sensor_device, etc.
    source_name = Column(String(255), nullable=False)
    description = Column(Text)
    endpoint_url = Column(String(500))  # API endpoint or device address
    authentication_type = Column(String(50), default="none")
    configuration = Column(JSON)  # JSON field for source-specific config
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)  # 1 = highest priority
    retry_count = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=30)
    cache_ttl_seconds = Column(Integer, default=300)  # 5 minutes default
    last_success = Column(DateTime)
    last_failure = Column(DateTime)
    failure_count = Column(Integer, default=0)
    success_rate = Column(Float, default=1.0)
    average_response_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __init__(self, source_id: str, source_type: str, source_name: str,
                 endpoint_url: str = None, authentication_type: str = "none",
                 configuration: Dict[str, Any] = None, is_active: bool = True,
                 priority: int = 1):
        self.source_id = source_id
        self.source_type = source_type
        self.source_name = source_name
        self.endpoint_url = endpoint_url
        self.authentication_type = authentication_type
        self.configuration = configuration or {}
        self.is_active = is_active
        self.priority = priority
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update_success_metrics(self, response_time_ms: int):
        """Update metrics after successful operation"""
        self.last_success = datetime.now()
        self.failure_count = 0  # Reset failure count on success
        
        # Update average response time
        if self.average_response_time_ms == 0:
            self.average_response_time_ms = response_time_ms
        else:
            self.average_response_time_ms = int(
                (self.average_response_time_ms + response_time_ms) / 2
            )
        
        self.updated_at = datetime.now()
    
    def update_failure_metrics(self):
        """Update metrics after failed operation"""
        self.last_failure = datetime.now()
        self.failure_count += 1
        
        # Deactivate source if too many failures
        if self.failure_count >= 5:
            self.is_active = False
        
        self.updated_at = datetime.now()


class DataSourceConfig(BaseModel):
    """Pydantic model for data source configuration"""
    source_type: SourceType = Field(..., description="Type of data source")
    source_name: str = Field(..., min_length=1, description="Human-readable name")
    description: Optional[str] = Field(None, description="Source description")
    endpoint: Optional[str] = Field(None, description="API endpoint or device address")
    authentication: AuthType = Field(AuthType.NONE, description="Authentication method")
    credentials: Optional[Dict[str, str]] = Field(None, description="Authentication credentials")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Source-specific parameters")
    priority: int = Field(1, ge=1, le=10, description="Priority level (1=highest)")
    timeout_seconds: int = Field(30, ge=5, le=300, description="Request timeout")
    retry_count: int = Field(3, ge=0, le=10, description="Retry attempts")
    cache_ttl_seconds: int = Field(300, ge=0, le=3600, description="Cache TTL")
    
    class Config:
        from_attributes = True


class SourceData(BaseModel):
    """Pydantic model for data returned from sources"""
    source_id: str
    source_type: str
    data: Dict[str, Any]
    timestamp: str
    response_time_ms: int
    cache_hit: bool = False
    quality_score: float = Field(1.0, ge=0.0, le=1.0)
    
    class Config:
        from_attributes = True


class AggregatedData(BaseModel):
    """Pydantic model for aggregated multi-source data"""
    aggregation_id: str
    sources: List[str]
    data: Dict[str, Any]
    aggregation_timestamp: str
    source_count: int
    successful_sources: int
    failed_sources: List[str]
    quality_score: float
    confidence_level: float
    
    class Config:
        from_attributes = True


class StreamConfig(BaseModel):
    """Pydantic model for real-time streaming configuration"""
    stream_id: str
    sources: List[str]
    interval_seconds: int = Field(1, ge=1, le=60)
    buffer_size: int = Field(100, ge=10, le=1000)
    auto_restart: bool = Field(True, description="Auto-restart on failure")
    context: Optional[Dict[str, Any]] = Field(None, description="Stream context")
    
    class Config:
        from_attributes = True


class WeatherData(BaseModel):
    """Pydantic model for weather data"""
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: int = Field(..., ge=0, le=100, description="Humidity percentage")
    weather_condition: str = Field(..., description="Weather condition")
    wind_speed: Optional[float] = Field(None, ge=0, description="Wind speed")
    pressure: Optional[float] = Field(None, description="Atmospheric pressure")
    visibility: Optional[float] = Field(None, description="Visibility in km")
    timestamp: str
    location: Dict[str, float]
    
    class Config:
        from_attributes = True


class TimeData(BaseModel):
    """Pydantic model for time/calendar data"""
    current_time: str
    time_of_day: str = Field(..., description="morning, afternoon, evening, night")
    day_of_week: str
    season: str = Field(..., description="spring, summer, autumn, winter")
    is_weekend: bool
    is_holiday: bool = False
    timezone: str
    
    class Config:
        from_attributes = True


class SensorData(BaseModel):
    """Pydantic model for sensor device data"""
    device_id: str
    temperature: Optional[float] = Field(None, description="Device temperature")
    humidity: Optional[int] = Field(None, ge=0, le=100, description="Humidity")
    light_level: int = Field(..., ge=0, le=100, description="Light level percentage")
    button_states: Dict[str, bool] = Field(..., description="Button states")
    battery_level: Optional[int] = Field(None, ge=0, le=100, description="Battery percentage")
    wifi_signal: Optional[int] = Field(None, ge=0, le=100, description="WiFi signal strength")
    timestamp: str
    
    class Config:
        from_attributes = True