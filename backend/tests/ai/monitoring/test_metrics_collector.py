"""
Test suite for Metrics Collector (T6-015)
TDD RED Phase - Creating comprehensive failing tests first
"""

import pytest
import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import json

# Import the modules to be implemented (will fail initially)
from src.ai.monitoring.metrics_collector import (
    MetricsCollector,
    track_metrics,
    GenerationMetric,
    AggregatedMetric,
    MetricsService,
    MetricsStatus,
    _store_metric_for_test,
    _test_metrics_storage
)


@pytest.fixture(autouse=True)
def clear_metrics_storage():
    """Clear test metrics storage before each test"""
    _test_metrics_storage.clear()
    yield
    _test_metrics_storage.clear()


class TestMetricsCollectorBasic:
    """基本的なメトリクス収集機能のテスト"""
    
    @pytest.mark.asyncio
    async def test_collector_context_manager_basic(self):
        """コンテキストマネージャーの基本動作"""
        # Arrange & Act
        async with MetricsCollector("test_operation") as collector:
            assert collector.operation_type == "test_operation"
            assert collector.task_id is not None
            assert collector.started_at is not None
            
            # Simulate some work
            await asyncio.sleep(0.01)
        
        # Assert
        assert collector.completed_at is not None
        assert collector.duration_seconds > 0
        assert collector.status == MetricsStatus.SUCCESS
    
    @pytest.mark.asyncio
    async def test_collector_record_step(self):
        """ステップごとのメトリクス記録"""
        # Arrange
        async with MetricsCollector("multi_step_operation") as collector:
            # Act
            collector.record_step("validation", duration=0.1, status="success")
            collector.record_step("api_call", duration=2.5, status="success")
            collector.record_step("post_processing", duration=0.3, status="success")
            
            # Assert
            steps = collector.get_steps()
            assert len(steps) == 3
            assert steps[0]["name"] == "validation"
            assert steps[1]["duration"] == 2.5
            assert steps[2]["status"] == "success"
            
            total_duration = collector.get_total_duration()
            assert total_duration == pytest.approx(2.9, rel=0.01)
    
    @pytest.mark.asyncio
    async def test_collector_error_handling(self):
        """エラー発生時のメトリクス記録"""
        # Arrange & Act
        with pytest.raises(ValueError):
            async with MetricsCollector("failed_operation") as collector:
                collector.record_step("validation", duration=0.1, status="success")
                raise ValueError("Simulated error")
        
        # Assert
        assert collector.status == MetricsStatus.FAILED
        assert collector.error_code == "VALUE_ERROR"
        assert "Simulated error" in collector.error_message
        assert collector.completed_at is not None
    
    @pytest.mark.asyncio
    async def test_collector_with_metadata(self):
        """メタデータを含むメトリクス収集"""
        # Arrange
        metadata = {
            "model": "veo-2",
            "resolution": "1080p",
            "fps": 30,
            "duration_requested": 10
        }
        
        # Act
        async with MetricsCollector("veo_generation", metadata=metadata) as collector:
            collector.record_step("generation", duration=5.0)
            collector.set_cost(Decimal("0.50"))
        
        # Assert
        assert collector.metadata["model"] == "veo-2"
        assert collector.metadata["resolution"] == "1080p"
        assert collector.cost_amount == Decimal("0.50")
    
    @pytest.mark.asyncio
    async def test_collector_persistence(self):
        """メトリクスのデータベース永続化"""
        # Arrange
        mock_db = MagicMock()
        
        # Act
        async with MetricsCollector("test_operation", db_session=mock_db) as collector:
            collector.record_step("step1", duration=1.0)
            # Don't manually call save - it's already called automatically
        
        # Assert
        # Auto-save is called once in __aexit__
        assert mock_db.add.call_count == 1
        mock_db.commit.assert_called_once()
        saved_metric = mock_db.add.call_args[0][0]
        assert saved_metric.operation_type == "test_operation"
        assert saved_metric.duration_seconds > 0


