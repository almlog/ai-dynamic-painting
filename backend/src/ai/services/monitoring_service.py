"""Monitoring Service for AI system health and performance tracking."""

import asyncio
import logging
import psutil
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import os
import threading
from collections import deque
import aiohttp
import sqlite3
from pathlib import Path

logger = logging.getLogger("ai_system.monitoring")


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics to monitor."""
    SYSTEM_CPU = "system_cpu"
    SYSTEM_MEMORY = "system_memory"
    SYSTEM_DISK = "system_disk"
    VEO_API_CALLS = "veo_api_calls"
    VEO_API_ERRORS = "veo_api_errors"
    VEO_API_LATENCY = "veo_api_latency"
    VEO_QUOTA_USAGE = "veo_quota_usage"
    GENERATION_SUCCESS_RATE = "generation_success_rate"
    GENERATION_QUEUE_SIZE = "generation_queue_size"
    QUALITY_SCORES = "quality_scores"
    COST_PER_HOUR = "cost_per_hour"
    USER_ACTIVITY = "user_activity"


@dataclass
class MetricData:
    """Single metric data point."""
    metric_type: MetricType
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """System alert data."""
    alert_id: str
    level: AlertLevel
    title: str
    message: str
    metric_type: Optional[MetricType] = None
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthStatus:
    """Overall system health status."""
    status: str  # "healthy", "degraded", "unhealthy"
    score: float  # 0-100
    last_updated: datetime
    components: Dict[str, Dict[str, Any]]
    active_alerts: List[Alert]
    recommendations: List[str]


class MonitoringService:
    """Comprehensive monitoring service for AI system."""
    
    def __init__(self, db_path: str = "monitoring.db"):
        self.db_path = db_path
        self.metrics_buffer: deque = deque(maxlen=10000)
        self.alerts: List[Alert] = []
        self.alert_callbacks: Dict[AlertLevel, List[Callable]] = {
            level: [] for level in AlertLevel
        }
        
        # Monitoring configuration
        self.monitoring_config = {
            "collection_interval": 30,  # seconds
            "retention_days": 30,
            "alert_thresholds": {
                MetricType.SYSTEM_CPU: {"warning": 80.0, "critical": 95.0},
                MetricType.SYSTEM_MEMORY: {"warning": 85.0, "critical": 95.0},
                MetricType.SYSTEM_DISK: {"warning": 90.0, "critical": 95.0},
                MetricType.VEO_API_ERRORS: {"warning": 5.0, "critical": 10.0},  # %
                MetricType.VEO_QUOTA_USAGE: {"warning": 80.0, "critical": 95.0},  # %
                MetricType.GENERATION_SUCCESS_RATE: {"warning": 85.0, "critical": 70.0},  # % (lower is worse)
                MetricType.QUALITY_SCORES: {"warning": 7.0, "critical": 6.0},  # (lower is worse)
                MetricType.COST_PER_HOUR: {"warning": 5.0, "critical": 10.0}  # USD
            }
        }
        
        # Service references (injected)
        self.veo_service = None
        self.scheduling_service = None
        self.quality_service = None
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_task = None
        
        # Statistics
        self.stats = {
            "uptime_start": datetime.now(),
            "total_metrics_collected": 0,
            "total_alerts_generated": 0,
            "last_health_check": None
        }
        
        # Initialize database
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize SQLite database for metrics storage."""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_type TEXT NOT NULL,
                        value REAL NOT NULL,
                        timestamp TEXT NOT NULL,
                        tags TEXT,
                        metadata TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alert_id TEXT UNIQUE NOT NULL,
                        level TEXT NOT NULL,
                        title TEXT NOT NULL,
                        message TEXT NOT NULL,
                        metric_type TEXT,
                        triggered_at TEXT NOT NULL,
                        acknowledged_at TEXT,
                        resolved_at TEXT,
                        metadata TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_metrics_type_time 
                    ON metrics(metric_type, timestamp)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_alerts_level_time 
                    ON alerts(level, triggered_at)
                """)
                
                conn.commit()
                logger.info("Monitoring database initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize monitoring database: {e}")
            raise
    
    def set_services(
        self,
        veo_service=None,
        scheduling_service=None,
        quality_service=None
    ):
        """Inject service dependencies."""
        self.veo_service = veo_service
        self.scheduling_service = scheduling_service
        self.quality_service = quality_service
    
    async def start_monitoring(self):
        """Start the monitoring service."""
        
        if self.monitoring_active:
            logger.warning("Monitoring service already active")
            return
        
        try:
            self.monitoring_active = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("Monitoring service started")
            
            # Initial health check
            await self.perform_health_check()
            
        except Exception as e:
            logger.error(f"Failed to start monitoring service: {e}")
            self.monitoring_active = False
            raise
    
    async def stop_monitoring(self):
        """Stop the monitoring service."""
        
        self.monitoring_active = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Flush remaining metrics to database
        await self._flush_metrics_to_db()
        
        logger.info("Monitoring service stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        
        interval = self.monitoring_config["collection_interval"]
        
        try:
            while self.monitoring_active:
                start_time = time.time()
                
                # Collect all metrics
                await self._collect_system_metrics()
                await self._collect_veo_metrics()
                await self._collect_generation_metrics()
                await self._collect_quality_metrics()
                await self._collect_cost_metrics()
                
                # Process alerts
                await self._process_alerts()
                
                # Flush metrics to database periodically
                if len(self.metrics_buffer) > 100:
                    await self._flush_metrics_to_db()
                
                # Calculate sleep time to maintain interval
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                
                await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Monitoring loop error: {e}")
            # Try to restart monitoring after error
            await asyncio.sleep(30)
            if self.monitoring_active:
                self.monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def _collect_system_metrics(self):
        """Collect system resource metrics."""
        
        try:
            current_time = datetime.now()
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            await self._record_metric(
                MetricType.SYSTEM_CPU,
                cpu_percent,
                current_time,
                tags={"component": "system"}
            )
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            await self._record_metric(
                MetricType.SYSTEM_MEMORY,
                memory_percent,
                current_time,
                tags={"component": "system"},
                metadata={
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2)
                }
            )
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            await self._record_metric(
                MetricType.SYSTEM_DISK,
                disk_percent,
                current_time,
                tags={"component": "system", "mount": "/"},
                metadata={
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    async def _collect_veo_metrics(self):
        """Collect VEO API related metrics."""
        
        if not self.veo_service:
            return
        
        try:
            current_time = datetime.now()
            
            # API call count (would be tracked by VEO service)
            # For now, simulate or get from service if available
            
            # Quota usage
            daily_quota = getattr(self.veo_service, 'daily_quota', 100)
            quota_used = 0  # Would get from VEO service stats
            
            if daily_quota > 0:
                quota_percent = (quota_used / daily_quota) * 100
                await self._record_metric(
                    MetricType.VEO_QUOTA_USAGE,
                    quota_percent,
                    current_time,
                    tags={"component": "veo_api"},
                    metadata={
                        "quota_used": quota_used,
                        "quota_total": daily_quota
                    }
                )
            
            # VEO API health check
            try:
                if hasattr(self.veo_service, 'health_check'):
                    health_result = await self.veo_service.health_check()
                    latency_ms = health_result.get("latency_ms", 0)
                    
                    await self._record_metric(
                        MetricType.VEO_API_LATENCY,
                        latency_ms,
                        current_time,
                        tags={"component": "veo_api"},
                        metadata=health_result
                    )
                    
            except Exception as health_error:
                logger.warning(f"VEO health check failed: {health_error}")
                await self._record_metric(
                    MetricType.VEO_API_ERRORS,
                    1,
                    current_time,
                    tags={"component": "veo_api", "error_type": "health_check"}
                )
                
        except Exception as e:
            logger.error(f"Failed to collect VEO metrics: {e}")
    
    async def _collect_generation_metrics(self):
        """Collect video generation related metrics."""
        
        if not self.scheduling_service:
            return
        
        try:
            current_time = datetime.now()
            
            # Get scheduling service statistics
            stats = self.scheduling_service.get_statistics()
            
            # Queue size
            active_tasks = stats.get("active_tasks", 0)
            await self._record_metric(
                MetricType.GENERATION_QUEUE_SIZE,
                active_tasks,
                current_time,
                tags={"component": "generation"}
            )
            
            # Success rate calculation
            total_tasks = stats.get("total_tasks", 0)
            completed_tasks = stats.get("completed_tasks", 0)
            
            if total_tasks > 0:
                success_rate = (completed_tasks / total_tasks) * 100
                await self._record_metric(
                    MetricType.GENERATION_SUCCESS_RATE,
                    success_rate,
                    current_time,
                    tags={"component": "generation"},
                    metadata={
                        "total_tasks": total_tasks,
                        "completed_tasks": completed_tasks,
                        "failed_tasks": stats.get("failed_tasks", 0)
                    }
                )
                
        except Exception as e:
            logger.error(f"Failed to collect generation metrics: {e}")
    
    async def _collect_quality_metrics(self):
        """Collect quality assurance metrics."""
        
        if not self.quality_service:
            return
        
        try:
            current_time = datetime.now()
            
            # Get quality statistics
            stats = self.quality_service.get_quality_statistics()
            
            # Average quality score
            avg_score = stats.get("recent_average", 0.0)
            if avg_score > 0:
                await self._record_metric(
                    MetricType.QUALITY_SCORES,
                    avg_score,
                    current_time,
                    tags={"component": "quality"},
                    metadata=stats
                )
                
        except Exception as e:
            logger.error(f"Failed to collect quality metrics: {e}")
    
    async def _collect_cost_metrics(self):
        """Collect cost-related metrics."""
        
        try:
            current_time = datetime.now()
            
            # Calculate estimated hourly cost
            # This would be based on VEO API usage, generation frequency, etc.
            
            # For now, simulate cost calculation
            # Real implementation would track actual API costs
            estimated_hourly_cost = 0.0  # USD
            
            # If we have VEO service, estimate based on usage
            if self.veo_service and hasattr(self.veo_service, 'daily_quota'):
                # Estimate based on quota usage and typical cost per generation
                cost_per_generation = 0.05  # Estimated cost
                generations_per_hour = 2  # Estimated rate
                estimated_hourly_cost = cost_per_generation * generations_per_hour
            
            await self._record_metric(
                MetricType.COST_PER_HOUR,
                estimated_hourly_cost,
                current_time,
                tags={"component": "cost"},
                metadata={"currency": "USD"}
            )
            
        except Exception as e:
            logger.error(f"Failed to collect cost metrics: {e}")
    
    async def _record_metric(
        self,
        metric_type: MetricType,
        value: float,
        timestamp: datetime,
        tags: Dict[str, str] = None,
        metadata: Dict[str, Any] = None
    ):
        """Record a metric data point."""
        
        metric = MetricData(
            metric_type=metric_type,
            value=value,
            timestamp=timestamp,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        self.metrics_buffer.append(metric)
        self.stats["total_metrics_collected"] += 1
    
    async def _process_alerts(self):
        """Process metrics and generate alerts."""
        
        try:
            # Get recent metrics for alert processing
            current_time = datetime.now()
            recent_metrics = [
                m for m in self.metrics_buffer
                if (current_time - m.timestamp).total_seconds() < 300  # Last 5 minutes
            ]
            
            # Group metrics by type
            metrics_by_type = {}
            for metric in recent_metrics:
                if metric.metric_type not in metrics_by_type:
                    metrics_by_type[metric.metric_type] = []
                metrics_by_type[metric.metric_type].append(metric)
            
            # Check thresholds for each metric type
            for metric_type, metrics in metrics_by_type.items():
                if metric_type not in self.monitoring_config["alert_thresholds"]:
                    continue
                
                thresholds = self.monitoring_config["alert_thresholds"][metric_type]
                latest_metric = max(metrics, key=lambda m: m.timestamp)
                
                await self._check_metric_thresholds(latest_metric, thresholds)
                
        except Exception as e:
            logger.error(f"Failed to process alerts: {e}")
    
    async def _check_metric_thresholds(
        self,
        metric: MetricData,
        thresholds: Dict[str, float]
    ):
        """Check if metric exceeds alert thresholds."""
        
        try:
            value = metric.value
            metric_type = metric.metric_type
            
            # Determine alert level
            alert_level = None
            threshold_value = None
            
            if "critical" in thresholds:
                critical_threshold = thresholds["critical"]
                
                # Handle metrics where lower is worse
                if metric_type in [MetricType.GENERATION_SUCCESS_RATE, MetricType.QUALITY_SCORES]:
                    if value <= critical_threshold:
                        alert_level = AlertLevel.CRITICAL
                        threshold_value = critical_threshold
                else:
                    if value >= critical_threshold:
                        alert_level = AlertLevel.CRITICAL
                        threshold_value = critical_threshold
            
            elif "warning" in thresholds:
                warning_threshold = thresholds["warning"]
                
                # Handle metrics where lower is worse
                if metric_type in [MetricType.GENERATION_SUCCESS_RATE, MetricType.QUALITY_SCORES]:
                    if value <= warning_threshold:
                        alert_level = AlertLevel.WARNING
                        threshold_value = warning_threshold
                else:
                    if value >= warning_threshold:
                        alert_level = AlertLevel.WARNING
                        threshold_value = warning_threshold
            
            # Generate alert if threshold exceeded
            if alert_level:
                await self._generate_alert(
                    level=alert_level,
                    metric_type=metric_type,
                    current_value=value,
                    threshold_value=threshold_value,
                    metric_data=metric
                )
                
        except Exception as e:
            logger.error(f"Failed to check metric thresholds: {e}")
    
    async def _generate_alert(
        self,
        level: AlertLevel,
        metric_type: MetricType,
        current_value: float,
        threshold_value: float,
        metric_data: MetricData
    ):
        """Generate an alert."""
        
        try:
            # Check if similar alert already exists (avoid spam)
            existing_alerts = [
                alert for alert in self.alerts
                if alert.metric_type == metric_type
                and alert.level == level
                and not alert.resolved_at
                and (datetime.now() - alert.triggered_at).total_seconds() < 3600  # 1 hour
            ]
            
            if existing_alerts:
                logger.debug(f"Similar alert already exists for {metric_type.value}")
                return
            
            # Create alert
            alert_id = f"alert_{metric_type.value}_{int(time.time())}"
            
            title = f"{level.value.upper()}: {metric_type.value.replace('_', ' ').title()}"
            
            if metric_type in [MetricType.GENERATION_SUCCESS_RATE, MetricType.QUALITY_SCORES]:
                message = (f"{metric_type.value.replace('_', ' ').title()} dropped to {current_value:.1f} "
                          f"(threshold: {threshold_value})")
            else:
                message = (f"{metric_type.value.replace('_', ' ').title()} exceeded {current_value:.1f} "
                          f"(threshold: {threshold_value})")
            
            alert = Alert(
                alert_id=alert_id,
                level=level,
                title=title,
                message=message,
                metric_type=metric_type,
                metadata={
                    "current_value": current_value,
                    "threshold_value": threshold_value,
                    "metric_data": asdict(metric_data)
                }
            )
            
            self.alerts.append(alert)
            self.stats["total_alerts_generated"] += 1
            
            # Store alert in database
            await self._store_alert(alert)
            
            # Call alert callbacks
            for callback in self.alert_callbacks.get(level, []):
                try:
                    await callback(alert)
                except Exception as callback_error:
                    logger.error(f"Alert callback failed: {callback_error}")
            
            logger.warning(f"Alert generated: {alert.title} - {alert.message}")
            
        except Exception as e:
            logger.error(f"Failed to generate alert: {e}")
    
    async def _flush_metrics_to_db(self):
        """Flush metrics buffer to database."""
        
        if not self.metrics_buffer:
            return
        
        try:
            metrics_to_store = list(self.metrics_buffer)
            self.metrics_buffer.clear()
            
            with sqlite3.connect(self.db_path) as conn:
                for metric in metrics_to_store:
                    conn.execute(
                        """
                        INSERT INTO metrics (metric_type, value, timestamp, tags, metadata)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            metric.metric_type.value,
                            metric.value,
                            metric.timestamp.isoformat(),
                            json.dumps(metric.tags),
                            json.dumps(metric.metadata)
                        )
                    )
                conn.commit()
            
            logger.debug(f"Flushed {len(metrics_to_store)} metrics to database")
            
        except Exception as e:
            logger.error(f"Failed to flush metrics to database: {e}")
    
    async def _store_alert(self, alert: Alert):
        """Store alert in database."""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO alerts (alert_id, level, title, message, metric_type, 
                                      triggered_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        alert.alert_id,
                        alert.level.value,
                        alert.title,
                        alert.message,
                        alert.metric_type.value if alert.metric_type else None,
                        alert.triggered_at.isoformat(),
                        json.dumps(alert.metadata)
                    )
                )
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to store alert in database: {e}")
    
    async def perform_health_check(self) -> HealthStatus:
        """Perform comprehensive system health check."""
        
        try:
            current_time = datetime.now()
            components = {}
            overall_score = 100.0
            recommendations = []
            
            # System health
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
            
            components["system"] = {
                "status": "healthy" if max(cpu_percent, memory_percent, disk_percent) < 80 else "degraded",
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent
            }
            
            if max(cpu_percent, memory_percent, disk_percent) > 80:
                overall_score -= 20
                recommendations.append("System resources under pressure")
            
            # VEO API health
            if self.veo_service:
                try:
                    if hasattr(self.veo_service, 'health_check'):
                        veo_health = await self.veo_service.health_check()
                        components["veo_api"] = {
                            "status": "healthy" if veo_health.get("authenticated") else "unhealthy",
                            **veo_health
                        }
                        
                        if not veo_health.get("authenticated"):
                            overall_score -= 30
                            recommendations.append("VEO API authentication issue")
                    else:
                        components["veo_api"] = {"status": "unknown"}
                        
                except Exception as e:
                    components["veo_api"] = {"status": "unhealthy", "error": str(e)}
                    overall_score -= 30
                    recommendations.append("VEO API unreachable")
            else:
                components["veo_api"] = {"status": "not_configured"}
            
            # Generation service health
            if self.scheduling_service:
                sched_stats = self.scheduling_service.get_statistics()
                active_tasks = sched_stats.get("active_tasks", 0)
                scheduler_running = sched_stats.get("scheduler_running", False)
                
                components["generation"] = {
                    "status": "healthy" if scheduler_running else "unhealthy",
                    "active_tasks": active_tasks,
                    "scheduler_running": scheduler_running
                }
                
                if not scheduler_running:
                    overall_score -= 25
                    recommendations.append("Generation scheduler not running")
                    
                if active_tasks > 10:
                    overall_score -= 10
                    recommendations.append("High number of pending generation tasks")
            else:
                components["generation"] = {"status": "not_configured"}
            
            # Quality service health
            if self.quality_service:
                quality_stats = self.quality_service.get_quality_statistics()
                avg_score = quality_stats.get("recent_average", 0.0)
                
                components["quality"] = {
                    "status": "healthy" if avg_score >= 7.0 else "degraded",
                    "average_score": avg_score,
                    "total_assessments": quality_stats.get("total_assessments", 0)
                }
                
                if avg_score < 6.0:
                    overall_score -= 15
                    recommendations.append("Quality scores below acceptable threshold")
            else:
                components["quality"] = {"status": "not_configured"}
            
            # Active alerts
            active_alerts = [alert for alert in self.alerts if not alert.resolved_at]
            critical_alerts = [alert for alert in active_alerts if alert.level == AlertLevel.CRITICAL]
            
            if critical_alerts:
                overall_score -= len(critical_alerts) * 20
                recommendations.append(f"{len(critical_alerts)} critical alerts need attention")
            
            # Determine overall status
            if overall_score >= 80:
                status = "healthy"
            elif overall_score >= 60:
                status = "degraded"
            else:
                status = "unhealthy"
            
            health_status = HealthStatus(
                status=status,
                score=max(0.0, overall_score),
                last_updated=current_time,
                components=components,
                active_alerts=active_alerts,
                recommendations=recommendations
            )
            
            self.stats["last_health_check"] = current_time
            
            logger.info(f"Health check completed: {status} (score: {overall_score:.1f})")
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            
            return HealthStatus(
                status="unhealthy",
                score=0.0,
                last_updated=current_time,
                components={"error": {"status": "failed", "message": str(e)}},
                active_alerts=[],
                recommendations=["Health check system failure - manual investigation required"]
            )
    
    def register_alert_callback(self, level: AlertLevel, callback: Callable):
        """Register callback for specific alert level."""
        self.alert_callbacks[level].append(callback)
        logger.info(f"Alert callback registered for level: {level.value}")
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        
        for alert in self.alerts:
            if alert.alert_id == alert_id and not alert.acknowledged_at:
                alert.acknowledged_at = datetime.now()
                
                # Update in database
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute(
                            "UPDATE alerts SET acknowledged_at = ? WHERE alert_id = ?",
                            (alert.acknowledged_at.isoformat(), alert_id)
                        )
                        conn.commit()
                except Exception as e:
                    logger.error(f"Failed to update alert acknowledgment: {e}")
                
                logger.info(f"Alert {alert_id} acknowledged")
                return True
        
        return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        
        for alert in self.alerts:
            if alert.alert_id == alert_id and not alert.resolved_at:
                alert.resolved_at = datetime.now()
                
                # Update in database
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute(
                            "UPDATE alerts SET resolved_at = ? WHERE alert_id = ?",
                            (alert.resolved_at.isoformat(), alert_id)
                        )
                        conn.commit()
                except Exception as e:
                    logger.error(f"Failed to update alert resolution: {e}")
                
                logger.info(f"Alert {alert_id} resolved")
                return True
        
        return False
    
    def get_metrics(
        self,
        metric_type: MetricType = None,
        start_time: datetime = None,
        end_time: datetime = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get historical metrics from database."""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM metrics WHERE 1=1"
                params = []
                
                if metric_type:
                    query += " AND metric_type = ?"
                    params.append(metric_type.value)
                
                if start_time:
                    query += " AND timestamp >= ?"
                    params.append(start_time.isoformat())
                
                if end_time:
                    query += " AND timestamp <= ?"
                    params.append(end_time.isoformat())
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                metrics = []
                for row in rows:
                    metric = {
                        "id": row[0],
                        "metric_type": row[1],
                        "value": row[2],
                        "timestamp": row[3],
                        "tags": json.loads(row[4]) if row[4] else {},
                        "metadata": json.loads(row[5]) if row[5] else {}
                    }
                    metrics.append(metric)
                
                return metrics
                
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return []
    
    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """Get comprehensive monitoring statistics."""
        
        uptime = datetime.now() - self.stats["uptime_start"]
        active_alerts = [alert for alert in self.alerts if not alert.resolved_at]
        
        return {
            **self.stats,
            "uptime_seconds": int(uptime.total_seconds()),
            "monitoring_active": self.monitoring_active,
            "metrics_buffer_size": len(self.metrics_buffer),
            "active_alerts_count": len(active_alerts),
            "total_alerts": len(self.alerts),
            "database_path": self.db_path,
            "collection_interval": self.monitoring_config["collection_interval"]
        }