"""
Videos API routes - Phase 1 手動動画管理システム
T034: Minimal GET /api/videos endpoint implementation to pass contract tests
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from src.models.video import VideoResponse
from src.services.video_service import VideoService

router = APIRouter()
video_service = VideoService()


@router.get("/videos", response_model=dict)
async def get_videos(
    status: Optional[str] = Query(None, description="Filter by video status"),
    limit: int = Query(20, ge=1, le=100, description="Limit number of results")
):
    """
    Get list of videos with optional filtering
    Minimal implementation to pass T009 contract test
    """
    # Validate status parameter
    valid_statuses = ["active", "archived", "processing", "error"]
    if status and status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid status", "message": f"Status must be one of: {valid_statuses}"}
        )
    
    try:
        # Get videos from service
        videos = video_service.get_all_videos(status=status, limit=limit)
        total_count = video_service.get_video_count()
        
        # Convert to response format
        video_responses = []
        for video in videos:
            video_responses.append({
                "id": video.id,
                "title": video.title,
                "file_path": video.file_path,
                "file_size": video.file_size,
                "duration": video.duration,
                "format": video.format,
                "resolution": video.resolution,
                "upload_timestamp": video.upload_timestamp.isoformat(),
                "status": video.status,
                "play_count": video.play_count
            })
        
        # Return format expected by contract test
        return {
            "videos": video_responses,
            "total": total_count,
            "page": 1  # Simplified pagination for minimal implementation
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "message": str(e)}
        )


@router.get("/videos/{video_id}", response_model=dict)
async def get_video(video_id: str):
    """
    Get single video by ID
    Minimal implementation for video retrieval
    """
    video = video_service.get_video_by_id(video_id)
    
    if not video:
        raise HTTPException(
            status_code=404,
            detail={"error": "Video not found", "message": f"Video with ID {video_id} not found"}
        )
    
    return {
        "id": video.id,
        "title": video.title,
        "file_path": video.file_path,
        "file_size": video.file_size,
        "duration": video.duration,
        "format": video.format,
        "resolution": video.resolution,
        "upload_timestamp": video.upload_timestamp.isoformat(),
        "status": video.status,
        "play_count": video.play_count
    }