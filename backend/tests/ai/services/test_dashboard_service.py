"""
Test suite for Dashboard Service (T6-016)
TDD RED Phase - Creating comprehensive failing tests first
"""

import pytest
import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any

# Import the modules to be implemented (will fail initially)
from src.ai.services.dashboard_service import (
    DashboardService,
    DashboardSummary,
    ChartDataCollection,
    DashboardReport,
    ChartDataPoint,
    ReportSection,
    DashboardError
)


class TestDashboardServiceBasic:
    """基本的なダッシュボードサービス機能のテスト"""
    
    @pytest.mark.asyncio
    async def test_dashboard_service_initialization(self):
        """DashboardServiceの初期化テスト"""
        # Arrange
        mock_cost_tracker = MagicMock()
        mock_metrics_service = MagicMock()
        
        # Act
        dashboard = DashboardService(
            cost_tracker=mock_cost_tracker,
            metrics_service=mock_metrics_service
        )
        
        # Assert
        assert dashboard.cost_tracker == mock_cost_tracker
        assert dashboard.metrics_service == mock_metrics_service
        assert dashboard is not None
    
    @pytest.mark.asyncio
    async def test_get_summary_stats_basic(self):
        """基本的なサマリー統計取得テスト"""
        # Arrange
        mock_cost_tracker = MagicMock()
        mock_metrics_service = MagicMock()
        dashboard = DashboardService(mock_cost_tracker, mock_metrics_service)
        
        # Mock data setup
        mock_cost_tracker.get_total_cost = AsyncMock(return_value=Decimal("25.50"))
        mock_cost_tracker.get_remaining_budget = AsyncMock(return_value=Decimal("74.50"))
        mock_metrics_service.get_success_rate = AsyncMock(return_value=0.94)
        mock_metrics_service.get_total_generations = AsyncMock(return_value=150)
        
        # Act
        summary = await dashboard.get_summary_stats()
        
        # Assert
        assert isinstance(summary, DashboardSummary)
        assert summary.total_cost == Decimal("25.50")
        assert summary.remaining_budget == Decimal("74.50")
        assert summary.success_rate == 0.94
        assert summary.total_generations == 150
    
    @pytest.mark.asyncio
    async def test_dashboard_summary_model(self):
        """DashboardSummaryモデルの構造テスト"""
        # Arrange & Act
        summary = DashboardSummary(
            total_cost=Decimal("10.00"),
            remaining_budget=Decimal("90.00"),
            success_rate=0.95,
            total_generations=100,
            avg_generation_time=12.5,
            last_24h_generations=25,
            current_alerts=[]
        )
        
        # Assert
        assert summary.total_cost == Decimal("10.00")
        assert summary.remaining_budget == Decimal("90.00")
        assert summary.success_rate == 0.95
        assert summary.budget_utilization_percent == 10.0  # calculated property


class TestChartDataGeneration:
    """チャートデータ生成機能のテスト"""
    
    @pytest.mark.asyncio
    async def test_get_chart_data_usage_trend(self):
        """使用量推移チャートデータ取得テスト"""
        # Arrange
        mock_cost_tracker = MagicMock()
        mock_metrics_service = MagicMock()
        dashboard = DashboardService(mock_cost_tracker, mock_metrics_service)
        
        # Mock aggregated data
        mock_chart_data = [
            {"hour": "2025-09-26T10:00:00", "generations": 10, "success_rate": 0.9},
            {"hour": "2025-09-26T11:00:00", "generations": 15, "success_rate": 0.95},
            {"hour": "2025-09-26T12:00:00", "generations": 8, "success_rate": 0.85},
        ]
        mock_metrics_service.get_hourly_aggregated_data = AsyncMock(return_value=mock_chart_data)
        
        # Act
        chart_data = await dashboard.get_chart_data(chart_type="usage", period="24h")
        
        # Assert
        assert isinstance(chart_data, ChartDataCollection)
        assert chart_data.chart_type == "usage"
        assert chart_data.period == "24h"
        assert len(chart_data.data_points) == 3
        assert chart_data.data_points[0].timestamp == "2025-09-26T10:00:00"
        assert chart_data.data_points[0].value == 10
    
    @pytest.mark.asyncio
    async def test_get_chart_data_cost_trend(self):
        """コスト推移チャートデータ取得テスト"""
        # Arrange
        mock_cost_tracker = MagicMock()
        mock_metrics_service = MagicMock()
        dashboard = DashboardService(mock_cost_tracker, mock_metrics_service)
        
        # Mock cost data
        mock_cost_data = [
            {"date": "2025-09-24", "daily_cost": Decimal("8.50")},
            {"date": "2025-09-25", "daily_cost": Decimal("12.75")},
            {"date": "2025-09-26", "daily_cost": Decimal("4.25")},
        ]
        mock_cost_tracker.get_daily_cost_breakdown = AsyncMock(return_value=mock_cost_data)
        
        # Act
        chart_data = await dashboard.get_chart_data(chart_type="costs", period="7d")
        
        # Assert
        assert isinstance(chart_data, ChartDataCollection)
        assert chart_data.chart_type == "costs"
        assert len(chart_data.data_points) == 3
        assert chart_data.data_points[1].value == 12.75
    
    @pytest.mark.asyncio
    async def test_chart_data_point_model(self):
        """ChartDataPointモデルの構造テスト"""
        # Arrange & Act
        data_point = ChartDataPoint(
            timestamp="2025-09-26T12:00:00",
            value=25.5,
            metadata={"success_count": 23, "fail_count": 2}
        )
        
        # Assert
        assert data_point.timestamp == "2025-09-26T12:00:00"
        assert data_point.value == 25.5
        assert data_point.metadata["success_count"] == 23


