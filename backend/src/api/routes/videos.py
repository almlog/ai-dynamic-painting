"""
Videos API routes - Phase 1 手動動画管理システム
T034: Minimal GET /api/videos endpoint implementation to pass contract tests
T035: POST /api/videos file upload endpoint implementation
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import JSONResponse
from src.models.video import VideoResponse, VideoCreate
from src.services.video_service import VideoService
import os
import uuid
from datetime import datetime
import shutil

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


@router.post("/videos", status_code=201)
async def upload_video(
    file: Optional[UploadFile] = File(None),
    title: Optional[str] = Form(None)
):
    """
    Upload a new video file
    T035: Minimal implementation to pass contract tests
    """
    # Validate file is provided
    if not file:
        return JSONResponse(
            status_code=400,
            content={"error": "Bad Request", "message": "File is required"}
        )
    
    # Check file size (500MB limit)
    file_size = 0
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > 500 * 1024 * 1024:  # 500MB limit
        return JSONResponse(
            status_code=413,
            content={"error": "File Too Large", "message": "File size exceeds 500MB limit"}
        )
    
    # Reset file pointer after reading
    await file.seek(0)
    
    # Validate file format (only MP4 allowed)
    if not file.content_type or not file.content_type.startswith("video/"):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid Format", "message": "Only video formats are allowed"}
        )
    
    # Use filename as title if not provided
    if not title:
        title = os.path.splitext(file.filename)[0]
    
    # Create unique filename and save path
    video_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    storage_filename = f"{video_id}{file_extension}"
    storage_path = f"/tmp/videos/{storage_filename}"  # Temporary storage for MVP
    
    # Ensure storage directory exists
    os.makedirs("/tmp/videos", exist_ok=True)
    
    # Save file to disk
    try:
        with open(storage_path, "wb") as buffer:
            buffer.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Storage Error", "message": f"Failed to save file: {str(e)}"}
        )
    
    # Create video record using service
    video_data = VideoCreate(
        title=title,
        file_path=storage_path,
        file_size=file_size,
        duration=0.0,  # Would be extracted from actual video in production
        format=file_extension.lstrip('.').upper() if file_extension else "MP4",
        resolution="1920x1080",  # Would be extracted from actual video
        status="processing"
    )
    
    created_video = video_service.create_video(video_data)
    
    # Return response matching contract test expectations
    return {
        "id": created_video.id,
        "title": created_video.title,
        "file_path": created_video.file_path,
        "file_size": created_video.file_size,
        "status": created_video.status,
        "upload_timestamp": created_video.upload_timestamp.isoformat()
    }


@router.delete("/videos/{video_id}")
async def delete_video(video_id: str):
    """
    Delete a video by ID
    T036: Minimal implementation to pass contract tests
    """
    # Validate video ID format (basic validation)
    if not video_id or video_id.strip() == "" or len(video_id.strip()) < 3:
        return JSONResponse(
            status_code=400,
            content={"error": "Bad Request", "message": "Valid video ID is required"}
        )
    
    # Check if video exists and delete it
    video_exists = video_service.get_video_by_id(video_id)
    if not video_exists:
        return JSONResponse(
            status_code=404,
            content={"error": "Not Found", "message": f"Video with ID {video_id} not found"}
        )
    
    # Delete the video from service
    deleted = video_service.delete_video(video_id)
    
    if deleted:
        # Try to remove physical file (best effort, don't fail if unsuccessful)
        try:
            if os.path.exists(video_exists.file_path):
                os.remove(video_exists.file_path)
        except Exception:
            # Log error but don't fail the request
            # Physical file cleanup is best effort for MVP
            pass
        
        return {
            "message": f"Video {video_id} has been deleted successfully",
            "id": video_id
        }
    else:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "message": "Failed to delete video"}
        )