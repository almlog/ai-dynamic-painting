"""
M5STACK API routes - Phase 1 + Phase 2 AI統合システム
T042-T043: Minimal M5STACK control endpoints to pass contract tests
T267: M5STACK AI preference buttons implementation
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

router = APIRouter()


class DeviceInfo(BaseModel):
    """Device information model"""
    device_id: str
    ip_address: Optional[str] = None


class ControlRequest(BaseModel):
    """M5STACK control request model"""
    action: str
    device_info: DeviceInfo


class AIPreferenceRequest(BaseModel):
    """M5STACK AI preference button data model"""
    user_id: str
    action: str
    preference_type: str  # "good", "bad", "skip"
    content_id: str
    device_info: Dict[str, Any]


@router.get("/m5stack/status", response_model=dict)
async def get_m5stack_status():
    """
    Get M5STACK system status
    Minimal implementation to pass contract tests
    """
    # Mock system status for minimal implementation
    return {
        "system_status": {
            "id": "system-status-1",
            "timestamp": "2025-09-11T22:00:00Z",
            "cpu_usage": 25.5,
            "memory_usage": 45.2,
            "disk_usage": 30.1,
            "uptime": 86400,
            "active_sessions": 1 if hasattr(get_m5stack_status, '_active_session') else 0,
            "total_videos": 1,
            "m5stack_status": "online",
            "display_status": "active",
            "api_status": "healthy"
        },
        "current_session": getattr(get_m5stack_status, '_active_session', None)
    }


@router.post("/m5stack/control", response_model=dict)
async def handle_m5stack_control(request: ControlRequest):
    """
    Handle M5STACK button control actions
    Minimal implementation to pass T016 contract test
    """
    # Validate action
    valid_actions = ["next", "previous", "play_pause", "stop", "volume_up", "volume_down"]
    if request.action not in valid_actions:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid action",
                "message": f"Action must be one of: {valid_actions}"
            }
        )
    
    # Mock control logic for minimal implementation
    result_messages = {
        "play_pause": "Toggle playback state",
        "stop": "Stopped playback",
        "next": "Skip to next video",
        "previous": "Skip to previous video", 
        "volume_up": "Increased volume",
        "volume_down": "Decreased volume"
    }
    
    result = result_messages.get(request.action, f"Executed {request.action}")
    
    # Mock current session for response
    current_session = {
        "id": "mock-session-123",
        "video_id": "sample-video-123",
        "playback_status": "playing" if request.action == "play_pause" else "stopped",
        "current_position": 45.2
    } if request.action != "stop" else None
    
    # Store session for status endpoint
    get_m5stack_status._active_session = current_session
    
    return {
        "result": result,
        "current_session": current_session
    }


@router.post("/m5stack/ai-preference", response_model=dict)
async def handle_ai_preference(request: AIPreferenceRequest):
    """
    Handle M5STACK AI preference button actions (Good/Bad/Skip)
    T267: M5STACK AI preference buttons implementation
    """
    # Validate preference type
    valid_preferences = ["good", "bad", "skip"]
    if request.preference_type not in valid_preferences:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid preference type",
                "message": f"Preference must be one of: {valid_preferences}"
            }
        )
    
    # Record preference (minimal implementation for GREEN phase)
    preference_id = f"pref_{uuid.uuid4().hex[:8]}"
    
    # In real implementation, this would integrate with preference learning service
    # For now, just record the preference structurally
    recorded_preference = {
        "preference_id": preference_id,
        "user_id": request.user_id,
        "content_id": request.content_id,
        "preference_type": request.preference_type,
        "timestamp": datetime.now().isoformat(),
        "device_info": request.device_info,
        "status": "recorded"
    }
    
    return {
        "success": True,
        "message": "AI preference recorded successfully",
        "preference_id": preference_id,
        "data": recorded_preference
    }


@router.get("/m5stack/ai-status", response_model=dict)
async def get_ai_status():
    """
    Get AI generation and learning status for M5STACK display
    T267: M5STACK AI status display support
    """
    # Mock AI status for minimal implementation (GREEN phase)
    ai_status = {
        "ai_generation_status": {
            "status": "idle",  # idle, generating, processing, error
            "current_task": None,
            "progress_percentage": 0,
            "last_generation": "2025-09-18T10:00:00Z",
            "total_generated": 15
        },
        "learning_progress": {
            "total_interactions": 42,
            "preferences_learned": 28,
            "confidence_score": 0.75,
            "learning_active": True
        },
        "current_recommendations": {
            "next_video_suggestion": "nature_sunset_ocean",
            "confidence": 0.82,
            "reason": "User prefers nature content in evening",
            "alternatives": ["mountain_landscape", "forest_rain"]
        },
        "device_status": {
            "ai_features_enabled": True,
            "learning_mode": "active",
            "last_sync": datetime.now().isoformat()
        }
    }
    
    return ai_status