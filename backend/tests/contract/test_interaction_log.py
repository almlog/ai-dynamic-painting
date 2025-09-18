"""
Contract test for InteractionLog model
Test File: backend/tests/contract/test_interaction_log.py

This test MUST FAIL initially (RED phase of TDD)
"""

import pytest
from pathlib import Path
import sys
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_interaction_log_model_exists():
    """Test that InteractionLog model exists and has required fields"""
    # This should initially FAIL until we implement the model
    try:
        from src.ai.models.interaction_log import InteractionLog
        
        # Test model can be instantiated
        log = InteractionLog()
        assert log is not None
        
        # Test required fields exist
        required_fields = [
            'log_id', 'user_id', 'interaction_type', 'interaction_data',
            'timestamp', 'session_id', 'device_info', 'response_time_ms',
            'success', 'error_message', 'context', 'metadata', 'tags'
        ]
        
        for field in required_fields:
            assert hasattr(log, field), f"Missing required field: {field}"
            
    except ImportError:
        pytest.fail("InteractionLog model not implemented yet")


def test_interaction_log_type_enum():
    """Test that interaction type enum is properly defined"""
    try:
        from src.ai.models.interaction_log import InteractionType
        
        # Test enum values exist
        expected_types = ['button_press', 'video_generation', 'preference_update', 'schedule_change', 'api_call', 'system_event']
        
        for interaction_type in expected_types:
            assert hasattr(InteractionType, interaction_type.upper()), f"Missing interaction type: {interaction_type}"
            
    except ImportError:
        pytest.fail("InteractionType enum not implemented yet")


def test_interaction_log_crud_operations():
    """Test basic CRUD operations for InteractionLog"""
    try:
        from src.ai.models.interaction_log import InteractionLog, InteractionType
        
        # Test creation with required fields
        log_data = {
            'log_id': 'log_001',
            'user_id': 'user_123',
            'interaction_type': InteractionType.BUTTON_PRESS,
            'interaction_data': {'button': 'like', 'video_id': 'vid_001'},
            'session_id': 'session_abc',
            'device_info': {'type': 'm5stack', 'version': '1.0'},
            'response_time_ms': 150,
            'success': True
        }
        
        log = InteractionLog(**log_data)
        assert log.log_id == 'log_001'
        assert log.user_id == 'user_123'
        assert log.interaction_type == InteractionType.BUTTON_PRESS
        assert log.response_time_ms == 150
        assert log.success == True
        
        # Test data access
        assert log.get_interaction_value('button') == 'like'
        log.set_interaction_value('rating', 5)
        assert log.get_interaction_value('rating') == 5
        
    except ImportError:
        pytest.fail("InteractionLog model not fully implemented")


def test_interaction_log_validation():
    """Test data validation for InteractionLog"""
    try:
        from src.ai.models.interaction_log import InteractionLog, InteractionType
        
        # Test response time validation
        log = InteractionLog(
            log_id='test_002',
            user_id='user_456',
            interaction_type=InteractionType.API_CALL,
            interaction_data={'endpoint': '/api/videos'},
            response_time_ms=-10  # Should be clamped to 0
        )
        
        assert log.response_time_ms >= 0
        
        # Test timestamp validation
        assert log.timestamp is not None
        assert isinstance(log.timestamp, datetime)
        
        # Test success flag
        assert isinstance(log.success, bool)
        
    except ImportError:
        pytest.fail("InteractionLog validation not implemented")


def test_interaction_log_session_management():
    """Test session and device tracking"""
    try:
        from src.ai.models.interaction_log import InteractionLog, InteractionType
        
        log = InteractionLog(
            log_id='session_test_001',
            user_id='user_session',
            interaction_type=InteractionType.VIDEO_GENERATION,
            interaction_data={'prompt': 'sunset scene'},
            session_id='session_xyz',
            device_info={'type': 'web', 'browser': 'chrome', 'version': '120.0'}
        )
        
        # Test session tracking
        assert log.session_id == 'session_xyz'
        assert log.is_same_session('session_xyz') == True
        assert log.is_same_session('session_abc') == False
        
        # Test device info
        assert log.get_device_type() == 'web'
        assert log.get_device_info('browser') == 'chrome'
        
    except ImportError:
        pytest.fail("InteractionLog session management not implemented")