class TestReportGeneration:
    """レポート生成機能のテスト"""
    
    @pytest.mark.asyncio
    async def test_generate_daily_report(self):
        """日次レポート生成テスト"""
        # Arrange
        mock_cost_tracker = MagicMock()
        mock_metrics_service = MagicMock()
        dashboard = DashboardService(mock_cost_tracker, mock_metrics_service)
        
        # Mock report data
        target_date = datetime(2025, 9, 26)
        mock_cost_tracker.get_daily_summary = AsyncMock(return_value={
            "total_cost": Decimal("15.50"),
            "generation_count": 45,
            "avg_cost_per_generation": Decimal("0.344")
        })
        mock_metrics_service.get_daily_metrics = AsyncMock(return_value={
            "success_rate": 0.91,
            "avg_duration": 11.2,
            "error_breakdown": {"timeout": 2, "api_error": 1}
        })
        
        # Act
        report = await dashboard.generate_report(
            report_type="daily",
            date=target_date
        )
        
        # Assert
        assert isinstance(report, DashboardReport)
        assert report.report_type == "daily"
        assert report.generated_at is not None
        assert len(report.sections) >= 2  # Cost section + Metrics section
        
        # Check report sections
        cost_section = next((s for s in report.sections if s.title == "Cost Summary"), None)
        assert cost_section is not None
        assert cost_section.data["total_cost"] == Decimal("15.50")
    
    @pytest.mark.asyncio
    async def test_export_report_to_csv(self):
        """レポートCSV出力テスト"""
        # Arrange
        mock_cost_tracker = MagicMock()
        mock_metrics_service = MagicMock()
        dashboard = DashboardService(mock_cost_tracker, mock_metrics_service)
        
        # Create sample report
        report = DashboardReport(
            report_type="daily",
            generated_at=datetime.utcnow(),
            sections=[
                ReportSection(
                    title="Test Section",
                    data={"metric1": 100, "metric2": 200}
                )
            ]
        )
        
        # Act
        csv_content = await dashboard.export_report_to_csv(report)
        
        # Assert
        assert isinstance(csv_content, str)
        assert "Test Section" in csv_content
        assert "metric1,100" in csv_content
        assert "metric2,200" in csv_content
    
    @pytest.mark.asyncio
    async def test_report_section_model(self):
        """ReportSectionモデルの構造テスト"""
        # Arrange & Act
        section = ReportSection(
            title="Performance Metrics",
            data={
                "avg_response_time": 12.5,
                "peak_usage_hour": "14:00",
                "total_requests": 150
            },
            chart_data=[
                {"time": "10:00", "requests": 10},
                {"time": "11:00", "requests": 15}
            ]
        )
        
        # Assert
        assert section.title == "Performance Metrics"
        assert section.data["avg_response_time"] == 12.5
        assert len(section.chart_data) == 2


