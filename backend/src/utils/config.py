"""
Configuration management - Phase 1 手動動画管理システム
T057: Centralized configuration management with environment-based settings
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    path: str = "data/ai_painting_development.db"
    echo_sql: bool = False
    connection_timeout: int = 20
    pool_recycle: int = 3600
    

@dataclass
class VideoConfig:
    """Video processing configuration settings"""
    upload_dir: str = "data/videos"
    max_file_size: int = 524288000  # 500MB
    allowed_formats: list = None
    thumbnail_dir: str = "data/thumbnails"
    ffmpeg_path: str = "/usr/bin/ffmpeg"
    
    def __post_init__(self):
        if self.allowed_formats is None:
            self.allowed_formats = ['mp4', 'avi', 'mov', 'mkv', 'webm']


@dataclass
class APIConfig:
    """API server configuration settings"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False
    workers: int = 1
    cors_origins: list = None
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173"
            ]


@dataclass
class HardwareConfig:
    """Hardware integration configuration settings"""
    m5stack_enabled: bool = True
    raspberry_pi_enabled: bool = True
    display_device: str = "/dev/fb0"
    video_output: str = "hdmi"
    m5stack_api_endpoint: str = "http://192.168.1.200"
    display_check_interval: int = 2  # seconds
    

@dataclass
class LoggingConfig:
    """Logging configuration settings"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_dir: str = "logs"
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    log_to_console: bool = True
    log_to_file: bool = True


@dataclass
class SecurityConfig:
    """Security configuration settings"""
    secret_key: str = ""
    session_timeout: int = 86400  # 24 hours
    max_login_attempts: int = 5
    rate_limit_per_minute: int = 60
    enable_cors: bool = True
    enable_csrf_protection: bool = False  # Disabled for Phase 1
    
    def __post_init__(self):
        if not self.secret_key:
            import secrets
            self.secret_key = secrets.token_urlsafe(32)


class Config:
    """Main configuration manager"""
    
    def __init__(self, config_file: Optional[str] = None, environment: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to configuration file
            environment: Environment name (dev, prod, test)
        """
        self.environment = environment or os.getenv('ENVIRONMENT', 'development')
        self.config_file = config_file or self._get_default_config_file()
        
        # Initialize configuration objects
        self.database = DatabaseConfig()
        self.video = VideoConfig()
        self.api = APIConfig()
        self.hardware = HardwareConfig()
        self.logging = LoggingConfig()
        self.security = SecurityConfig()
        
        # Load configuration
        self._load_configuration()
        self._apply_environment_overrides()
        self._validate_configuration()
    
    def _get_default_config_file(self) -> str:
        """
        Get default configuration file path based on environment
        
        Returns:
            Configuration file path
        """
        base_dir = Path(__file__).parent.parent.parent
        config_dir = base_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        if self.environment == 'production':
            return str(config_dir / "production.json")
        elif self.environment == 'test':
            return str(config_dir / "test.json")
        else:
            return str(config_dir / "development.json")
    
    def _load_configuration(self) -> None:
        """Load configuration from file if it exists"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Update configuration objects with loaded data
                if 'database' in config_data:
                    self._update_config_object(self.database, config_data['database'])
                
                if 'video' in config_data:
                    self._update_config_object(self.video, config_data['video'])
                
                if 'api' in config_data:
                    self._update_config_object(self.api, config_data['api'])
                
                if 'hardware' in config_data:
                    self._update_config_object(self.hardware, config_data['hardware'])
                
                if 'logging' in config_data:
                    self._update_config_object(self.logging, config_data['logging'])
                
                if 'security' in config_data:
                    self._update_config_object(self.security, config_data['security'])
                    
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load configuration file {self.config_file}: {e}")
    
    def _update_config_object(self, config_obj: Any, config_data: Dict[str, Any]) -> None:
        """
        Update configuration object with data from config file
        
        Args:
            config_obj: Configuration object to update
            config_data: Configuration data dictionary
        """
        for key, value in config_data.items():
            if hasattr(config_obj, key):
                setattr(config_obj, key, value)
    
    def _apply_environment_overrides(self) -> None:
        """Apply environment variable overrides"""
        # Database overrides
        if os.getenv('DATABASE_PATH'):
            self.database.path = os.getenv('DATABASE_PATH')
        if os.getenv('DATABASE_ECHO'):
            self.database.echo_sql = os.getenv('DATABASE_ECHO').lower() == 'true'
        
        # API overrides
        if os.getenv('API_HOST'):
            self.api.host = os.getenv('API_HOST')
        if os.getenv('API_PORT'):
            self.api.port = int(os.getenv('API_PORT'))
        if os.getenv('API_DEBUG'):
            self.api.debug = os.getenv('API_DEBUG').lower() == 'true'
        
        # Video overrides
        if os.getenv('VIDEO_UPLOAD_DIR'):
            self.video.upload_dir = os.getenv('VIDEO_UPLOAD_DIR')
        if os.getenv('VIDEO_MAX_SIZE'):
            self.video.max_file_size = int(os.getenv('VIDEO_MAX_SIZE'))
        
        # Hardware overrides
        if os.getenv('M5STACK_ENDPOINT'):
            self.hardware.m5stack_api_endpoint = os.getenv('M5STACK_ENDPOINT')
        if os.getenv('HARDWARE_ENABLED'):
            enabled = os.getenv('HARDWARE_ENABLED').lower() == 'true'
            self.hardware.m5stack_enabled = enabled
            self.hardware.raspberry_pi_enabled = enabled
        
        # Logging overrides
        if os.getenv('LOG_LEVEL'):
            self.logging.level = os.getenv('LOG_LEVEL').upper()
        if os.getenv('LOG_DIR'):
            self.logging.log_dir = os.getenv('LOG_DIR')
        
        # Security overrides
        if os.getenv('SECRET_KEY'):
            self.security.secret_key = os.getenv('SECRET_KEY')
        if os.getenv('SESSION_TIMEOUT'):
            self.security.session_timeout = int(os.getenv('SESSION_TIMEOUT'))
    
    def _validate_configuration(self) -> None:
        """Validate configuration settings"""
        # Create required directories
        directories_to_create = [
            self.video.upload_dir,
            self.video.thumbnail_dir,
            self.logging.log_dir,
            os.path.dirname(self.database.path)
        ]
        
        for directory in directories_to_create:
            if directory:
                Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Validate numeric ranges
        if self.api.port < 1 or self.api.port > 65535:
            raise ValueError(f"Invalid API port: {self.api.port}")
        
        if self.video.max_file_size < 1:
            raise ValueError(f"Invalid max file size: {self.video.max_file_size}")
        
        if self.security.session_timeout < 60:
            raise ValueError(f"Session timeout too short: {self.security.session_timeout}")
    
    def save_configuration(self, config_file: Optional[str] = None) -> bool:
        """
        Save current configuration to file
        
        Args:
            config_file: Optional custom config file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            target_file = config_file or self.config_file
            
            config_dict = {
                'database': asdict(self.database),
                'video': asdict(self.video),
                'api': asdict(self.api),
                'hardware': asdict(self.hardware),
                'logging': asdict(self.logging),
                'security': asdict(self.security),
                'environment': self.environment
            }
            
            # Ensure config directory exists
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            
            with open(target_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            return True
            
        except (IOError, OSError) as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def get_database_url(self) -> str:
        """
        Get database connection URL
        
        Returns:
            SQLite database URL string
        """
        return f"sqlite:///{self.database.path}"
    
    def get_cors_settings(self) -> Dict[str, Any]:
        """
        Get CORS settings for FastAPI
        
        Returns:
            CORS settings dictionary
        """
        return {
            "allow_origins": self.api.cors_origins,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["*"],
        }
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == 'development'
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == 'production'
    
    def is_testing(self) -> bool:
        """Check if running in test environment"""
        return self.environment == 'test'


# Global configuration instance
_config: Optional[Config] = None


def get_config(config_file: Optional[str] = None, 
               environment: Optional[str] = None) -> Config:
    """
    Get global configuration instance
    
    Args:
        config_file: Optional configuration file path
        environment: Optional environment name
        
    Returns:
        Configuration instance
    """
    global _config
    
    if _config is None:
        _config = Config(config_file, environment)
    
    return _config


def reload_config(config_file: Optional[str] = None, 
                 environment: Optional[str] = None) -> Config:
    """
    Reload global configuration instance
    
    Args:
        config_file: Optional configuration file path
        environment: Optional environment name
        
    Returns:
        New configuration instance
    """
    global _config
    _config = Config(config_file, environment)
    return _config


def create_default_config_file(environment: str = 'development') -> str:
    """
    Create default configuration file for specified environment
    
    Args:
        environment: Environment name
        
    Returns:
        Path to created configuration file
    """
    config = Config(environment=environment)
    config_file = config._get_default_config_file()
    config.save_configuration(config_file)
    return config_file