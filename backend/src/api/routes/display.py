"""
Display API routes - Phase 1 手動動画管理システム
T037: Minimal display control endpoints to pass contract tests
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.models.display_session import DisplaySession
from src.services.video_service import VideoService

router = APIRouter()
video_service = VideoService()

# Simple in-memory session storage for minimal implementation
current_session: dict = {}


class PlayRequest(BaseModel):
    """Request model for play endpoint"""
    video_id: str
    loop_enabled: bool = False
    start_position: float = 0


@router.post("/display/play", response_model=dict)
async def play_video(request: PlayRequest):
    """
    Start video playback
    Minimal implementation to pass T012 contract test
    """
    # Verify video exists
    video = video_service.get_video_by_id(request.video_id)
    if not video:
        raise HTTPException(
            status_code=404,
            detail={"error": "Video not found", "message": f"Video {request.video_id} not found"}
        )
    
    # Create display session
    session_id = str(uuid.uuid4())
    session = DisplaySession(
        id=session_id,
        video_id=request.video_id,
        start_time=datetime.now(),
        session_type="manual",
        current_position=request.start_position,
        playback_status="playing",
        display_mode="fullscreen",
        loop_enabled=request.loop_enabled,
        created_by="web"
    )
    
    # Store as current session (simplified for minimal implementation)
    global current_session
    current_session = {
        "id": session.id,
        "video_id": session.video_id,
        "start_time": session.start_time.isoformat(),
        "playback_status": session.playback_status,
        "current_position": session.current_position,
        "loop_enabled": session.loop_enabled
    }
    
    return current_session


@router.post("/display/pause", response_model=dict)
async def pause_video():
    """Pause current video playback"""
    global current_session
    if not current_session:
        raise HTTPException(
            status_code=409,
            detail={"error": "No active playback", "message": "No video currently playing"}
        )
    
    current_session["playback_status"] = "paused"
    return current_session


@router.post("/display/resume", response_model=dict)
async def resume_video():
    """Resume paused video playback"""
    global current_session
    if not current_session:
        raise HTTPException(
            status_code=409,
            detail={"error": "No active session", "message": "No video session to resume"}
        )
    
    current_session["playback_status"] = "playing"
    return current_session


@router.post("/display/stop", response_model=dict)
async def stop_video():
    """Stop current video playback"""
    global current_session
    if not current_session:
        raise HTTPException(
            status_code=409,
            detail={"error": "No active playback", "message": "No video currently playing"}
        )
    
    current_session["playback_status"] = "stopped"
    return current_session


@router.get("/display/status", response_model=dict)
async def get_display_status():
    """Get current display status"""
    global current_session
    if not current_session:
        return {"session": None, "status": "idle"}
    
    return current_session