"""
Performance metrics model for tracking system performance and optimization.
Stores execution times, resource usage, and throughput metrics.
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

Base = declarative_base()


class PerformanceMetrics(Base):
    """SQLAlchemy model for storing performance metrics data"""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True)
    metric_id = Column(String(255), nullable=False, unique=True, index=True)
    operation_type = Column(String(100), nullable=False)  # video_generation, prompt_enhancement, etc.
    execution_time_ms = Column(Integer, nullable=False)
    memory_usage_mb = Column(Float, nullable=False)
    cpu_usage_percent = Column(Float, nullable=False)
    throughput_ops_per_sec = Column(Float, default=0.0)
    success_rate = Column(Float, default=1.0)
    error_count = Column(Integer, default=0)
    optimization_applied = Column(String(255))  # Type of optimization used
    baseline_time_ms = Column(Integer)  # Baseline time before optimization
    improvement_ratio = Column(Float, default=1.0)  # Performance improvement ratio
    session_id = Column(String(255), index=True)  # Profiling session ID
    created_at = Column(DateTime, default=datetime.now)
    
    def __init__(self, metric_id: str, operation_type: str, execution_time_ms: int,
                 memory_usage_mb: float, cpu_usage_percent: float, 
                 throughput_ops_per_sec: float = 0.0, success_rate: float = 1.0):
        self.metric_id = metric_id
        self.operation_type = operation_type
        self.execution_time_ms = execution_time_ms
        self.memory_usage_mb = memory_usage_mb
        self.cpu_usage_percent = cpu_usage_percent
        self.throughput_ops_per_sec = throughput_ops_per_sec
        self.success_rate = success_rate
        self.created_at = datetime.now()
    
    def calculate_improvement(self, baseline_time_ms: int):
        """Calculate performance improvement ratio"""
        if baseline_time_ms > 0:
            self.baseline_time_ms = baseline_time_ms
            self.improvement_ratio = baseline_time_ms / self.execution_time_ms
        else:
            self.improvement_ratio = 1.0


class ResourceMetrics(BaseModel):
    """Pydantic model for resource usage metrics"""
    monitoring_id: str
    cpu_usage: Dict[str, float] = Field(..., description="CPU usage statistics")
    memory_usage: Dict[str, float] = Field(..., description="Memory usage statistics")
    disk_io: Dict[str, float] = Field(..., description="Disk I/O statistics")
    network_io: Dict[str, float] = Field(..., description="Network I/O statistics")
    timestamp: str = Field(..., description="Metrics timestamp")
    
    class Config:
        from_attributes = True


class PerformanceReport(BaseModel):
    """Pydantic model for performance reports"""
    session_id: str
    operation_count: int
    total_duration_ms: int
    average_execution_time_ms: float
    peak_memory_usage_mb: float
    average_cpu_usage_percent: float
    overall_throughput: float
    success_rate: float
    optimizations_applied: List[str]
    improvement_summary: Dict[str, float]
    
    class Config:
        from_attributes = True


class ProfilingResult(BaseModel):
    """Pydantic model for profiling results"""
    session_id: str
    operations: List[Dict[str, Any]]
    total_duration_ms: int
    operation_breakdown: Dict[str, Dict[str, Any]]
    performance_bottlenecks: List[str]
    optimization_recommendations: List[str]
    
    class Config:
        from_attributes = True


class OptimizationConfig(BaseModel):
    """Pydantic model for optimization configuration"""
    cache_enabled: bool = Field(True, description="Enable caching optimization")
    batch_processing_enabled: bool = Field(True, description="Enable batch processing")
    concurrent_processing_enabled: bool = Field(True, description="Enable concurrent processing")
    max_workers: int = Field(3, ge=1, le=10, description="Maximum concurrent workers")
    cache_ttl_seconds: int = Field(300, ge=60, le=3600, description="Cache TTL in seconds")
    batch_size: int = Field(5, ge=1, le=20, description="Batch processing size")
    memory_limit_mb: int = Field(512, ge=128, le=2048, description="Memory usage limit")
    enable_profiling: bool = Field(False, description="Enable detailed profiling")
    
    class Config:
        from_attributes = True