"""
AI動的絵画システム - データベースパッケージ
博士の実験データ管理システムなのだ〜！
"""

from .database import DatabaseManager
from .models import (
    Base, Video, UserPreference, SystemStatus, 
    GenerationLog, Tag, VideoTag
)

__all__ = [
    'DatabaseManager',
    'Base', 
    'Video',
    'UserPreference', 
    'SystemStatus',
    'GenerationLog',
    'Tag',
    'VideoTag'
]

__version__ = '1.0.0'