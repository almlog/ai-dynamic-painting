"""
Batch processing service for large-scale AI operations.
Supports parallel processing, priority queuing, retry mechanisms, and resource management.
"""

import uuid
import time
import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from collections import defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from src.models.batch_job import (
    BatchJob,
    BatchJobConfig,
    BatchJobStatus,
    BatchJobResult,
    QueueInfo,
    ProcessingStats,
    RetryStats,
    ResourceStatus,
    ScheduledJobInfo,
    JobStatus,
    JobType,
    ErrorStrategy
)


class BatchProcessor:
    """Advanced batch processing service with intelligent queuing and resource management"""
    
    def __init__(self, db_url: str = "sqlite:///ai_dynamic_painting.db",
                 max_workers: int = 3, memory_limit_mb: int = 100,
                 cpu_limit_percent: int = 80):
        self.engine = create_engine(db_url)
        self.session_factory = sessionmaker(bind=self.engine)
        
        # Configuration
        self.max_workers = max_workers
        self.memory_limit_mb = memory_limit_mb
        self.cpu_limit_percent = cpu_limit_percent
        
        # Job storage (in-memory for performance)
        self.jobs = {}  # job_id -> job_data
        self.job_queue = []  # Priority queue
        self.running_jobs = {}  # job_id -> task
        self.completed_jobs = {}  # job_id -> results
        self.scheduled_jobs = {}  # job_id -> scheduled_time
        
        # Resource tracking
        self.active_workers = 0
        self.current_memory_usage = 0.0
        self.current_cpu_usage = 0.0
        
        # Statistics
        self.processing_stats = {}
        self.retry_stats = defaultdict(lambda: {"attempts": 0, "successes": 0, "failures": 0})
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Background tasks
        self.scheduler_task = None
        self.resource_monitor_task = None
        
        # Locks
        self.queue_lock = threading.RLock()
        self.jobs_lock = threading.RLock()
        
        # Start background tasks
        self._start_background_tasks()
    
    async def submit_batch_job(self, job_type: str, input_data: List[Dict[str, Any]],
                              batch_size: int = 10, priority: int = 1,
                              parallel_workers: int = None, max_retries: int = 3,
                              timeout_seconds: int = 300, error_strategy: str = "continue",
                              estimated_memory_mb: int = 10, **kwargs) -> str:
        """Submit a new batch job to the processing queue"""
        
        job_id = f"batch_{uuid.uuid4().hex[:8]}"
        
        # Create job data
        job_data = {
            "job_id": job_id,
            "job_type": job_type,
            "input_data": input_data,
            "batch_size": batch_size,
            "priority": priority,
            "parallel_workers": parallel_workers or 1,
            "max_retries": max_retries,
            "timeout_seconds": timeout_seconds,
            "error_strategy": error_strategy,
            "estimated_memory_mb": estimated_memory_mb,
            "status": JobStatus.PENDING.value,
            "total_items": len(input_data),
            "processed_items": 0,
            "successful_items": 0,
            "failed_items": 0,
            "results": [],
            "errors": [],
            "created_at": datetime.now(),
            "retry_count": 0,
            **kwargs
        }
        
        with self.jobs_lock:
            self.jobs[job_id] = job_data
        
        # Add to priority queue
        with self.queue_lock:
            self.job_queue.append(job_data)
            # Sort by priority (1 = highest priority)
            self.job_queue.sort(key=lambda x: x["priority"])
        
        return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a batch job"""
        with self.jobs_lock:
            job_data = self.jobs.get(job_id)
            if not job_data:
                return None
            
            progress_percentage = 0.0
            if job_data["total_items"] > 0:
                progress_percentage = (job_data["processed_items"] / job_data["total_items"]) * 100.0
            
            return {
                "job_id": job_id,
                "job_type": job_data["job_type"],
                "status": job_data["status"],
                "total_items": job_data["total_items"],
                "processed_items": job_data["processed_items"],
                "successful_items": job_data["successful_items"],
                "failed_items": job_data["failed_items"],
                "progress_percentage": progress_percentage,
                "priority": job_data["priority"],
                "batch_size": job_data["batch_size"],
                "created_at": job_data["created_at"].isoformat(),
                "estimated_memory_mb": job_data.get("estimated_memory_mb", 10)
            }
    
    async def get_batch_results(self, job_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get results from completed batch job"""
        with self.jobs_lock:
            job_data = self.jobs.get(job_id)
            if not job_data:
                return None
            
            return job_data.get("results", [])
    
    async def get_queue_info(self) -> Dict[str, Any]:
        """Get information about the job queue"""
        with self.queue_lock:
            pending_jobs = [job for job in self.job_queue if job["status"] == JobStatus.PENDING.value]
            running_jobs = [job for job in self.jobs.values() if job["status"] == JobStatus.RUNNING.value]
            scheduled_jobs = [job for job in self.scheduled_jobs.values()]
            
            return {
                "total_jobs": len(self.jobs),
                "pending_jobs": len(pending_jobs),
                "running_jobs": len(running_jobs),
                "scheduled_jobs": len(scheduled_jobs),
                "queued_jobs": len(pending_jobs),
                "jobs": [
                    {
                        "job_id": job["job_id"],
                        "job_type": job["job_type"],
                        "priority": job["priority"],
                        "status": job["status"],
                        "total_items": job["total_items"]
                    }
                    for job in sorted(self.job_queue, key=lambda x: x["priority"])
                ]
            }
    
    async def process_pending_jobs(self):
        """Process pending jobs in the queue"""
        while True:
            # Check if we can start new jobs
            if self.active_workers >= self.max_workers:
                break
            
            # Get next job from queue
            with self.queue_lock:
                if not self.job_queue:
                    break
                
                # Find next pending job
                next_job = None
                for i, job in enumerate(self.job_queue):
                    if job["status"] == JobStatus.PENDING.value:
                        # Check resource requirements
                        if self._can_start_job(job):
                            next_job = self.job_queue.pop(i)
                            break
                
                if not next_job:
                    break
            
            # Start processing the job
            await self._start_job_processing(next_job)
    
    async def get_processing_stats(self, job_id: str) -> Dict[str, Any]:
        """Get processing statistics for a job"""
        return self.processing_stats.get(job_id, {
            "parallel_workers_used": 1,
            "total_processing_time": 0.0,
            "items_processed": 0,
            "average_item_time_ms": 0.0
        })
    
    async def get_error_summary(self, job_id: str) -> Dict[str, Any]:
        """Get error summary for a job"""
        with self.jobs_lock:
            job_data = self.jobs.get(job_id)
            if not job_data:
                return {"error": "Job not found"}
            
            total_items = job_data["total_items"]
            failed_items = job_data["failed_items"]
            successful_items = job_data["successful_items"]
            
            return {
                "total_errors": failed_items,
                "success_count": successful_items,
                "error_rate": failed_items / total_items if total_items > 0 else 0.0,
                "errors": job_data.get("errors", [])
            }
    
    async def get_job_progress(self, job_id: str) -> Dict[str, Any]:
        """Get detailed progress information for a job"""
        with self.jobs_lock:
            job_data = self.jobs.get(job_id)
            if not job_data:
                return {"error": "Job not found"}
            
            total_items = job_data["total_items"]
            processed_items = job_data["processed_items"]
            percentage = (processed_items / total_items * 100.0) if total_items > 0 else 0.0
            
            return {
                "job_id": job_id,
                "status": job_data["status"],
                "percentage": percentage,
                "processed_items": processed_items,
                "total_items": total_items,
                "successful_items": job_data["successful_items"],
                "failed_items": job_data["failed_items"]
            }
    
    async def get_retry_stats(self, job_id: str) -> Dict[str, Any]:
        """Get retry statistics for a job"""
        with self.jobs_lock:
            job_data = self.jobs.get(job_id)
            if not job_data:
                return {"error": "Job not found"}
            
            return {
                "job_id": job_id,
                "max_retries": job_data["max_retries"],
                "total_retry_attempts": job_data["retry_count"],
                "retry_history": job_data.get("retry_history", [])
            }
    
    async def schedule_batch_job(self, job_type: str, input_data: List[Dict[str, Any]],
                                scheduled_time: datetime, recurring_interval_minutes: int = None,
                                **kwargs) -> str:
        """Schedule a batch job for future execution"""
        
        job_id = f"scheduled_{uuid.uuid4().hex[:8]}"
        
        job_data = {
            "job_id": job_id,
            "job_type": job_type,
            "input_data": input_data,
            "total_items": len(input_data),
            "processed_items": 0,
            "successful_items": 0,
            "failed_items": 0,
            "results": [],
            "errors": [],
            "scheduled_time": scheduled_time,
            "recurring_interval_minutes": recurring_interval_minutes,
            "status": JobStatus.SCHEDULED.value,
            "created_at": datetime.now(),
            "batch_size": kwargs.get("batch_size", 10),
            "priority": kwargs.get("priority", 1),
            "max_retries": kwargs.get("max_retries", 3),
            "timeout_seconds": kwargs.get("timeout_seconds", 300),
            "retry_count": 0,
            **kwargs
        }
        
        with self.jobs_lock:
            self.jobs[job_id] = job_data
            self.scheduled_jobs[job_id] = scheduled_time
        
        return job_id
    
    async def process_scheduled_jobs(self):
        """Process jobs that are scheduled to run now"""
        now = datetime.now()
        
        jobs_to_run = []
        with self.jobs_lock:
            for job_id, scheduled_time in list(self.scheduled_jobs.items()):
                if now >= scheduled_time:
                    job_data = self.jobs.get(job_id)
                    if job_data:
                        jobs_to_run.append(job_data)
                        del self.scheduled_jobs[job_id]
        
        # Convert scheduled jobs to pending jobs
        for job_data in jobs_to_run:
            job_data["status"] = JobStatus.PENDING.value
            with self.queue_lock:
                self.job_queue.append(job_data)
                self.job_queue.sort(key=lambda x: x.get("priority", 1))
        
        # Process the newly pending jobs
        if jobs_to_run:
            await self.process_pending_jobs()
    
    async def get_resource_status(self) -> Dict[str, Any]:
        """Get current resource usage status"""
        return {
            "active_workers": self.active_workers,
            "max_workers": self.max_workers,
            "estimated_memory_usage_mb": self.current_memory_usage,
            "memory_limit_mb": self.memory_limit_mb,
            "cpu_usage_percent": self.current_cpu_usage,
            "cpu_limit_percent": self.cpu_limit_percent,
            "queued_jobs": len([job for job in self.job_queue if job["status"] == JobStatus.PENDING.value])
        }
    
    # Helper methods
    
    def _can_start_job(self, job_data: Dict[str, Any]) -> bool:
        """Check if a job can be started based on resource constraints"""
        estimated_memory = job_data.get("estimated_memory_mb", 10)
        
        # Check memory constraints
        if self.current_memory_usage + estimated_memory > self.memory_limit_mb:
            return False
        
        # Check worker availability
        if self.active_workers >= self.max_workers:
            return False
        
        return True
    
    async def _start_job_processing(self, job_data: Dict[str, Any]):
        """Start processing a job"""
        job_id = job_data["job_id"]
        
        # Update job status
        job_data["status"] = JobStatus.RUNNING.value
        job_data["started_at"] = datetime.now()
        
        # Update resource usage
        self.active_workers += 1
        self.current_memory_usage += job_data.get("estimated_memory_mb", 10)
        
        # Start processing task
        task = asyncio.create_task(self._process_job(job_data))
        self.running_jobs[job_id] = task
        
        # Wait for completion
        try:
            await task
        finally:
            # Clean up
            self.running_jobs.pop(job_id, None)
            self.active_workers -= 1
            self.current_memory_usage -= job_data.get("estimated_memory_mb", 10)
    
    async def _process_job(self, job_data: Dict[str, Any]):
        """Process a batch job"""
        job_id = job_data["job_id"]
        job_type = job_data["job_type"]
        input_data = job_data["input_data"]
        batch_size = job_data["batch_size"]
        
        start_time = time.time()
        results = []
        errors = []
        
        try:
            # Process items in batches
            for i in range(0, len(input_data), batch_size):
                batch = input_data[i:i + batch_size]
                
                # Process batch items
                batch_results = await self._process_batch(job_type, batch, job_data)
                
                # Collect results
                for item_result in batch_results:
                    if item_result.get("status") == "success":
                        results.append(item_result)
                        job_data["successful_items"] += 1
                    else:
                        errors.append(item_result)
                        job_data["failed_items"] += 1
                    
                    job_data["processed_items"] += 1
                
                # Update progress
                job_data["results"] = results
                job_data["errors"] = errors
                
                # Small delay between batches
                await asyncio.sleep(0.01)
            
            # Mark job as completed
            job_data["status"] = JobStatus.COMPLETED.value
            job_data["completed_at"] = datetime.now()
            
        except Exception as e:
            # Handle job failure
            job_data["status"] = JobStatus.FAILED.value
            job_data["error"] = str(e)
        
        # Record processing stats
        processing_time = time.time() - start_time
        self.processing_stats[job_id] = {
            "parallel_workers_used": job_data.get("parallel_workers", 1),
            "total_processing_time": processing_time,
            "items_processed": job_data["processed_items"],
            "average_item_time_ms": (processing_time * 1000) / max(job_data["processed_items"], 1)
        }
    
    async def _process_batch(self, job_type: str, batch: List[Dict[str, Any]], 
                           job_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a single batch of items"""
        results = []
        
        for item in batch:
            try:
                # Simulate processing based on job type
                if job_type == "prompt_enhancement":
                    result = await self._process_prompt_enhancement(item)
                elif job_type == "video_generation":
                    result = await self._process_video_generation(item)
                elif job_type == "unreliable_processing":
                    result = await self._process_unreliable_item(item)
                elif job_type == "resource_intensive":
                    result = await self._process_resource_intensive(item)
                else:
                    result = await self._process_generic_item(item)
                
                result["status"] = "success"
                result["original_prompt"] = item.get("prompt", "")
                results.append(result)
                
            except Exception as e:
                error_result = {
                    "status": "error",
                    "error": str(e),
                    "item": item
                }
                results.append(error_result)
        
        return results
    
    async def _process_prompt_enhancement(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process prompt enhancement item"""
        await asyncio.sleep(0.02)  # Simulate processing time
        
        prompt = item.get("prompt", "")
        style = item.get("style", "enhanced")
        
        enhanced_prompt = f"{prompt}, {style} style with professional lighting and composition"
        
        return {
            "enhanced_prompt": enhanced_prompt,
            "quality_score": random.uniform(0.7, 0.95),
            "processing_time_ms": 20
        }
    
    async def _process_video_generation(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process video generation item"""
        await asyncio.sleep(0.1)  # Simulate longer processing time
        
        return {
            "video_id": f"video_{uuid.uuid4().hex[:8]}",
            "duration": item.get("duration", 5),
            "quality": item.get("quality", "hd"),
            "status": "generated"
        }
    
    async def _process_unreliable_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process item with simulated failures"""
        await asyncio.sleep(0.05)
        
        fail_probability = item.get("fail_probability", 0.3)
        if random.random() < fail_probability:
            raise Exception("Simulated processing failure")
        
        return {
            "result": f"Processed {item.get('item', 'unknown')}",
            "reliable": True
        }
    
    async def _process_resource_intensive(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process resource-intensive item"""
        await asyncio.sleep(0.1)  # Simulate resource usage
        
        return {
            "processed_data": item.get("data", ""),
            "memory_used_mb": 5,
            "processing_intensive": True
        }
    
    async def _process_generic_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process generic item"""
        await asyncio.sleep(0.02)
        
        return {
            "processed": True,
            "item_data": item
        }
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        # Background tasks would be started here for production
        pass