def test_interaction_log_performance_tracking():
    """Test performance and timing metrics"""
    try:
        from src.ai.models.interaction_log import InteractionLog, InteractionType
        
        log = InteractionLog(
            log_id='perf_test_001',
            user_id='user_perf',
            interaction_type=InteractionType.VIDEO_GENERATION,
            interaction_data={'prompt': 'test generation'},
            response_time_ms=2500,
            success=True
        )
        
        # Test performance categorization
        assert log.is_fast_response() == False  # > 1000ms is slow
        assert log.is_slow_response() == True   # > 2000ms is slow
        
        # Test success tracking
        log.mark_successful(1800)
        assert log.success == True
        assert log.response_time_ms == 1800
        
        # Test failure tracking
        log.mark_failed('Generation timeout', 5000)
        assert log.success == False
        assert log.error_message == 'Generation timeout'
        
    except ImportError:
        pytest.fail("InteractionLog performance tracking not implemented")


def test_interaction_log_context_handling():
    """Test context and metadata management"""
    try:
        from src.ai.models.interaction_log import InteractionLog, InteractionType
        
        log = InteractionLog(
            log_id='context_test_001',
            user_id='user_context',
            interaction_type=InteractionType.PREFERENCE_UPDATE,
            interaction_data={'preference': 'style', 'value': 'modern'},
            context={'time_of_day': 'evening', 'weather': 'rainy'},
            metadata={'source': 'mobile_app', 'version': '2.1'},
            tags=['user_action', 'preference']
        )
        
        # Test context operations
        assert log.get_context_value('time_of_day') == 'evening'
        log.set_context_value('mood', 'relaxed')
        assert log.get_context_value('mood') == 'relaxed'
        
        # Test metadata operations
        assert log.get_metadata_value('source') == 'mobile_app'
        log.set_metadata_value('processed', True)
        assert log.get_metadata_value('processed') == True
        
        # Test tags
        assert 'user_action' in log.tags
        log.add_tag('validated')
        assert 'validated' in log.tags
        
    except ImportError:
        pytest.fail("InteractionLog context handling not implemented")


def test_interaction_log_analytics():
    """Test analytics and aggregation methods"""
    try:
        from src.ai.models.interaction_log import InteractionLog, InteractionType
        
        logs = []
        for i in range(3):
            log = InteractionLog(
                log_id=f'analytics_test_{i:03d}',
                user_id='user_analytics',
                interaction_type=InteractionType.BUTTON_PRESS,
                interaction_data={'button': f'button_{i}'},
                response_time_ms=100 + (i * 50),
                success=(i != 1)  # Second log fails
            )
            logs.append(log)
        
        # Test analytics
        success_rate = InteractionLog.calculate_success_rate(logs)
        assert success_rate == 2/3  # 2 successful out of 3
        
        avg_response_time = InteractionLog.calculate_average_response_time(logs)
        assert avg_response_time == 150.0  # (100 + 150 + 200) / 3
        
        # Test filtering
        successful_logs = InteractionLog.filter_successful(logs)
        assert len(successful_logs) == 2
        
    except ImportError:
        pytest.fail("InteractionLog analytics not implemented")


def test_interaction_log_json_serialization():
    """Test JSON serialization/deserialization"""
    try:
        from src.ai.models.interaction_log import InteractionLog, InteractionType
        import json
        
        log = InteractionLog(
            log_id='serialize_test_001',
            user_id='user_serialize',
            interaction_type=InteractionType.SYSTEM_EVENT,
            interaction_data={'event': 'startup', 'duration_ms': 3000},
            session_id='session_serialize',
            device_info={'type': 'raspberry_pi', 'model': '4B'},
            response_time_ms=500,
            success=True,
            context={'system_load': 0.3},
            metadata={'version': '1.0', 'build': 'prod'},
            tags=['system', 'startup']
        )
        
        # Test to_dict method
        log_dict = log.to_dict()
        assert isinstance(log_dict, dict)
        assert log_dict['log_id'] == 'serialize_test_001'
        assert log_dict['user_id'] == 'user_serialize'
        assert log_dict['response_time_ms'] == 500
        
        # Test JSON serialization
        json_str = json.dumps(log_dict)
        assert isinstance(json_str, str)
        
        # Test deserialization
        loaded_dict = json.loads(json_str)
        assert loaded_dict['log_id'] == 'serialize_test_001'
        
    except ImportError:
        pytest.fail("InteractionLog serialization not implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])