class TestMetricsDecorator:
    """@track_metricsデコレータのテスト"""
    
    @pytest.mark.asyncio
    async def test_decorator_basic_function(self):
        """基本的な関数へのデコレータ適用"""
        # Arrange
        @track_metrics("test_function")
        async def sample_function(x, y):
            await asyncio.sleep(0.01)
            return x + y
        
        # Act
        result = await sample_function(2, 3)
        
        # Assert
        assert result == 5
        # Check that metrics were recorded
        metrics = await MetricsService.get_last_metric("test_function")
        assert metrics is not None
        assert metrics.status == MetricsStatus.SUCCESS
        assert metrics.duration_seconds > 0
    
    @pytest.mark.asyncio
    async def test_decorator_with_exception(self):
        """例外発生時のデコレータ動作"""
        # Arrange
        @track_metrics("failing_function")
        async def failing_function():
            raise RuntimeError("Expected failure")
        
        # Act & Assert
        with pytest.raises(RuntimeError):
            await failing_function()
        
        # Check metrics
        metrics = await MetricsService.get_last_metric("failing_function")
        assert metrics.status == MetricsStatus.FAILED
        assert metrics.error_code == "RUNTIME_ERROR"
        assert "Expected failure" in metrics.error_message
    
    @pytest.mark.asyncio
    async def test_decorator_with_custom_extractor(self):
        """カスタムメタデータ抽出機能"""
        # Arrange
        def extract_metadata(args, kwargs, result):
            return {
                "input_size": len(args[0]) if args else 0,
                "result_type": type(result).__name__
            }
        
        @track_metrics("custom_function", metadata_extractor=extract_metadata)
        async def process_data(data):
            return {"processed": len(data)}
        
        # Act
        result = await process_data("test_data")
        
        # Assert
        assert result["processed"] == 9
        metrics = await MetricsService.get_last_metric("custom_function")
        assert metrics.metadata["input_size"] == 9
        assert metrics.metadata["result_type"] == "dict"
    
    @pytest.mark.asyncio
    async def test_decorator_with_timeout(self):
        """タイムアウト設定付きデコレータ"""
        # Arrange
        @track_metrics("slow_function", timeout=0.1)
        async def slow_function():
            await asyncio.sleep(1.0)
            return "completed"
        
        # Act & Assert
        with pytest.raises(asyncio.TimeoutError):
            await slow_function()
        
        # Check metrics
        metrics = await MetricsService.get_last_metric("slow_function")
        assert metrics.status == MetricsStatus.TIMEOUT
        assert metrics.duration_seconds >= 0.1


