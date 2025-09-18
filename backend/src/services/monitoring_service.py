"""
MonitoringService - Phase 1 手動動画管理システム
T033: System monitoring and health tracking
"""
import uuid
import psutil
import shutil
from datetime import datetime, timedelta
from typing import List, Optional
from src.models.system_status import SystemStatus


class MonitoringService:
    """System monitoring and health tracking service"""
    
    def __init__(self):
        """Initialize monitoring service with in-memory storage for minimal implementation"""
        self._status_history: List[SystemStatus] = []
        self._max_history_size = 1000  # Keep last 1000 entries in memory
    
    def get_current_status(self) -> SystemStatus:
        """
        Get current system status with real-time metrics
        Returns SystemStatus object with all current metrics
        """
        try:
            # Get system resource metrics
            cpu_usage = self.get_cpu_usage()
            memory_usage = self.get_memory_usage()
            disk_usage = self.get_disk_usage()
            uptime = self.get_uptime()
            
            # Get application metrics
            active_sessions = self.get_active_sessions_count()
            total_videos = self.get_total_videos_count()
            
            # Check external services
            m5stack_status = self.check_m5stack_status()
            display_status = self.check_display_status()
            api_status = self.check_api_status()
            
            return SystemStatus(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                uptime=uptime,
                active_sessions=active_sessions,
                total_videos=total_videos,
                m5stack_status=m5stack_status,
                display_status=display_status,
                api_status=api_status,
                timestamp=datetime.now()
            )
        except Exception as e:
            # Fallback status in case of errors
            return SystemStatus(
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                uptime=0,
                active_sessions=0,
                total_videos=0,
                m5stack_status="error",
                display_status="error",
                api_status="degraded",
                timestamp=datetime.now()
            )
    
    def record_system_status(self) -> SystemStatus:
        """
        Record current system status to storage
        Returns the recorded SystemStatus object
        """
        status = self.get_current_status()
        
        # Assign unique ID
        status.id = str(uuid.uuid4())
        
        # Store in memory (minimal implementation)
        self._status_history.append(status)
        
        # Keep history size manageable
        if len(self._status_history) > self._max_history_size:
            self._status_history = self._status_history[-self._max_history_size:]
        
        return status
    
    def get_status_history(self, limit: int = 100, hours: Optional[int] = None) -> List[SystemStatus]:
        """
        Get historical system status entries
        
        Args:
            limit: Maximum number of entries to return
            hours: Filter entries within last N hours
            
        Returns:
            List of SystemStatus objects, newest first
        """
        try:
            history = self._status_history.copy()
            
            # Filter by time if hours specified
            if hours is not None:
                cutoff_time = datetime.now() - timedelta(hours=hours)
                history = [s for s in history if s.timestamp >= cutoff_time]
            
            # Sort by timestamp, newest first
            history.sort(key=lambda s: s.timestamp, reverse=True)
            
            # Apply limit
            return history[:limit]
        except Exception:
            return []
    
    def cleanup_old_logs(self, days: int = 7) -> int:
        """
        Remove system status logs older than specified days
        
        Args:
            days: Remove logs older than this many days
            
        Returns:
            Number of deleted entries
        """
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            initial_count = len(self._status_history)
            
            # Keep only recent entries
            self._status_history = [s for s in self._status_history if s.timestamp >= cutoff_time]
            
            deleted_count = initial_count - len(self._status_history)
            return deleted_count
        except Exception:
            return 0
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            return float(psutil.cpu_percent(interval=1))
        except Exception:
            return 0.0
    
    def get_memory_usage(self) -> float:
        """Get current memory usage percentage"""
        try:
            memory = psutil.virtual_memory()
            return float(memory.percent)
        except Exception:
            return 0.0
    
    def get_disk_usage(self) -> float:
        """Get current disk usage percentage"""
        try:
            disk = shutil.disk_usage('/')
            used_percent = (disk.used / disk.total) * 100
            return float(used_percent)
        except Exception:
            return 0.0
    
    def get_uptime(self) -> int:
        """Get system uptime in seconds"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.now().timestamp() - boot_time
            return int(uptime_seconds)
        except Exception:
            return 0
    
    def get_active_sessions_count(self) -> int:
        """Get number of active display sessions"""
        try:
            # TODO: Implement actual session counting
            # For minimal implementation, return 0
            return 0
        except Exception:
            return 0
    
    def get_total_videos_count(self) -> int:
        """Get total number of videos in system"""
        try:
            # TODO: Implement actual video counting
            # For minimal implementation, return 0
            return 0
        except Exception:
            return 0
    
    def check_m5stack_status(self) -> str:
        """
        Check M5STACK device connectivity status
        Returns: 'online', 'offline', or 'error'
        """
        try:
            # TODO: Implement actual M5STACK health check
            # For minimal implementation, assume offline
            return "offline"
        except Exception:
            return "error"
    
    def check_display_status(self) -> str:
        """
        Check display system status
        Returns: 'active', 'idle', or 'error'
        """
        try:
            # TODO: Implement actual display status check
            # For minimal implementation, assume idle
            return "idle"
        except Exception:
            return "error"
    
    def check_api_status(self) -> str:
        """
        Check API health status
        Returns: 'healthy', 'degraded', or 'error'
        """
        try:
            # Simple health check - if we can execute this, API is healthy
            return "healthy"
        except Exception:
            return "error"