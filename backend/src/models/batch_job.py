"""
Batch job model for managing large-scale processing tasks.
Supports queuing, priority scheduling, parallel processing, and progress tracking.
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum

Base = declarative_base()


class JobStatus(str, Enum):
    """Enumeration of batch job statuses"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobType(str, Enum):
    """Enumeration of supported job types"""
    PROMPT_ENHANCEMENT = "prompt_enhancement"
    VIDEO_GENERATION = "video_generation"
    CONTEXT_ANALYSIS = "context_analysis"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    CACHE_WARMING = "cache_warming"
    DATA_EXPORT = "data_export"
    SYSTEM_MAINTENANCE = "system_maintenance"
    CUSTOM = "custom"


class ErrorStrategy(str, Enum):
    """Enumeration of error handling strategies"""
    FAIL_FAST = "fail_fast"  # Stop on first error
    CONTINUE = "continue"    # Continue processing despite errors
    RETRY_FAILED = "retry_failed"  # Retry failed items
    SKIP_INVALID = "skip_invalid"  # Skip invalid items


class BatchJob(Base):
    """SQLAlchemy model for storing batch job information"""
    __tablename__ = "batch_jobs"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(String(255), nullable=False, unique=True, index=True)
    job_type = Column(String(100), nullable=False)
    job_name = Column(String(255))
    description = Column(Text)
    
    # Input and configuration
    input_data = Column(JSON, nullable=False)  # Array of input items
    batch_size = Column(Integer, default=10)
    parallel_workers = Column(Integer, default=1)
    
    # Scheduling and priority
    priority = Column(Integer, default=1)  # 1 = highest priority
    scheduled_time = Column(DateTime)
    recurring_interval_minutes = Column(Integer)  # For recurring jobs
    
    # Processing configuration
    max_retries = Column(Integer, default=3)
    retry_delay_seconds = Column(Integer, default=5)
    timeout_seconds = Column(Integer, default=300)
    error_strategy = Column(String(50), default="continue")
    
    # Resource management
    estimated_memory_mb = Column(Integer, default=10)
    estimated_cpu_percent = Column(Integer, default=25)
    max_execution_time_seconds = Column(Integer, default=3600)
    
    # Status and progress
    status = Column(String(50), default="pending")
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    successful_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    skipped_items = Column(Integer, default=0)
    
    # Results and errors
    results = Column(JSON)  # Array of results
    errors = Column(JSON)   # Array of error information
    progress_details = Column(JSON)  # Detailed progress information
    
    # Performance metrics
    actual_memory_mb = Column(Float, default=0.0)
    actual_cpu_percent = Column(Float, default=0.0)
    processing_time_seconds = Column(Float, default=0.0)
    average_item_time_ms = Column(Float, default=0.0)
    
    # Retry tracking
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime)
    retry_history = Column(JSON)  # History of retry attempts
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # User and context
    user_id = Column(String(255), index=True)
    context_data = Column(JSON)  # Additional context information
    
    def __init__(self, job_id: str, job_type: str, input_data: List[Dict[str, Any]],
                 batch_size: int = 10, priority: int = 1, max_retries: int = 3,
                 timeout_seconds: int = 300, parallel_workers: int = 1):
        self.job_id = job_id
        self.job_type = job_type
        self.input_data = input_data
        self.total_items = len(input_data)
        self.batch_size = batch_size
        self.priority = priority
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.parallel_workers = parallel_workers
        self.status = JobStatus.PENDING.value
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.results = []
        self.errors = []
        self.retry_history = []
    
    def start_processing(self):
        """Mark job as started"""
        self.status = JobStatus.RUNNING.value
        self.started_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update_progress(self, processed: int, successful: int, failed: int, skipped: int = 0):
        """Update job progress"""
        self.processed_items = processed
        self.successful_items = successful
        self.failed_items = failed
        self.skipped_items = skipped
        self.updated_at = datetime.now()
    
    def complete_job(self, success: bool = True):
        """Mark job as completed"""
        self.status = JobStatus.COMPLETED.value if success else JobStatus.FAILED.value
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()
        
        if self.started_at:
            self.processing_time_seconds = (self.completed_at - self.started_at).total_seconds()
            if self.processed_items > 0:
                self.average_item_time_ms = (self.processing_time_seconds * 1000) / self.processed_items
    
    def add_retry_attempt(self, error_message: str):
        """Record retry attempt"""
        self.retry_count += 1
        self.last_retry_at = datetime.now()
        self.status = JobStatus.RETRYING.value
        
        retry_record = {
            "attempt": self.retry_count,
            "timestamp": self.last_retry_at.isoformat(),
            "error": error_message
        }
        
        if not self.retry_history:
            self.retry_history = []
        self.retry_history.append(retry_record)
        self.updated_at = datetime.now()
    
    def get_progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.total_items == 0:
            return 100.0
        return (self.processed_items / self.total_items) * 100.0
    
    def is_expired(self) -> bool:
        """Check if job has exceeded timeout"""
        if not self.started_at:
            return False
        
        elapsed = (datetime.now() - self.started_at).total_seconds()
        return elapsed > self.timeout_seconds
    
    def can_retry(self) -> bool:
        """Check if job can be retried"""
        return self.retry_count < self.max_retries and self.status == JobStatus.FAILED.value


