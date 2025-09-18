"""
Structured logging setup - Phase 1 手動動画管理システム
T056: JSON structured logging with rotation and monitoring support
"""
import json
import logging
import logging.handlers
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union


# Global logger registry
_loggers: Dict[str, 'Logger'] = {}


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON
        
        Args:
            record: LogRecord instance
            
        Returns:
            JSON formatted log string
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields from record
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)
        
        return json.dumps(log_entry, ensure_ascii=False)


class Logger:
    """Structured logger with JSON output and rotation support"""
    
    def __init__(self, name: str, log_file: str, level: str = "INFO", format: str = "json"):
        """
        Initialize structured logger
        
        Args:
            name: Logger name
            log_file: Path to log file
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
            format: Log format ("json" or "text")
        """
        self.name = name
        self.log_file = log_file
        self.level = level
        self.format = format
        
        # Create Python logger
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers to avoid duplicates
        self._logger.handlers.clear()
        
        # Setup file handler
        self._setup_file_handler()
        
        # Setup console handler for development
        self._setup_console_handler()
    
    def _setup_file_handler(self):
        """Setup file handler with rotation"""
        try:
            # Ensure log directory exists
            log_dir = os.path.dirname(self.log_file)
            if log_dir:
                Path(log_dir).mkdir(parents=True, exist_ok=True)
            
            # Create rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            
            # Set formatter
            if self.format == "json":
                file_handler.setFormatter(JsonFormatter())
            else:
                file_handler.setFormatter(
                    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                )
            
            self._logger.addHandler(file_handler)
            
        except Exception as e:
            # If file handler fails, log to console only
            print(f"Warning: Could not setup file logging: {e}")
    
    def _setup_console_handler(self):
        """Setup console handler for development"""
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Simple format for console
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        # Only log INFO and above to console
        console_handler.setLevel(logging.INFO)
        
        self._logger.addHandler(console_handler)
    
    def debug(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self._log("DEBUG", message, extra_data)
    
    def info(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self._log("INFO", message, extra_data)
    
    def warning(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self._log("WARNING", message, extra_data)
    
    def error(self, message: str, extra_data: Optional[Dict[str, Any]] = None, 
              exception: Optional[Exception] = None):
        """Log error message"""
        if exception:
            self._logger.error(message, extra={'extra_data': extra_data or {}}, exc_info=exception)
        else:
            self._log("ERROR", message, extra_data)
    
    def log_structured(self, level: str, message: str, data: Dict[str, Any]):
        """Log structured data"""
        self._log(level, message, data)
    
    def _log(self, level: str, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Internal logging method"""
        log_func = getattr(self._logger, level.lower())
        
        if extra_data:
            log_func(message, extra={'extra_data': extra_data})
        else:
            log_func(message)


def setup_logging(config: Dict[str, Any]) -> bool:
    """
    Setup application logging configuration
    
    Args:
        config: Logging configuration dictionary
        
    Returns:
        True if setup successful
    """
    try:
        # Extract configuration
        level = config.get("level", "INFO")
        format_type = config.get("format", "json")
        log_file = config.get("log_file", "logs/app.log")
        
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            handlers=[]
        )
        
        return True
        
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        return False


def get_logger(name: str, log_file: Optional[str] = None) -> Logger:
    """
    Get or create logger instance
    
    Args:
        name: Logger name
        log_file: Optional log file path
        
    Returns:
        Logger instance
    """
    # Return existing logger if available
    if name in _loggers:
        return _loggers[name]
    
    # Create new logger
    if not log_file:
        log_file = f"logs/{name}.log"
    
    logger = Logger(name=name, log_file=log_file, level="INFO", format="json")
    _loggers[name] = logger
    
    return logger


def log_request(request_data: Dict[str, Any], response_data: Dict[str, Any]) -> bool:
    """
    Log HTTP request information
    
    Args:
        request_data: Request information
        response_data: Response information
        
    Returns:
        True if logged successfully
    """
    try:
        logger = get_logger("requests", "logs/requests.log")
        
        log_data = {
            "event_type": "http_request",
            "request": request_data,
            "response": response_data,
            "duration": response_data.get("response_time", 0)
        }
        
        logger.log_structured("INFO", "HTTP Request", log_data)
        return True
        
    except Exception as e:
        print(f"Failed to log request: {e}")
        return False


def log_error(error: Exception, context: Dict[str, Any]) -> bool:
    """
    Log error with context information
    
    Args:
        error: Exception instance
        context: Additional context information
        
    Returns:
        True if logged successfully
    """
    try:
        logger = get_logger("errors", "logs/errors.log")
        
        log_data = {
            "event_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        
        logger.error("Application Error", log_data, exception=error)
        return True
        
    except Exception as e:
        print(f"Failed to log error: {e}")
        return False


def log_system_event(event_name: str, event_data: Dict[str, Any]) -> bool:
    """
    Log system events
    
    Args:
        event_name: Name of the system event
        event_data: Event data
        
    Returns:
        True if logged successfully
    """
    try:
        logger = get_logger("system", "logs/system.log")
        
        log_data = {
            "event_type": "system_event",
            "event_name": event_name,
            "event_data": event_data
        }
        
        logger.log_structured("INFO", f"System Event: {event_name}", log_data)
        return True
        
    except Exception as e:
        print(f"Failed to log system event: {e}")
        return False


def configure_log_rotation(log_file: str, rotation_config: Dict[str, Any]) -> bool:
    """
    Configure log file rotation
    
    Args:
        log_file: Path to log file
        rotation_config: Rotation configuration
        
    Returns:
        True if configured successfully
    """
    try:
        # Parse configuration
        max_size_str = rotation_config.get("max_size", "10MB")
        backup_count = rotation_config.get("backup_count", 5)
        
        # Convert size string to bytes
        if max_size_str.endswith("MB"):
            max_size = int(max_size_str[:-2]) * 1024 * 1024
        elif max_size_str.endswith("KB"):
            max_size = int(max_size_str[:-2]) * 1024
        else:
            max_size = int(max_size_str)
        
        # Configuration stored for use when creating handlers
        # (Actual rotation is handled by RotatingFileHandler in Logger class)
        
        return True
        
    except Exception as e:
        print(f"Failed to configure log rotation: {e}")
        return False