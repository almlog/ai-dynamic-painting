"""
Performance monitoring service for AI operations optimization.
Provides caching, batch processing, concurrent execution, and profiling.
"""

import uuid
import time
import asyncio
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Awaitable
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from src.models.performance_metrics import (
    PerformanceMetrics,
    ResourceMetrics,
    PerformanceReport,
    ProfilingResult,
    OptimizationConfig
)


class PerformanceMonitor:
    """Service for monitoring and optimizing AI operations performance"""
    
    def __init__(self, db_url: str = "sqlite:///ai_dynamic_painting.db"):
        self.engine = create_engine(db_url)
        self.session_factory = sessionmaker(bind=self.engine)
        
        # Performance optimization features
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = {}  # Cache TTL tracking
        self.active_sessions = {}  # Active profiling sessions
        self.resource_monitors = {}  # Active resource monitors
        
        # Configuration
        self.config = OptimizationConfig()
        
        # Thread pool for concurrent operations
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.max_workers)
        
    async def measure_operation(self, operation: Awaitable[Any], 
                              operation_type: str) -> tuple[Any, Dict[str, Any]]:
        """Measure performance of an async operation"""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        start_cpu = psutil.cpu_percent()
        
        try:
            # Execute the operation
            result = await operation
            success = True
            error_count = 0
        except Exception as e:
            result = {"error": str(e)}
            success = False
            error_count = 1
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        end_cpu = psutil.cpu_percent()
        
        # Calculate metrics
        execution_time_ms = int((end_time - start_time) * 1000)
        memory_usage_mb = max(end_memory - start_memory, 0)
        cpu_usage_percent = (start_cpu + end_cpu) / 2
        
        metrics = {
            "operation_type": operation_type,
            "execution_time_ms": execution_time_ms,
            "memory_usage_mb": memory_usage_mb,
            "cpu_usage_percent": cpu_usage_percent,
            "success_rate": 1.0 if success else 0.0,
            "error_count": error_count
        }
        
        return result, metrics
    
    async def get_cached_result(self, cache_key: str, 
                              compute_func: Callable[[], Any]) -> Any:
        """Get result from cache or compute and cache it"""
        if not self.config.cache_enabled:
            return compute_func()
        
        # Check cache validity
        if cache_key in self.cache:
            cache_time = self.cache_ttl.get(cache_key, 0)
            if time.time() - cache_time < self.config.cache_ttl_seconds:
                return self.cache[cache_key]
            else:
                # Cache expired
                del self.cache[cache_key]
                del self.cache_ttl[cache_key]
        
        # Compute and cache result
        result = compute_func()
        self.cache[cache_key] = result
        self.cache_ttl[cache_key] = time.time()
        
        return result
    
    async def process_single_prompt(self, prompt: str) -> Dict[str, Any]:
        """Process a single prompt (simulated)"""
        await asyncio.sleep(0.02)  # Simulate processing time
        return {
            "base_prompt": prompt,
            "enhanced_prompt": f"{prompt}, enhanced with style and quality",
            "processing_time_ms": 20
        }
    
    async def process_batch_prompts(self, prompts: List[str]) -> List[Dict[str, Any]]:
        """Process prompts in batch for better performance"""
        if not self.config.batch_processing_enabled:
            # Fall back to individual processing
            results = []
            for prompt in prompts:
                result = await self.process_single_prompt(prompt)
                results.append(result)
            return results
        
        # Batch processing optimization
        batch_start = time.time()
        results = []
        
        # Process in batches
        batch_size = min(self.config.batch_size, len(prompts))
        for i in range(0, len(prompts), batch_size):
            batch = prompts[i:i + batch_size]
            
            # Simulate batch processing efficiency
            await asyncio.sleep(0.01 * len(batch))  # Less time per item in batch
            
            for prompt in batch:
                results.append({
                    "base_prompt": prompt,
                    "enhanced_prompt": f"{prompt}, batch processed with optimizations",
                    "processing_time_ms": 10  # Faster due to batch processing
                })
        
        return results
    
    async def get_current_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        return self._get_memory_usage()
    
    async def create_large_dataset(self, size_mb: int) -> List[str]:
        """Create a large dataset for testing memory usage"""
        # Create approximately size_mb of data
        data_size = size_mb * 1024 * 1024 // 100  # Roughly 100 bytes per item
        return [f"data_item_{i}_" + "x" * 80 for i in range(data_size)]
    
    async def cleanup_memory(self, data: Any):
        """Clean up memory usage"""
        del data
        # Force garbage collection would happen automatically
        await asyncio.sleep(0.01)  # Allow for cleanup
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single task"""
        start_time = time.time()
        task_type = task.get("type", "unknown")
        data = task.get("data", "")
        
        # Simulate task processing
        if task_type == "enhancement":
            await asyncio.sleep(0.05)  # Simulate enhancement work
            result = f"Enhanced: {data}"
        else:
            await asyncio.sleep(0.03)  # Simulate other work
            result = f"Processed: {data}"
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "status": "completed",
            "result": result,
            "processing_time": processing_time,
            "task_type": task_type
        }
    
    async def process_tasks_concurrent(self, tasks: List[Dict[str, Any]], 
                                     max_workers: int = 3) -> List[Dict[str, Any]]:
        """Process tasks concurrently for better throughput"""
        if not self.config.concurrent_processing_enabled:
            # Fall back to sequential processing
            results = []
            for task in tasks:
                result = await self.process_task(task)
                results.append(result)
            return results
        
        # Concurrent processing with semaphore to limit workers
        semaphore = asyncio.Semaphore(max_workers)
        
        async def process_with_semaphore(task):
            async with semaphore:
                return await self.process_task(task)
        
        # Execute all tasks concurrently
        tasks_concurrent = [process_with_semaphore(task) for task in tasks]
        results = await asyncio.gather(*tasks_concurrent)
        
        return results
    
    async def start_profiling_session(self, session_name: str) -> str:
        """Start a profiling session"""
        session_id = f"prof_{uuid.uuid4().hex[:8]}"
        self.active_sessions[session_id] = {
            "name": session_name,
            "start_time": time.time(),
            "operations": [],
            "resource_snapshots": []
        }
        return session_id
    
    async def profile_operation(self, operation_name: str, operation_func: Callable):
        """Profile a specific operation"""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        # Execute operation
        if asyncio.iscoroutinefunction(operation_func):
            await operation_func()
        else:
            operation_func()
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        duration_ms = int((end_time - start_time) * 1000)
        memory_delta = end_memory - start_memory
        
        # Store operation metrics for all active sessions
        operation_data = {
            "name": operation_name,
            "duration_ms": duration_ms,
            "memory_delta_mb": memory_delta,
            "timestamp": start_time
        }
        
        for session in self.active_sessions.values():
            session["operations"].append(operation_data)
    
    async def get_profiling_results(self, session_id: str) -> Dict[str, Any]:
        """Get profiling results for a session"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        operations = session["operations"]
        
        return {
            "session_id": session_id,
            "operations": operations,
            "total_duration_ms": int((time.time() - session["start_time"]) * 1000),
            "operation_count": len(operations)
        }
    
    async def start_resource_monitoring(self, monitor_name: str) -> str:
        """Start resource monitoring"""
        monitor_id = f"mon_{uuid.uuid4().hex[:8]}"
        self.resource_monitors[monitor_id] = {
            "name": monitor_name,
            "start_time": time.time(),
            "cpu_samples": [],
            "memory_samples": [],
            "is_running": True
        }
        
        # Start background monitoring
        asyncio.create_task(self._monitor_resources(monitor_id))
        
        return monitor_id
    
    async def get_resource_metrics(self, monitor_id: str) -> Dict[str, Any]:
        """Get current resource metrics"""
        if monitor_id not in self.resource_monitors:
            return {"error": "Monitor not found"}
        
        monitor = self.resource_monitors[monitor_id]
        cpu_samples = monitor["cpu_samples"]
        memory_samples = monitor["memory_samples"]
        
        current_memory = self._get_memory_usage()
        current_cpu = psutil.cpu_percent()
        
        return {
            "monitoring_id": monitor_id,
            "cpu_usage": {
                "current": current_cpu,
                "average": sum(cpu_samples) / len(cpu_samples) if cpu_samples else current_cpu,
                "peak": max(cpu_samples) if cpu_samples else current_cpu
            },
            "memory_usage": {
                "current_mb": current_memory,
                "peak_mb": max(memory_samples) if memory_samples else current_memory,
                "average_mb": sum(memory_samples) / len(memory_samples) if memory_samples else current_memory
            },
            "disk_io": {
                "read_mb": 0.0,  # Simplified for demo
                "write_mb": 0.0
            },
            "network_io": {
                "sent_mb": 0.0,  # Simplified for demo
                "received_mb": 0.0
            }
        }
    
    async def stop_resource_monitoring(self, monitor_id: str) -> Dict[str, Any]:
        """Stop resource monitoring and get final report"""
        if monitor_id not in self.resource_monitors:
            return {"error": "Monitor not found"}
        
        monitor = self.resource_monitors[monitor_id]
        monitor["is_running"] = False
        
        total_duration_ms = int((time.time() - monitor["start_time"]) * 1000)
        
        final_report = {
            "monitoring_id": monitor_id,
            "total_duration_ms": total_duration_ms,
            "sample_count": len(monitor["cpu_samples"]),
            "final_metrics": await self.get_resource_metrics(monitor_id)
        }
        
        # Cleanup
        del self.resource_monitors[monitor_id]
        
        return final_report
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    async def _monitor_resources(self, monitor_id: str):
        """Background task to monitor resources"""
        monitor = self.resource_monitors.get(monitor_id)
        if not monitor:
            return
        
        while monitor.get("is_running", False):
            try:
                cpu_usage = psutil.cpu_percent()
                memory_usage = self._get_memory_usage()
                
                monitor["cpu_samples"].append(cpu_usage)
                monitor["memory_samples"].append(memory_usage)
                
                await asyncio.sleep(0.1)  # Sample every 100ms
            except Exception:
                break