"""
Contract test for GenerationSchedule model
Test File: backend/tests/contract/test_generation_schedule.py

This test MUST FAIL initially (RED phase of TDD)
"""

import pytest
from pathlib import Path
import sys
from datetime import datetime, timedelta
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_generation_schedule_model_exists():
    """Test that GenerationSchedule model exists and has required fields"""
    # This should initially FAIL until we implement the model
    try:
        from src.ai.models.generation_schedule import GenerationSchedule
        
        # Test model can be instantiated
        schedule = GenerationSchedule()
        assert schedule is not None
        
        # Test required fields exist
        required_fields = [
            'schedule_id', 'name', 'is_active', 'schedule_type', 'frequency',
            'start_time', 'end_time', 'creation_time', 'last_run_time',
            'next_run_time', 'run_count', 'success_count', 'failure_count',
            'template_ids', 'context_preferences', 'priority_level'
        ]
        
        for field in required_fields:
            assert hasattr(schedule, field), f"Missing required field: {field}"
            
    except ImportError:
        pytest.fail("GenerationSchedule model not implemented yet")


def test_generation_schedule_type_enum():
    """Test that schedule type enum is properly defined"""
    try:
        from src.ai.models.generation_schedule import ScheduleType
        
        # Test enum values exist
        expected_types = ['once', 'hourly', 'daily', 'weekly', 'monthly', 'cron', 'event_driven']
        
        for schedule_type in expected_types:
            assert hasattr(ScheduleType, schedule_type.upper()), f"Missing schedule type: {schedule_type}"
            
    except ImportError:
        pytest.fail("ScheduleType enum not implemented yet")


def test_generation_schedule_frequency_enum():
    """Test that frequency enum is properly defined"""
    try:
        from src.ai.models.generation_schedule import ScheduleFrequency
        
        # Test enum values exist
        expected_frequencies = ['low', 'normal', 'high', 'burst']
        
        for frequency in expected_frequencies:
            assert hasattr(ScheduleFrequency, frequency.upper()), f"Missing frequency: {frequency}"
            
    except ImportError:
        pytest.fail("ScheduleFrequency enum not implemented yet")


def test_generation_schedule_crud_operations():
    """Test basic CRUD operations for GenerationSchedule"""
    try:
        from src.ai.models.generation_schedule import GenerationSchedule, ScheduleType, ScheduleFrequency
        
        # Test creation with required fields
        schedule_data = {
            'schedule_id': 'sch_001',
            'name': 'Morning Sunrise Schedule',
            'schedule_type': ScheduleType.DAILY,
            'frequency': ScheduleFrequency.NORMAL,
            'start_time': datetime(2025, 1, 1, 6, 0, 0),
            'end_time': datetime(2025, 12, 31, 23, 59, 59),
            'template_ids': ['tpl_sunrise_001', 'tpl_morning_002'],
            'priority_level': 5
        }
        
        schedule = GenerationSchedule(**schedule_data)
        assert schedule.schedule_id == 'sch_001'
        assert schedule.name == 'Morning Sunrise Schedule'
        assert schedule.schedule_type == ScheduleType.DAILY
        assert schedule.priority_level == 5
        
        # Test template management
        schedule.add_template('tpl_new_003')
        assert 'tpl_new_003' in schedule.template_ids
        
        schedule.remove_template('tpl_sunrise_001')
        assert 'tpl_sunrise_001' not in schedule.template_ids
        
    except ImportError:
        pytest.fail("GenerationSchedule model not fully implemented")


def test_generation_schedule_time_validation():
    """Test time-based validation for GenerationSchedule"""
    try:
        from src.ai.models.generation_schedule import GenerationSchedule, ScheduleType
        
        now = datetime.now()
        future = now + timedelta(days=30)
        
        schedule = GenerationSchedule(
            schedule_id='time_test_001',
            name='Time Validation Test',
            schedule_type=ScheduleType.DAILY,
            start_time=now,
            end_time=future
        )
        
        # Test time validation
        assert schedule.start_time < schedule.end_time
        
        # Test if schedule is currently active
        is_active_now = schedule.is_active_at(now + timedelta(days=1))
        assert is_active_now == True
        
        # Test if schedule is inactive after end time
        is_active_after = schedule.is_active_at(future + timedelta(days=1))
        assert is_active_after == False
        
    except ImportError:
        pytest.fail("GenerationSchedule time validation not implemented")


def test_generation_schedule_next_run_calculation():
    """Test next run time calculation"""
    try:
        from src.ai.models.generation_schedule import GenerationSchedule, ScheduleType
        
        now = datetime.now()
        
        # Daily schedule
        daily_schedule = GenerationSchedule(
            schedule_id='daily_001',
            name='Daily Test',
            schedule_type=ScheduleType.DAILY,
            start_time=now
        )
        
        next_run = daily_schedule.calculate_next_run_time(now)
        assert next_run > now
        assert (next_run - now).days <= 1
        
        # Hourly schedule
        hourly_schedule = GenerationSchedule(
            schedule_id='hourly_001',
            name='Hourly Test',
            schedule_type=ScheduleType.HOURLY,
            start_time=now
        )
        
        next_hourly = hourly_schedule.calculate_next_run_time(now)
        assert next_hourly > now
        assert (next_hourly - now).seconds <= 3600
        
    except ImportError:
        pytest.fail("GenerationSchedule next run calculation not implemented")


def test_generation_schedule_statistics_tracking():
    """Test run statistics tracking"""
    try:
        from src.ai.models.generation_schedule import GenerationSchedule, ScheduleType
        
        schedule = GenerationSchedule(
            schedule_id='stats_test_001',
            name='Statistics Test',
            schedule_type=ScheduleType.DAILY,
            run_count=0,
            success_count=0,
            failure_count=0
        )
        
        # Test successful run recording
        initial_runs = schedule.run_count
        schedule.record_successful_run()
        assert schedule.run_count == initial_runs + 1
        assert schedule.success_count == 1
        
        # Test failed run recording
        schedule.record_failed_run()
        assert schedule.run_count == initial_runs + 2
        assert schedule.failure_count == 1
        
        # Test success rate calculation
        success_rate = schedule.calculate_success_rate()
        assert success_rate == 0.5  # 1 success out of 2 runs
        
    except ImportError:
        pytest.fail("GenerationSchedule statistics tracking not implemented")


def test_generation_schedule_json_serialization():
    """Test JSON serialization/deserialization"""
    try:
        from src.ai.models.generation_schedule import GenerationSchedule, ScheduleType, ScheduleFrequency
        import json
        
        now = datetime.now()
        
        schedule = GenerationSchedule(
            schedule_id='serialize_test_001',
            name='Serialization Test',
            schedule_type=ScheduleType.WEEKLY,
            frequency=ScheduleFrequency.HIGH,
            start_time=now,
            template_ids=['tpl_001', 'tpl_002'],
            context_preferences={'weather': 'sunny', 'mood': 'bright'},
            priority_level=8
        )
        
        # Test to_dict method
        schedule_dict = schedule.to_dict()
        assert isinstance(schedule_dict, dict)
        assert schedule_dict['schedule_id'] == 'serialize_test_001'
        assert schedule_dict['name'] == 'Serialization Test'
        assert schedule_dict['priority_level'] == 8
        
        # Test JSON serialization
        json_str = json.dumps(schedule_dict)
        assert isinstance(json_str, str)
        
        # Test deserialization
        loaded_dict = json.loads(json_str)
        assert loaded_dict['schedule_id'] == 'serialize_test_001'
        
    except ImportError:
        pytest.fail("GenerationSchedule serialization not implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])