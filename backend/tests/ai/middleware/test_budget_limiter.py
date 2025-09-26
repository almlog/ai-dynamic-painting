"""
Test suite for Budget Limiter middleware (T6-014)
TDD RED Phase - Creating failing tests first
"""

import pytest
import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse
import json

# Import the module to be implemented (will fail initially)
from src.ai.middleware.budget_limiter import (
    BudgetLimiter,
    BudgetExceededException, 
    AlertLevel,
    AlertChannel,
    BudgetStatus
)
from src.ai.services.cost_tracker import CostTracker, CostExceededError


class TestBudgetLimiterBasic:
    """基本的な予算チェック機能のテスト"""
    
    @pytest.mark.asyncio
    async def test_allow_request_within_budget(self):
        """予算内でのリクエストが許可されること"""
        # Arrange
        cost_tracker = MagicMock(spec=CostTracker)
        cost_tracker.is_budget_exceeded = AsyncMock(return_value=False)
        cost_tracker.get_budget_usage_rate = AsyncMock(return_value=Decimal('0.5'))  # 50%使用
        
        limiter = BudgetLimiter(cost_tracker=cost_tracker)
        
        # Act
        is_allowed = await limiter.check_budget_available()
        
        # Assert
        assert is_allowed is True
        cost_tracker.is_budget_exceeded.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_deny_request_when_budget_exceeded(self):
        """予算超過時にリクエストが拒否されること"""
        # Arrange
        cost_tracker = MagicMock(spec=CostTracker)
        cost_tracker.is_budget_exceeded = AsyncMock(return_value=True)
        cost_tracker.get_budget_usage_rate = AsyncMock(return_value=Decimal('1.05'))  # 105%使用
        
        limiter = BudgetLimiter(cost_tracker=cost_tracker)
        
        # Act
        is_allowed = await limiter.check_budget_available()
        
        # Assert
        assert is_allowed is False
        cost_tracker.is_budget_exceeded.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_boundary_case_exactly_100_percent(self):
        """ちょうど100%使用時の境界値動作"""
        # Arrange
        cost_tracker = MagicMock(spec=CostTracker)
        cost_tracker.is_budget_exceeded = AsyncMock(return_value=False)  # まだ超過していない
        cost_tracker.get_budget_usage_rate = AsyncMock(return_value=Decimal('1.00'))  # ちょうど100%
        
        limiter = BudgetLimiter(cost_tracker=cost_tracker, strict_at_limit=True)
        
        # Act
        is_allowed = await limiter.check_budget_available()
        
        # Assert
        assert is_allowed is False  # strict_at_limit=Trueの場合、100%で停止
    
    @pytest.mark.asyncio
    async def test_default_behavior_without_budget(self):
        """予算未設定時のデフォルト動作"""
        # Arrange
        limiter = BudgetLimiter(cost_tracker=None, default_allow=True)
        
        # Act
        is_allowed = await limiter.check_budget_available()
        
        # Assert
        assert is_allowed is True  # デフォルトで許可
    
    @pytest.mark.asyncio
    async def test_handle_invalid_budget_value(self):
        """無効な予算値のハンドリング"""
        # Arrange
        cost_tracker = MagicMock(spec=CostTracker)
        cost_tracker.daily_budget = Decimal('-100.00')  # 負の値
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid budget value"):
            BudgetLimiter(cost_tracker=cost_tracker)


