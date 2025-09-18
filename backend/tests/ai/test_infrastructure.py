"""Test AI infrastructure setup (T201-T208)."""

import pytest
import os
from pathlib import Path
import sqlite3
import json
from unittest.mock import Mock, patch
import sys

# Add source to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestAIDirectoryStructure:
    """Test T201: AI directory structure creation."""
    
    def test_ai_directories_exist(self):
        """Verify all AI directories were created."""
        base_path = Path(__file__).parent.parent.parent
        
        # Backend AI directories
        assert (base_path / "src" / "ai").exists()
        assert (base_path / "src" / "ai" / "models").exists()
        assert (base_path / "src" / "ai" / "services").exists()
        assert (base_path / "src" / "ai" / "utils").exists()
        
        # Test directories
        assert (base_path / "tests" / "ai").exists()
        
        # Frontend AI directories
        frontend_base = base_path.parent.parent / "frontend" / "src" / "ai"
        assert frontend_base.exists()
        assert (frontend_base / "components").exists()
        assert (frontend_base / "services").exists()
        assert (frontend_base / "hooks").exists()
        
    def test_python_init_files_exist(self):
        """Verify Python __init__.py files exist."""
        base_path = Path(__file__).parent.parent.parent / "src" / "ai"
        
        assert (base_path / "__init__.py").exists()
        assert (base_path / "models" / "__init__.py").exists()
        assert (base_path / "services" / "__init__.py").exists()
        assert (base_path / "utils" / "__init__.py").exists()


class TestVEOAPISDK:
    """Test T202: VEO API SDK installation."""
    
    def test_google_cloud_aiplatform_installed(self):
        """Verify Google Cloud AI Platform is installed."""
        try:
            import google.cloud.aiplatform
            assert True
        except ImportError:
            pytest.fail("google-cloud-aiplatform not installed")
            
    def test_google_auth_installed(self):
        """Verify Google Auth libraries are installed."""
        try:
            import google.auth
            import google.auth.transport.requests
            assert True
        except ImportError:
            pytest.fail("google-auth not installed")


class TestWeatherAPI:
    """Test T203: Weather API dependencies."""
    
    def test_requests_library_installed(self):
        """Verify requests library is installed."""
        try:
            import requests
            assert True
        except ImportError:
            pytest.fail("requests not installed")
            
    def test_weather_api_mock(self, mock_weather_api):
        """Test weather API mock works correctly."""
        import requests
        response = requests.get("http://api.test.com/weather")
        data = response.json()
        
        assert response.status_code == 200
        assert 'weather' in data
        assert data['main']['temp'] == 22.5


class TestEnvironmentVariables:
    """Test T204: AI environment variables."""
    
    def test_env_template_exists(self):
        """Verify .env.template file exists."""
        env_path = Path(__file__).parent.parent.parent / ".env.template"
        assert env_path.exists()
        
    def test_env_template_has_ai_variables(self):
        """Verify .env.template contains AI-specific variables."""
        env_path = Path(__file__).parent.parent.parent / ".env.template"
        with open(env_path, 'r') as f:
            content = f.read()
            
        # Check Phase 2 AI variables
        assert 'VEO_PROJECT_ID' in content
        assert 'VEO_API_QUOTA_PER_DAY' in content
        assert 'WEATHER_API_KEY' in content
        assert 'AI_GENERATION_INTERVAL' in content
        assert 'AI_LEARNING_ENABLED' in content
        assert 'SCHEDULER_TIMEZONE' in content
        assert 'CELERY_BROKER_URL' in content
        assert 'MAX_MONTHLY_API_COST_USD' in content
        
    def test_mock_env_variables(self, mock_env_variables):
        """Test environment variables can be loaded."""
        assert os.getenv('VEO_PROJECT_ID') == 'test-project'
        assert os.getenv('MAX_MONTHLY_API_COST_USD') == '50'


