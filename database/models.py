"""
AI動的絵画システム - データベースモデル定義
詳細設計書に基づく SQLAlchemy モデルなのだ〜！
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, 
    CheckConstraint, Index, ForeignKey
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional

Base = declarative_base()


class Video(Base):
    """動画情報テーブル - メインコンテンツなのだ！"""
    __tablename__ = 'videos'
    
    # プライマリキー
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # ファイル情報
    filepath = Column(String(512), unique=True, nullable=False)
    file_size = Column(Integer, default=0)
    duration = Column(Float, default=8.0)
    
    # 生成情報
    prompt = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    is_manual_upload = Column(Boolean, default=False)
    
    # コンテキスト情報（CHECK制約付き）
    time_period = Column(
        String(20), 
        CheckConstraint("time_period IN ('morning', 'daytime', 'evening', 'night')"),
        nullable=True
    )
    weather = Column(
        String(20),
        CheckConstraint("weather IN ('sunny', 'cloudy', 'rainy', 'snowy', 'stormy')"),
        nullable=True
    )
    season = Column(
        String(20),
        CheckConstraint("season IN ('spring', 'summer', 'autumn', 'winter')"),
        nullable=True
    )
    
    # スタイル・品質
    mood = Column(String(50), nullable=True)
    style = Column(String(50), default='realistic')
    
    # 統計情報
    view_count = Column(Integer, default=0)
    user_rating = Column(Float, default=0.0)
    api_cost = Column(Float, default=0.0)
    
    # メタデータ
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # インデックス
    __table_args__ = (
        Index('idx_video_context', 'time_period', 'weather', 'season'),
        Index('idx_video_rating', 'user_rating'),
        Index('idx_video_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Video(id={self.id}, filepath='{self.filepath}', prompt='{self.prompt[:50]}...')>"


class UserPreference(Base):
    """ユーザー設定テーブル - カスタマイズなのだ！"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    category = Column(String(50), default='general')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserPreference(key='{self.key}', value='{self.value}')>"


class SystemStatus(Base):
    """システム状態テーブル - 健康管理なのだ！"""
    __tablename__ = 'system_status'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    component = Column(String(100), nullable=False)
    status = Column(
        String(20), 
        CheckConstraint("status IN ('ok', 'warning', 'error', 'unknown')"),
        nullable=False
    )
    last_check = Column(DateTime, default=datetime.utcnow)
    error_count = Column(Integer, default=0)
    data = Column(Text, nullable=True)  # JSON形式の詳細データ
    
    __table_args__ = (
        Index('idx_system_component', 'component'),
        Index('idx_system_status', 'status'),
    )
    
    def __repr__(self):
        return f"<SystemStatus(component='{self.component}', status='{self.status}')>"


class GenerationLog(Base):
    """生成ログテーブル - 実験記録なのだ！"""
    __tablename__ = 'generation_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD形式
    videos_generated = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    api_calls = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_generation_date', 'date'),
    )
    
    def __repr__(self):
        return f"<GenerationLog(date='{self.date}', videos={self.videos_generated})>"


class VideoTag(Base):
    """動画タグテーブル - 分類なのだ！"""
    __tablename__ = 'video_tags'
    
    video_id = Column(Integer, ForeignKey('videos.id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
    
    # リレーションシップ
    video = relationship("Video", backref="video_tags")
    tag = relationship("Tag", backref="video_tags")


class Tag(Base):
    """タグマスターテーブル"""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Tag(name='{self.name}', category='{self.category}')>"


# データベース初期化用データ
INITIAL_USER_PREFERENCES = [
    {
        'key': 'display_overlay',
        'value': 'true',
        'description': 'オーバーレイ表示設定',
        'category': 'display'
    },
    {
        'key': 'auto_generation',
        'value': 'true',
        'description': '自動生成有効化',
        'category': 'generation'
    },
    {
        'key': 'preferred_time_morning',
        'value': '06:00',
        'description': '朝の開始時刻',
        'category': 'schedule'
    },
    {
        'key': 'preferred_time_evening',
        'value': '18:00',
        'description': '夕方の開始時刻',
        'category': 'schedule'
    },
    {
        'key': 'daily_generation_limit',
        'value': '3',
        'description': '1日の生成上限',
        'category': 'generation'
    },
    {
        'key': 'video_cache_size_gb',
        'value': '10',
        'description': '動画キャッシュサイズ(GB)',
        'category': 'storage'
    }
]

INITIAL_SYSTEM_COMPONENTS = [
    'database',
    'display_controller', 
    'video_manager',
    'veo_api',
    'weather_api',
    'm5stack_connection',
    'disk_space',
    'memory_usage',
    'cpu_temperature'
]