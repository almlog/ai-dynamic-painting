"""AI-specific logging configuration for Phase 2."""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

# Create logs directory if not exists
LOG_DIR = Path("./logs/ai")
LOG_DIR.mkdir(parents=True, exist_ok=True)


class AILogFormatter(logging.Formatter):
    """Custom formatter for AI operations with structured logging."""
    
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        
        # Add AI-specific context if present
        if hasattr(record, 'ai_context'):
            log_obj['ai_context'] = record.ai_context
            
        # Add metrics if present
        if hasattr(record, 'metrics'):
            log_obj['metrics'] = record.metrics
            
        # Add cost tracking if present
        if hasattr(record, 'api_cost'):
            log_obj['api_cost'] = record.api_cost
            
        return json.dumps(log_obj)


def setup_ai_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Setup AI-specific logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("ai_system")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler with standard formatting
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    )
    logger.addHandler(console_handler)
    
    # File handler with JSON formatting for structured logs
    if log_file is None:
        log_file = LOG_DIR / "ai_system.log"
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10_000_000,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(AILogFormatter())
    logger.addHandler(file_handler)
    
    # Separate handlers for different AI components
    
    # VEO API specific logger
    veo_logger = logging.getLogger("ai_system.veo_api")
    veo_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "veo_api.log",
        maxBytes=5_000_000,
        backupCount=3
    )
    veo_handler.setFormatter(AILogFormatter())
    veo_logger.addHandler(veo_handler)
    
    # Scheduler specific logger
    scheduler_logger = logging.getLogger("ai_system.scheduler")
    scheduler_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "scheduler.log",
        maxBytes=5_000_000,
        backupCount=3
    )
    scheduler_handler.setFormatter(AILogFormatter())
    scheduler_logger.addHandler(scheduler_handler)
    
    # Learning system logger
    learning_logger = logging.getLogger("ai_system.learning")
    learning_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "learning.log",
        maxBytes=5_000_000,
        backupCount=3
    )
    learning_handler.setFormatter(AILogFormatter())
    learning_logger.addHandler(learning_handler)
    
    # Cost tracking logger
    cost_logger = logging.getLogger("ai_system.cost")
    cost_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "api_cost.log",
        maxBytes=5_000_000,
        backupCount=10  # Keep more history for cost analysis
    )
    cost_handler.setFormatter(AILogFormatter())
    cost_logger.addHandler(cost_handler)
    
    logger.info("AI logging system initialized", extra={
        "ai_context": {
            "phase": "2",
            "component": "logging",
            "status": "initialized"
        }
    })
    
    return logger


class AIMetricsLogger:
    """Logger for AI performance metrics and monitoring."""
    
    def __init__(self):
        self.logger = logging.getLogger("ai_system.metrics")
        handler = logging.handlers.RotatingFileHandler(
            LOG_DIR / "metrics.log",
            maxBytes=10_000_000,
            backupCount=5
        )
        handler.setFormatter(AILogFormatter())
        self.logger.addHandler(handler)
        
    def log_generation_metrics(
        self,
        prompt: str,
        generation_time: float,
        video_duration: float,
        api_calls: int,
        success: bool,
        error: Optional[str] = None
    ):
        """Log video generation metrics."""
        self.logger.info(
            "Video generation metrics",
            extra={
                "metrics": {
                    "prompt_length": len(prompt),
                    "generation_time_seconds": generation_time,
                    "video_duration_seconds": video_duration,
                    "api_calls": api_calls,
                    "success": success,
                    "error": error
                }
            }
        )
        
    def log_learning_metrics(
        self,
        user_feedback: str,
        preference_score: float,
        model_update_time: float
    ):
        """Log user learning system metrics."""
        self.logger.info(
            "Learning system metrics",
            extra={
                "metrics": {
                    "user_feedback": user_feedback,
                    "preference_score": preference_score,
                    "model_update_time_seconds": model_update_time
                }
            }
        )
        
    def log_cost_metrics(
        self,
        api_name: str,
        operation: str,
        cost_usd: float,
        monthly_total: float
    ):
        """Log API cost metrics."""
        self.logger.warning(
            f"API cost tracked: ${cost_usd:.4f}",
            extra={
                "api_cost": {
                    "api": api_name,
                    "operation": operation,
                    "cost_usd": cost_usd,
                    "monthly_total_usd": monthly_total
                }
            }
        )