class BatchJobConfig(BaseModel):
    """Pydantic model for batch job configuration"""
    job_type: JobType = Field(..., description="Type of batch job")
    job_name: Optional[str] = Field(None, description="Human-readable job name")
    batch_size: int = Field(10, ge=1, le=100, description="Items per batch")
    parallel_workers: int = Field(1, ge=1, le=10, description="Parallel workers")
    priority: int = Field(1, ge=1, le=5, description="Job priority (1=highest)")
    max_retries: int = Field(3, ge=0, le=10, description="Maximum retry attempts")
    timeout_seconds: int = Field(300, ge=30, le=3600, description="Job timeout")
    error_strategy: ErrorStrategy = Field(ErrorStrategy.CONTINUE, description="Error handling strategy")
    estimated_memory_mb: int = Field(10, ge=1, le=1000, description="Estimated memory usage")
    
    class Config:
        from_attributes = True


class BatchJobStatus(BaseModel):
    """Pydantic model for batch job status"""
    job_id: str
    job_type: str
    status: JobStatus
    total_items: int
    processed_items: int
    successful_items: int
    failed_items: int
    progress_percentage: float
    estimated_completion_time: Optional[str]
    created_at: str
    started_at: Optional[str]
    
    class Config:
        from_attributes = True


class BatchJobResult(BaseModel):
    """Pydantic model for batch job results"""
    job_id: str
    status: JobStatus
    results: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    processing_stats: Dict[str, Any]
    performance_metrics: Dict[str, float]
    
    class Config:
        from_attributes = True


class QueueInfo(BaseModel):
    """Pydantic model for job queue information"""
    total_jobs: int
    pending_jobs: int
    running_jobs: int
    scheduled_jobs: int
    failed_jobs: int
    jobs: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class ProcessingStats(BaseModel):
    """Pydantic model for processing statistics"""
    job_id: str
    parallel_workers_used: int
    total_processing_time: float
    items_processed: int
    average_item_time_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    
    class Config:
        from_attributes = True


class RetryStats(BaseModel):
    """Pydantic model for retry statistics"""
    job_id: str
    max_retries: int
    total_retry_attempts: int
    successful_retries: int
    failed_retries: int
    retry_success_rate: float
    
    class Config:
        from_attributes = True


class ResourceStatus(BaseModel):
    """Pydantic model for resource status"""
    active_workers: int
    max_workers: int
    estimated_memory_usage_mb: float
    memory_limit_mb: float
    cpu_usage_percent: float
    cpu_limit_percent: float
    queued_jobs: int
    
    class Config:
        from_attributes = True


class ScheduledJobInfo(BaseModel):
    """Pydantic model for scheduled job information"""
    job_id: str
    job_type: str
    scheduled_time: str
    recurring_interval_minutes: Optional[int]
    next_run_time: Optional[str]
    is_recurring: bool
    
    class Config:
        from_attributes = True