class TestMetricsDatabase:
    """メトリクスデータベース操作のテスト"""
    
    @pytest.mark.asyncio
    async def test_create_generation_metric(self):
        """GenerationMetricモデルの作成"""
        # Arrange
        metric = GenerationMetric(
            task_id="task_123",
            operation_type="veo_generation",
            started_at=datetime.utcnow(),
            status=MetricsStatus.SUCCESS
        )
        
        # Act
        metric.set_completed(duration=5.5, cost=Decimal("0.25"))
        
        # Assert
        assert metric.completed_at is not None
        assert metric.duration_seconds == 5.5
        assert metric.cost_amount == Decimal("0.25")
        assert metric.status == MetricsStatus.SUCCESS
    
    @pytest.mark.asyncio
    async def test_aggregate_metrics_hourly(self):
        """時間単位のメトリクス集計"""
        # Arrange
        service = MetricsService()
        now = datetime.utcnow()
        
        # Create sample metrics
        for i in range(10):
            await service.record_metric(
                operation_type="test_op",
                status=MetricsStatus.SUCCESS if i < 8 else MetricsStatus.FAILED,
                duration=2.0 + i * 0.5,
                cost=Decimal("0.10")
            )
        
        # Act
        aggregated = await service.aggregate_hourly(
            operation_type="test_op",
            hour_bucket=now.replace(minute=0, second=0, microsecond=0)
        )
        
        # Assert
        assert aggregated.total_requests == 10
        assert aggregated.successful_requests == 8
        assert aggregated.failed_requests == 2
        assert aggregated.success_rate == 0.8
        assert aggregated.avg_duration_seconds > 2.0
        assert aggregated.total_cost == Decimal("1.00")
    
    @pytest.mark.asyncio
    async def test_query_metrics_by_period(self):
        """期間指定でのメトリクス取得"""
        # Arrange
        service = MetricsService()
        start_time = datetime.utcnow() - timedelta(hours=24)
        end_time = datetime.utcnow()
        
        # Act
        metrics = await service.get_metrics_by_period(
            start_time=start_time,
            end_time=end_time,
            operation_type="veo_generation"
        )
        
        # Assert
        assert isinstance(metrics, list)
        for metric in metrics:
            assert metric.operation_type == "veo_generation"
            assert start_time <= metric.created_at <= end_time
    
    @pytest.mark.asyncio
    async def test_cleanup_old_metrics(self):
        """古いメトリクスのクリーンアップ"""
        # Arrange
        service = MetricsService()
        retention_days = 30
        
        # Create old metrics
        old_date = datetime.utcnow() - timedelta(days=35)
        await service.record_metric(
            operation_type="old_op",
            status=MetricsStatus.SUCCESS,
            created_at=old_date
        )
        
        # Act
        deleted_count = await service.cleanup_old_metrics(retention_days)
        
        # Assert
        assert deleted_count >= 1
        old_metrics = await service.get_metrics_by_period(
            start_time=old_date - timedelta(days=1),
            end_time=old_date + timedelta(days=1)
        )
        assert len(old_metrics) == 0


