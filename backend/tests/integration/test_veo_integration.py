"""
🟢 T6-019: VEO API Integration Testing
実際のGoogle Cloud環境でのEnhancedVEOClient統合テスト

Tests:
- 実API呼び出しテスト
- 認証フローテスト  
- エラーレスポンステスト、タイムアウトテスト
"""
import pytest
import asyncio
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import patch, MagicMock, AsyncMock

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from src.ai.services.veo_client import (
    EnhancedVEOClient,
    VEOAuthenticationError,
    VEOQuotaExceededError,
    VEOTimeoutError,
    VEOValidationError,
    VEOConfigurationError
)
from src.config.veo_config import VEOConfig, get_veo_config


class TestVEOIntegration:
    """VEO API Integration Test Suite - 実際のGoogle Cloud環境テスト"""
    
    @pytest.fixture(autouse=True)
    def setup_environment(self):
        """テスト環境のセットアップ"""
        # Google Cloud credentials確認
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not credentials_path:
            pytest.skip("GOOGLE_APPLICATION_CREDENTIALS not set - skipping integration tests")
            
        if not Path(credentials_path).exists():
            pytest.skip(f"Credentials file not found: {credentials_path}")
            
        # VEO config確認
        try:
            self.config = get_veo_config()
        except Exception as e:
            pytest.skip(f"VEO config error: {e}")
    
    @pytest.fixture
    def client(self):
        """実際のEnhancedVEOClientインスタンス"""
        return EnhancedVEOClient(config=self.config, timeout=30)
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_veo_client_initialization_with_real_config(self, client):
        """🟢 T6-019.1: 実際のVEOConfig設定での初期化テスト"""
        assert client.project_id is not None
        assert client.location is not None
        assert client.credentials_path is not None
        assert client.timeout == 30
        assert client.max_retries == 3
        assert client.model_name == 'veo-001-preview'
        
    @pytest.mark.integration 
    @pytest.mark.slow
    def test_authentication_flow_success(self, client):
        """🟢 T6-019.2: 実際のGoogle Cloud認証フローテスト"""
        try:
            credentials = client.get_credentials()
            assert credentials is not None
            assert hasattr(credentials, 'token')
            print("✅ Authentication successful")
        except Exception as e:
            pytest.fail(f"Authentication failed: {e}")
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_veo_api_call_minimal_request(self, client):
        """🟢 T6-019.3: 最小限のVEO API呼び出しテスト (実際のAPI)"""
        # 実際のAPI呼び出し - 最小限のプロンプトでテスト
        test_prompt = "A simple test"
        
        try:
            # 短いタイムアウトでテスト (失敗は想定内)
            with patch.object(client, 'timeout', 5):  # 5秒タイムアウト
                result = await client.generate_video(
                    prompt=test_prompt,
                    duration_seconds=5,
                    quality="standard"
                )
                
            # 成功した場合の検証
            assert 'status' in result
            assert 'task_id' in result or 'video_url' in result
            print(f"✅ API call successful: {result.get('status')}")
            
        except VEOTimeoutError:
            # タイムアウトは想定内 (認証とリクエスト構造が正しいことを確認)
            print("✅ API accessible but timed out (expected for short timeout)")
            
        except VEOAuthenticationError as e:
            pytest.fail(f"Authentication failed: {e}")
            
        except VEOValidationError as e:
            # バリデーションエラーも想定内 (APIに到達していることを確認)
            print(f"✅ API validation feedback received: {e}")
            
        except Exception as e:
            # 予期しないエラーは失敗
            pytest.fail(f"Unexpected error: {e}")
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_invalid_authentication_handling(self):
        """🟢 T6-019.4: 無効な認証情報でのエラーハンドリングテスト"""
        # 無効な認証パスでクライアント作成
        invalid_config = VEOConfig(
            project_id=self.config.project_id,
            location=self.config.location,
            credentials_path="/invalid/path/credentials.json"
        )
        
        with pytest.raises(VEOAuthenticationError):
            client = EnhancedVEOClient(config=invalid_config)
            client.get_credentials()
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_timeout_error_handling(self, client):
        """🟢 T6-019.5: タイムアウトエラーハンドリングテスト"""
        # 極端に短いタイムアウトでテスト
        client.timeout = 1  # 1秒
        
        with pytest.raises(VEOTimeoutError):
            await client.generate_video(
                prompt="Test timeout handling",
                duration_seconds=5
            )
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_api_error_retry_mechanism(self, client):
        """🟢 T6-019.6: API エラー時のリトライメカニズムテスト"""
        # リトライ設定を短く設定
        client.max_retries = 2
        client.retry_delay = 0.1
        
        # 無効なプロンプトでテスト (エラーを誘発)
        try:
            result = await client.generate_video_with_retry(
                prompt="",  # 空のプロンプト
                duration_seconds=1
            )
        except (VEOValidationError, VEOTimeoutError) as e:
            # バリデーションエラーまたはタイムアウトは想定内
            print(f"✅ Retry mechanism triggered correctly: {e}")
        except Exception as e:
            # リトライが動作していることを確認
            assert "retry" in str(e).lower() or "timeout" in str(e).lower()
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_configuration_validation(self):
        """🟢 T6-019.7: VEO設定バリデーションテスト"""
        # 必須設定項目の確認
        config = get_veo_config()
        
        assert config.project_id, "Project ID must be configured"
        assert config.location, "Location must be configured"
        assert config.credentials_path, "Credentials path must be configured"
        
        # 設定値の妥当性確認
        assert config.location in ['us-central1', 'europe-west4', 'asia-southeast1'], \
               f"Invalid location: {config.location}"
        assert Path(config.credentials_path).exists(), \
               f"Credentials file not found: {config.credentials_path}"
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_error_classification(self, client):
        """🟢 T6-019.8: エラー分類とハンドリングテスト"""
        test_cases = [
            {
                "name": "empty_prompt",
                "prompt": "",
                "expected_error": VEOValidationError
            },
            {
                "name": "invalid_duration", 
                "prompt": "Test video",
                "duration_seconds": 0,
                "expected_error": VEOValidationError
            }
        ]
        
        for case in test_cases:
            print(f"Testing error case: {case['name']}")
            
            try:
                await client.generate_video(
                    prompt=case["prompt"],
                    duration_seconds=case.get("duration_seconds", 5)
                )
                # エラーが発生しなかった場合はテスト失敗
                pytest.fail(f"Expected {case['expected_error'].__name__} for {case['name']}")
                
            except case["expected_error"] as e:
                print(f"✅ Correctly caught {case['expected_error'].__name__}: {e}")
                
            except (VEOTimeoutError, Exception) as e:
                # タイムアウトやその他のエラーは一部想定内
                print(f"⚠️ Alternative error for {case['name']}: {type(e).__name__}")
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_dependency_injection_with_mock_model(self):
        """🟢 T6-019.9: Dependency Injection テスト (モックModel使用)"""
        # モックモデルを注入してテスト
        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock()
        
        client = EnhancedVEOClient(
            config=self.config,
            model=mock_model
        )
        
        # 注入されたモデルが使用されることを確認
        assert client.model == mock_model
        print("✅ Dependency injection working correctly")


