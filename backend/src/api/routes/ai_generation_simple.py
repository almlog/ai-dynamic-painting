"""
Simple AI Generation API - Direct VEO video generation
最小限の実装で確実に動作する動画生成API
"""

import logging
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import os

# Import direct services
from src.services.gemini_service import GeminiService

logger = logging.getLogger("ai_generation_simple")

router = APIRouter(prefix="/ai", tags=["AI Generation Simple"])

# Simple request/response models
class SimpleVideoRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000, description="動画生成プロンプト")
    duration_seconds: int = Field(5, ge=5, le=30, description="動画の長さ（秒）")
    resolution: str = Field("720p", description="解像度")
    fps: int = Field(24, ge=24, le=60, description="フレームレート")
    loop_mode: bool = Field(True, description="ループ動画生成")

class SimpleVideoResponse(BaseModel):
    success: bool
    task_id: str
    message: str
    estimated_cost: Optional[float] = None
    video_url: Optional[str] = None

# Global service instance
gemini_service: Optional[GeminiService] = None

@router.post("/generate", response_model=SimpleVideoResponse)
async def generate_video_simple(request: SimpleVideoRequest):
    """
    最小限のVEO動画生成エンドポイント
    直接GeminiServiceのgenerate_videoメソッドを呼び出します
    """
    
    try:
        logger.info(f"Simple video generation request: {request.prompt[:100]}...")
        
        # Initialize service if needed
        global gemini_service
        if gemini_service is None:
            gemini_service = GeminiService()
            logger.info("GeminiService initialized")
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Call generate_video directly
        video_bytes = gemini_service.generate_video(
            prompt=request.prompt,
            duration_seconds=request.duration_seconds,
            resolution=request.resolution,
            fps=request.fps,
            loop_mode=request.loop_mode
        )
        
        if video_bytes:
            # Save video file
            output_dir = "/home/aipainting/ai-dynamic-painting/backend/generated_videos"
            os.makedirs(output_dir, exist_ok=True)
            
            filename = f"video_{task_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(video_bytes)
            
            logger.info(f"Video saved: {filepath} ({len(video_bytes)} bytes)")
            
            return SimpleVideoResponse(
                success=True,
                task_id=task_id,
                message=f"動画生成成功: {filename}",
                estimated_cost=0.50,  # Rough estimate
                video_url=f"/videos/{filename}"
            )
        else:
            logger.error("Video generation returned None")
            return SimpleVideoResponse(
                success=False,
                task_id=task_id,
                message="動画生成に失敗しました"
            )
            
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        return SimpleVideoResponse(
            success=False,
            task_id=str(uuid.uuid4()),
            message=f"動画生成エラー: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """シンプルなヘルスチェック"""
    return {
        "status": "healthy",
        "service": "ai_generation_simple",
        "timestamp": datetime.now().isoformat()
    }