"""
AI動的絵画システム - 設定管理システム
詳細設計書に基づく設定・環境管理クラスなのだ〜！
"""
import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass, asdict
from datetime import datetime

from pydantic import field_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


@dataclass
class DisplayConfig:
    """表示設定"""
    width: int = 1920
    height: int = 1080
    fullscreen: bool = True
    overlay_enabled: bool = True
    brightness: float = 1.0
    auto_brightness: bool = True


@dataclass
class GenerationConfig:
    """生成設定"""
    daily_limit: int = 3
    auto_generation: bool = True
    quality: str = 'high'  # high, medium, fast
    style_preference: str = 'realistic'
    custom_prompts_enabled: bool = False


@dataclass
class ScheduleConfig:
    """スケジュール設定"""
    morning_start: str = '06:00'
    morning_end: str = '10:00'
    daytime_start: str = '10:00'
    daytime_end: str = '18:00'
    evening_start: str = '18:00'
    evening_end: str = '22:00'
    night_start: str = '22:00'
    night_end: str = '06:00'
    weekend_special: bool = True


@dataclass
class StorageConfig:
    """ストレージ設定"""
    video_cache_size_gb: int = 10
    cache_cleanup_days: int = 30
    backup_enabled: bool = True
    backup_retention_days: int = 7


@dataclass
class APIConfig:
    """API設定"""
    veo_api_key: str = ""
    weather_api_key: str = ""
    api_timeout: int = 30
    max_retries: int = 3
    quota_warning_threshold: float = 0.8


@dataclass
class M5StackConfig:
    """M5STACK設定"""
    ip_address: str = "192.168.1.100"
    update_interval: int = 30
    sensor_threshold_light: int = 50
    sensor_threshold_temp: float = 25.0
    display_timeout: int = 300


@dataclass
class SystemConfig:
    """システム全体設定"""
    log_level: str = 'INFO'
    debug_mode: bool = False
    auto_update: bool = True
    health_check_interval: int = 300
    startup_delay: int = 10


class Settings(BaseSettings):
    """環境変数ベース設定（Pydantic V2）"""
    
    # API Keys（環境変数から読み込み）
    veo_api_key: str = ""
    weather_api_key: str = ""
    
    # Database
    database_url: str = "sqlite:///./painting_system.db"
    
    # System
    log_level: str = "INFO"
    debug: bool = False
    
    # Directories
    video_cache_dir: str = "./video_cache"
    logs_dir: str = "./logs"
    backup_dir: str = "./backups"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'log_level must be one of {valid_levels}')
        return v.upper()


