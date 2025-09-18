"""AI task scheduling configuration using APScheduler."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ai_system.scheduler")


class AIScheduler:
    """AI task scheduler for video generation and learning updates."""
    
    def __init__(self):
        """Initialize the scheduler with configured settings."""
        self.scheduler = AsyncIOScheduler(
            jobstores={
                'default': MemoryJobStore()
            },
            executors={
                'default': AsyncIOExecutor()
            },
            job_defaults={
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 300  # 5 minutes grace time
            },
            timezone=os.getenv('SCHEDULER_TIMEZONE', 'Asia/Tokyo')
        )
        
        self._setup_scheduled_tasks()
        
    def _setup_scheduled_tasks(self):
        """Setup all scheduled AI tasks."""
        
        # Morning video generation (6:00 AM)
        morning_time = os.getenv('SCHEDULER_MORNING_TIME', '06:00').split(':')
        self.scheduler.add_job(
            func=self._generate_morning_video,
            trigger=CronTrigger(
                hour=int(morning_time[0]),
                minute=int(morning_time[1])
            ),
            id='morning_generation',
            name='Morning Video Generation',
            replace_existing=True
        )
        
        # Afternoon video generation (12:00 PM)
        afternoon_time = os.getenv('SCHEDULER_AFTERNOON_TIME', '12:00').split(':')
        self.scheduler.add_job(
            func=self._generate_afternoon_video,
            trigger=CronTrigger(
                hour=int(afternoon_time[0]),
                minute=int(afternoon_time[1])
            ),
            id='afternoon_generation',
            name='Afternoon Video Generation',
            replace_existing=True
        )
        
        # Evening video generation (6:00 PM)
        evening_time = os.getenv('SCHEDULER_EVENING_TIME', '18:00').split(':')
        self.scheduler.add_job(
            func=self._generate_evening_video,
            trigger=CronTrigger(
                hour=int(evening_time[0]),
                minute=int(evening_time[1])
            ),
            id='evening_generation',
            name='Evening Video Generation',
            replace_existing=True
        )
        
        # Night video generation (10:00 PM)
        night_time = os.getenv('SCHEDULER_NIGHT_TIME', '22:00').split(':')
        self.scheduler.add_job(
            func=self._generate_night_video,
            trigger=CronTrigger(
                hour=int(night_time[0]),
                minute=int(night_time[1])
            ),
            id='night_generation',
            name='Night Video Generation',
            replace_existing=True
        )
        
        # Weather update (every hour)
        weather_interval = int(os.getenv('WEATHER_UPDATE_INTERVAL', '3600'))
        self.scheduler.add_job(
            func=self._update_weather_context,
            trigger=IntervalTrigger(seconds=weather_interval),
            id='weather_update',
            name='Weather Context Update',
            replace_existing=True
        )
        
        # Learning system update (daily)
        learning_interval = int(os.getenv('AI_LEARNING_UPDATE_INTERVAL', '86400'))
        self.scheduler.add_job(
            func=self._update_learning_model,
            trigger=IntervalTrigger(seconds=learning_interval),
            id='learning_update',
            name='Learning Model Update',
            replace_existing=True
        )
        
        # Cost monitoring (every 5 minutes)
        self.scheduler.add_job(
            func=self._monitor_api_costs,
            trigger=IntervalTrigger(seconds=300),
            id='cost_monitor',
            name='API Cost Monitor',
            replace_existing=True
        )
        
    async def _generate_morning_video(self):
        """Generate morning-themed video."""
        logger.info("Starting morning video generation", extra={
            "ai_context": {
                "task": "morning_generation",
                "time": datetime.now().isoformat()
            }
        })
        # Implementation will be added in T239-T244
        
    async def _generate_afternoon_video(self):
        """Generate afternoon-themed video."""
        logger.info("Starting afternoon video generation", extra={
            "ai_context": {
                "task": "afternoon_generation",
                "time": datetime.now().isoformat()
            }
        })
        # Implementation will be added in T239-T244
        
    async def _generate_evening_video(self):
        """Generate evening-themed video."""
        logger.info("Starting evening video generation", extra={
            "ai_context": {
                "task": "evening_generation",
                "time": datetime.now().isoformat()
            }
        })
        # Implementation will be added in T239-T244
        
    async def _generate_night_video(self):
        """Generate night-themed video."""
        logger.info("Starting night video generation", extra={
            "ai_context": {
                "task": "night_generation",
                "time": datetime.now().isoformat()
            }
        })
        # Implementation will be added in T239-T244
        
    async def _update_weather_context(self):
        """Update weather context for prompt generation."""
        logger.info("Updating weather context", extra={
            "ai_context": {
                "task": "weather_update",
                "time": datetime.now().isoformat()
            }
        })
        # Implementation will be added in T239-T244
        
    async def _update_learning_model(self):
        """Update learning model based on user feedback."""
        logger.info("Updating learning model", extra={
            "ai_context": {
                "task": "learning_update",
                "time": datetime.now().isoformat()
            }
        })
        # Implementation will be added in T239-T244
        
    async def _monitor_api_costs(self):
        """Monitor API costs and send alerts if needed."""
        logger.debug("Monitoring API costs", extra={
            "ai_context": {
                "task": "cost_monitor",
                "time": datetime.now().isoformat()
            }
        })
        # Implementation will be added in T269-T270
        
    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("AI Scheduler started successfully")
            
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("AI Scheduler stopped")
            
    def get_jobs(self) -> list:
        """Get list of all scheduled jobs."""
        return self.scheduler.get_jobs()
    
    def pause_job(self, job_id: str):
        """Pause a specific job."""
        self.scheduler.pause_job(job_id)
        logger.info(f"Job {job_id} paused")
        
    def resume_job(self, job_id: str):
        """Resume a specific job."""
        self.scheduler.resume_job(job_id)
        logger.info(f"Job {job_id} resumed")
        
    def trigger_job(self, job_id: str):
        """Manually trigger a job."""
        job = self.scheduler.get_job(job_id)
        if job:
            self.scheduler.add_job(
                func=job.func,
                trigger='date',
                id=f"{job_id}_manual_{datetime.now().timestamp()}",
                name=f"Manual: {job.name}"
            )
            logger.info(f"Job {job_id} triggered manually")
        else:
            logger.error(f"Job {job_id} not found")


# Singleton instance
_scheduler_instance: Optional[AIScheduler] = None


def get_scheduler() -> AIScheduler:
    """Get singleton scheduler instance."""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = AIScheduler()
    return _scheduler_instance