class TestAlertNotifications:
    """アラート通知機能のテスト"""
    
    @pytest.mark.asyncio
    async def test_warning_at_80_percent_usage(self):
        """80%使用時に警告が発生すること"""
        # Arrange
        cost_tracker = MagicMock(spec=CostTracker)
        cost_tracker.get_budget_usage_rate = AsyncMock(return_value=Decimal('0.80'))
        
        limiter = BudgetLimiter(cost_tracker=cost_tracker)
        
        # Act
        alerts = await limiter.check_and_generate_alerts()
        
        # Assert
        assert len(alerts) == 1
        assert alerts[0]['level'] == AlertLevel.WARNING_80
        assert alerts[0]['usage_percentage'] == 80.0
    
    @pytest.mark.asyncio
    async def test_warning_at_90_percent_usage(self):
        """90%使用時に警告が発生すること"""
        # Arrange
        cost_tracker = MagicMock(spec=CostTracker)
        cost_tracker.get_budget_usage_rate = AsyncMock(return_value=Decimal('0.90'))
        
        limiter = BudgetLimiter(cost_tracker=cost_tracker)
        
        # Act
        alerts = await limiter.check_and_generate_alerts()
        
        # Assert
        assert len(alerts) == 1
        assert alerts[0]['level'] == AlertLevel.WARNING_90
        assert alerts[0]['usage_percentage'] == 90.0
    
    @pytest.mark.asyncio
    async def test_critical_alert_at_100_percent(self):
        """100%超過時に停止通知が発生すること"""
        # Arrange
        cost_tracker = MagicMock(spec=CostTracker)
        cost_tracker.get_budget_usage_rate = AsyncMock(return_value=Decimal('1.01'))
        cost_tracker.is_budget_exceeded = AsyncMock(return_value=True)
        
        limiter = BudgetLimiter(cost_tracker=cost_tracker)
        
        # Act
        alerts = await limiter.check_and_generate_alerts()
        
        # Assert
        assert any(alert['level'] == AlertLevel.CRITICAL_100 for alert in alerts)
    
    @pytest.mark.asyncio
    async def test_alert_logging_output(self):
        """アラートがログに出力されること"""
        # Arrange
        cost_tracker = MagicMock(spec=CostTracker)
        cost_tracker.get_budget_usage_rate = AsyncMock(return_value=Decimal('0.85'))
        
        limiter = BudgetLimiter(cost_tracker=cost_tracker)
        
        # Act & Assert
        with patch('src.ai.middleware.budget_limiter.logger') as mock_logger:
            await limiter.send_alert(AlertLevel.WARNING_80, {"usage": 85})
            mock_logger.warning.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_alert_in_response_header(self):
        """アラートがレスポンスヘッダーに含まれること"""
        # Arrange
        cost_tracker = MagicMock(spec=CostTracker)
        cost_tracker.get_budget_usage_rate = AsyncMock(return_value=Decimal('0.82'))
        
        limiter = BudgetLimiter(cost_tracker=cost_tracker)
        response = Response()
        
        # Act
        await limiter.add_budget_headers(response)
        
        # Assert
        assert 'X-Budget-Warning' in response.headers
        assert 'X-Budget-Usage' in response.headers
        assert response.headers['X-Budget-Usage'] == '82%'


class TestManagementAPI:
    """管理API機能のテスト"""
    
    @pytest.mark.asyncio
    async def test_get_budget_status_api(self):
        """予算使用状況取得APIのテスト"""
        # Arrange
        cost_tracker = MagicMock(spec=CostTracker)
        cost_tracker.daily_budget = Decimal('50.00')
        cost_tracker.get_daily_cost = AsyncMock(return_value=Decimal('25.50'))
        cost_tracker.get_budget_usage_rate = AsyncMock(return_value=Decimal('0.51'))
        cost_tracker.is_budget_exceeded = AsyncMock(return_value=False)
        
        limiter = BudgetLimiter(cost_tracker=cost_tracker)
        
        # Act
        status = await limiter.get_budget_status()
        
        # Assert
        assert status['daily_limit'] == '50.00'
        assert status['current_usage'] == '25.50'
        assert status['usage_percentage'] == 51.0
        assert status['remaining'] == '24.50'
        assert status['is_exceeded'] is False
    
    @pytest.mark.asyncio
    async def test_update_budget_limit_api(self):
        """予算上限変更APIのテスト"""
        # Arrange
        cost_tracker = MagicMock(spec=CostTracker)
        limiter = BudgetLimiter(cost_tracker=cost_tracker)
        
        # Act
        result = await limiter.update_budget_limit(
            new_limit=Decimal('75.00'),
            effective_from='immediate',
            reason='Increased demand'
        )
        
        # Assert
        assert result['success'] is True
        assert result['new_limit'] == '75.00'
        assert cost_tracker.daily_budget == Decimal('75.00')
    
    @pytest.mark.asyncio
    async def test_manual_override_api(self):
        """手動オーバーライドAPIのテスト"""
        # Arrange
        cost_tracker = MagicMock(spec=CostTracker)
        limiter = BudgetLimiter(cost_tracker=cost_tracker)
        
        # Act
        result = await limiter.manual_override(
            action='resume',
            duration_minutes=60,
            admin_key='secret-override-key'
        )
        
        # Assert
        assert result['success'] is True
        assert result['override_active'] is True
        assert limiter.override_expiry > datetime.utcnow()
    
    @pytest.mark.asyncio
    async def test_get_cost_history_api(self):
        """コスト履歴取得APIのテスト"""
        # Arrange
        cost_tracker = MagicMock(spec=CostTracker)
        cost_tracker.get_cost_analysis = AsyncMock(return_value={
            'total_cost': Decimal('315.10'),
            'daily_average': Decimal('45.01'),
            'service_breakdown': {}
        })
        
        limiter = BudgetLimiter(cost_tracker=cost_tracker)
        
        # Act
        history = await limiter.get_cost_history(days=7)
        
        # Assert
        assert 'history' in history
        assert history['total_cost'] == '315.10'
        assert history['daily_average'] == '45.01'
    
    @pytest.mark.asyncio
    async def test_unauthorized_management_api_access(self):
        """認証なしでの管理API拒否のテスト"""
        # Arrange
        limiter = BudgetLimiter(cost_tracker=MagicMock())
        
        # Act & Assert
        with pytest.raises(PermissionError, match="Unauthorized"):
            await limiter.manual_override(
                action='resume',
                duration_minutes=60,
                admin_key='wrong-key'
            )