class TestAILogging:
    """Test T205: AI logging configuration."""
    
    def test_logging_config_module_exists(self):
        """Verify logging config module exists."""
        from src.ai.utils import logging_config
        assert hasattr(logging_config, 'setup_ai_logging')
        assert hasattr(logging_config, 'AIMetricsLogger')
        
    def test_setup_ai_logging(self, tmp_path):
        """Test AI logging setup."""
        from src.ai.utils.logging_config import setup_ai_logging
        
        log_file = tmp_path / "test_ai.log"
        logger = setup_ai_logging(log_level="INFO", log_file=str(log_file))
        
        assert logger is not None
        assert logger.name == "ai_system"
        
        # Test logging
        logger.info("Test message", extra={
            "ai_context": {"test": "value"}
        })
        
    def test_metrics_logger(self):
        """Test AI metrics logger."""
        from src.ai.utils.logging_config import AIMetricsLogger
        
        metrics_logger = AIMetricsLogger()
        assert metrics_logger is not None
        
        # Test logging methods exist
        assert hasattr(metrics_logger, 'log_generation_metrics')
        assert hasattr(metrics_logger, 'log_learning_metrics')
        assert hasattr(metrics_logger, 'log_cost_metrics')


class TestSchedulerConfig:
    """Test T206: Scheduler configuration."""
    
    def test_scheduler_module_exists(self):
        """Verify scheduler module exists."""
        from src.ai.utils import scheduler_config
        assert hasattr(scheduler_config, 'AIScheduler')
        assert hasattr(scheduler_config, 'get_scheduler')
        
    def test_apscheduler_installed(self):
        """Verify APScheduler is installed."""
        try:
            import apscheduler
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            assert True
        except ImportError:
            pytest.fail("APScheduler not installed")
            
    def test_scheduler_initialization(self, mock_scheduler):
        """Test scheduler can be initialized."""
        assert mock_scheduler is not None
        assert hasattr(mock_scheduler, 'start')
        assert hasattr(mock_scheduler, 'stop')
        assert hasattr(mock_scheduler, 'get_jobs')


class TestDatabaseSchema:
    """Test T207: AI database schema."""
    
    def test_ai_schema_file_exists(self):
        """Verify AI schema SQL file exists."""
        schema_path = Path(__file__).parent.parent.parent / "src" / "database" / "ai_schema.sql"
        assert schema_path.exists()
        
    def test_ai_schema_creates_tables(self, test_ai_database):
        """Test AI schema creates all required tables."""
        conn = sqlite3.connect(test_ai_database)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Check AI-specific tables exist
        expected_tables = [
            'ai_generation_tasks',
            'ai_prompts',
            'user_preferences',
            'user_feedback',
            'weather_cache',
            'api_costs',
            'generation_schedule',
            'ai_metrics',
            'feature_flags'
        ]
        
        for table in expected_tables:
            assert table in tables, f"Table {table} not found"
            
        conn.close()
        
    def test_feature_flags_initialized(self, test_ai_database):
        """Test feature flags are properly initialized."""
        conn = sqlite3.connect(test_ai_database)
        cursor = conn.cursor()
        
        cursor.execute("SELECT feature_name, is_enabled FROM feature_flags")
        flags = {row[0]: row[1] for row in cursor.fetchall()}
        
        assert 'ai_generation' in flags
        assert 'weather_integration' in flags
        assert 'user_learning' in flags
        assert flags['ai_generation'] == 1  # Should be enabled
        
        conn.close()


class TestPytestConfiguration:
    """Test T208: Pytest configuration for AI tests."""
    
    def test_conftest_exists(self):
        """Verify conftest.py exists for AI tests."""
        conftest_path = Path(__file__).parent / "conftest.py"
        assert conftest_path.exists()
        
    def test_fixtures_available(self):
        """Test that AI test fixtures are available."""
        from conftest import (
            mock_veo_api,
            mock_weather_api,
            test_ai_database,
            mock_scheduler,
            sample_generation_params
        )
        
        # Just importing them verifies they exist
        assert True
        
    def test_mock_veo_api_fixture(self, mock_veo_api):
        """Test VEO API mock fixture works."""
        result = mock_veo_api.generate_video.return_value
        assert result['video_id'] == 'test_video_123'
        assert result['cost_usd'] == 0.05


if __name__ == "__main__":
    pytest.main([__file__, "-v"])