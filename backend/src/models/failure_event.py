"""
Failure event model for tracking and managing system failures.
Supports recovery strategies, escalation, and failure analytics.
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum

Base = declarative_base()


class FailureSeverity(str, Enum):
    """Enumeration of failure severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStrategy(str, Enum):
    """Enumeration of recovery strategies"""
    RETRY_WITH_BACKOFF = "retry_with_backoff"
    CIRCUIT_BREAKER = "circuit_breaker"
    FALLBACK = "fallback"
    DEGRADED_MODE = "degraded_mode"
    HEALTH_CHECK_RECOVERY = "health_check_recovery"
    ESCALATION = "escalation"
    MANUAL_INTERVENTION = "manual_intervention"
    IGNORE = "ignore"


class RecoveryStatus(str, Enum):
    """Enumeration of recovery status"""
    NOT_ATTEMPTED = "not_attempted"
    IN_PROGRESS = "in_progress"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ESCALATED = "escalated"
    ABANDONED = "abandoned"


class CircuitState(str, Enum):
    """Enumeration of circuit breaker states"""
    CLOSED = "closed"    # Normal operation
    OPEN = "open"        # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


class FailureEvent(Base):
    """SQLAlchemy model for storing failure events"""
    __tablename__ = "failure_events"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(String(255), nullable=False, unique=True, index=True)
    event_type = Column(String(100), nullable=False)  # api_timeout, db_error, etc.
    component = Column(String(100), nullable=False, index=True)  # Component that failed
    severity = Column(String(20), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text)
    
    # Context and metadata
    context_data = Column(JSON)  # Additional context about the failure
    user_id = Column(String(255), index=True)
    request_id = Column(String(255), index=True)
    session_id = Column(String(255), index=True)
    
    # Recovery configuration
    recovery_strategy = Column(String(50), nullable=False)
    max_retry_attempts = Column(Integer, default=3)
    retry_delay_seconds = Column(Integer, default=5)
    backoff_multiplier = Column(Float, default=2.0)
    circuit_breaker_threshold = Column(Integer, default=5)
    
    # Recovery tracking
    recovery_status = Column(String(20), default="not_attempted")
    recovery_attempts = Column(Integer, default=0)
    last_recovery_attempt = Column(DateTime)
    recovery_started_at = Column(DateTime)
    recovery_completed_at = Column(DateTime)
    recovery_success = Column(Boolean, default=False)
    
    # Escalation
    escalation_level = Column(Integer, default=0)
    escalated_at = Column(DateTime)
    escalation_reason = Column(Text)
    
    # Analytics and metrics
    occurrence_count = Column(Integer, default=1)  # How many times this failure occurred
    first_occurrence = Column(DateTime)
    last_occurrence = Column(DateTime)
    average_recovery_time_seconds = Column(Float, default=0.0)
    
    # Resolution
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolution_method = Column(String(100))
    resolution_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __init__(self, event_id: str, event_type: str, component: str,
                 severity: str, error_message: str, context_data: Dict[str, Any] = None,
                 recovery_strategy: str = "retry_with_backoff", max_retry_attempts: int = 3):
        self.event_id = event_id
        self.event_type = event_type
        self.component = component
        self.severity = severity
        self.error_message = error_message
        self.context_data = context_data or {}
        self.recovery_strategy = recovery_strategy
        self.max_retry_attempts = max_retry_attempts
        self.recovery_status = RecoveryStatus.NOT_ATTEMPTED.value
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.first_occurrence = datetime.now()
        self.last_occurrence = datetime.now()
    
    def start_recovery(self):
        """Mark recovery as started"""
        self.recovery_status = RecoveryStatus.IN_PROGRESS.value
        self.recovery_started_at = datetime.now()
        self.updated_at = datetime.now()
    
    def record_recovery_attempt(self, success: bool = False):
        """Record a recovery attempt"""
        self.recovery_attempts += 1
        self.last_recovery_attempt = datetime.now()
        
        if success:
            self.recovery_status = RecoveryStatus.SUCCEEDED.value
            self.recovery_success = True
            self.recovery_completed_at = datetime.now()
            self.resolved = True
            self.resolved_at = datetime.now()
            self.resolution_method = self.recovery_strategy
        elif self.recovery_attempts >= self.max_retry_attempts:
            self.recovery_status = RecoveryStatus.FAILED.value
        
        self.updated_at = datetime.now()
    
    def escalate(self, level: int, reason: str):
        """Escalate the failure to a higher level"""
        self.escalation_level = level
        self.escalated_at = datetime.now()
        self.escalation_reason = reason
        self.recovery_status = RecoveryStatus.ESCALATED.value
        self.updated_at = datetime.now()
    
    def mark_as_duplicate(self, original_event_id: str):
        """Mark this event as a duplicate occurrence"""
        self.occurrence_count += 1
        self.last_occurrence = datetime.now()
        self.updated_at = datetime.now()
    
    def calculate_recovery_time(self) -> float:
        """Calculate recovery time in seconds"""
        if self.recovery_started_at and self.recovery_completed_at:
            return (self.recovery_completed_at - self.recovery_started_at).total_seconds()
        return 0.0