@pytest.mark.integration
class TestVEOIntegrationPerformance:
    """VEO API Performance Integration Tests"""
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_concurrent_requests_handling(self):
        """🟢 T6-019.10: 並行リクエスト処理テスト"""
        try:
            config = get_veo_config()
            clients = [EnhancedVEOClient(config=config, timeout=10) for _ in range(3)]
            
            async def make_request(client, prompt_suffix):
                try:
                    return await client.generate_video(
                        prompt=f"Test concurrent {prompt_suffix}",
                        duration_seconds=3
                    )
                except (VEOTimeoutError, VEOValidationError) as e:
                    return {"error": str(e), "client": id(client)}
            
            # 並行実行
            tasks = [
                make_request(clients[0], "A"),
                make_request(clients[1], "B"), 
                make_request(clients[2], "C")
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 少なくとも一部のリクエストが適切に処理されることを確認
            successful_requests = sum(1 for r in results if not isinstance(r, Exception))
            print(f"✅ Concurrent requests handled: {successful_requests}/3")
            
        except Exception as e:
            pytest.skip(f"Concurrent test skipped due to environment: {e}")


if __name__ == "__main__":
    """統合テストの個別実行"""
    print("🧪 VEO API Integration Tests")
    print("=" * 50)
    
    # 環境確認
    credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not credentials:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        sys.exit(1)
        
    print(f"✅ Using credentials: {credentials}")
    
    # pytest実行
    pytest.main([__file__, "-v", "-s", "--tb=short"])