class TestDashboardAPI:
    """ダッシュボードAPIエンドポイントのテスト"""
    
    @pytest.mark.asyncio
    async def test_dashboard_summary_endpoint(self):
        """ダッシュボードサマリーAPI取得テスト"""
        # Arrange
        from fastapi.testclient import TestClient
        from src.main import app
        
        client = TestClient(app)
        
        # Act
        response = client.get("/api/admin/dashboard/summary")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "total_cost" in data
        assert "remaining_budget" in data
        assert "success_rate" in data
        assert "total_generations" in data
        assert "last_24h_generations" in data
    
    @pytest.mark.asyncio
    async def test_chart_data_endpoint(self):
        """チャートデータAPI取得テスト"""
        # Arrange
        from fastapi.testclient import TestClient
        from src.main import app
        
        client = TestClient(app)
        
        # Act
        response = client.get(
            "/api/admin/dashboard/charts/usage",
            params={"period": "24h"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "chart_type" in data
        assert "period" in data
        assert "data_points" in data
        assert data["chart_type"] == "usage"
        assert isinstance(data["data_points"], list)
    
    @pytest.mark.asyncio
    async def test_report_export_endpoint(self):
        """レポートエクスポートAPI取得テスト"""
        # Arrange
        from fastapi.testclient import TestClient
        from src.main import app
        
        client = TestClient(app)
        
        # Act
        response = client.get(
            "/api/admin/dashboard/reports/export",
            params={"report_type": "daily", "format": "csv", "date": "2025-09-26"}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv"
        assert "content-disposition" in response.headers
        assert "attachment" in response.headers["content-disposition"]
    
    @pytest.mark.asyncio
    async def test_admin_authentication_placeholder(self):
        """管理者認証プレースホルダーテスト"""
        # Arrange
        from src.api.dependencies.auth import verify_admin_access
        
        # Act & Assert - should not raise exception with valid placeholder key
        result = await verify_admin_access(api_key="admin-test-key")
        assert result is not None
        
        # Act & Assert - should raise exception with invalid key
        with pytest.raises(Exception):  # Specific exception type TBD
            await verify_admin_access(api_key="invalid-key")


class TestDashboardIntegration:
    """既存システムとのダッシュボード統合テスト"""
    
    @pytest.mark.asyncio
    async def test_cost_tracker_integration(self):
        """CostTrackerとのダッシュボード統合"""
        # Arrange
        with patch('src.ai.services.cost_tracker.CostTracker') as MockCostTracker:
            mock_tracker = MockCostTracker.return_value
            mock_tracker.get_total_cost = AsyncMock(return_value=Decimal("50.75"))
            mock_tracker.get_remaining_budget = AsyncMock(return_value=Decimal("49.25"))
            
            mock_metrics = MagicMock()
            mock_metrics.get_success_rate = AsyncMock(return_value=0.95)
            mock_metrics.get_total_generations = AsyncMock(return_value=100)
            
            dashboard = DashboardService(mock_tracker, mock_metrics)
            
            # Act
            summary = await dashboard.get_summary_stats()
            
            # Assert
            assert summary.total_cost == Decimal("50.75")
            assert summary.remaining_budget == Decimal("49.25")
            mock_tracker.get_total_cost.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_metrics_collector_integration(self):
        """MetricsCollectorとのダッシュボード統合"""
        # Arrange
        with patch('src.ai.monitoring.metrics_collector.MetricsService') as MockMetrics:
            mock_metrics = MockMetrics.return_value
            mock_metrics.get_success_rate = AsyncMock(return_value=0.87)
            mock_metrics.get_total_generations = AsyncMock(return_value=200)
            mock_metrics.get_avg_generation_time = AsyncMock(return_value=12.5)
            mock_metrics.get_last_24h_generations = AsyncMock(return_value=25)
            
            mock_tracker = MagicMock()
            mock_tracker.get_total_cost = AsyncMock(return_value=Decimal("25.50"))
            mock_tracker.get_remaining_budget = AsyncMock(return_value=Decimal("74.50"))
            
            dashboard = DashboardService(mock_tracker, mock_metrics)
            
            # Act
            summary = await dashboard.get_summary_stats()
            
            # Assert
            assert summary.success_rate == 0.87
            assert summary.total_generations == 200
            mock_metrics.get_success_rate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_budget_limiter_alert_integration(self):
        """BudgetLimiterアラート統合テスト"""
        # Arrange
        with patch('src.ai.middleware.budget_limiter.BudgetLimiter') as MockLimiter:
            mock_limiter = MockLimiter.return_value
            mock_limiter.get_current_alerts = AsyncMock(return_value=[
                {"type": "budget_warning", "message": "Budget 80% exceeded"},
                {"type": "rate_limit", "message": "High request rate detected"}
            ])
            
            mock_tracker = MagicMock()
            mock_tracker.get_total_cost = AsyncMock(return_value=Decimal("25.50"))
            mock_tracker.get_remaining_budget = AsyncMock(return_value=Decimal("74.50"))
            
            mock_metrics = MagicMock()
            mock_metrics.get_success_rate = AsyncMock(return_value=0.91)
            mock_metrics.get_total_generations = AsyncMock(return_value=150)
            mock_metrics.get_avg_generation_time = AsyncMock(return_value=12.5)
            mock_metrics.get_last_24h_generations = AsyncMock(return_value=25)
            
            dashboard = DashboardService(mock_tracker, mock_metrics)
            dashboard.budget_limiter = mock_limiter
            
            # Act
            summary = await dashboard.get_summary_stats()
            
            # Assert
            assert len(summary.current_alerts) == 2
            assert summary.current_alerts[0]["type"] == "budget_warning"


class TestDashboardErrorHandling:
    """ダッシュボードエラーハンドリングのテスト"""
    
    @pytest.mark.asyncio
    async def test_cost_tracker_failure_handling(self):
        """CostTracker障害時のグレースフル処理"""
        # Arrange
        mock_cost_tracker = MagicMock()
        mock_cost_tracker.get_total_cost = AsyncMock(side_effect=Exception("Database error"))
        mock_metrics = MagicMock()
        mock_metrics.get_success_rate = AsyncMock(return_value=0.94)
        mock_metrics.get_total_generations = AsyncMock(return_value=150)
        
        dashboard = DashboardService(mock_cost_tracker, mock_metrics)
        
        # Act & Assert
        with pytest.raises(DashboardError) as exc_info:
            await dashboard.get_summary_stats()
        
        assert "Cost data unavailable" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_metrics_service_timeout_handling(self):
        """MetricsService タイムアウト時の処理"""
        # Arrange
        mock_metrics = MagicMock()
        mock_metrics.get_success_rate = AsyncMock(side_effect=asyncio.TimeoutError())
        mock_metrics.get_total_generations = AsyncMock(return_value=150)
        mock_metrics.get_avg_generation_time = AsyncMock(return_value=12.5)
        mock_metrics.get_last_24h_generations = AsyncMock(return_value=25)
        
        mock_tracker = MagicMock()
        mock_tracker.get_total_cost = AsyncMock(return_value=Decimal("25.50"))
        mock_tracker.get_remaining_budget = AsyncMock(return_value=Decimal("74.50"))
        
        dashboard = DashboardService(mock_tracker, mock_metrics)
        
        # Act & Assert
        with pytest.raises(DashboardError) as exc_info:
            await dashboard.get_summary_stats()
        
        assert "Metrics timeout" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_service_unavailable_handling(self):
        """サービス利用不可時のハンドリング"""
        # Arrange
        mock_cost_tracker = MagicMock()
        mock_cost_tracker.get_total_cost = MagicMock()  # Not async mock
        mock_metrics = MagicMock()
        
        dashboard = DashboardService(mock_cost_tracker, mock_metrics)
        
        # Act & Assert
        with pytest.raises(DashboardError) as exc_info:
            await dashboard.get_summary_stats()
        
        assert "Service unavailable" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """段階的劣化処理テスト"""
        # Arrange
        mock_cost_tracker = MagicMock()
        mock_cost_tracker.get_total_cost = AsyncMock(return_value=Decimal("10.00"))
        mock_cost_tracker.get_remaining_budget = AsyncMock(return_value=Decimal("90.00"))
        mock_metrics = MagicMock()
        mock_metrics.get_success_rate = AsyncMock(return_value=0.95)
        mock_metrics.get_total_generations = AsyncMock(return_value=100)
        
        dashboard = DashboardService(mock_cost_tracker, mock_metrics)
        
        # Act
        summary = await dashboard.get_summary_stats()
        
        # Assert
        assert summary.total_cost == Decimal("10.00")
        assert summary.success_rate == 0.95
        assert summary.budget_utilization_percent == 10.0


# Test count verification
def test_count_verification():
    """テスト数の確認（20個）"""
    test_classes = [
        TestDashboardServiceBasic,
        TestChartDataGeneration,
        TestReportGeneration,
        TestDashboardAPI,
        TestDashboardIntegration,
        TestDashboardErrorHandling
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