class TestMiddlewareIntegration:
    """FastAPIミドルウェア統合のテスト"""
    
    @pytest.mark.asyncio
    async def test_middleware_integration_with_fastapi(self):
        """FastAPIミドルウェアとしての動作テスト"""
        # Arrange
        app = FastAPI()
        cost_tracker = MagicMock(spec=CostTracker)
        cost_tracker.is_budget_exceeded = AsyncMock(return_value=False)
        
        limiter = BudgetLimiter(cost_tracker=cost_tracker)
        
        @app.middleware("http")
        async def budget_middleware(request: Request, call_next):
            return await limiter.process_request(request, call_next)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        # Act
        client = TestClient(app)
        response = client.get("/test")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": "success"}
    
    @pytest.mark.asyncio
    async def test_async_processing_performance(self):
        """非同期処理での正常動作テスト"""
        # Arrange
        cost_tracker = MagicMock(spec=CostTracker)
        cost_tracker.is_budget_exceeded = AsyncMock(return_value=False)
        
        limiter = BudgetLimiter(cost_tracker=cost_tracker)
        
        # Act - 複数の非同期チェックを並行実行
        tasks = [limiter.check_budget_available() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # Assert
        assert all(results)  # すべてTrue
        assert cost_tracker.is_budget_exceeded.call_count == 10
    
    @pytest.mark.asyncio
    async def test_error_fallback_behavior(self):
        """エラー時のフォールバック動作テスト"""
        # Arrange
        cost_tracker = MagicMock(spec=CostTracker)
        cost_tracker.is_budget_exceeded = AsyncMock(side_effect=Exception("DB Error"))
        
        limiter = BudgetLimiter(
            cost_tracker=cost_tracker,
            fallback_on_error='allow'  # エラー時は許可
        )
        
        # Act
        is_allowed = await limiter.check_budget_available()
        
        # Assert
        assert is_allowed is True  # フォールバックで許可


class TestEdgeCases:
    """エッジケースのテスト"""
    
    @pytest.mark.asyncio
    async def test_concurrent_request_accuracy(self):
        """並行リクエスト時の正確な計算テスト"""
        # Arrange
        cost_tracker = MagicMock(spec=CostTracker)
        call_count = 0
        
        async def mock_usage():
            nonlocal call_count
            call_count += 1
            # 呼び出しごとに使用率を増やす
            return Decimal(str(0.7 + call_count * 0.05))
        
        cost_tracker.get_budget_usage_rate = AsyncMock(side_effect=mock_usage)
        limiter = BudgetLimiter(cost_tracker=cost_tracker)
        
        # Act - 10個の並行リクエスト
        tasks = [limiter.get_current_usage() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # Assert
        assert len(results) == 10
        assert all(isinstance(r, Decimal) for r in results)
        # 使用率が順次増加していることを確認
        for i in range(1, len(results)):
            assert results[i] >= results[i-1]
    
    @pytest.mark.asyncio
    async def test_state_restoration_after_restart(self):
        """システム再起動後の状態復元テスト"""
        # Arrange
        # 保存された状態をシミュレート
        saved_state = {
            'daily_limit': '50.00',
            'override_active': True,
            'override_expiry': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'alert_thresholds': [80, 90, 100]
        }
        
        # Act
        limiter = BudgetLimiter.from_saved_state(saved_state)
        
        # Assert
        assert limiter.daily_limit == Decimal('50.00')
        assert limiter.override_active is True
        assert limiter.override_expiry > datetime.utcnow()
        assert limiter.alert_thresholds == [80, 90, 100]


# Test count verification
def test_count_verification():
    """テスト数の確認（20個）"""
    test_classes = [
        TestBudgetLimiterBasic,
        TestAlertNotifications, 
        TestManagementAPI,
        TestMiddlewareIntegration,
        TestEdgeCases
    ]
    
    total_tests = 0
    for test_class in test_classes:
        # Count methods that start with 'test_'
        test_methods = [m for m in dir(test_class) if m.startswith('test_')]
        total_tests += len(test_methods)
    
    print(f"Total test count: {total_tests}")
    assert total_tests == 20, f"Expected 20 tests, but found {total_tests}"


if __name__ == "__main__":
    # REDフェーズ - すべてのテストが失敗することを確認
    pytest.main([__file__, "-v", "--tb=short"])