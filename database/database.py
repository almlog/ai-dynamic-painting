"""
AI動的絵画システム - DatabaseManager実装
詳細設計書に基づくデータベース操作クラスなのだ〜！
"""
import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .models import (
    Base, Video, UserPreference, SystemStatus, 
    GenerationLog, Tag, VideoTag,
    INITIAL_USER_PREFERENCES, INITIAL_SYSTEM_COMPONENTS
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """データベース管理クラス - 博士の実験データ管理なのだ！"""
    
    def __init__(self, db_path: str = "painting_system.db"):
        """
        データベースマネージャー初期化
        
        Args:
            db_path: データベースファイルパス
        """
        self.db_path = db_path
        self.db_url = f"sqlite:///{db_path}"
        
        # SQLAlchemyエンジン・セッション設定
        self.engine = create_engine(
            self.db_url,
            echo=False,  # SQL出力制御
            pool_pre_ping=True,  # 接続チェック
            connect_args={"check_same_thread": False}  # SQLite用
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine
        )
        
        # 初期化実行
        self.create_tables()
        self.initialize_data()
        
        logger.info(f"DatabaseManager initialized: {db_path}")
    
    def create_tables(self) -> None:
        """テーブル作成"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def initialize_data(self) -> None:
        """初期データ投入"""
        with self.get_session() as session:
            # ユーザー設定初期化
            for pref_data in INITIAL_USER_PREFERENCES:
                existing = session.query(UserPreference).filter_by(key=pref_data['key']).first()
                if not existing:
                    pref = UserPreference(**pref_data)
                    session.add(pref)
            
            # システムコンポーネント初期化
            for component in INITIAL_SYSTEM_COMPONENTS:
                existing = session.query(SystemStatus).filter_by(component=component).first()
                if not existing:
                    status = SystemStatus(
                        component=component,
                        status='unknown',
                        last_check=datetime.utcnow()
                    )
                    session.add(status)
            
            session.commit()
            logger.info("Initial data inserted successfully")
    
    @contextmanager
    def get_session(self) -> Session:
        """セッションコンテキストマネージャー"""
        session = self.SessionLocal()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def is_connected(self) -> bool:
        """データベース接続確認"""
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    def table_exists(self, table_name: str) -> bool:
        """テーブル存在確認"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table"),
                    {"table": table_name}
                )
                return result.fetchone() is not None
        except Exception as e:
            logger.error(f"Table existence check failed for {table_name}: {e}")
            return False
    
    # ========================
    # 動画管理メソッド
    # ========================
    
    def add_video(self, video_data: Dict[str, Any]) -> int:
        """
        動画追加
        
        Args:
            video_data: 動画データ辞書
            
        Returns:
            追加された動画のID
        """
        with self.get_session() as session:
            video = Video(**video_data)
            session.add(video)
            session.commit()
            session.refresh(video)
            
            logger.info(f"Video added: {video.id} - {video.filepath}")
            return video.id
    
    def get_videos_by_context(self, context: Dict[str, str]) -> List[Dict]:
        """
        コンテキストによる動画検索
        
        Args:
            context: 検索条件 {time_period, weather, season}
            
        Returns:
            マッチした動画リスト
        """
        with self.get_session() as session:
            query = session.query(Video)
            
            # フィルタリング条件追加
            if 'time_period' in context and context['time_period']:
                query = query.filter(Video.time_period == context['time_period'])
            
            if 'weather' in context and context['weather']:
                query = query.filter(Video.weather == context['weather'])
                
            if 'season' in context and context['season']:
                query = query.filter(Video.season == context['season'])
            
            # 評価順でソート
            videos = query.order_by(Video.user_rating.desc(), Video.view_count.desc()).all()
            
            # 辞書形式で返却
            result = []
            for video in videos:
                result.append({
                    'id': video.id,
                    'filepath': video.filepath,
                    'prompt': video.prompt,
                    'time_period': video.time_period,
                    'weather': video.weather,
                    'season': video.season,
                    'view_count': video.view_count,
                    'user_rating': video.user_rating,
                    'duration': video.duration,
                    'generated_at': video.generated_at,
                    'is_manual_upload': video.is_manual_upload
                })
            
            logger.info(f"Found {len(result)} videos for context: {context}")
            return result
    
    def update_video_stats(self, video_id: int, view_count: int = None, rating: float = None) -> bool:
        """
        動画統計更新
        
        Args:
            video_id: 動画ID
            view_count: 視聴回数
            rating: 評価
            
        Returns:
            更新成功フラグ
        """
        with self.get_session() as session:
            video = session.query(Video).filter_by(id=video_id).first()
            if not video:
                logger.warning(f"Video not found for update: {video_id}")
                return False
            
            if view_count is not None:
                video.view_count = view_count
            
            if rating is not None:
                video.user_rating = rating
            
            video.updated_at = datetime.utcnow()
            session.commit()
            
            logger.info(f"Video stats updated: {video_id}")
            return True
    
    def delete_video(self, video_id: int) -> bool:
        """
        動画削除
        
        Args:
            video_id: 動画ID
            
        Returns:
            削除成功フラグ
        """
        with self.get_session() as session:
            video = session.query(Video).filter_by(id=video_id).first()
            if not video:
                logger.warning(f"Video not found for deletion: {video_id}")
                return False
            
            filepath = video.filepath
            session.delete(video)
            session.commit()
            
            logger.info(f"Video deleted: {video_id} - {filepath}")
            return True
    
    def get_all_videos(self) -> List[Dict]:
        """全動画取得"""
        with self.get_session() as session:
            videos = session.query(Video).order_by(Video.created_at.desc()).all()
            
            result = []
            for video in videos:
                result.append({
                    'id': video.id,
                    'filepath': video.filepath,
                    'prompt': video.prompt,
                    'time_period': video.time_period,
                    'weather': video.weather,
                    'season': video.season,
                    'mood': video.mood,
                    'style': video.style,
                    'view_count': video.view_count,
                    'user_rating': video.user_rating,
                    'duration': video.duration,
                    'file_size': video.file_size,
                    'generated_at': video.generated_at,
                    'is_manual_upload': video.is_manual_upload,
                    'created_at': video.created_at
                })
            
            return result
    
    # ========================
    # 設定管理メソッド
    # ========================
    
    def get_preference(self, key: str) -> Optional[str]:
        """設定値取得"""
        with self.get_session() as session:
            pref = session.query(UserPreference).filter_by(key=key).first()
            return pref.value if pref else None
    
    def set_preference(self, key: str, value: str, description: str = None, category: str = 'general') -> bool:
        """設定値保存"""
        with self.get_session() as session:
            pref = session.query(UserPreference).filter_by(key=key).first()
            
            if pref:
                pref.value = value
                if description:
                    pref.description = description
                pref.updated_at = datetime.utcnow()
            else:
                pref = UserPreference(
                    key=key,
                    value=value,
                    description=description,
                    category=category
                )
                session.add(pref)
            
            session.commit()
            logger.info(f"Preference updated: {key} = {value}")
            return True
    
    def get_all_preferences(self) -> Dict[str, str]:
        """全設定取得"""
        with self.get_session() as session:
            prefs = session.query(UserPreference).all()
            return {pref.key: pref.value for pref in prefs}
    
    # ========================
    # システム状態管理メソッド
    # ========================
    
    def update_system_status(self, component: str, status: str, data: Dict = None) -> bool:
        """システム状態更新"""
        with self.get_session() as session:
            sys_status = session.query(SystemStatus).filter_by(component=component).first()
            
            if sys_status:
                sys_status.status = status
                sys_status.last_check = datetime.utcnow()
                if status == 'error':
                    sys_status.error_count += 1
                else:
                    sys_status.error_count = 0
            else:
                sys_status = SystemStatus(
                    component=component,
                    status=status,
                    last_check=datetime.utcnow(),
                    error_count=1 if status == 'error' else 0
                )
                session.add(sys_status)
            
            if data:
                sys_status.data = json.dumps(data)
            
            session.commit()
            logger.info(f"System status updated: {component} = {status}")
            return True
    
    def get_system_health(self) -> Dict[str, Dict]:
        """システムヘルス状態取得"""
        with self.get_session() as session:
            statuses = session.query(SystemStatus).all()
            
            health = {}
            for status in statuses:
                health[status.component] = {
                    'status': status.status,
                    'last_check': status.last_check.isoformat() if status.last_check else None,
                    'error_count': status.error_count,
                    'data': json.loads(status.data) if status.data else None
                }
            
            return health
    
    # ========================
    # ログ・統計メソッド
    # ========================
    
    def log_generation(self, date_str: str, videos_generated: int = 0, cost: float = 0.0, api_calls: int = 0, success_rate: float = 0.0) -> bool:
        """生成ログ記録"""
        with self.get_session() as session:
            log = session.query(GenerationLog).filter_by(date=date_str).first()
            
            if log:
                log.videos_generated += videos_generated
                log.total_cost += cost
                log.api_calls += api_calls
                if api_calls > 0:
                    log.success_rate = (log.success_rate * (log.api_calls - api_calls) + success_rate * api_calls) / log.api_calls
            else:
                log = GenerationLog(
                    date=date_str,
                    videos_generated=videos_generated,
                    total_cost=cost,
                    api_calls=api_calls,
                    success_rate=success_rate
                )
                session.add(log)
            
            session.commit()
            logger.info(f"Generation logged: {date_str} - {videos_generated} videos")
            return True
    
    def get_monthly_stats(self, year_month: str) -> Dict:
        """月次統計取得"""
        with self.get_session() as session:
            logs = session.query(GenerationLog).filter(
                GenerationLog.date.like(f"{year_month}%")
            ).all()
            
            total_videos = sum(log.videos_generated for log in logs)
            total_cost = sum(log.total_cost for log in logs)
            total_api_calls = sum(log.api_calls for log in logs)
            avg_success_rate = sum(log.success_rate for log in logs) / len(logs) if logs else 0
            
            return {
                'year_month': year_month,
                'total_videos': total_videos,
                'total_cost': total_cost,
                'total_api_calls': total_api_calls,
                'average_success_rate': avg_success_rate,
                'days_with_generation': len(logs)
            }
    
    def get_database_stats(self) -> Dict:
        """データベース統計情報"""
        with self.get_session() as session:
            video_count = session.query(Video).count()
            manual_count = session.query(Video).filter_by(is_manual_upload=True).count()
            generated_count = video_count - manual_count
            
            # ファイルサイズ合計
            total_size_result = session.query(
                session.query(Video.file_size).filter(Video.file_size.isnot(None)).subquery()
            ).scalar() or 0
            
            return {
                'total_videos': video_count,
                'manual_uploads': manual_count,
                'ai_generated': generated_count,
                'total_file_size_mb': total_size_result / (1024 * 1024) if total_size_result else 0,
                'database_size_kb': Path(self.db_path).stat().st_size / 1024 if Path(self.db_path).exists() else 0
            }
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> Dict:
        """古いデータクリーンアップ"""
        cutoff_date = datetime.utcnow() - datetime.timedelta(days=days_to_keep)
        
        with self.get_session() as session:
            # 古い生成ログを削除
            old_logs = session.query(GenerationLog).filter(
                GenerationLog.created_at < cutoff_date
            ).delete()
            
            # 低評価の古い動画を削除（手動アップロード以外）
            old_videos = session.query(Video).filter(
                Video.created_at < cutoff_date,
                Video.is_manual_upload == False,
                Video.user_rating < 2.0
            ).delete()
            
            session.commit()
            
            logger.info(f"Cleanup completed: {old_logs} logs, {old_videos} videos removed")
            return {
                'logs_removed': old_logs,
                'videos_removed': old_videos,
                'cutoff_date': cutoff_date.isoformat()
            }