class ConfigManager:
    """設定管理クラス - 博士の設定ラボなのだ！"""
    
    def __init__(self, config_file: str = "config.json", db_manager=None):
        """
        設定マネージャー初期化
        
        Args:
            config_file: 設定ファイルパス
            db_manager: データベースマネージャー（設定永続化用）
        """
        self.config_file = Path(config_file)
        self.db_manager = db_manager
        
        # 設定インスタンス初期化
        self.display = DisplayConfig()
        self.generation = GenerationConfig()
        self.schedule = ScheduleConfig()
        self.storage = StorageConfig()
        self.api = APIConfig()
        self.m5stack = M5StackConfig()
        self.system = SystemConfig()
        
        # Pydantic設定
        self.settings = Settings()
        
        # 設定読み込み
        self.load_config()
        self._create_directories()
        
        logger.info(f"ConfigManager initialized with config: {config_file}")
    
    def _create_directories(self) -> None:
        """必要なディレクトリ作成"""
        directories = [
            self.settings.video_cache_dir,
            self.settings.logs_dir,
            self.settings.backup_dir
        ]
        
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory created/verified: {dir_path}")
    
    def load_config(self) -> None:
        """設定読み込み（ファイル→DB→デフォルト値の優先順）"""
        # 1. ファイルから読み込み
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                self._apply_config_dict(file_config)
                logger.info(f"Config loaded from file: {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load config file: {e}")
        
        # 2. データベースから読み込み（ファイル設定を上書き）
        if self.db_manager:
            try:
                db_prefs = self.db_manager.get_all_preferences()
                self._apply_db_preferences(db_prefs)
                logger.info("Config loaded from database")
            except Exception as e:
                logger.error(f"Failed to load config from database: {e}")
        
        # 3. 環境変数からAPI設定を上書き
        if self.settings.veo_api_key:
            self.api.veo_api_key = self.settings.veo_api_key
        if self.settings.weather_api_key:
            self.api.weather_api_key = self.settings.weather_api_key
    
    def _apply_config_dict(self, config_dict: Dict[str, Any]) -> None:
        """辞書形式の設定を適用"""
        for section_name, section_config in config_dict.items():
            if hasattr(self, section_name):
                section = getattr(self, section_name)
                for key, value in section_config.items():
                    if hasattr(section, key):
                        setattr(section, key, value)
                        logger.debug(f"Config updated: {section_name}.{key} = {value}")
    
    def _apply_db_preferences(self, preferences: Dict[str, str]) -> None:
        """データベース設定を適用"""
        # 設定キーのマッピング
        preference_mapping = {
            'display_overlay': ('display', 'overlay_enabled', bool),
            'auto_generation': ('generation', 'auto_generation', bool),
            'preferred_time_morning': ('schedule', 'morning_start', str),
            'preferred_time_evening': ('schedule', 'evening_start', str),
            'daily_generation_limit': ('generation', 'daily_limit', int),
            'video_cache_size_gb': ('storage', 'video_cache_size_gb', int),
            'auto_brightness': ('display', 'auto_brightness', bool),
            'weekend_special': ('schedule', 'weekend_special', bool),
        }
        
        for pref_key, pref_value in preferences.items():
            if pref_key in preference_mapping:
                section_name, attr_name, value_type = preference_mapping[pref_key]
                section = getattr(self, section_name)
                
                # 型変換
                try:
                    if value_type == bool:
                        converted_value = pref_value.lower() in ('true', '1', 'yes', 'on')
                    elif value_type == int:
                        converted_value = int(pref_value)
                    elif value_type == float:
                        converted_value = float(pref_value)
                    else:
                        converted_value = pref_value
                    
                    setattr(section, attr_name, converted_value)
                    logger.debug(f"DB preference applied: {section_name}.{attr_name} = {converted_value}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to convert preference {pref_key}={pref_value}: {e}")
    
    def save_config(self) -> bool:
        """設定保存（ファイル＋DB）"""
        try:
            # ファイルに保存
            config_dict = {
                'display': asdict(self.display),
                'generation': asdict(self.generation),
                'schedule': asdict(self.schedule),
                'storage': asdict(self.storage),
                'api': {k: v for k, v in asdict(self.api).items() if k not in ['veo_api_key', 'weather_api_key']},  # API key除外
                'm5stack': asdict(self.m5stack),
                'system': asdict(self.system)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            # データベースに保存
            if self.db_manager:
                self._save_to_database()
            
            logger.info(f"Config saved successfully: {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def _save_to_database(self) -> None:
        """データベースに設定保存"""
        preference_mapping = {
            ('display', 'overlay_enabled'): 'display_overlay',
            ('generation', 'auto_generation'): 'auto_generation',
            ('schedule', 'morning_start'): 'preferred_time_morning',
            ('schedule', 'evening_start'): 'preferred_time_evening',
            ('generation', 'daily_limit'): 'daily_generation_limit',
            ('storage', 'video_cache_size_gb'): 'video_cache_size_gb',
            ('display', 'auto_brightness'): 'auto_brightness',
            ('schedule', 'weekend_special'): 'weekend_special',
        }
        
        for (section_name, attr_name), pref_key in preference_mapping.items():
            section = getattr(self, section_name)
            value = getattr(section, attr_name)
            self.db_manager.set_preference(pref_key, str(value))
    
    def get_config_value(self, section: str, key: str) -> Any:
        """設定値取得"""
        if hasattr(self, section):
            section_obj = getattr(self, section)
            if hasattr(section_obj, key):
                return getattr(section_obj, key)
        return None
    
    def set_config_value(self, section: str, key: str, value: Any) -> bool:
        """設定値更新"""
        try:
            if hasattr(self, section):
                section_obj = getattr(self, section)
                if hasattr(section_obj, key):
                    setattr(section_obj, key, value)
                    logger.info(f"Config value updated: {section}.{key} = {value}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to set config value {section}.{key}={value}: {e}")
            return False
    
    def get_all_config(self) -> Dict[str, Dict[str, Any]]:
        """全設定取得"""
        return {
            'display': asdict(self.display),
            'generation': asdict(self.generation),
            'schedule': asdict(self.schedule),
            'storage': asdict(self.storage),
            'api': asdict(self.api),
            'm5stack': asdict(self.m5stack),
            'system': asdict(self.system),
            'settings': {
                'database_url': self.settings.database_url,
                'video_cache_dir': self.settings.video_cache_dir,
                'logs_dir': self.settings.logs_dir,
                'backup_dir': self.settings.backup_dir,
                'log_level': self.settings.log_level,
                'debug': self.settings.debug
            }
        }
    
    def validate_config(self) -> List[str]:
        """設定値検証"""
        errors = []
        
        # API キー検証
        if not self.api.veo_api_key.strip():
            errors.append("VEO API key is missing")
        
        # ディレクトリパス検証
        if not Path(self.settings.video_cache_dir).exists():
            errors.append(f"Video cache directory does not exist: {self.settings.video_cache_dir}")
        
        # スケジュール設定検証
        try:
            from datetime import time
            time.fromisoformat(self.schedule.morning_start)
            time.fromisoformat(self.schedule.evening_start)
        except ValueError:
            errors.append("Invalid time format in schedule settings")
        
        # 数値範囲検証
        if not 1 <= self.generation.daily_limit <= 100:
            errors.append("Daily generation limit must be between 1 and 100")
        
        if not 0.1 <= self.display.brightness <= 2.0:
            errors.append("Display brightness must be between 0.1 and 2.0")
        
        if errors:
            logger.warning(f"Config validation errors: {errors}")
        else:
            logger.info("Config validation passed")
        
        return errors
    
    def reset_to_defaults(self) -> bool:
        """デフォルト設定にリセット"""
        try:
            self.display = DisplayConfig()
            self.generation = GenerationConfig()
            self.schedule = ScheduleConfig()
            self.storage = StorageConfig()
            self.api = APIConfig()
            self.m5stack = M5StackConfig()
            self.system = SystemConfig()
            
            logger.info("Config reset to defaults")
            return True
        except Exception as e:
            logger.error(f"Failed to reset config: {e}")
            return False
    
    def export_config(self, export_path: str) -> bool:
        """設定エクスポート"""
        try:
            config_data = {
                'exported_at': datetime.now().isoformat(),
                'config': self.get_all_config()
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Config exported to: {export_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export config: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """設定インポート"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            if 'config' in config_data:
                self._apply_config_dict(config_data['config'])
                logger.info(f"Config imported from: {import_path}")
                return True
            else:
                logger.error("Invalid config file format")
                return False
        except Exception as e:
            logger.error(f"Failed to import config: {e}")
            return False
    
    def get_runtime_info(self) -> Dict[str, Any]:
        """実行時情報取得"""
        return {
            'config_file': str(self.config_file),
            'config_file_exists': self.config_file.exists(),
            'config_loaded_at': datetime.now().isoformat(),
            'database_connected': self.db_manager is not None and self.db_manager.is_connected() if self.db_manager else False,
            'api_keys_configured': {
                'veo_api': bool(self.api.veo_api_key.strip()),
                'weather_api': bool(self.api.weather_api_key.strip())
            },
            'directories': {
                'video_cache': str(Path(self.settings.video_cache_dir).resolve()),
                'logs': str(Path(self.settings.logs_dir).resolve()),
                'backup': str(Path(self.settings.backup_dir).resolve())
            }
        }