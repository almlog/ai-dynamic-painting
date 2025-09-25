"""
🔴 T6-011 RED Phase: VEO Config Testing
Google Cloud認証設定の失敗テスト実装
"""
import pytest
import os
from unittest.mock import patch, MagicMock

# TDD RED Phase: Import will fail until implementation exists
try:
    from src.config.veo_config import (
        VEOConfig,
        get_veo_config,
        ImproperlyConfiguredError
    )
except ImportError:
    # Expected to fail in RED phase
    pass


class TestVEOConfig:
    """VEO Configuration Testing Suite"""
    
    def test_missing_google_application_credentials_raises_error(self):
        """
        🔴 RED: 必要な環境変数が設定されていない場合のエラー検証
        GOOGLE_APPLICATION_CREDENTIALS が未設定時に適切なエラーを発生
        """
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ImproperlyConfiguredError) as exc_info:
                get_veo_config()
            
            assert "GOOGLE_APPLICATION_CREDENTIALS" in str(exc_info.value)
            assert "environment variable" in str(exc_info.value).lower()

    def test_missing_veo_project_id_raises_error(self):
        """
        🔴 RED: VEO_PROJECT_ID環境変数が未設定時のエラー検証
        """
        with patch.dict(os.environ, {
            'GOOGLE_APPLICATION_CREDENTIALS': '/path/to/credentials.json'
        }, clear=True):
            with pytest.raises(ImproperlyConfiguredError) as exc_info:
                get_veo_config()
            
            assert "VEO_PROJECT_ID" in str(exc_info.value)
            assert "required" in str(exc_info.value).lower()

    def test_invalid_credentials_file_raises_error(self):
        """
        🔴 RED: 存在しないクレデンシャルファイルパス指定時のエラー検証
        """
        with patch.dict(os.environ, {
            'GOOGLE_APPLICATION_CREDENTIALS': '/nonexistent/credentials.json',
            'VEO_PROJECT_ID': 'test-project'
        }):
            with pytest.raises(ImproperlyConfiguredError) as exc_info:
                get_veo_config()
            
            assert "credentials file not found" in str(exc_info.value).lower()
            assert "/nonexistent/credentials.json" in str(exc_info.value)

    def test_valid_config_returns_veo_config_instance(self):
        """
        🔴 RED: 正常な設定でVEOConfigインスタンスが返されることを検証
        """
        with patch.dict(os.environ, {
            'GOOGLE_APPLICATION_CREDENTIALS': '/valid/credentials.json',
            'VEO_PROJECT_ID': 'test-project-id',
            'VEO_LOCATION': 'us-central1'  # Optional
        }):
            with patch('os.path.exists', return_value=True):
                config = get_veo_config()
                
                assert isinstance(config, VEOConfig)
                assert config.project_id == 'test-project-id'
                assert config.credentials_path == '/valid/credentials.json'
                assert config.location == 'us-central1'

    def test_default_location_when_not_specified(self):
        """
        🔴 RED: VEO_LOCATION未指定時のデフォルト値設定検証
        """
        with patch.dict(os.environ, {
            'GOOGLE_APPLICATION_CREDENTIALS': '/valid/credentials.json',
            'VEO_PROJECT_ID': 'test-project'
        }, clear=True):
            with patch('os.path.exists', return_value=True):
                config = get_veo_config()
                
                # Default location should be 'us-central1'
                assert config.location == 'us-central1'

    def test_veo_config_properties(self):
        """
        🔴 RED: VEOConfigクラスのプロパティ検証
        """
        config = VEOConfig(
            project_id='test-project',
            credentials_path='/path/to/creds.json',
            location='europe-west1'
        )
        
        assert config.project_id == 'test-project'
        assert config.credentials_path == '/path/to/creds.json' 
        assert config.location == 'europe-west1'

    def test_veo_config_validation_on_init(self):
        """
        🔴 RED: VEOConfigインスタンス作成時の値検証
        """
        # Empty project_id should raise error
        with pytest.raises(ValueError) as exc_info:
            VEOConfig(project_id="", credentials_path="/valid.json", location="us-central1")
        
        assert "project_id cannot be empty" in str(exc_info.value)

        # Empty credentials_path should raise error  
        with pytest.raises(ValueError) as exc_info:
            VEOConfig(project_id="test-project", credentials_path="", location="us-central1")
        
        assert "credentials_path cannot be empty" in str(exc_info.value)

    def test_get_google_credentials_method(self):
        """
        🔴 RED: Google認証情報取得メソッドの検証
        """
        with patch('src.config.veo_config.load_credentials_from_file') as mock_load_creds:
            mock_creds = MagicMock()
            mock_load_creds.return_value = (mock_creds, 'test-project')
            
            config = VEOConfig(
                project_id='test-project',
                credentials_path='/valid/creds.json',
                location='us-central1'
            )
            
            credentials = config.get_google_credentials()
            
            assert credentials == mock_creds
            mock_load_creds.assert_called_once_with('/valid/creds.json')

    def test_config_caching(self):
        """
        🔴 RED: 設定情報のキャッシュ動作検証
        """
        with patch.dict(os.environ, {
            'GOOGLE_APPLICATION_CREDENTIALS': '/valid/credentials.json',
            'VEO_PROJECT_ID': 'test-project'
        }):
            with patch('os.path.exists', return_value=True):
                config1 = get_veo_config()
                config2 = get_veo_config()
                
                # Same instance should be returned (singleton pattern)
                assert config1 is config2