"""AI Generation API endpoints for Phase 2 AI integration."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from pydantic import BaseModel, Field, validator
import asyncio
import json

# Import AI services
from src.ai.services.veo_client import VEOGenerationService, VEOValidationError, VEOQuotaExceededError, VEOTimeoutError
from src.ai.services.prompt_generation_service import PromptGenerationService
from src.ai.services.context_aware_service import ContextAwareService
from src.ai.services.scheduling_service import SchedulingService, Priority
from src.ai.services.quality_assurance_service import QualityAssuranceService
from src.ai.services.monitoring_service import MonitoringService

# Import models
from src.ai.models.ai_generation_task import AIGenerationTaskCreate, AIGenerationTaskResponse
from src.ai.models.generated_video import GeneratedVideoCreate, GeneratedVideoResponse

logger = logging.getLogger("ai_generation_api")

router = APIRouter(prefix="/ai", tags=["AI Generation"])

# Service instances (will be initialized during startup)
veo_service: Optional[VEOGenerationService] = None
prompt_service: Optional[PromptGenerationService] = None
context_service: Optional[ContextAwareService] = None
scheduling_service: Optional[SchedulingService] = None
quality_service: Optional[QualityAssuranceService] = None
monitoring_service: Optional[MonitoringService] = None


class GenerateVideoRequest(BaseModel):
    """Request model for video generation."""
    prompt: str = Field(..., min_length=1, max_length=1000, description="Video generation prompt")
    duration_seconds: int = Field(30, ge=5, le=60, description="Video duration in seconds")
    resolution: str = Field("1920x1080", pattern="^(1920x1080|1280x720|854x480)$", description="Video resolution")
    fps: int = Field(30, ge=24, le=60, description="Frames per second")
    quality: str = Field("high", pattern="^(draft|standard|high)$", description="Generation quality")
    style: Optional[str] = Field(None, max_length=100, description="Visual style preference")
    use_context: bool = Field(True, description="Use environmental context for prompt enhancement")
    priority: str = Field("normal", pattern="^(low|normal|high|urgent)$", description="Generation priority")
    
    @validator('resolution')
    def validate_resolution(cls, v):
        valid_resolutions = ["1920x1080", "1280x720", "854x480"]
        if v not in valid_resolutions:
            raise ValueError(f"Resolution must be one of: {valid_resolutions}")
        return v


class GenerateVideoResponse(BaseModel):
    """Response model for video generation."""
    task_id: str
    status: str
    scheduled_time: datetime
    prompt_used: str
    generation_params: Dict[str, Any]
    estimated_completion_time: Optional[datetime] = None
    message: str


class VideoGenerationStatus(BaseModel):
    """Video generation status response."""
    task_id: str
    status: str
    progress_percent: float
    prompt: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    result: Optional[Dict[str, Any]] = None


class ScheduleGenerationRequest(BaseModel):
    """Request model for scheduling video generation."""
    prompt_template: str = Field(..., min_length=1, max_length=500)
    scheduled_time: datetime = Field(..., description="When to generate the video")
    duration_seconds: int = Field(30, ge=5, le=60)
    resolution: str = Field("1920x1080", pattern="^(1920x1080|1280x720|854x480)$")
    quality: str = Field("high", pattern="^(draft|standard|high)$")
    use_context: bool = Field(True, description="Use environmental context")
    priority: str = Field("normal", pattern="^(low|normal|high|urgent)$")


class ContextPromptRequest(BaseModel):
    """Request model for context-based prompt generation."""
    base_prompt: str = Field(..., min_length=1, max_length=500)
    sensor_data: Optional[Dict[str, Any]] = Field(None, description="Current sensor readings")
    style: Optional[str] = Field(None, max_length=100)
    custom_elements: Optional[List[str]] = Field(None, max_items=5)


async def get_services():
    """Dependency to ensure services are available."""
    global veo_service, prompt_service, context_service, scheduling_service, quality_service, monitoring_service
    
    if not all([veo_service, prompt_service, context_service, scheduling_service]):
        raise HTTPException(
            status_code=503,
            detail="AI services not properly initialized"
        )
    
    return {
        "veo": veo_service,
        "prompt": prompt_service,
        "context": context_service,
        "scheduling": scheduling_service,
        "quality": quality_service,
        "monitoring": monitoring_service
    }


@router.post("/generate", response_model=GenerateVideoResponse)
async def generate_video(
    request: GenerateVideoRequest,
    background_tasks: BackgroundTasks,
    services: Dict[str, Any] = Depends(get_services)
):
    """Generate a video using AI with optional context enhancement."""
    
    try:
        logger.info(f"Video generation request: {request.prompt[:100]}...")
        
        # Get services
        veo = services["veo"]
        prompt_svc = services["prompt"]
        context_svc = services["context"]
        scheduling_svc = services["scheduling"]
        
        # Enhance prompt with context if requested
        final_prompt = request.prompt
        context_data = None
        
        if request.use_context:
            try:
                # Get current sensor data (would come from M5Stack in real implementation)
                sensor_data = {
                    "temperature": 22.0,
                    "humidity": 50.0,
                    "light_level": 100,
                    "motion_detected": False
                }
                
                # Generate context
                context_data = context_svc.update_sensor_data(sensor_data)
                
                # Generate enhanced prompt
                final_prompt = prompt_svc.generate_prompt(
                    context_data=context_data,
                    style=request.style
                )
                
                logger.info(f"Enhanced prompt with context: {final_prompt[:100]}...")
                
            except Exception as e:
                logger.warning(f"Failed to enhance prompt with context: {e}")
                # Continue with original prompt
        
        # Map priority
        priority_map = {
            "low": Priority.LOW,
            "normal": Priority.NORMAL,
            "high": Priority.HIGH,
            "urgent": Priority.URGENT
        }
        
        # Schedule generation task
        scheduled_time = datetime.now() + timedelta(seconds=10)  # Small delay for processing
        
        generation_params = {
            "duration_seconds": request.duration_seconds,
            "resolution": request.resolution,
            "fps": request.fps,
            "quality": request.quality,
            "style": request.style
        }
        
        task_id = await scheduling_svc.schedule_task(
            prompt=final_prompt,
            scheduled_time=scheduled_time,
            priority=priority_map[request.priority],
            context_data=context_data.__dict__ if context_data else None,
            generation_params=generation_params
        )
        
        # Estimate completion time based on queue and quality
        estimated_completion = scheduled_time + timedelta(minutes=5)  # Base estimate
        if request.quality == "high":
            estimated_completion += timedelta(minutes=2)
        
        response = GenerateVideoResponse(
            task_id=task_id,
            status="scheduled",
            scheduled_time=scheduled_time,
            prompt_used=final_prompt,
            generation_params=generation_params,
            estimated_completion_time=estimated_completion,
            message=f"Video generation task scheduled. Task ID: {task_id}"
        )
        
        logger.info(f"Video generation scheduled: {task_id}")
        
        return response
        
    except VEOQuotaExceededError:
        raise HTTPException(
            status_code=429,
            detail="VEO API quota exceeded. Please try again later."
        )
    except VEOValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid generation parameters: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to schedule video generation"
        )


@router.get("/generation/{task_id}", response_model=VideoGenerationStatus)
async def get_generation_status(
    task_id: str,
    services: Dict[str, Any] = Depends(get_services)
):
    """Get the status of a video generation task."""
    
    try:
        scheduling_svc = services["scheduling"]
        
        # Get task status
        task = scheduling_svc.get_task_status(task_id)
        
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Generation task {task_id} not found"
            )
        
        # Calculate progress
        progress_percent = 0.0
        if task.status.value == "pending":
            progress_percent = 0.0
        elif task.status.value == "running":
            progress_percent = 50.0
        elif task.status.value == "completed":
            progress_percent = 100.0
        elif task.status.value in ["failed", "cancelled"]:
            progress_percent = 0.0
        
        response = VideoGenerationStatus(
            task_id=task.task_id,
            status=task.status.value,
            progress_percent=progress_percent,
            prompt=task.prompt,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            error_message=task.error_message,
            retry_count=task.retry_count,
            result=task.result_data
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get generation status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve generation status"
        )


@router.post("/schedule", response_model=GenerateVideoResponse)
async def schedule_generation(
    request: ScheduleGenerationRequest,
    services: Dict[str, Any] = Depends(get_services)
):
    """Schedule a video generation for a future time."""
    
    try:
        logger.info(f"Scheduling video generation for {request.scheduled_time}")
        
        # Validate scheduled time is in future
        if request.scheduled_time <= datetime.now():
            raise HTTPException(
                status_code=400,
                detail="Scheduled time must be in the future"
            )
        
        # Validate not too far in future (1 week max)
        if request.scheduled_time > datetime.now() + timedelta(days=7):
            raise HTTPException(
                status_code=400,
                detail="Cannot schedule more than 7 days in advance"
            )
        
        scheduling_svc = services["scheduling"]
        
        # Map priority
        priority_map = {
            "low": Priority.LOW,
            "normal": Priority.NORMAL,
            "high": Priority.HIGH,
            "urgent": Priority.URGENT
        }
        
        generation_params = {
            "duration_seconds": request.duration_seconds,
            "resolution": request.resolution,
            "quality": request.quality,
            "use_context": request.use_context
        }
        
        task_id = await scheduling_svc.schedule_task(
            prompt=request.prompt_template,
            scheduled_time=request.scheduled_time,
            priority=priority_map[request.priority],
            generation_params=generation_params
        )
        
        response = GenerateVideoResponse(
            task_id=task_id,
            status="scheduled",
            scheduled_time=request.scheduled_time,
            prompt_used=request.prompt_template,
            generation_params=generation_params,
            message=f"Video generation scheduled for {request.scheduled_time}. Task ID: {task_id}"
        )
        
        logger.info(f"Video generation scheduled: {task_id} for {request.scheduled_time}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to schedule generation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to schedule video generation"
        )


@router.post("/prompt/generate")
async def generate_contextual_prompt(
    request: ContextPromptRequest,
    services: Dict[str, Any] = Depends(get_services)
):
    """Generate a contextualized prompt based on environmental data."""
    
    try:
        prompt_svc = services["prompt"]
        context_svc = services["context"]
        
        # Use provided sensor data or default
        sensor_data = request.sensor_data or {
            "temperature": 22.0,
            "humidity": 50.0,
            "light_level": 100,
            "motion_detected": False
        }
        
        # Generate context
        context_data = context_svc.update_sensor_data(sensor_data)
        
        # Generate enhanced prompt
        enhanced_prompt = prompt_svc.generate_prompt(
            context_data=context_data,
            style=request.style,
            custom_elements=request.custom_elements
        )
        
        # Get alternative suggestions
        suggestions = prompt_svc.get_prompt_suggestions(context_data)
        
        return {
            "original_prompt": request.base_prompt,
            "enhanced_prompt": enhanced_prompt,
            "context_used": context_data.__dict__,
            "alternative_suggestions": suggestions,
            "generation_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to generate contextual prompt: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate contextual prompt"
        )


@router.get("/tasks")
async def get_active_tasks(
    limit: int = Query(20, ge=1, le=100),
    services: Dict[str, Any] = Depends(get_services)
):
    """Get list of active generation tasks."""
    
    try:
        scheduling_svc = services["scheduling"]
        
        active_tasks = scheduling_svc.get_active_tasks()
        
        # Convert to response format
        tasks = []
        for task in active_tasks[:limit]:
            task_info = {
                "task_id": task.task_id,
                "prompt": task.prompt[:100] + "..." if len(task.prompt) > 100 else task.prompt,
                "status": task.status.value,
                "priority": task.priority.name.lower(),
                "scheduled_time": task.scheduled_time.isoformat(),
                "created_at": task.created_at.isoformat(),
                "retry_count": task.retry_count
            }
            
            if task.started_at:
                task_info["started_at"] = task.started_at.isoformat()
            if task.error_message:
                task_info["error_message"] = task.error_message
            
            tasks.append(task_info)
        
        return {
            "tasks": tasks,
            "total_count": len(active_tasks),
            "returned_count": len(tasks)
        }
        
    except Exception as e:
        logger.error(f"Failed to get active tasks: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve active tasks"
        )


@router.delete("/generation/{task_id}")
async def cancel_generation(
    task_id: str,
    services: Dict[str, Any] = Depends(get_services)
):
    """Cancel a scheduled generation task."""
    
    try:
        scheduling_svc = services["scheduling"]
        
        success = await scheduling_svc.cancel_task(task_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found or cannot be cancelled"
            )
        
        return {
            "message": f"Generation task {task_id} cancelled successfully",
            "task_id": task_id,
            "cancelled_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel generation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to cancel generation task"
        )


@router.get("/health")
async def get_ai_system_health(
    services: Dict[str, Any] = Depends(get_services)
):
    """Get AI system health status."""
    
    try:
        monitoring_svc = services["monitoring"]
        
        if monitoring_svc:
            health_status = await monitoring_svc.perform_health_check()
            
            return {
                "status": health_status.status,
                "score": health_status.score,
                "last_updated": health_status.last_updated.isoformat(),
                "components": health_status.components,
                "active_alerts": [
                    {
                        "alert_id": alert.alert_id,
                        "level": alert.level.value,
                        "title": alert.title,
                        "message": alert.message,
                        "triggered_at": alert.triggered_at.isoformat()
                    }
                    for alert in health_status.active_alerts
                ],
                "recommendations": health_status.recommendations
            }
        else:
            return {
                "status": "unknown",
                "score": 0.0,
                "message": "Monitoring service not available",
                "components": {}
            }
            
    except Exception as e:
        logger.error(f"Failed to get AI system health: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve AI system health"
        )


@router.get("/statistics")
async def get_ai_statistics(
    services: Dict[str, Any] = Depends(get_services)
):
    """Get comprehensive AI system statistics."""
    
    try:
        stats = {}
        
        # Scheduling statistics
        if services["scheduling"]:
            stats["scheduling"] = services["scheduling"].get_statistics()
        
        # Quality statistics
        if services["quality"]:
            stats["quality"] = services["quality"].get_quality_statistics()
        
        # Monitoring statistics
        if services["monitoring"]:
            stats["monitoring"] = services["monitoring"].get_monitoring_statistics()
        
        # VEO service info (if available)
        if services["veo"]:
            stats["veo_api"] = {
                "daily_quota": getattr(services["veo"], 'daily_quota', 0),
                "per_minute_quota": getattr(services["veo"], 'per_minute_quota', 0),
                "model_name": getattr(services["veo"], 'model_name', 'unknown')
            }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get AI statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve AI statistics"
        )


# T246: Quality Assessment API Endpoints
class QualityAssessmentRequest(BaseModel):
    """Request model for video quality assessment."""
    video_url: str = Field(..., description="URL of the video to assess")
    video_metadata: Dict[str, Any] = Field(..., description="Video metadata")
    original_prompt: str = Field(..., min_length=1, description="Original generation prompt")
    expected_quality: Optional[float] = Field(None, ge=0.0, le=10.0, description="Expected quality threshold")


class QualityAssessmentResponse(BaseModel):
    """Response model for quality assessment results."""
    overall_score: float
    resolution_score: float
    clarity_score: float
    color_score: float
    composition_score: float
    prompt_adherence_score: float
    technical_quality_score: float
    issues: List[str]
    recommendations: List[str]
    quality_category: str  # excellent, good, fair, poor
    passed_threshold: bool
    analysis_timestamp: str
    processing_time_ms: int


@router.post("/quality/assess", response_model=QualityAssessmentResponse)
async def assess_video_quality(
    request: QualityAssessmentRequest,
    services: Dict[str, Any] = Depends(get_services)
):
    """Assess the quality of a generated video."""
    
    try:
        logger.info(f"Quality assessment request for: {request.video_url}")
        
        quality_svc = services["quality"]
        if not quality_svc:
            raise HTTPException(
                status_code=503,
                detail="Quality assessment service not available"
            )
        
        # Perform quality assessment
        metrics = await quality_svc.assess_video_quality(
            video_url=request.video_url,
            video_metadata=request.video_metadata,
            original_prompt=request.original_prompt
        )
        
        # Determine quality category
        if metrics.overall_score >= 9.0:
            quality_category = "excellent"
        elif metrics.overall_score >= 7.5:
            quality_category = "good"
        elif metrics.overall_score >= 6.0:
            quality_category = "fair"
        else:
            quality_category = "poor"
        
        # Check if passed threshold
        threshold = request.expected_quality or 6.0
        passed_threshold = metrics.overall_score >= threshold
        
        response = QualityAssessmentResponse(
            overall_score=metrics.overall_score,
            resolution_score=metrics.resolution_score,
            clarity_score=metrics.clarity_score,
            color_score=metrics.color_score,
            composition_score=metrics.composition_score,
            prompt_adherence_score=metrics.prompt_adherence_score,
            technical_quality_score=metrics.technical_quality_score,
            issues=[issue.value for issue in metrics.issues],
            recommendations=metrics.recommendations,
            quality_category=quality_category,
            passed_threshold=passed_threshold,
            analysis_timestamp=metrics.analysis_timestamp.isoformat(),
            processing_time_ms=metrics.processing_time_ms
        )
        
        logger.info(f"Quality assessment completed: score={metrics.overall_score:.2f}, category={quality_category}")
        
        return response
        
    except Exception as e:
        logger.error(f"Quality assessment failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to assess video quality"
        )


@router.get("/quality/trends")
async def get_quality_trends(
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    services: Dict[str, Any] = Depends(get_services)
):
    """Get quality trends over time."""
    
    try:
        quality_svc = services["quality"]
        if not quality_svc:
            raise HTTPException(
                status_code=503,
                detail="Quality assessment service not available"
            )
        
        trends = await quality_svc.get_quality_trends(days=days)
        
        return {
            "period_days": days,
            "trends": trends,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get quality trends: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve quality trends"
        )


@router.post("/quality/validate")
async def validate_quality_requirements(
    video_url: str,
    requirements: Dict[str, Any],
    services: Dict[str, Any] = Depends(get_services)
):
    """Validate video against specific quality requirements."""
    
    try:
        quality_svc = services["quality"]
        if not quality_svc:
            raise HTTPException(
                status_code=503,
                detail="Quality assessment service not available"
            )
        
        # First assess the video
        metrics = await quality_svc.assess_video_quality(
            video_url=video_url,
            video_metadata=requirements.get("metadata", {}),
            original_prompt=requirements.get("original_prompt", "")
        )
        
        # Validate against requirements
        passed, violations = await quality_svc.validate_quality_requirements(
            metrics=metrics,
            requirements=requirements
        )
        
        return {
            "video_url": video_url,
            "validation_passed": passed,
            "overall_score": metrics.overall_score,
            "requirements": requirements,
            "violations": violations,
            "validated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Quality validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to validate quality requirements"
        )


# T247: Scheduling Management API Endpoints
class SchedulingRuleRequest(BaseModel):
    """Request model for creating scheduling rules."""
    name: str = Field(..., min_length=1, max_length=100, description="Rule name")
    rule_type: str = Field(..., pattern="^(cron|interval|context)$", description="Rule type")
    prompt_template: str = Field(..., min_length=1, max_length=500, description="Prompt template")
    trigger_config: Dict[str, Any] = Field(..., description="Trigger configuration")
    context_conditions: Optional[Dict[str, Any]] = Field(None, description="Context conditions")
    generation_params: Optional[Dict[str, Any]] = Field(None, description="Generation parameters")
    priority: str = Field("normal", pattern="^(low|normal|high|urgent)$", description="Rule priority")
    enabled: bool = Field(True, description="Whether rule is enabled")


class SchedulingRuleResponse(BaseModel):
    """Response model for scheduling rules."""
    rule_id: str
    name: str
    rule_type: str
    prompt_template: str
    trigger_config: Dict[str, Any]
    context_conditions: Optional[Dict[str, Any]]
    generation_params: Optional[Dict[str, Any]]
    priority: str
    enabled: bool
    created_at: str


@router.post("/scheduling/rules", response_model=SchedulingRuleResponse)
async def create_scheduling_rule(
    request: SchedulingRuleRequest,
    services: Dict[str, Any] = Depends(get_services)
):
    """Create a new scheduling rule."""
    
    try:
        logger.info(f"Creating scheduling rule: {request.name}")
        
        scheduling_svc = services["scheduling"]
        if not scheduling_svc:
            raise HTTPException(
                status_code=503,
                detail="Scheduling service not available"
            )
        
        # Map priority
        priority_map = {
            "low": scheduling_svc.Priority.LOW,
            "normal": scheduling_svc.Priority.NORMAL,
            "high": scheduling_svc.Priority.HIGH,
            "urgent": scheduling_svc.Priority.URGENT
        }
        
        # Create rule based on type
        if request.rule_type == "cron":
            cron_expression = request.trigger_config.get("cron")
            if not cron_expression:
                raise HTTPException(
                    status_code=400,
                    detail="Cron expression required for cron rule type"
                )
            
            rule_id = await scheduling_svc.schedule_recurring_task(
                prompt_template=request.prompt_template,
                cron_expression=cron_expression,
                priority=priority_map[request.priority],
                generation_params=request.generation_params,
                rule_name=request.name
            )
            
        elif request.rule_type == "context":
            check_interval = request.trigger_config.get("interval_minutes", 30)
            
            rule_id = await scheduling_svc.schedule_context_based_task(
                prompt_template=request.prompt_template,
                context_conditions=request.context_conditions or {},
                check_interval_minutes=check_interval,
                priority=priority_map[request.priority],
                rule_name=request.name
            )
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported rule type: {request.rule_type}"
            )
        
        # Get the created rule
        rule = scheduling_svc.scheduling_rules.get(rule_id)
        if not rule:
            raise HTTPException(
                status_code=500,
                detail="Failed to create scheduling rule"
            )
        
        response = SchedulingRuleResponse(
            rule_id=rule.rule_id,
            name=rule.name,
            rule_type=rule.trigger_type,
            prompt_template=rule.prompt_template,
            trigger_config=rule.trigger_config,
            context_conditions=rule.context_conditions,
            generation_params=rule.generation_params,
            priority=rule.priority.name.lower(),
            enabled=rule.enabled,
            created_at=datetime.now().isoformat()
        )
        
        logger.info(f"Scheduling rule created: {rule_id}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create scheduling rule: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create scheduling rule"
        )


@router.get("/scheduling/rules")
async def get_scheduling_rules(
    enabled_only: bool = Query(False, description="Return only enabled rules"),
    services: Dict[str, Any] = Depends(get_services)
):
    """Get all scheduling rules."""
    
    try:
        scheduling_svc = services["scheduling"]
        if not scheduling_svc:
            raise HTTPException(
                status_code=503,
                detail="Scheduling service not available"
            )
        
        rules = scheduling_svc.get_scheduling_rules()
        
        if enabled_only:
            rules = [rule for rule in rules if rule.enabled]
        
        rule_responses = []
        for rule in rules:
            rule_responses.append({
                "rule_id": rule.rule_id,
                "name": rule.name,
                "rule_type": rule.trigger_type,
                "prompt_template": rule.prompt_template,
                "trigger_config": rule.trigger_config,
                "context_conditions": rule.context_conditions,
                "generation_params": rule.generation_params,
                "priority": rule.priority.name.lower(),
                "enabled": rule.enabled
            })
        
        return {
            "rules": rule_responses,
            "total_count": len(rule_responses),
            "enabled_count": len([r for r in rules if r.enabled])
        }
        
    except Exception as e:
        logger.error(f"Failed to get scheduling rules: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve scheduling rules"
        )


@router.put("/scheduling/rules/{rule_id}/enable")
async def enable_scheduling_rule(
    rule_id: str,
    services: Dict[str, Any] = Depends(get_services)
):
    """Enable a scheduling rule."""
    
    try:
        scheduling_svc = services["scheduling"]
        if not scheduling_svc:
            raise HTTPException(
                status_code=503,
                detail="Scheduling service not available"
            )
        
        success = await scheduling_svc.enable_rule(rule_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Scheduling rule {rule_id} not found"
            )
        
        return {
            "message": f"Scheduling rule {rule_id} enabled",
            "rule_id": rule_id,
            "enabled_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enable scheduling rule: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to enable scheduling rule"
        )


@router.put("/scheduling/rules/{rule_id}/disable")
async def disable_scheduling_rule(
    rule_id: str,
    services: Dict[str, Any] = Depends(get_services)
):
    """Disable a scheduling rule."""
    
    try:
        scheduling_svc = services["scheduling"]
        if not scheduling_svc:
            raise HTTPException(
                status_code=503,
                detail="Scheduling service not available"
            )
        
        success = await scheduling_svc.disable_rule(rule_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Scheduling rule {rule_id} not found"
            )
        
        return {
            "message": f"Scheduling rule {rule_id} disabled",
            "rule_id": rule_id,
            "disabled_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disable scheduling rule: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to disable scheduling rule"
        )


@router.get("/scheduling/queue")
async def get_generation_queue(
    status_filter: Optional[str] = Query(None, pattern="^(pending|running|completed|failed|cancelled)$"),
    limit: int = Query(50, ge=1, le=100),
    services: Dict[str, Any] = Depends(get_services)
):
    """Get current generation queue status."""
    
    try:
        scheduling_svc = services["scheduling"]
        if not scheduling_svc:
            raise HTTPException(
                status_code=503,
                detail="Scheduling service not available"
            )
        
        active_tasks = scheduling_svc.get_active_tasks()
        
        # Filter by status if specified
        if status_filter:
            active_tasks = [task for task in active_tasks if task.status.value == status_filter]
        
        # Limit results
        active_tasks = active_tasks[:limit]
        
        queue_info = []
        for task in active_tasks:
            task_info = {
                "task_id": task.task_id,
                "prompt": task.prompt[:100] + "..." if len(task.prompt) > 100 else task.prompt,
                "status": task.status.value,
                "priority": task.priority.name.lower(),
                "scheduled_time": task.scheduled_time.isoformat(),
                "created_at": task.created_at.isoformat(),
                "retry_count": task.retry_count
            }
            
            if task.started_at:
                task_info["started_at"] = task.started_at.isoformat()
                if task.status.value == "running":
                    elapsed_seconds = (datetime.now() - task.started_at).total_seconds()
                    task_info["elapsed_seconds"] = elapsed_seconds
                    
            if task.completed_at:
                task_info["completed_at"] = task.completed_at.isoformat()
                duration_seconds = (task.completed_at - task.started_at).total_seconds()
                task_info["duration_seconds"] = duration_seconds
                
            if task.error_message:
                task_info["error_message"] = task.error_message
            
            queue_info.append(task_info)
        
        # Get queue statistics
        all_tasks = scheduling_svc.get_active_tasks()
        stats = {
            "total_tasks": len(all_tasks),
            "pending_tasks": len([t for t in all_tasks if t.status.value == "pending"]),
            "running_tasks": len([t for t in all_tasks if t.status.value == "running"]),
            "failed_tasks": len([t for t in all_tasks if t.status.value == "failed"]),
            "retry_tasks": len([t for t in all_tasks if t.retry_count > 0])
        }
        
        return {
            "queue": queue_info,
            "statistics": stats,
            "filter_applied": status_filter,
            "total_returned": len(queue_info),
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get generation queue: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve generation queue"
        )


# T248: Monitoring & Alert Endpoints
class AlertRequest(BaseModel):
    """Request model for alert operations."""
    alert_id: str = Field(..., description="Alert identifier")
    action: str = Field(..., pattern="^(acknowledge|resolve|dismiss)$", description="Action to perform")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes for the action")


class MonitoringConfigRequest(BaseModel):
    """Request model for monitoring configuration."""
    component: str = Field(..., description="Component to monitor")
    enabled: bool = Field(..., description="Enable/disable monitoring")
    thresholds: Dict[str, float] = Field(..., description="Monitoring thresholds")
    check_interval_seconds: int = Field(60, ge=10, le=3600, description="Check interval in seconds")


@router.post("/monitoring/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    request: AlertRequest,
    services: Dict[str, Any] = Depends(get_services)
):
    """Acknowledge an active alert."""
    
    try:
        monitoring_svc = services.get("monitoring")
        if not monitoring_svc:
            raise HTTPException(status_code=503, detail="Monitoring service not available")
        
        success = await monitoring_svc.acknowledge_alert(alert_id, request.notes or "")
        
        if not success:
            raise HTTPException(
                status_code=404, 
                detail=f"Alert {alert_id} not found or already acknowledged"
            )
        
        return {
            "message": f"Alert {alert_id} acknowledged successfully",
            "alert_id": alert_id,
            "acknowledged_at": datetime.now().isoformat(),
            "notes": request.notes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to acknowledge alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to acknowledge alert")


@router.post("/monitoring/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    request: AlertRequest,
    services: Dict[str, Any] = Depends(get_services)
):
    """Resolve an active alert."""
    
    try:
        monitoring_svc = services.get("monitoring")
        if not monitoring_svc:
            raise HTTPException(status_code=503, detail="Monitoring service not available")
        
        success = await monitoring_svc.resolve_alert(alert_id, request.notes or "")
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Alert {alert_id} not found or already resolved"
            )
        
        return {
            "message": f"Alert {alert_id} resolved successfully",
            "alert_id": alert_id,
            "resolved_at": datetime.now().isoformat(),
            "notes": request.notes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to resolve alert")


@router.get("/monitoring/alerts")
async def get_active_alerts(
    level: Optional[str] = Query(None, description="Filter by alert level"),
    limit: int = Query(50, ge=1, le=200),
    services: Dict[str, Any] = Depends(get_services)
):
    """Get list of active alerts with optional filtering."""
    
    try:
        monitoring_svc = services.get("monitoring")
        if not monitoring_svc:
            return {"alerts": [], "total_count": 0}
        
        alerts = await monitoring_svc.get_active_alerts(level_filter=level, limit=limit)
        
        alert_list = []
        for alert in alerts:
            alert_info = {
                "alert_id": alert.alert_id,
                "level": alert.level.value,
                "title": alert.title,
                "message": alert.message,
                "component": alert.component,
                "triggered_at": alert.triggered_at.isoformat(),
                "is_acknowledged": alert.is_acknowledged,
                "retry_count": getattr(alert, 'retry_count', 0)
            }
            
            if alert.acknowledged_at:
                alert_info["acknowledged_at"] = alert.acknowledged_at.isoformat()
            if hasattr(alert, 'tags') and alert.tags:
                alert_info["tags"] = alert.tags
            
            alert_list.append(alert_info)
        
        return {
            "alerts": alert_list,
            "total_count": len(alert_list),
            "filtered_by": {"level": level} if level else None
        }
        
    except Exception as e:
        logger.error(f"Failed to get active alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve active alerts")


@router.get("/monitoring/metrics")
async def get_monitoring_metrics(
    component: Optional[str] = Query(None, description="Filter by component"),
    timeframe: str = Query("1h", description="Time frame: 1h, 6h, 24h, 7d"),
    services: Dict[str, Any] = Depends(get_services)
):
    """Get system monitoring metrics."""
    
    try:
        monitoring_svc = services.get("monitoring")
        if not monitoring_svc:
            return {"metrics": {}, "message": "Monitoring service not available"}
        
        # Parse timeframe
        timeframe_mapping = {
            "1h": 3600,
            "6h": 21600, 
            "24h": 86400,
            "7d": 604800
        }
        
        seconds = timeframe_mapping.get(timeframe, 3600)
        start_time = datetime.now() - timedelta(seconds=seconds)
        
        metrics = await monitoring_svc.get_metrics(
            component_filter=component,
            start_time=start_time
        )
        
        return {
            "metrics": metrics,
            "timeframe": timeframe,
            "component_filter": component,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get monitoring metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve monitoring metrics")


@router.put("/monitoring/config/{component}")
async def update_monitoring_config(
    component: str,
    config: MonitoringConfigRequest,
    services: Dict[str, Any] = Depends(get_services)
):
    """Update monitoring configuration for a specific component."""
    
    try:
        monitoring_svc = services.get("monitoring")
        if not monitoring_svc:
            raise HTTPException(status_code=503, detail="Monitoring service not available")
        
        success = await monitoring_svc.update_component_config(
            component=component,
            enabled=config.enabled,
            thresholds=config.thresholds,
            check_interval=config.check_interval_seconds
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to update monitoring config for component: {component}"
            )
        
        return {
            "message": f"Monitoring configuration updated for {component}",
            "component": component,
            "config": {
                "enabled": config.enabled,
                "thresholds": config.thresholds,
                "check_interval_seconds": config.check_interval_seconds
            },
            "updated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update monitoring config: {e}")
        raise HTTPException(status_code=500, detail="Failed to update monitoring configuration")


@router.get("/monitoring/status")
async def get_monitoring_status(
    services: Dict[str, Any] = Depends(get_services)
):
    """Get real-time monitoring system status."""
    
    try:
        monitoring_svc = services.get("monitoring")
        if not monitoring_svc:
            return {
                "status": "unavailable",
                "message": "Monitoring service not available",
                "components": {}
            }
        
        status = await monitoring_svc.get_system_status()
        
        return {
            "status": status.get("overall_status", "unknown"),
            "components": status.get("components", {}),
            "active_monitors": status.get("active_monitors", 0),
            "alert_count": status.get("alert_count", 0),
            "last_check": status.get("last_check", datetime.now().isoformat()),
            "uptime_seconds": status.get("uptime_seconds", 0)
        }
        
    except Exception as e:
        logger.error(f"Failed to get monitoring status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve monitoring status")


# T249: Task Management Endpoints
class BulkTaskRequest(BaseModel):
    """Request model for bulk task operations."""
    task_ids: List[str] = Field(..., min_items=1, max_items=50, description="List of task IDs")
    action: str = Field(..., pattern="^(cancel|retry|delete|priority_update)$", description="Bulk action to perform")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional parameters for the action")


@router.get("/tasks/{task_id}")
async def get_task_details(
    task_id: str,
    include_logs: bool = Query(False, description="Include execution logs"),
    services: Dict[str, Any] = Depends(get_services)
):
    """Get detailed information about a specific task."""
    
    try:
        scheduling_svc = services.get("scheduling")
        if not scheduling_svc:
            raise HTTPException(status_code=503, detail="Scheduling service not available")
        
        # Get task details
        task = scheduling_svc.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        task_details = {
            "task_id": task.task_id,
            "prompt": task.prompt,
            "status": task.status.value,
            "priority": task.priority.name.lower(),
            "scheduled_time": task.scheduled_time.isoformat(),
            "created_at": task.created_at.isoformat(),
            "retry_count": task.retry_count,
            "max_retries": getattr(task, 'max_retries', 3),
            "generation_params": getattr(task, 'generation_params', {})
        }
        
        # Optional timestamps
        if task.started_at:
            task_details["started_at"] = task.started_at.isoformat()
        if task.completed_at:
            task_details["completed_at"] = task.completed_at.isoformat()
            if task.started_at:
                duration = (task.completed_at - task.started_at).total_seconds()
                task_details["duration_seconds"] = duration
        
        # Error information
        if task.error_message:
            task_details["error_message"] = task.error_message
            task_details["last_error_at"] = getattr(task, 'last_error_at', task.created_at).isoformat()
        
        # Video information if completed
        if hasattr(task, 'video_id') and task.video_id:
            task_details["video_id"] = task.video_id
            task_details["video_url"] = getattr(task, 'video_url', None)
        
        # Include logs if requested
        if include_logs:
            logs = scheduling_svc.get_task_logs(task_id)
            task_details["logs"] = [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level,
                    "message": log.message,
                    "component": getattr(log, 'component', 'scheduling')
                }
                for log in logs[-50:]  # Last 50 log entries
            ]
        
        return task_details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task details: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve task details")


@router.get("/tasks/{task_id}/logs")
async def get_task_logs(
    task_id: str,
    limit: int = Query(100, ge=1, le=500),
    level: Optional[str] = Query(None, description="Filter by log level"),
    services: Dict[str, Any] = Depends(get_services)
):
    """Get execution logs for a specific task."""
    
    try:
        scheduling_svc = services.get("scheduling")
        if not scheduling_svc:
            raise HTTPException(status_code=503, detail="Scheduling service not available")
        
        # Verify task exists
        task = scheduling_svc.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        # Get logs
        logs = scheduling_svc.get_task_logs(task_id, limit=limit, level_filter=level)
        
        log_entries = []
        for log in logs:
            log_entry = {
                "id": getattr(log, 'id', f"{log.timestamp.timestamp()}"),
                "timestamp": log.timestamp.isoformat(),
                "level": log.level,
                "message": log.message,
                "component": getattr(log, 'component', 'scheduling')
            }
            
            if hasattr(log, 'metadata') and log.metadata:
                log_entry["metadata"] = log.metadata
            
            log_entries.append(log_entry)
        
        return {
            "task_id": task_id,
            "logs": log_entries,
            "total_count": len(log_entries),
            "filtered_by": {"level": level} if level else None,
            "retrieved_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve task logs")


@router.post("/tasks/bulk")
async def bulk_task_operation(
    request: BulkTaskRequest,
    services: Dict[str, Any] = Depends(get_services)
):
    """Perform bulk operations on multiple tasks."""
    
    try:
        scheduling_svc = services.get("scheduling")
        if not scheduling_svc:
            raise HTTPException(status_code=503, detail="Scheduling service not available")
        
        results = []
        successful_ops = 0
        failed_ops = 0
        
        for task_id in request.task_ids:
            try:
                # Verify task exists
                task = scheduling_svc.get_task_by_id(task_id)
                if not task:
                    results.append({
                        "task_id": task_id,
                        "success": False,
                        "error": "Task not found"
                    })
                    failed_ops += 1
                    continue
                
                # Perform requested action
                success = False
                error_msg = None
                
                if request.action == "cancel":
                    success = await scheduling_svc.cancel_task(task_id)
                    error_msg = "Could not cancel task" if not success else None
                
                elif request.action == "retry":
                    success = await scheduling_svc.retry_task(task_id)
                    error_msg = "Could not retry task" if not success else None
                
                elif request.action == "delete":
                    success = await scheduling_svc.delete_task(task_id)
                    error_msg = "Could not delete task" if not success else None
                
                elif request.action == "priority_update":
                    new_priority = request.parameters.get("priority", "normal")
                    success = await scheduling_svc.update_task_priority(task_id, new_priority)
                    error_msg = "Could not update priority" if not success else None
                
                results.append({
                    "task_id": task_id,
                    "success": success,
                    "error": error_msg,
                    "action": request.action
                })
                
                if success:
                    successful_ops += 1
                else:
                    failed_ops += 1
                    
            except Exception as e:
                results.append({
                    "task_id": task_id,
                    "success": False,
                    "error": str(e),
                    "action": request.action
                })
                failed_ops += 1
        
        return {
            "action": request.action,
            "results": results,
            "summary": {
                "total_tasks": len(request.task_ids),
                "successful_operations": successful_ops,
                "failed_operations": failed_ops,
                "success_rate": successful_ops / len(request.task_ids) if request.task_ids else 0
            },
            "processed_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to perform bulk operation: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform bulk task operation")


# T250: System Administration Endpoints
class SystemConfigRequest(BaseModel):
    """Request model for system configuration updates."""
    component: str = Field(..., description="Component to configure")
    settings: Dict[str, Any] = Field(..., description="Configuration settings")
    restart_required: bool = Field(False, description="Whether restart is required after change")


class ServiceRestartRequest(BaseModel):
    """Request model for service restart operations."""
    services: List[str] = Field(..., description="List of services to restart")
    force: bool = Field(False, description="Force restart even if busy")
    delay_seconds: int = Field(0, ge=0, le=300, description="Delay before restart")


@router.get("/admin/info")
async def get_system_info(
    services: Dict[str, Any] = Depends(get_services)
):
    """Get comprehensive system information."""
    
    try:
        import psutil
        import platform
        import sys
        from datetime import datetime
        
        # System information
        system_info = {
            "platform": {
                "system": platform.system(),
                "platform": platform.platform(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": sys.version
            },
            "resources": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": {
                    "total": psutil.disk_usage('/').total,
                    "used": psutil.disk_usage('/').used,
                    "free": psutil.disk_usage('/').free
                }
            },
            "process": {
                "pid": psutil.Process().pid,
                "cpu_percent": psutil.Process().cpu_percent(),
                "memory_info": psutil.Process().memory_info()._asdict(),
                "create_time": datetime.fromtimestamp(psutil.Process().create_time()).isoformat(),
                "status": psutil.Process().status()
            }
        }
        
        # AI Services status
        services_status = {}
        for service_name, service in services.items():
            if service:
                services_status[service_name] = {
                    "status": "running",
                    "type": str(type(service).__name__),
                    "initialized": True
                }
            else:
                services_status[service_name] = {
                    "status": "not_available",
                    "initialized": False
                }
        
        return {
            "system": system_info,
            "services": services_status,
            "api_version": "2.0.0",
            "startup_time": getattr(get_system_info, '_startup_time', datetime.now().isoformat()),
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system information")


@router.get("/admin/config")
async def get_system_config(
    component: Optional[str] = Query(None, description="Filter by component"),
    services: Dict[str, Any] = Depends(get_services)
):
    """Get current system configuration."""
    
    try:
        import os
        
        config = {
            "environment_variables": {
                "VEO_PROJECT_ID": "***REDACTED***" if os.getenv('VEO_PROJECT_ID') else None,
                "VEO_LOCATION": os.getenv('VEO_LOCATION', 'us-central1'),
                "VEO_MODEL": os.getenv('VEO_MODEL', 'veo-2'),
                "DATABASE_URL": "***REDACTED***" if os.getenv('DATABASE_URL') else None,
                "LOG_LEVEL": os.getenv('LOG_LEVEL', 'INFO')
            },
            "service_configs": {}
        }
        
        # Get service-specific configurations
        for service_name, service in services.items():
            if service and hasattr(service, 'get_config'):
                try:
                    service_config = service.get_config()
                    config["service_configs"][service_name] = service_config
                except Exception as e:
                    config["service_configs"][service_name] = {"error": f"Failed to get config: {e}"}
        
        # Filter by component if requested
        if component:
            if component in config["service_configs"]:
                return {
                    "component": component,
                    "config": config["service_configs"][component],
                    "retrieved_at": datetime.now().isoformat()
                }
            else:
                raise HTTPException(status_code=404, detail=f"Component {component} not found")
        
        return {
            "config": config,
            "retrieved_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get system config: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system configuration")


@router.put("/admin/config")
async def update_system_config(
    request: SystemConfigRequest,
    services: Dict[str, Any] = Depends(get_services)
):
    """Update system configuration."""
    
    try:
        service = services.get(request.component)
        if not service:
            raise HTTPException(
                status_code=404,
                detail=f"Service {request.component} not found"
            )
        
        # Update configuration if service supports it
        if hasattr(service, 'update_config'):
            success = await service.update_config(request.settings)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Service {request.component} does not support configuration updates"
            )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to update configuration for {request.component}"
            )
        
        result = {
            "message": f"Configuration updated for {request.component}",
            "component": request.component,
            "settings_updated": request.settings,
            "restart_required": request.restart_required,
            "updated_at": datetime.now().isoformat()
        }
        
        if request.restart_required:
            result["restart_recommendation"] = f"Service {request.component} should be restarted for changes to take effect"
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update system config: {e}")
        raise HTTPException(status_code=500, detail="Failed to update system configuration")


@router.post("/admin/restart")
async def restart_services(
    request: ServiceRestartRequest,
    services: Dict[str, Any] = Depends(get_services)
):
    """Restart specified services."""
    
    try:
        results = []
        
        for service_name in request.services:
            service = services.get(service_name)
            if not service:
                results.append({
                    "service": service_name,
                    "success": False,
                    "error": "Service not found"
                })
                continue
            
            try:
                # Check if service is busy (if applicable)
                if not request.force and hasattr(service, 'is_busy'):
                    if service.is_busy():
                        results.append({
                            "service": service_name,
                            "success": False,
                            "error": "Service is busy, use force=true to restart anyway"
                        })
                        continue
                
                # Apply delay if specified
                if request.delay_seconds > 0:
                    import asyncio
                    await asyncio.sleep(request.delay_seconds)
                
                # Restart service
                if hasattr(service, 'restart'):
                    await service.restart()
                elif hasattr(service, 'stop') and hasattr(service, 'start'):
                    await service.stop()
                    await service.start()
                else:
                    results.append({
                        "service": service_name,
                        "success": False,
                        "error": "Service does not support restart"
                    })
                    continue
                
                results.append({
                    "service": service_name,
                    "success": True,
                    "restarted_at": datetime.now().isoformat()
                })
                
            except Exception as e:
                results.append({
                    "service": service_name,
                    "success": False,
                    "error": str(e)
                })
        
        successful_restarts = len([r for r in results if r["success"]])
        
        return {
            "results": results,
            "summary": {
                "total_services": len(request.services),
                "successful_restarts": successful_restarts,
                "failed_restarts": len(request.services) - successful_restarts
            },
            "processed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to restart services: {e}")
        raise HTTPException(status_code=500, detail="Failed to restart services")


@router.get("/admin/logs")
async def get_system_logs(
    component: Optional[str] = Query(None, description="Filter by component"),
    level: Optional[str] = Query(None, description="Filter by log level"),
    limit: int = Query(100, ge=1, le=1000),
    since: Optional[str] = Query(None, description="Get logs since this timestamp (ISO format)"),
    services: Dict[str, Any] = Depends(get_services)
):
    """Get system logs with filtering options."""
    
    try:
        import logging
        from datetime import datetime, timezone
        
        # Parse since parameter if provided
        since_datetime = None
        if since:
            try:
                since_datetime = datetime.fromisoformat(since.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid since timestamp format")
        
        logs = []
        
        # Get logs from services that support it
        for service_name, service in services.items():
            if component and service_name != component:
                continue
            
            if service and hasattr(service, 'get_logs'):
                try:
                    service_logs = service.get_logs(
                        level=level,
                        limit=limit,
                        since=since_datetime
                    )
                    
                    for log in service_logs:
                        log_entry = {
                            "timestamp": log.timestamp.isoformat(),
                            "level": log.level,
                            "component": service_name,
                            "message": log.message,
                            "source": "service"
                        }
                        
                        if hasattr(log, 'metadata') and log.metadata:
                            log_entry["metadata"] = log.metadata
                        
                        logs.append(log_entry)
                        
                except Exception as e:
                    logger.error(f"Failed to get logs from {service_name}: {e}")
        
        # Sort by timestamp (most recent first)
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply limit
        logs = logs[:limit]
        
        return {
            "logs": logs,
            "total_count": len(logs),
            "filters": {
                "component": component,
                "level": level,
                "since": since
            },
            "retrieved_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get system logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system logs")


# Service initialization function (called during app startup)
async def initialize_ai_services():
    """Initialize all AI services."""
    global veo_service, prompt_service, context_service, scheduling_service, quality_service, monitoring_service
    
    try:
        logger.info("Initializing AI services...")
        
        # Initialize services
        veo_service = VEOGenerationService()
        prompt_service = PromptGenerationService()
        context_service = ContextAwareService()
        scheduling_service = SchedulingService()
        quality_service = QualityAssuranceService()
        monitoring_service = MonitoringService()
        
        # Set service dependencies
        # Note: These services don't have set_services methods yet
        # This will need to be implemented when services require cross-dependencies
        # scheduling_service.set_services(
        #     veo_service=veo_service,
        #     prompt_service=prompt_service,
        #     context_service=context_service
        # )
        
        # monitoring_service.set_services(
        #     veo_service=veo_service,
        #     scheduling_service=scheduling_service,
        #     quality_service=quality_service
        # )
        
        # Start services
        # Note: Services don't have start methods yet, will be implemented later
        # scheduling_service.start()
        # await monitoring_service.start_monitoring()
        
        logger.info("AI services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize AI services: {e}")
        raise


# Service cleanup function (called during app shutdown)
async def cleanup_ai_services():
    """Cleanup AI services."""
    global scheduling_service, monitoring_service
    
    try:
        logger.info("Cleaning up AI services...")
        
        if scheduling_service:
            scheduling_service.stop()
        
        if monitoring_service:
            await monitoring_service.stop_monitoring()
        
        logger.info("AI services cleaned up successfully")
        
    except Exception as e:
        logger.error(f"Failed to cleanup AI services: {e}")