"""
Unit tests for AI Analytics Service - T270 AI unit tests comprehensive coverage
Tests the analytics and reporting system for AI video generation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ai.services.analytics_service import (
    AnalyticsService,
    MetricType,
    ReportType,
    AggregationType,
    TimeRange,
    AnalyticsReport,
    MetricData,
    AlertThreshold
)


class TestAnalyticsService:
    """Test cases for AnalyticsService"""
    
    @pytest.fixture
    def analytics_service(self):
        """Create AnalyticsService instance for testing"""
        return AnalyticsService()
    
    @pytest.fixture
    def sample_metrics(self):
        """Sample metrics data for testing"""
        return [
            {
                "timestamp": datetime.now() - timedelta(hours=1),
                "metric_type": MetricType.GENERATION_COUNT,
                "value": 5,
                "metadata": {"quality": "high", "user_id": "user1"}
            },
            {
                "timestamp": datetime.now() - timedelta(hours=2), 
                "metric_type": MetricType.PROCESSING_TIME,
                "value": 45.3,
                "metadata": {"duration": 30, "resolution": "1080p"}
            },
            {
                "timestamp": datetime.now() - timedelta(hours=3),
                "metric_type": MetricType.API_COST,
                "value": 2.75,
                "metadata": {"api_provider": "VEO", "generation_id": "gen123"}
            }
        ]
    
    def test_service_initialization(self, analytics_service):
        """Test AnalyticsService initialization"""
        assert analytics_service is not None
        assert hasattr(analytics_service, 'metrics_store')
        assert hasattr(analytics_service, 'report_generator')
        assert hasattr(analytics_service, 'alert_manager')
        
    def test_metric_recording(self, analytics_service):
        """Test recording individual metrics"""
        metric_data = {
            "metric_type": MetricType.GENERATION_COUNT,
            "value": 10,
            "metadata": {"user_id": "test_user"}
        }
        
        result = analytics_service.record_metric(**metric_data)
        
        assert result["status"] == "success"
        assert "metric_id" in result
        
    def test_batch_metric_recording(self, analytics_service, sample_metrics):
        """Test recording multiple metrics in batch"""
        result = analytics_service.record_metrics_batch(sample_metrics)
        
        assert result["status"] == "success"
        assert result["recorded_count"] == len(sample_metrics)
        assert "failed_metrics" in result
        
    def test_metric_retrieval(self, analytics_service, sample_metrics):
        """Test retrieving metrics by various filters"""
        # Record sample metrics first
        analytics_service.record_metrics_batch(sample_metrics)
        
        # Test retrieval by metric type
        generation_metrics = analytics_service.get_metrics(
            metric_type=MetricType.GENERATION_COUNT
        )
        
        assert len(generation_metrics) >= 1
        assert all(m.metric_type == MetricType.GENERATION_COUNT for m in generation_metrics)
        
        # Test retrieval by time range
        recent_metrics = analytics_service.get_metrics(
            time_range=TimeRange.LAST_24_HOURS
        )
        
        assert len(recent_metrics) >= len(sample_metrics)
        
    def test_aggregation_calculations(self, analytics_service, sample_metrics):
        """Test metric aggregation calculations"""
        analytics_service.record_metrics_batch(sample_metrics)
        
        # Test sum aggregation
        total_cost = analytics_service.aggregate_metrics(
            metric_type=MetricType.API_COST,
            aggregation=AggregationType.SUM,
            time_range=TimeRange.LAST_24_HOURS
        )
        
        assert total_cost >= 2.75
        
        # Test average aggregation
        avg_processing_time = analytics_service.aggregate_metrics(
            metric_type=MetricType.PROCESSING_TIME,
            aggregation=AggregationType.AVERAGE,
            time_range=TimeRange.LAST_24_HOURS
        )
        
        assert avg_processing_time > 0
        
        # Test count aggregation
        generation_count = analytics_service.aggregate_metrics(
            metric_type=MetricType.GENERATION_COUNT,
            aggregation=AggregationType.COUNT,
            time_range=TimeRange.LAST_24_HOURS
        )
        
        assert generation_count >= 1
        
    def test_trend_analysis(self, analytics_service):
        """Test trend analysis functionality"""
        # Create trending data
        base_time = datetime.now()
        trending_metrics = [
            {
                "timestamp": base_time - timedelta(days=i),
                "metric_type": MetricType.GENERATION_COUNT,
                "value": 10 + i * 2,  # Increasing trend
                "metadata": {}
            }
            for i in range(7)
        ]
        
        analytics_service.record_metrics_batch(trending_metrics)
        
        trend = analytics_service.analyze_trend(
            metric_type=MetricType.GENERATION_COUNT,
            time_range=TimeRange.LAST_7_DAYS
        )
        
        assert "trend_direction" in trend
        assert "trend_strength" in trend
        assert "trend_confidence" in trend
        assert trend["trend_direction"] in ["increasing", "decreasing", "stable"]
        
    def test_performance_report_generation(self, analytics_service, sample_metrics):
        """Test performance report generation"""
        analytics_service.record_metrics_batch(sample_metrics)
        
        report = analytics_service.generate_report(
            report_type=ReportType.PERFORMANCE,
            time_range=TimeRange.LAST_24_HOURS
        )
        
        assert isinstance(report, AnalyticsReport)
        assert report.report_type == ReportType.PERFORMANCE
        assert "metrics_summary" in report.data
        assert "performance_indicators" in report.data
        
    def test_cost_analysis_report(self, analytics_service, sample_metrics):
        """Test cost analysis report generation"""
        analytics_service.record_metrics_batch(sample_metrics)
        
        report = analytics_service.generate_report(
            report_type=ReportType.COST_ANALYSIS,
            time_range=TimeRange.LAST_24_HOURS
        )
        
        assert report.report_type == ReportType.COST_ANALYSIS
        assert "total_cost" in report.data
        assert "cost_breakdown" in report.data
        assert "cost_trends" in report.data
        
    def test_usage_patterns_analysis(self, analytics_service):
        """Test usage patterns analysis"""
        # Create usage pattern data
        usage_data = []
        for hour in range(24):
            for _ in range(hour % 6 + 1):  # Variable usage by hour
                usage_data.append({
                    "timestamp": datetime.now().replace(hour=hour, minute=0, second=0),
                    "metric_type": MetricType.USER_ACTIVITY,
                    "value": 1,
                    "metadata": {"activity": "generation_request"}
                })
        
        analytics_service.record_metrics_batch(usage_data)
        
        patterns = analytics_service.analyze_usage_patterns(
            time_range=TimeRange.LAST_24_HOURS
        )
        
        assert "peak_hours" in patterns
        assert "low_activity_hours" in patterns
        assert "usage_distribution" in patterns
        assert len(patterns["peak_hours"]) > 0
        
    def test_alert_threshold_monitoring(self, analytics_service):
        """Test alert threshold monitoring"""
        # Set up alert threshold
        threshold = AlertThreshold(
            metric_type=MetricType.API_COST,
            threshold_value=5.0,
            comparison="greater_than",
            severity="warning"
        )
        
        analytics_service.add_alert_threshold(threshold)
        
        # Record metric that should trigger alert
        analytics_service.record_metric(
            metric_type=MetricType.API_COST,
            value=6.5,
            metadata={"test": "alert_trigger"}
        )
        
        alerts = analytics_service.check_alerts()
        
        assert len(alerts) > 0
        assert any(alert.metric_type == MetricType.API_COST for alert in alerts)
        
    def test_dashboard_data_preparation(self, analytics_service, sample_metrics):
        """Test dashboard data preparation"""
        analytics_service.record_metrics_batch(sample_metrics)
        
        dashboard_data = analytics_service.prepare_dashboard_data(
            time_range=TimeRange.LAST_24_HOURS
        )
        
        assert "key_metrics" in dashboard_data
        assert "charts" in dashboard_data
        assert "alerts" in dashboard_data
        assert "summary_stats" in dashboard_data
        
        # Verify key metrics structure
        assert "total_generations" in dashboard_data["key_metrics"]
        assert "total_cost" in dashboard_data["key_metrics"]
        assert "avg_processing_time" in dashboard_data["key_metrics"]
        
    def test_metric_data_validation(self, analytics_service):
        """Test metric data validation"""
        # Valid metric
        valid_metric = {
            "metric_type": MetricType.GENERATION_COUNT,
            "value": 10,
            "metadata": {"user_id": "test"}
        }
        
        is_valid, errors = analytics_service.validate_metric_data(valid_metric)
        assert is_valid is True
        assert len(errors) == 0
        
        # Invalid metric (missing required fields)
        invalid_metric = {
            "value": 10
        }
        
        is_valid, errors = analytics_service.validate_metric_data(invalid_metric)
        assert is_valid is False
        assert len(errors) > 0
        
    def test_data_retention_management(self, analytics_service):
        """Test data retention and cleanup"""
        # Create old metrics
        old_metrics = [
            {
                "timestamp": datetime.now() - timedelta(days=40),
                "metric_type": MetricType.GENERATION_COUNT,
                "value": 5,
                "metadata": {}
            }
        ]
        
        analytics_service.record_metrics_batch(old_metrics)
        
        # Test cleanup
        cleanup_result = analytics_service.cleanup_old_data(retention_days=30)
        
        assert "deleted_count" in cleanup_result
        assert cleanup_result["deleted_count"] >= 0
        
    def test_export_import_functionality(self, analytics_service, sample_metrics):
        """Test data export and import"""
        analytics_service.record_metrics_batch(sample_metrics)
        
        # Test export
        exported_data = analytics_service.export_metrics(
            time_range=TimeRange.LAST_24_HOURS,
            format="json"
        )
        
        assert "metrics" in exported_data
        assert "metadata" in exported_data
        assert len(exported_data["metrics"]) >= len(sample_metrics)
        
        # Test import
        import_result = analytics_service.import_metrics(exported_data)
        
        assert import_result["status"] == "success"
        assert import_result["imported_count"] >= 0
        
    def test_real_time_metrics_streaming(self, analytics_service):
        """Test real-time metrics streaming capability"""
        # Set up mock stream handler
        stream_handler = Mock()
        analytics_service.register_stream_handler(stream_handler)
        
        # Record metric
        analytics_service.record_metric(
            metric_type=MetricType.GENERATION_COUNT,
            value=1,
            metadata={"real_time": True}
        )
        
        # Verify stream handler was called
        assert stream_handler.called
        
    def test_custom_metric_types(self, analytics_service):
        """Test custom metric type registration"""
        custom_metric_type = "custom_ai_quality_score"
        
        analytics_service.register_custom_metric_type(
            custom_metric_type,
            description="Custom AI quality scoring metric",
            data_type="float",
            valid_range=(0.0, 1.0)
        )
        
        # Test recording custom metric
        result = analytics_service.record_metric(
            metric_type=custom_metric_type,
            value=0.85,
            metadata={"model": "test_model"}
        )
        
        assert result["status"] == "success"
        
    def test_comparative_analysis(self, analytics_service):
        """Test comparative analysis between time periods"""
        # Create data for two different periods
        current_period = [
            {
                "timestamp": datetime.now() - timedelta(hours=i),
                "metric_type": MetricType.GENERATION_COUNT,
                "value": 10,
                "metadata": {}
            }
            for i in range(24)
        ]
        
        previous_period = [
            {
                "timestamp": datetime.now() - timedelta(days=1, hours=i),
                "metric_type": MetricType.GENERATION_COUNT,
                "value": 8,
                "metadata": {}
            }
            for i in range(24)
        ]
        
        analytics_service.record_metrics_batch(current_period + previous_period)
        
        comparison = analytics_service.compare_periods(
            metric_type=MetricType.GENERATION_COUNT,
            current_period=TimeRange.LAST_24_HOURS,
            comparison_period=TimeRange.PREVIOUS_24_HOURS
        )
        
        assert "current_value" in comparison
        assert "previous_value" in comparison
        assert "change_percentage" in comparison
        assert "change_direction" in comparison
        
    def test_anomaly_detection(self, analytics_service):
        """Test anomaly detection in metrics"""
        # Create normal data with one anomaly
        normal_data = [
            {
                "timestamp": datetime.now() - timedelta(hours=i),
                "metric_type": MetricType.PROCESSING_TIME,
                "value": 30.0 + (i % 5),  # Normal range 30-35
                "metadata": {}
            }
            for i in range(10)
        ]
        
        # Add anomaly
        anomaly_data = {
            "timestamp": datetime.now(),
            "metric_type": MetricType.PROCESSING_TIME,
            "value": 120.0,  # Anomalous value
            "metadata": {}
        }
        
        analytics_service.record_metrics_batch(normal_data + [anomaly_data])
        
        anomalies = analytics_service.detect_anomalies(
            metric_type=MetricType.PROCESSING_TIME,
            time_range=TimeRange.LAST_24_HOURS
        )
        
        assert len(anomalies) > 0
        assert any(anomaly.value == 120.0 for anomaly in anomalies)
        
    def test_correlation_analysis(self, analytics_service):
        """Test correlation analysis between metrics"""
        # Create correlated data
        correlated_data = []
        for i in range(20):
            processing_time = 30 + i
            cost = processing_time * 0.1  # Correlated cost
            
            correlated_data.extend([
                {
                    "timestamp": datetime.now() - timedelta(hours=i),
                    "metric_type": MetricType.PROCESSING_TIME,
                    "value": processing_time,
                    "metadata": {"batch": i}
                },
                {
                    "timestamp": datetime.now() - timedelta(hours=i),
                    "metric_type": MetricType.API_COST,
                    "value": cost,
                    "metadata": {"batch": i}
                }
            ])
        
        analytics_service.record_metrics_batch(correlated_data)
        
        correlation = analytics_service.analyze_correlation(
            metric_type_1=MetricType.PROCESSING_TIME,
            metric_type_2=MetricType.API_COST,
            time_range=TimeRange.LAST_24_HOURS
        )
        
        assert "correlation_coefficient" in correlation
        assert "correlation_strength" in correlation
        assert "p_value" in correlation
        assert abs(correlation["correlation_coefficient"]) > 0.5  # Should be strongly correlated
        
    def test_metric_forecasting(self, analytics_service):
        """Test metric forecasting capability"""
        # Create trend data for forecasting
        trend_data = [
            {
                "timestamp": datetime.now() - timedelta(days=i),
                "metric_type": MetricType.GENERATION_COUNT,
                "value": 100 + i * 5,  # Linear trend
                "metadata": {}
            }
            for i in range(30)
        ]
        
        analytics_service.record_metrics_batch(trend_data)
        
        forecast = analytics_service.forecast_metric(
            metric_type=MetricType.GENERATION_COUNT,
            forecast_days=7,
            confidence_level=0.95
        )
        
        assert "forecast_values" in forecast
        assert "confidence_intervals" in forecast
        assert "model_accuracy" in forecast
        assert len(forecast["forecast_values"]) == 7
        
    def test_business_metrics_calculation(self, analytics_service, sample_metrics):
        """Test business-specific metrics calculation"""
        analytics_service.record_metrics_batch(sample_metrics)
        
        business_metrics = analytics_service.calculate_business_metrics(
            time_range=TimeRange.LAST_24_HOURS
        )
        
        assert "roi" in business_metrics  # Return on Investment
        assert "efficiency_score" in business_metrics
        assert "user_satisfaction" in business_metrics
        assert "cost_per_generation" in business_metrics
        
    def test_performance_benchmarking(self, analytics_service):
        """Test performance benchmarking against targets"""
        # Set performance targets
        targets = {
            MetricType.PROCESSING_TIME: {"target": 30.0, "tolerance": 5.0},
            MetricType.API_COST: {"target": 2.0, "tolerance": 0.5}
        }
        
        analytics_service.set_performance_targets(targets)
        
        # Record performance data
        performance_data = [
            {
                "timestamp": datetime.now(),
                "metric_type": MetricType.PROCESSING_TIME,
                "value": 28.0,
                "metadata": {}
            },
            {
                "timestamp": datetime.now(),
                "metric_type": MetricType.API_COST,
                "value": 2.3,
                "metadata": {}
            }
        ]
        
        analytics_service.record_metrics_batch(performance_data)
        
        benchmark_result = analytics_service.benchmark_performance(
            time_range=TimeRange.LAST_24_HOURS
        )
        
        assert "target_compliance" in benchmark_result
        assert "performance_score" in benchmark_result
        assert "recommendations" in benchmark_result


class TestAnalyticsReporting:
    """Test analytics reporting functionality"""
    
    def test_report_generation_types(self):
        """Test different report type generation"""
        service = AnalyticsService()
        
        report_types = [
            ReportType.PERFORMANCE,
            ReportType.COST_ANALYSIS,
            ReportType.USAGE_SUMMARY,
            ReportType.TREND_ANALYSIS
        ]
        
        for report_type in report_types:
            report = service.generate_report(
                report_type=report_type,
                time_range=TimeRange.LAST_7_DAYS
            )
            
            assert isinstance(report, AnalyticsReport)
            assert report.report_type == report_type
            assert report.generated_at is not None
            
    def test_report_customization(self):
        """Test custom report generation"""
        service = AnalyticsService()
        
        custom_config = {
            "metrics": [MetricType.GENERATION_COUNT, MetricType.API_COST],
            "aggregations": [AggregationType.SUM, AggregationType.AVERAGE],
            "visualizations": ["line_chart", "bar_chart"],
            "filters": {"user_id": "test_user"}
        }
        
        report = service.generate_custom_report(
            config=custom_config,
            time_range=TimeRange.LAST_30_DAYS
        )
        
        assert report is not None
        assert "custom_metrics" in report.data
        assert "visualizations" in report.data
        
    def test_report_scheduling(self):
        """Test automated report scheduling"""
        service = AnalyticsService()
        
        schedule_config = {
            "report_type": ReportType.COST_ANALYSIS,
            "frequency": "daily",
            "time": "09:00",
            "recipients": ["admin@example.com"],
            "format": "pdf"
        }
        
        schedule_id = service.schedule_report(schedule_config)
        
        assert schedule_id is not None
        
        # Test retrieving scheduled reports
        scheduled_reports = service.get_scheduled_reports()
        assert len(scheduled_reports) > 0
        assert any(sr.schedule_id == schedule_id for sr in scheduled_reports)


class TestMetricDataStructures:
    """Test metric data structures and validation"""
    
    def test_metric_data_creation(self):
        """Test MetricData creation and validation"""
        metric = MetricData(
            metric_type=MetricType.GENERATION_COUNT,
            value=10,
            timestamp=datetime.now(),
            metadata={"user_id": "test", "quality": "high"}
        )
        
        assert metric.metric_type == MetricType.GENERATION_COUNT
        assert metric.value == 10
        assert metric.metadata["user_id"] == "test"
        
    def test_alert_threshold_validation(self):
        """Test AlertThreshold validation"""
        # Valid threshold
        threshold = AlertThreshold(
            metric_type=MetricType.API_COST,
            threshold_value=10.0,
            comparison="greater_than",
            severity="critical"
        )
        
        assert threshold.is_valid()
        
        # Invalid threshold
        invalid_threshold = AlertThreshold(
            metric_type=MetricType.API_COST,
            threshold_value=-1.0,  # Invalid negative value
            comparison="invalid_comparison",
            severity="unknown_severity"
        )
        
        assert not invalid_threshold.is_valid()
        
    def test_analytics_report_serialization(self):
        """Test AnalyticsReport serialization"""
        report = AnalyticsReport(
            report_id="test_report",
            report_type=ReportType.PERFORMANCE,
            time_range=TimeRange.LAST_24_HOURS,
            data={"test": "data"},
            generated_at=datetime.now()
        )
        
        serialized = report.to_dict()
        
        assert "report_id" in serialized
        assert "report_type" in serialized
        assert "data" in serialized
        assert serialized["report_id"] == "test_report"