"""
🔴 T6-012 RED Phase: VEO Client Enhanced Testing
VEOConfigと統合されたVEOクライアント強化テスト
"""
import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from typing import Dict, Any

# TDD RED Phase: Import will fail until enhanced implementation exists
try:
    from src.ai.services.veo_client import (
        EnhancedVEOClient,
        VEOAuthenticationError,
        VEOQuotaExceededError, 
        VEOTimeoutError,
        VEOValidationError,
        VEOConfigurationError
    )
    from src.config.veo_config import VEOConfig, get_veo_config
except ImportError:
    # Expected to fail in RED phase
    pass


class TestEnhancedVEOClient:
    """Enhanced VEO Client Testing Suite with VEOConfig Integration"""

    def test_enhanced_veo_client_initialization_with_veo_config(self):
        """
        🟢 GREEN: Dependency Injection - VEOConfigを使用したEnhancedVEOClient初期化テスト
        T6-011で作成したVEOConfigクラスとの統合確認
        """
        # Dependency Injection: モックVEOConfigを直接注入
        mock_config = MagicMock()
        mock_config.project_id = 'test-project-id'
        mock_config.location = 'us-central1'
        mock_config.credentials_path = '/path/to/credentials.json'
        
        client = EnhancedVEOClient(config=mock_config, timeout=300)
        
        assert client.project_id == 'test-project-id'
        assert client.location == 'us-central1'
        assert client.credentials_path == '/path/to/credentials.json'
        assert client.timeout == 300

    def test_enhanced_veo_client_initialization_failure_with_invalid_config(self):
        """
        🟢 GREEN: Dependency Injection - 不正なVEOConfig設定時の初期化失敗テスト
        """
        # 不正なモックconfig（必要なプロパティが不足）
        invalid_config = MagicMock()
        invalid_config.project_id.side_effect = Exception("Configuration error")
        
        with pytest.raises(VEOConfigurationError) as exc_info:
            EnhancedVEOClient(config=invalid_config)
        
        assert "Configuration error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_video_success_response_parsing(self):
        """
        🔴 RED: 動画生成メソッドの成功レスポンス正常パーステスト
        レスポンス形式の正確な解析とデータ抽出確認
        """
        mock_config = MagicMock()
        client = EnhancedVEOClient(config=mock_config)
        
        # Mock successful API response
        mock_response = {
                "status": "completed",
                "video_data": {
                    "video_url": "https://storage.googleapis.com/test-video.mp4",
                    "video_id": "veo_12345",
                    "duration_seconds": 8,
                    "resolution": "1920x1080"
                },
                "generation_time_ms": 45000,
                "metadata": {
                    "prompt": "A beautiful sunset",
                    "style": "cinematic",
                    "model_version": "veo-001-preview"
                }
        }
        
        with patch.object(client, '_call_veo_api', return_value=mock_response) as mock_api:
            result = await client.generate_video(
                prompt="A beautiful sunset",
                style="cinematic"
            )
            
            assert result["status"] == "completed"
            assert result["video_id"] == "veo_12345"
            assert result["video_url"] == "https://storage.googleapis.com/test-video.mp4"
            assert result["duration_seconds"] == 8
            assert result["resolution"] == "1920x1080"
            assert result["generation_time_ms"] == 45000
            mock_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_api_503_error_retry_logic(self):
        """
        🔴 RED: API 503エラー時のリトライロジック検証テスト
        一時的なサーバエラー時の自動リトライ機能確認
        """
        mock_config = MagicMock()
        client = EnhancedVEOClient(config=mock_config, max_retries=3, retry_delay=0.1)
        
        # Mock API responses: 503 -> 503 -> 200 (success on 3rd try)
        mock_responses = [
            Exception("503 Service Temporarily Unavailable"),
            Exception("503 Service Temporarily Unavailable"), 
            {
                "status": "completed",
                "video_id": "veo_retry_success",
                "video_url": "https://storage.googleapis.com/retry-video.mp4"
            }
        ]
        
        with patch.object(client, '_call_veo_api', side_effect=mock_responses) as mock_api:
            result = await client.generate_video_with_retry(prompt="Test retry")
            
            assert result["status"] == "completed"
            assert result["video_id"] == "veo_retry_success"
            assert mock_api.call_count == 3  # Called 3 times due to retries

    @pytest.mark.asyncio
    async def test_api_503_error_max_retries_exceeded(self):
        """
        🔴 RED: 最大リトライ回数超過時の例外発生テスト
        """
        mock_config = MagicMock()
        client = EnhancedVEOClient(config=mock_config, max_retries=2, retry_delay=0.1)
        
        # All attempts fail with 503
        with patch.object(client, '_call_veo_api', side_effect=Exception("503 Service Temporarily Unavailable")):
            with pytest.raises(VEOTimeoutError) as exc_info:
                await client.generate_video_with_retry(prompt="Test max retry")
            
            assert "max retries exceeded" in str(exc_info.value).lower()

    @patch('logging.Logger.info')
    @patch('logging.Logger.error')
    @pytest.mark.asyncio
    async def test_successful_api_call_logging(self, mock_log_error, mock_log_info):
        """
        🔴 RED: 成功時のログ出力確認テスト
        API呼び出し成功時に適切なログが出力されることを検証
        """
        mock_config = MagicMock()
        client = EnhancedVEOClient(config=mock_config)
        
        mock_response = {
            "status": "completed",
            "video_id": "veo_success_log",
            "generation_time_ms": 30000
        }
        
        with patch.object(client, '_call_veo_api', return_value=mock_response):
            await client.generate_video(prompt="Test successful logging")
            
            # Check success logs
            mock_log_info.assert_any_call("Starting VEO video generation with prompt: Test successful logging")
            mock_log_info.assert_any_call("VEO video generation completed successfully. Video ID: veo_success_log, Time: 30000ms")
            mock_log_error.assert_not_called()

    @patch('logging.Logger.error')
    @pytest.mark.asyncio  
    async def test_failed_api_call_logging(self, mock_log_error):
        """
        🔴 RED: 失敗時のログ出力確認テスト
        API呼び出し失敗時に適切なエラーログが出力されることを検証
        """
        mock_config = MagicMock()
        client = EnhancedVEOClient(config=mock_config)
            
            error_message = "VEO API authentication failed"
            
            with patch.object(client, '_call_veo_api', side_effect=VEOAuthenticationError(error_message)):
                with pytest.raises(VEOAuthenticationError):
                    await client.generate_video(prompt="Test error logging")
                
                # Check error logs
                mock_log_error.assert_called_with(f"VEO video generation failed: {error_message}")

    def test_enhanced_client_google_credentials_integration(self):
        """
        🟢 GREEN: Dependency Injection - Google Cloud認証情報との統合テスト
        VEOConfigから取得した認証情報の正常な使用確認
        """
        # Dependency Injection: モックVEOConfigを直接注入
        mock_config = MagicMock()
        mock_credentials = MagicMock()
        mock_config.get_google_credentials.return_value = mock_credentials
        
        client = EnhancedVEOClient(config=mock_config)
        credentials = client.get_credentials()
        
        assert credentials is not None
        assert credentials is mock_credentials
        mock_config.get_google_credentials.assert_called_once()

    @pytest.mark.asyncio
    async def test_quota_exceeded_error_handling(self):
        """
        🔴 RED: クォータ超過エラーの適切な処理テスト
        """
        mock_config = MagicMock()
        client = EnhancedVEOClient(config=mock_config)
            
            with patch.object(client, '_call_veo_api', side_effect=VEOQuotaExceededError("Daily quota exceeded")):
                with pytest.raises(VEOQuotaExceededError) as exc_info:
                    await client.generate_video(prompt="Test quota error")
                
                assert "Daily quota exceeded" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self):
        """
        🔴 RED: タイムアウトエラーの適切な処理テスト
        """
        mock_config = MagicMock()
        client = EnhancedVEOClient(config=mock_config, timeout=1)  # Very short timeout
            
            with patch.object(client, '_call_veo_api', side_effect=asyncio.sleep(2)):
                with pytest.raises(VEOTimeoutError) as exc_info:
                    await client.generate_video(prompt="Test timeout")
                
                assert "timeout" in str(exc_info.value).lower()

    def test_validation_error_empty_prompt(self):
        """
        🔴 RED: 空プロンプト時のバリデーションエラーテスト
        """
        mock_config = MagicMock()
        client = EnhancedVEOClient(config=mock_config)
            
            with pytest.raises(VEOValidationError) as exc_info:
                asyncio.run(client.generate_video(prompt=""))
            
            assert "prompt cannot be empty" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_image_to_video_generation_support(self):
        """
        🔴 RED: 画像から動画生成機能のサポートテスト
        """
        mock_config = MagicMock()
        client = EnhancedVEOClient(config=mock_config)
            
            mock_image_bytes = b"fake_image_data"
            mock_response = {
                "status": "completed",
                "video_id": "veo_image_to_video",
                "generation_type": "image_to_video"
            }
            
            with patch.object(client, '_call_veo_api', return_value=mock_response):
                result = await client.generate_video(
                    prompt="Transform this image into a video",
                    image_bytes=mock_image_bytes
                )
                
                assert result["status"] == "completed" 
                assert result["generation_type"] == "image_to_video"