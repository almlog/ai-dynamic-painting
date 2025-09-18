"""AI System Configuration model for managing AI system settings."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum
import json
import uuid
import copy

Base = declarative_base()


class ConfigCategory(Enum):
    """Enumeration for configuration categories"""
    VEO_API = "veo_api"
    GENERATION = "generation"
    SCHEDULING = "scheduling"
    LEARNING = "learning"
    COST = "cost"
    QUALITY = "quality"
    PERFORMANCE = "performance"
    SYSTEM = "system"


class AISystemConfig:
    """Simple AISystemConfig class for contract test compatibility"""
    
    def __init__(self, config_id=None, config_name=None, version=None, 
                 is_active=True, is_default=False, veo_api_settings=None,
                 generation_settings=None, scheduling_settings=None,
                 learning_settings=None, cost_settings=None, quality_settings=None,
                 performance_settings=None, creation_time=None, last_updated=None,
                 created_by=None, metadata=None):
        
        # Allow default constructor for testing
        if config_id is None and config_name is None:
            config_name = "default_config"
            
        self.config_id = config_id or f"config_{uuid.uuid4().hex[:8]}"
        self.config_name = config_name
        self.version = version or "1.0.0"
        self.is_active = is_active
        self.is_default = is_default
        self.creation_time = creation_time or datetime.now()
        self.last_updated = last_updated or datetime.now()
        self.created_by = created_by or "system"
        self.metadata = metadata or {}
        
        # Initialize settings with defaults
        self.veo_api_settings = veo_api_settings or self._default_veo_api_settings()
        self.generation_settings = generation_settings or self._default_generation_settings()
        self.scheduling_settings = scheduling_settings or self._default_scheduling_settings()
        self.learning_settings = learning_settings or self._default_learning_settings()
        self.cost_settings = cost_settings or self._default_cost_settings()
        self.quality_settings = quality_settings or self._default_quality_settings()
        self.performance_settings = performance_settings or self._default_performance_settings()
    
    def _default_veo_api_settings(self):
        """Default VEO API settings"""
        return {
            'api_key': '',
            'endpoint': 'https://api.veo.com',
            'timeout_seconds': 30,
            'max_retries': 3,
            'rate_limit_per_minute': 60
        }
    
    def _default_generation_settings(self):
        """Default generation settings"""
        return {
            'default_resolution': '1920x1080',
            'default_fps': 30,
            'max_duration_seconds': 120,
            'quality': 'high',
            'aspect_ratio': '16:9'
        }
    
    def _default_scheduling_settings(self):
        """Default scheduling settings"""
        return {
            'auto_schedule': True,
            'max_concurrent_tasks': 3,
            'retry_failed_tasks': True,
            'max_queue_size': 10
        }
    
    def _default_learning_settings(self):
        """Default learning settings"""
        return {
            'enable_learning': True,
            'learning_rate': 0.1,
            'min_feedback_count': 5,
            'preference_weight_decay': 0.05
        }
    
    def _default_cost_settings(self):
        """Default cost settings"""
        return {
            'monthly_budget_usd': 50.0,
            'cost_per_generation': 0.25,
            'alert_threshold': 0.8,
            'hard_limit': True
        }
    
    def _default_quality_settings(self):
        """Default quality settings"""
        return {
            'min_quality_score': 0.7,
            'auto_retry_low_quality': True,
            'quality_threshold': 0.8,
            'enable_quality_checks': True
        }
    
    def _default_performance_settings(self):
        """Default performance settings"""
        return {
            'max_response_time_ms': 5000,
            'enable_caching': True,
            'cache_duration_hours': 24,
            'parallel_processing': True
        }
    
    def get_setting(self, category, key):
        """Get a specific setting value"""
        category_settings = getattr(self, category, {})
        return category_settings.get(key)
    
    def set_setting(self, category, key, value):
        """Set a specific setting value"""
        if hasattr(self, category):
            category_settings = getattr(self, category)
            category_settings[key] = value
            self.last_updated = datetime.now()
    
    def configure_veo_api(self, api_key=None, endpoint=None, timeout_seconds=None, max_retries=None):
        """Configure VEO API settings"""
        if api_key is not None:
            self.veo_api_settings['api_key'] = api_key
        if endpoint is not None:
            self.veo_api_settings['endpoint'] = endpoint
        if timeout_seconds is not None:
            self.veo_api_settings['timeout_seconds'] = timeout_seconds
        if max_retries is not None:
            self.veo_api_settings['max_retries'] = max_retries
        self.last_updated = datetime.now()
    
    def configure_generation(self, default_resolution=None, default_fps=None, max_duration_seconds=None, quality=None):
        """Configure generation settings"""
        if default_resolution is not None:
            self.generation_settings['default_resolution'] = default_resolution
        if default_fps is not None:
            self.generation_settings['default_fps'] = default_fps
        if max_duration_seconds is not None:
            self.generation_settings['max_duration_seconds'] = max_duration_seconds
        if quality is not None:
            self.generation_settings['quality'] = quality
        self.last_updated = datetime.now()
    
    def configure_cost_limits(self, monthly_budget_usd=None, cost_per_generation=None, alert_threshold=None):
        """Configure cost limitation settings"""
        if monthly_budget_usd is not None:
            self.cost_settings['monthly_budget_usd'] = monthly_budget_usd
        if cost_per_generation is not None:
            self.cost_settings['cost_per_generation'] = cost_per_generation
        if alert_threshold is not None:
            self.cost_settings['alert_threshold'] = alert_threshold
        self.last_updated = datetime.now()
    
    def validate_veo_api_settings(self):
        """Validate VEO API settings"""
        settings = self.veo_api_settings
        return (
            settings.get('api_key', '') != '' and
            settings.get('endpoint', '').startswith('https://') and
            settings.get('timeout_seconds', 0) > 0 and
            settings.get('max_retries', 0) >= 0
        )
    
    def validate_generation_settings(self):
        """Validate generation settings"""
        settings = self.generation_settings
        return (
            settings.get('default_resolution', '') != '' and
            settings.get('default_fps', 0) > 0 and
            settings.get('max_duration_seconds', 0) > 0
        )
    
    def validate_cost_settings(self):
        """Validate cost settings"""
        settings = self.cost_settings
        return (
            settings.get('monthly_budget_usd', 0) > 0 and
            settings.get('cost_per_generation', 0) > 0 and
            0 <= settings.get('alert_threshold', 0) <= 1
        )
    
    def validate_all_settings(self):
        """Validate all configuration settings"""
        return (
            self.validate_veo_api_settings() and
            self.validate_generation_settings() and
            self.validate_cost_settings()
        )
    
    def get_validation_errors(self):
        """Get list of validation errors"""
        errors = []
        
        if not self.validate_veo_api_settings():
            errors.append("Invalid VEO API settings")
        if not self.validate_generation_settings():
            errors.append("Invalid generation settings")
        if not self.validate_cost_settings():
            errors.append("Invalid cost settings")
        
        return errors
    
    @classmethod
    def create_development_config(cls):
        """Create a development configuration template"""
        return cls(
            config_id=f"dev_{uuid.uuid4().hex[:8]}",
            config_name="Development Config",
            version="1.0.0",
            veo_api_settings={
                'api_key': 'dev_key',
                'endpoint': 'https://api-sandbox.veo.com',
                'timeout_seconds': 60,
                'max_retries': 5
            },
            generation_settings={
                'default_resolution': '1280x720',
                'default_fps': 24,
                'max_duration_seconds': 30,
                'quality': 'medium'
            },
            cost_settings={
                'monthly_budget_usd': 25.0,
                'cost_per_generation': 0.10,
                'alert_threshold': 0.7,
                'hard_limit': False
            }
        )
    
    @classmethod
    def create_production_config(cls):
        """Create a production configuration template"""
        return cls(
            config_id=f"prod_{uuid.uuid4().hex[:8]}",
            config_name="Production Config",
            version="1.0.0",
            veo_api_settings={
                'api_key': 'prod_key',
                'endpoint': 'https://api.veo.com',
                'timeout_seconds': 30,
                'max_retries': 3
            },
            generation_settings={
                'default_resolution': '1920x1080',
                'default_fps': 30,
                'max_duration_seconds': 120,
                'quality': 'high'
            },
            cost_settings={
                'monthly_budget_usd': 200.0,
                'cost_per_generation': 0.50,
                'alert_threshold': 0.8,
                'hard_limit': True
            }
        )
    
    @classmethod
    def create_testing_config(cls):
        """Create a testing configuration template"""
        return cls(
            config_id=f"test_{uuid.uuid4().hex[:8]}",
            config_name="Testing Config",
            version="1.0.0",
            veo_api_settings={
                'api_key': 'test_key',
                'endpoint': 'https://api-test.veo.com',
                'timeout_seconds': 15,
                'max_retries': 1
            },
            generation_settings={
                'default_resolution': '640x480',
                'default_fps': 15,
                'max_duration_seconds': 10,
                'quality': 'low'
            },
            cost_settings={
                'monthly_budget_usd': 5.0,
                'cost_per_generation': 0.01,
                'alert_threshold': 0.5,
                'hard_limit': True
            }
        )
    
    def export_config(self):
        """Export configuration to dictionary"""
        return {
            'config_id': self.config_id,
            'config_name': self.config_name,
            'version': self.version,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'veo_api_settings': copy.deepcopy(self.veo_api_settings),
            'generation_settings': copy.deepcopy(self.generation_settings),
            'scheduling_settings': copy.deepcopy(self.scheduling_settings),
            'learning_settings': copy.deepcopy(self.learning_settings),
            'cost_settings': copy.deepcopy(self.cost_settings),
            'quality_settings': copy.deepcopy(self.quality_settings),
            'performance_settings': copy.deepcopy(self.performance_settings),
            'creation_time': self.creation_time.isoformat() if self.creation_time else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'created_by': self.created_by,
            'metadata': copy.deepcopy(self.metadata)
        }
    
    @classmethod
    def import_config(cls, config_data):
        """Import configuration from dictionary"""
        # Parse datetime fields
        creation_time = None
        if config_data.get('creation_time'):
            creation_time = datetime.fromisoformat(config_data['creation_time'].replace('Z', '+00:00'))
        
        last_updated = None
        if config_data.get('last_updated'):
            last_updated = datetime.fromisoformat(config_data['last_updated'].replace('Z', '+00:00'))
        
        return cls(
            config_id=config_data.get('config_id'),
            config_name=config_data.get('config_name'),
            version=config_data.get('version'),
            is_active=config_data.get('is_active', True),
            is_default=config_data.get('is_default', False),
            veo_api_settings=config_data.get('veo_api_settings'),
            generation_settings=config_data.get('generation_settings'),
            scheduling_settings=config_data.get('scheduling_settings'),
            learning_settings=config_data.get('learning_settings'),
            cost_settings=config_data.get('cost_settings'),
            quality_settings=config_data.get('quality_settings'),
            performance_settings=config_data.get('performance_settings'),
            creation_time=creation_time,
            last_updated=last_updated,
            created_by=config_data.get('created_by'),
            metadata=config_data.get('metadata')
        )
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'config_id': self.config_id,
            'config_name': self.config_name,
            'version': self.version,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'veo_api_settings': self.veo_api_settings,
            'generation_settings': self.generation_settings,
            'scheduling_settings': self.scheduling_settings,
            'learning_settings': self.learning_settings,
            'cost_settings': self.cost_settings,
            'quality_settings': self.quality_settings,
            'performance_settings': self.performance_settings,
            'creation_time': self.creation_time.isoformat() if self.creation_time else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'created_by': self.created_by,
            'metadata': self.metadata,
            'is_valid': self.validate_all_settings(),
            'validation_errors': self.get_validation_errors()
        }


class AISystemConfigDB(Base):
    """SQLAlchemy model for AI system configurations."""
    
    __tablename__ = "ai_system_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_id = Column(String, unique=True, nullable=False, index=True)
    config_name = Column(String, nullable=False)
    version = Column(String, nullable=False, default="1.0.0")
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Configuration sections (JSON)
    veo_api_settings = Column(Text, nullable=True)
    generation_settings = Column(Text, nullable=True)
    scheduling_settings = Column(Text, nullable=True)
    learning_settings = Column(Text, nullable=True)
    cost_settings = Column(Text, nullable=True)
    quality_settings = Column(Text, nullable=True)
    performance_settings = Column(Text, nullable=True)
    
    # Metadata
    created_by = Column(String, nullable=True)
    config_metadata = Column(Text, nullable=True)  # JSON object
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AISystemConfigCreate(BaseModel):
    """Pydantic model for creating AI system configurations."""
    
    config_name: str = Field(..., min_length=1, max_length=100, description="Configuration name")
    version: Optional[str] = Field("1.0.0", description="Configuration version")
    veo_api_settings: Optional[Dict[str, Any]] = Field(None, description="VEO API settings")
    generation_settings: Optional[Dict[str, Any]] = Field(None, description="Generation settings")
    scheduling_settings: Optional[Dict[str, Any]] = Field(None, description="Scheduling settings")
    learning_settings: Optional[Dict[str, Any]] = Field(None, description="Learning settings")
    cost_settings: Optional[Dict[str, Any]] = Field(None, description="Cost settings")
    quality_settings: Optional[Dict[str, Any]] = Field(None, description="Quality settings")
    performance_settings: Optional[Dict[str, Any]] = Field(None, description="Performance settings")
    created_by: Optional[str] = Field(None, description="Creator identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AISystemConfigUpdate(BaseModel):
    """Pydantic model for updating AI system configurations."""
    
    config_name: Optional[str] = Field(None, min_length=1, max_length=100)
    version: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    veo_api_settings: Optional[Dict[str, Any]] = None
    generation_settings: Optional[Dict[str, Any]] = None
    scheduling_settings: Optional[Dict[str, Any]] = None
    learning_settings: Optional[Dict[str, Any]] = None
    cost_settings: Optional[Dict[str, Any]] = None
    quality_settings: Optional[Dict[str, Any]] = None
    performance_settings: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AISystemConfigResponse(BaseModel):
    """Pydantic model for AI system configuration responses."""
    
    id: int
    config_id: str
    config_name: str
    version: str = "1.0.0"
    is_active: bool = True
    is_default: bool = False
    veo_api_settings: Optional[Dict[str, Any]] = None
    generation_settings: Optional[Dict[str, Any]] = None
    scheduling_settings: Optional[Dict[str, Any]] = None
    learning_settings: Optional[Dict[str, Any]] = None
    cost_settings: Optional[Dict[str, Any]] = None
    quality_settings: Optional[Dict[str, Any]] = None
    performance_settings: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    # Calculated properties
    is_valid: bool = False
    validation_errors: List[str] = []
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def from_db(cls, db_config: AISystemConfigDB) -> "AISystemConfigResponse":
        """Create response model from database model."""
        
        # Parse JSON settings
        def parse_json_field(field_value):
            if field_value:
                try:
                    return json.loads(field_value)
                except json.JSONDecodeError:
                    return None
            return None
        
        veo_api_settings = parse_json_field(db_config.veo_api_settings)
        generation_settings = parse_json_field(db_config.generation_settings)
        scheduling_settings = parse_json_field(db_config.scheduling_settings)
        learning_settings = parse_json_field(db_config.learning_settings)
        cost_settings = parse_json_field(db_config.cost_settings)
        quality_settings = parse_json_field(db_config.quality_settings)
        performance_settings = parse_json_field(db_config.performance_settings)
        metadata = parse_json_field(db_config.config_metadata)
        
        # Create temporary config object for validation
        temp_config = AISystemConfig(
            config_id=db_config.config_id,
            config_name=db_config.config_name,
            version=db_config.version,
            veo_api_settings=veo_api_settings,
            generation_settings=generation_settings,
            cost_settings=cost_settings
        )
        
        is_valid = temp_config.validate_all_settings()
        validation_errors = temp_config.get_validation_errors()
        
        return cls(
            id=db_config.id,
            config_id=db_config.config_id,
            config_name=db_config.config_name,
            version=db_config.version,
            is_active=db_config.is_active,
            is_default=db_config.is_default,
            veo_api_settings=veo_api_settings,
            generation_settings=generation_settings,
            scheduling_settings=scheduling_settings,
            learning_settings=learning_settings,
            cost_settings=cost_settings,
            quality_settings=quality_settings,
            performance_settings=performance_settings,
            created_by=db_config.created_by,
            metadata=metadata,
            created_at=db_config.created_at,
            updated_at=db_config.updated_at,
            is_valid=is_valid,
            validation_errors=validation_errors
        )


class AISystemConfigStats(BaseModel):
    """Statistics for AI system configurations."""
    
    total_configs: int = 0
    active_configs: int = 0
    inactive_configs: int = 0
    default_configs: int = 0
    
    # Version distribution
    version_distribution: Dict[str, int] = {}
    
    # Validation statistics
    valid_configs: int = 0
    invalid_configs: int = 0
    
    # Settings completion
    configs_with_veo_api: int = 0
    configs_with_generation: int = 0
    configs_with_cost_limits: int = 0
    
    class Config:
        json_encoders = {
            float: lambda v: round(v, 2)
        }