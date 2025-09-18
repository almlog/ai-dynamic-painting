"""Pytest configuration for AI integration tests."""

import pytest
import asyncio
import os
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import tempfile
import sqlite3
from datetime import datetime
import json

# Add backend source to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_veo_api():
    """Mock VEO API client for testing."""
    with patch('google.cloud.aiplatform.PredictionServiceClient') as mock_veo:
        mock_instance = Mock()
        mock_instance.generate_video = AsyncMock(return_value={
            'video_id': 'test_video_123',
            'status': 'completed',
            'url': 'https://example.com/video.mp4',
            'duration': 30,
            'cost_usd': 0.05
        })
        mock_veo.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_weather_api():
    """Mock weather API for testing."""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'weather': [{'main': 'Clear', 'description': 'clear sky'}],
            'main': {
                'temp': 22.5,
                'humidity': 65,
                'pressure': 1013
            },
            'wind': {'speed': 3.5},
            'name': 'Tokyo'
        }
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def test_ai_database():
    """Create a temporary test database with AI schema."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    # Create database and apply schema
    conn = sqlite3.connect(db_path)
    
    # Read and execute AI schema
    schema_path = Path(__file__).parent.parent.parent / "src" / "database" / "ai_schema.sql"
    if schema_path.exists():
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            conn.executescript(schema_sql)
    else:
        # Minimal schema for testing if file doesn't exist yet
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_generation_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                prompt TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    os.unlink(db_path)


@pytest.fixture
def mock_scheduler():
    """Mock AI scheduler for testing."""
    from src.ai.utils.scheduler_config import AIScheduler
    
    with patch.object(AIScheduler, '__init__', lambda x: None):
        scheduler = AIScheduler()
        scheduler.scheduler = Mock()
        scheduler.scheduler.running = False
        scheduler.scheduler.get_jobs = Mock(return_value=[])
        scheduler.start = Mock()
        scheduler.stop = Mock()
        yield scheduler


@pytest.fixture
def mock_ai_logger():
    """Mock AI logger for testing."""
    logger = Mock()
    logger.info = Mock()
    logger.error = Mock()
    logger.warning = Mock()
    logger.debug = Mock()
    return logger


@pytest.fixture
def sample_generation_params():
    """Sample generation parameters for testing."""
    return {
        'prompt': 'A beautiful sunrise over Mount Fuji with cherry blossoms',
        'duration_seconds': 30,
        'resolution': '1920x1080',
        'fps': 30,
        'style': 'cinematic',
        'context': {
            'time_of_day': 'morning',
            'weather': 'clear',
            'season': 'spring',
            'location': 'Tokyo'
        }
    }


@pytest.fixture
def sample_user_feedback():
    """Sample user feedback data for testing."""
    return [
        {'video_id': 1, 'feedback_type': 'good', 'timestamp': '2025-09-17T06:00:00Z'},
        {'video_id': 2, 'feedback_type': 'bad', 'timestamp': '2025-09-17T12:00:00Z'},
        {'video_id': 3, 'feedback_type': 'skip', 'timestamp': '2025-09-17T18:00:00Z'},
        {'video_id': 4, 'feedback_type': 'good', 'timestamp': '2025-09-17T22:00:00Z'},
    ]


@pytest.fixture
def mock_env_variables():
    """Set up test environment variables."""
    test_env = {
        'VEO_PROJECT_ID': 'test-project',
        'VEO_LOCATION': 'us-central1',
        'VEO_MODEL_NAME': 'veo-001-preview',
        'VEO_API_QUOTA_PER_DAY': '100',
        'WEATHER_API_KEY': 'test-weather-key',
        'WEATHER_LOCATION': 'Tokyo,JP',
        'AI_GENERATION_INTERVAL': '21600',
        'SCHEDULER_TIMEZONE': 'Asia/Tokyo',
        'MAX_MONTHLY_API_COST_USD': '50'
    }
    
    with patch.dict(os.environ, test_env):
        yield test_env


@pytest.fixture
def mock_m5stack_client():
    """Mock M5STACK client for testing AI integration."""
    client = Mock()
    client.send_command = AsyncMock(return_value={'status': 'ok'})
    client.get_button_state = AsyncMock(return_value={'A': False, 'B': False, 'C': False})
    client.display_message = AsyncMock(return_value={'displayed': True})
    return client


@pytest.fixture
def cleanup_test_logs():
    """Clean up test log files after tests."""
    log_dir = Path("./logs/ai")
    yield
    # Cleanup any test logs created
    if log_dir.exists():
        for log_file in log_dir.glob("test_*.log"):
            try:
                log_file.unlink()
            except:
                pass


# Markers for different test categories
pytest.mark.ai = pytest.mark.mark(name="ai")
pytest.mark.veo = pytest.mark.mark(name="veo")
pytest.mark.scheduler = pytest.mark.mark(name="scheduler")
pytest.mark.learning = pytest.mark.mark(name="learning")
pytest.mark.integration = pytest.mark.mark(name="integration")