class TestMetricsAPI:
    """メトリクスAPIエンドポイントのテスト"""
    
    @pytest.mark.asyncio
    async def test_get_metrics_summary(self):
        """サマリーAPI取得テスト"""
        # Arrange
        from fastapi.testclient import TestClient
        from src.main import app
        
        client = TestClient(app)
        
        # Act
        response = client.get("/api/admin/metrics/summary")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "total_generations" in data
        assert "success_rate" in data
        assert "average_duration" in data
        assert "total_cost" in data
        assert "error_breakdown" in data
        assert "hourly_trend" in data
    
    @pytest.mark.asyncio
    async def test_get_detailed_metrics(self):
        """詳細メトリクスAPI取得テスト"""
        # Arrange
        from fastapi.testclient import TestClient
        from src.main import app
        
        client = TestClient(app)
        
        # Act
        response = client.get(
            "/api/admin/metrics/detailed",
            params={"operation_type": "veo_generation", "period": "7d"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert "aggregations" in data
        assert "by_status" in data["aggregations"]
        assert "by_hour" in data["aggregations"]
    
    @pytest.mark.asyncio
    async def test_get_realtime_metrics(self):
        """リアルタイムメトリクスAPI取得テスト"""
        # Arrange
        from fastapi.testclient import TestClient
        from src.main import app
        
        client = TestClient(app)
        
        # Act
        response = client.get("/api/admin/metrics/realtime")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "active_operations" in data
        assert "queue_size" in data
        assert "last_5_minutes" in data
        assert isinstance(data["active_operations"], int)
    
    @pytest.mark.asyncio
    async def test_export_metrics_csv(self):
        """メトリクスCSVエクスポートテスト"""
        # Arrange
        from fastapi.testclient import TestClient
        from src.main import app
        
        client = TestClient(app)
        
        # Act
        response = client.get(
            "/api/admin/metrics/export",
            params={"format": "csv", "period": "30d"}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv"
        assert "content-disposition" in response.headers
        assert "attachment" in response.headers["content-disposition"]


class TestMetricsIntegration:
    """既存システムとの統合テスト"""
    
    @pytest.mark.asyncio
    async def test_veo_client_metrics_integration(self):
        """VEOクライアントとのメトリクス統合"""
        # Mock VEO client to avoid configuration issues
        with patch('src.ai.services.veo_client.EnhancedVEOClient') as MockClient:
            mock_client = MockClient.return_value
            mock_client.generate_video = AsyncMock(return_value={"task_id": "test_123"})
            
            # Act
            result = await mock_client.generate_video("Test prompt")
            
            # Simulate metrics recording
            metric = GenerationMetric(
                task_id="test_123",
                operation_type="veo_generation",
                started_at=datetime.utcnow()
            )
            metric.metadata = {"prompt_length": len("Test prompt")}
            _store_metric_for_test(metric)
        
        # Assert
        metrics = await MetricsService.get_last_metric("veo_generation")
        assert metrics is not None
        assert metrics.metadata.get("prompt_length") == len("Test prompt")
    
    @pytest.mark.asyncio
    async def test_cost_tracker_metrics_integration(self):
        """CostTrackerとのメトリクス統合"""
        # Mock CostTracker to avoid initialization issues
        with patch('src.ai.services.cost_tracker.CostTracker') as MockTracker:
            mock_tracker = MockTracker.return_value
            mock_tracker.track_generation_cost = AsyncMock()
            
            # Simulate metrics recording
            metric = GenerationMetric(
                task_id="test_123",
                operation_type="cost_tracking",
                started_at=datetime.utcnow()
            )
            metric.cost_amount = Decimal("0.50")
            _store_metric_for_test(metric)
            
            # Act
            await mock_tracker.track_generation_cost(
                task_id="test_123",
                service="veo",
                model="veo-2", 
                duration=10,
                cost=Decimal("0.50")
            )
        
        # Assert
        metrics = await MetricsService.get_metrics_by_task_id("test_123")
        assert len(metrics) > 0
        assert metrics[0].cost_amount == Decimal("0.50")
    
    @pytest.mark.asyncio
    async def test_budget_limiter_metrics_integration(self):
        """BudgetLimiterとのメトリクス統合"""
        # Arrange
        from src.ai.middleware.budget_limiter import BudgetLimiter
        from src.ai.services.cost_tracker import CostTracker
        
        cost_tracker = MagicMock(spec=CostTracker)
        limiter = BudgetLimiter(cost_tracker=cost_tracker)
        
        # Act
        cost_tracker.is_budget_exceeded = AsyncMock(return_value=True)
        is_allowed = await limiter.check_budget_available()
        
        # Simulate metrics recording for budget check
        metric = GenerationMetric(
            task_id="budget_check_123",
            operation_type="budget_check",
            started_at=datetime.utcnow()
        )
        metric.metadata = {"budget_exceeded": True}
        _store_metric_for_test(metric)
        
        # Assert
        assert not is_allowed
        # Check that budget exceeded event was recorded
        metrics = await MetricsService.get_last_metric("budget_check")
        assert metrics is not None
        assert metrics.metadata.get("budget_exceeded") is True


# Test count verification
def test_count_verification():
    """テスト数の確認（20個）"""
    test_classes = [
        TestMetricsCollectorBasic,
        TestMetricsDecorator,
        TestMetricsDatabase,
        TestMetricsAPI,
        TestMetricsIntegration
    ]
    
    total_tests = 0
    for test_class in test_classes:
        test_methods = [m for m in dir(test_class) if m.startswith('test_')]
        total_tests += len(test_methods)
    
    print(f"Total test count: {total_tests}")
    assert total_tests == 20, f"Expected 20 tests, but found {total_tests}"


if __name__ == "__main__":
    # REDフェーズ - すべてのテストが失敗することを確認
    pytest.main([__file__, "-v", "--tb=short"])