class CircuitBreaker(Base):
    """SQLAlchemy model for circuit breaker state"""
    __tablename__ = "circuit_breakers"
    
    id = Column(Integer, primary_key=True)
    component = Column(String(100), nullable=False, unique=True, index=True)
    state = Column(String(20), default="closed")
    failure_count = Column(Integer, default=0)
    failure_threshold = Column(Integer, default=5)
    success_count = Column(Integer, default=0)
    last_failure_time = Column(DateTime)
    last_success_time = Column(DateTime)
    state_changed_at = Column(DateTime)
    timeout_duration_seconds = Column(Integer, default=60)
    
    def __init__(self, component: str, failure_threshold: int = 5, timeout_duration: int = 60):
        self.component = component
        self.state = CircuitState.CLOSED.value
        self.failure_threshold = failure_threshold
        self.timeout_duration_seconds = timeout_duration
        self.state_changed_at = datetime.now()
    
    def record_failure(self):
        """Record a failure and update state"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold and self.state == CircuitState.CLOSED.value:
            self.state = CircuitState.OPEN.value
            self.state_changed_at = datetime.now()
    
    def record_success(self):
        """Record a success and update state"""
        self.success_count += 1
        self.last_success_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN.value:
            self.state = CircuitState.CLOSED.value
            self.failure_count = 0
            self.state_changed_at = datetime.now()
    
    def can_attempt_request(self) -> bool:
        """Check if requests can be attempted"""
        if self.state == CircuitState.CLOSED.value:
            return True
        elif self.state == CircuitState.OPEN.value:
            # Check if timeout has passed
            if self.state_changed_at:
                elapsed = (datetime.now() - self.state_changed_at).total_seconds()
                if elapsed >= self.timeout_duration_seconds:
                    self.state = CircuitState.HALF_OPEN.value
                    self.state_changed_at = datetime.now()
                    return True
            return False
        elif self.state == CircuitState.HALF_OPEN.value:
            return True
        return False


class FailureEventConfig(BaseModel):
    """Pydantic model for failure event configuration"""
    event_type: str = Field(..., description="Type of failure event")
    component: str = Field(..., description="Component that failed")
    severity: FailureSeverity = Field(..., description="Failure severity level")
    recovery_strategy: RecoveryStrategy = Field(RecoveryStrategy.RETRY_WITH_BACKOFF, description="Recovery strategy")
    max_retry_attempts: int = Field(3, ge=0, le=10, description="Maximum retry attempts")
    retry_delay_seconds: int = Field(5, ge=1, le=300, description="Delay between retries")
    context_data: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    
    class Config:
        from_attributes = True


class RecoveryResult(BaseModel):
    """Pydantic model for recovery operation results"""
    event_id: str
    strategy_applied: str
    recovery_attempted: bool
    success: bool
    attempts_made: int
    recovery_time_seconds: float
    error_message: Optional[str]
    additional_info: Dict[str, Any]
    
    class Config:
        from_attributes = True


class FailureAnalytics(BaseModel):
    """Pydantic model for failure analytics"""
    total_failures: int
    failures_by_component: Dict[str, int]
    failures_by_severity: Dict[str, int]
    failures_by_type: Dict[str, int]
    recovery_success_rate: float
    average_recovery_time: float
    most_common_failures: List[Dict[str, Any]]
    failure_trends: Dict[str, Any]
    
    class Config:
        from_attributes = True


class ComponentHealth(BaseModel):
    """Pydantic model for component health status"""
    component: str
    status: str  # healthy, unhealthy, degraded, unknown
    last_check_time: str
    failure_count: int
    success_count: int
    uptime_percentage: float
    response_time_ms: float
    
    class Config:
        from_attributes = True


class EscalationConfig(BaseModel):
    """Pydantic model for escalation configuration"""
    levels: List[Dict[str, Any]] = Field(..., description="Escalation levels and actions")
    timeout_seconds: int = Field(300, description="Timeout for each level")
    auto_escalate: bool = Field(True, description="Enable automatic escalation")
    
    class Config:
        from_attributes = True


class DegradedModeConfig(BaseModel):
    """Pydantic model for degraded mode configuration"""
    disabled_features: List[str] = Field(..., description="Features to disable")
    reduced_capacity: Dict[str, float] = Field(..., description="Capacity reductions")
    quality_threshold: float = Field(0.7, description="Minimum quality threshold")
    max_concurrent_users: int = Field(100, description="Maximum concurrent users")
    
    class Config:
        from_attributes = True