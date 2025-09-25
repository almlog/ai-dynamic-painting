"""
Admin Dashboard用データモデル
画像生成品質管理のためのモデル定義
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class GenerationStatus(str, Enum):
    """生成ステータス"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PromptTemplate(BaseModel):
    """プロンプトテンプレート"""
    id: Optional[str] = None
    name: str = Field(..., description="テンプレート名")
    template: str = Field(..., description="プロンプトテンプレート本文")
    variables: List[str] = Field(default_factory=list, description="変数名リスト")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="生成パラメータ")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GenerationRequest(BaseModel):
    """画像生成リクエスト"""
    prompt_template_id: str = Field(..., description="使用するプロンプトテンプレートID")
    model: str = Field(default="gemini-1.5-flash", description="使用モデル")
    quality: str = Field(default="standard", description="生成品質 (standard, hd)")
    aspect_ratio: str = Field(default="1:1", description="アスペクト比 (1:1, 16:9, 9:16)")
    negative_prompt: Optional[str] = Field(default=None, description="ネガティブプロンプト")
    style_preset: Optional[str] = Field(default=None, description="スタイルプリセット (anime, photographic, digital-art)")
    seed: Optional[int] = Field(default=None, ge=0, le=2147483647, description="シード値 (reproducibility)")
    temperature: float = Field(default=0.7, ge=0.1, le=2.0, description="Temperature")
    top_k: int = Field(default=40, ge=1, le=100, description="Top-K")
    top_p: float = Field(default=0.95, ge=0.1, le=1.0, description="Top-P")
    max_tokens: int = Field(default=2048, ge=100, le=8192, description="最大トークン数")
    variables: Optional[Dict[str, str]] = Field(default_factory=dict, description="変数値")


class GenerationResult(BaseModel):
    """生成結果"""
    id: str = Field(..., description="生成ID")
    generation_id: Optional[str] = Field(None, description="生成ID（互換性）")
    request: GenerationRequest = Field(..., description="リクエスト内容")
    status: GenerationStatus = Field(..., description="生成ステータス")
    ai_instructions: Optional[str] = Field(None, description="AI生成指示")
    image_path: Optional[str] = Field(None, description="生成画像パス")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="メタデータ")
    quality_score: Optional[float] = Field(None, ge=0, le=1, description="品質スコア")
    error_message: Optional[str] = Field(None, description="エラーメッセージ")
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
    completed_at: Optional[datetime] = Field(None, description="完了日時")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Evaluation(BaseModel):
    """生成結果の評価"""
    id: Optional[str] = None
    generation_id: str = Field(..., description="評価対象の生成ID")
    rating: int = Field(..., ge=1, le=5, description="5段階評価")
    tags: List[str] = Field(default_factory=list, description="タグ")
    comment: Optional[str] = Field(None, description="コメント")
    created_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnalyticsData(BaseModel):
    """分析データ"""
    total_generations: int = Field(0, description="総生成数")
    success_rate: float = Field(0.0, ge=0, le=1, description="成功率")
    average_rating: float = Field(0.0, ge=0, le=5, description="平均評価")
    api_usage: Dict[str, int] = Field(default_factory=dict, description="API使用量")
    generation_trend: List[Dict[str, Any]] = Field(default_factory=list, description="生成トレンド")
    quality_trend: List[Dict[str, Any]] = Field(default_factory=list, description="品質トレンド")


class AdminSettings(BaseModel):
    """管理設定"""
    default_model: str = Field(default="gemini-1.5-flash", description="デフォルトモデル")
    rate_limit: int = Field(default=10, ge=1, le=100, description="レート制限（リクエスト/分）")
    retention_days: int = Field(default=30, ge=1, le=365, description="データ保持期間（日）")
    auto_evaluate: bool = Field(default=False, description="自動評価有効化")
    quality_threshold: float = Field(default=0.7, ge=0, le=1, description="品質閾値")


class GenerationResponse(BaseModel):
    """生成レスポンス"""
    generation_id: str = Field(..., description="生成ID")
    status: GenerationStatus = Field(..., description="ステータス")
    message: str = Field(..., description="メッセージ")