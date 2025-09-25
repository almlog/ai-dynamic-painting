"""
🔧 T6-011 REFACTOR Phase: VEO Config Implementation
Google Cloud VEO API認証設定の実装 (リファクタリング済み)
"""
import os
from typing import Optional, Tuple, Any
from google.oauth2.service_account import Credentials
from google.auth import load_credentials_from_file


class ImproperlyConfiguredError(Exception):
    """VEO Configuration Error - 設定不正時の例外"""
    pass


def _validate_non_empty_string(value: str, field_name: str) -> str:
    """
    文字列の非空チェックとトリミング
    
    Args:
        value: チェック対象文字列
        field_name: フィールド名（エラーメッセージ用）
        
    Returns:
        str: トリミング済み文字列
        
    Raises:
        ValueError: 文字列が空またはNoneの場合
    """
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value.strip()


class VEOConfig:
    """
    VEO API Configuration Class
    Google Cloud認証情報とプロジェクト設定を管理
    """
    
    def __init__(self, project_id: str, credentials_path: str, location: str = "us-central1"):
        """
        VEOConfig Constructor
        
        Args:
            project_id: Google Cloud Project ID
            credentials_path: Path to Google Cloud credentials JSON file
            location: VEO API location (default: us-central1)
            
        Raises:
            ValueError: If project_id or credentials_path is empty
        """
        # DRY principle: 統一されたバリデーション関数を使用
        self.project_id = _validate_non_empty_string(project_id, "project_id")
        self.credentials_path = _validate_non_empty_string(credentials_path, "credentials_path")
        self.location = location or "us-central1"
    
    def get_google_credentials(self) -> Credentials:
        """
        Google Cloud認証情報を取得
        
        Returns:
            Credentials: Google Cloud認証情報オブジェクト
            
        Raises:
            FileNotFoundError: 認証ファイルが見つからない場合
            ValueError: 認証ファイルが不正な場合
        """
        credentials, _ = load_credentials_from_file(self.credentials_path)
        return credentials


# Singleton pattern for configuration caching
_config_cache: Optional[VEOConfig] = None


def get_veo_config() -> VEOConfig:
    """
    VEO Configuration Singleton Factory
    環境変数から設定を読み込み、VEOConfigインスタンスを返す
    
    Returns:
        VEOConfig: VEO API設定インスタンス
        
    Raises:
        ImproperlyConfiguredError: 必要な環境変数が未設定または不正な場合
    """
    global _config_cache
    
    # Singletonパターン: キャッシュされた設定があれば返す
    if _config_cache is not None:
        return _config_cache
    
    # 環境変数取得
    google_credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    veo_project_id = os.environ.get('VEO_PROJECT_ID') 
    veo_location = os.environ.get('VEO_LOCATION', 'us-central1')
    
    # 必須環境変数のバリデーション
    if not google_credentials_path:
        raise ImproperlyConfiguredError(
            "GOOGLE_APPLICATION_CREDENTIALS environment variable is required"
        )
    
    if not veo_project_id:
        raise ImproperlyConfiguredError(
            "VEO_PROJECT_ID environment variable is required"
        )
    
    # 認証ファイル存在確認
    if not os.path.exists(google_credentials_path):
        raise ImproperlyConfiguredError(
            f"Google Cloud credentials file not found: {google_credentials_path}"
        )
    
    # 設定インスタンス作成とキャッシュ
    _config_cache = VEOConfig(
        project_id=veo_project_id,
        credentials_path=google_credentials_path,
        location=veo_location
    )
    
    return _config_cache