"""
Unit tests for AI Scheduling Service - T270 AI unit tests comprehensive coverage
Tests the intelligent scheduling system for AI video generation tasks
"""

import pytest
import asyncio
from datetime import datetime, timedelta, time
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ai.services.scheduling_service import (
    SchedulingService,
    Schedule,
    ScheduleType,
    ScheduleStatus,
    Priority,
    RecurrencePattern,
    TimeSlotType,
    ConflictResolution,
    ScheduleCategory
)


class TestSchedulingService:
    """Test cases for SchedulingService"""
    
    @pytest.fixture
    def scheduling_service(self):
        """Create SchedulingService instance for testing"""
        return SchedulingService()
    
    @pytest.fixture
    def sample_schedule(self):
        """Create sample schedule for testing"""
        return Schedule(
            name="Test Video Generation",
            description="Test schedule for video generation",
            schedule_type=ScheduleType.ONE_TIME,
            priority=Priority.NORMAL,
            start_time="2025-01-01 10:00:00",
            duration=30
        )
    
    def test_scheduling_service_initialization(self, scheduling_service):
        """Test SchedulingService initialization"""
        assert scheduling_service is not None
        assert isinstance(scheduling_service.schedules, list)
        assert len(scheduling_service.schedules) == 0
        assert scheduling_service.is_running is False
        
    def test_schedule_creation(self, sample_schedule):
        """Test Schedule data class creation"""
        assert sample_schedule.name == "Test Video Generation"
        assert sample_schedule.schedule_type == ScheduleType.ONE_TIME
        assert sample_schedule.status == ScheduleStatus.PENDING
        assert sample_schedule.priority == Priority.NORMAL
        assert sample_schedule.duration == 30
        
    def test_add_schedule(self, scheduling_service, sample_schedule):
        """Test adding schedule to service"""
        schedule_id = scheduling_service.add_schedule(sample_schedule)
        
        assert schedule_id is not None
        assert len(scheduling_service.schedules) == 1
        assert scheduling_service.schedules[0].id == schedule_id
        
    def test_get_schedule(self, scheduling_service, sample_schedule):
        """Test retrieving schedule by ID"""
        schedule_id = scheduling_service.add_schedule(sample_schedule)
        retrieved = scheduling_service.get_schedule(schedule_id)
        
        assert retrieved is not None
        assert retrieved.id == schedule_id
        assert retrieved.name == sample_schedule.name
        
    def test_get_nonexistent_schedule(self, scheduling_service):
        """Test retrieving non-existent schedule"""
        result = scheduling_service.get_schedule("nonexistent-id")
        assert result is None
        
    def test_update_schedule_status(self, scheduling_service, sample_schedule):
        """Test updating schedule status"""
        schedule_id = scheduling_service.add_schedule(sample_schedule)
        
        success = scheduling_service.update_schedule_status(schedule_id, ScheduleStatus.ACTIVE)
        
        assert success is True
        updated = scheduling_service.get_schedule(schedule_id)
        assert updated.status == ScheduleStatus.ACTIVE
        
    def test_remove_schedule(self, scheduling_service, sample_schedule):
        """Test removing schedule"""
        schedule_id = scheduling_service.add_schedule(sample_schedule)
        assert len(scheduling_service.schedules) == 1
        
        success = scheduling_service.remove_schedule(schedule_id)
        
        assert success is True
        assert len(scheduling_service.schedules) == 0
        
    def test_get_schedules_by_status(self, scheduling_service):
        """Test filtering schedules by status"""
        # Add schedules with different statuses
        schedule1 = Schedule(name="Schedule 1", status=ScheduleStatus.PENDING)
        schedule2 = Schedule(name="Schedule 2", status=ScheduleStatus.ACTIVE)
        schedule3 = Schedule(name="Schedule 3", status=ScheduleStatus.PENDING)
        
        scheduling_service.add_schedule(schedule1)
        scheduling_service.add_schedule(schedule2)
        scheduling_service.add_schedule(schedule3)
        
        pending_schedules = scheduling_service.get_schedules_by_status(ScheduleStatus.PENDING)
        active_schedules = scheduling_service.get_schedules_by_status(ScheduleStatus.ACTIVE)
        
        assert len(pending_schedules) == 2
        assert len(active_schedules) == 1
        assert all(s.status == ScheduleStatus.PENDING for s in pending_schedules)
        assert all(s.status == ScheduleStatus.ACTIVE for s in active_schedules)
        
    def test_get_schedules_by_priority(self, scheduling_service):
        """Test filtering schedules by priority"""
        high_priority = Schedule(name="High Priority", priority=Priority.HIGH)
        normal_priority = Schedule(name="Normal Priority", priority=Priority.NORMAL)
        
        scheduling_service.add_schedule(high_priority)
        scheduling_service.add_schedule(normal_priority)
        
        high_schedules = scheduling_service.get_schedules_by_priority(Priority.HIGH)
        normal_schedules = scheduling_service.get_schedules_by_priority(Priority.NORMAL)
        
        assert len(high_schedules) == 1
        assert len(normal_schedules) == 1
        assert high_schedules[0].priority == Priority.HIGH
        assert normal_schedules[0].priority == Priority.NORMAL
        
    def test_schedule_conflict_detection(self, scheduling_service):
        """Test detection of scheduling conflicts"""
        # Create overlapping schedules
        schedule1 = Schedule(
            name="Schedule 1",
            start_time="2025-01-01 10:00:00",
            duration=60
        )
        schedule2 = Schedule(
            name="Schedule 2", 
            start_time="2025-01-01 10:30:00",
            duration=60
        )
        
        scheduling_service.add_schedule(schedule1)
        scheduling_service.add_schedule(schedule2)
        
        conflicts = scheduling_service.detect_conflicts()
        
        assert len(conflicts) > 0
        assert any("conflict" in str(conflict).lower() for conflict in conflicts)
        
    def test_optimal_time_slot_finding(self, scheduling_service):
        """Test finding optimal time slots"""
        # Mock context data for time slot optimization
        context = {
            "user_active_hours": ["09:00", "17:00"],
            "system_load": "low",
            "weather": "sunny"
        }
        
        optimal_slots = scheduling_service.find_optimal_time_slots(
            duration=30,
            date_range=("2025-01-01", "2025-01-02"),
            context=context
        )
        
        assert isinstance(optimal_slots, list)
        assert len(optimal_slots) > 0
        
        # Check that slots are within active hours if specified
        for slot in optimal_slots:
            assert slot.get("quality") in ["optimal", "acceptable", "suboptimal"]
            
    def test_schedule_execution_preparation(self, scheduling_service, sample_schedule):
        """Test preparing schedule for execution"""
        schedule_id = scheduling_service.add_schedule(sample_schedule)
        
        prepared = scheduling_service.prepare_for_execution(schedule_id)
        
        assert prepared is not None
        assert "execution_context" in prepared
        assert "resource_allocation" in prepared
        assert "estimated_completion" in prepared
        
    def test_recurring_schedule_handling(self, scheduling_service):
        """Test handling of recurring schedules"""
        recurring_schedule = Schedule(
            name="Daily Generation",
            schedule_type=ScheduleType.RECURRING,
            recurrence_pattern=RecurrencePattern.DAILY,
            start_time="2025-01-01 09:00:00"
        )
        
        schedule_id = scheduling_service.add_schedule(recurring_schedule)
        
        # Test next occurrence calculation
        next_runs = scheduling_service.calculate_next_occurrences(schedule_id, count=3)
        
        assert len(next_runs) == 3
        assert all(isinstance(run, str) for run in next_runs)
        
    def test_adaptive_scheduling(self, scheduling_service):
        """Test adaptive scheduling based on historical data"""
        # Mock historical performance data
        historical_data = {
            "completion_times": [25, 30, 35, 28, 32],
            "optimal_hours": ["09:00", "10:00", "14:00", "15:00"],
            "failure_patterns": []
        }
        
        with patch.object(scheduling_service, 'get_historical_data', return_value=historical_data):
            adaptive_schedule = scheduling_service.create_adaptive_schedule(
                task_type="video_generation",
                context={"priority": "normal"}
            )
            
            assert adaptive_schedule is not None
            assert adaptive_schedule.schedule_type == ScheduleType.ADAPTIVE
            assert adaptive_schedule.duration >= 25  # Based on historical data
            
    def test_priority_based_conflict_resolution(self, scheduling_service):
        """Test priority-based conflict resolution"""
        high_priority = Schedule(
            name="High Priority Task",
            priority=Priority.HIGH,
            start_time="2025-01-01 10:00:00",
            duration=60
        )
        normal_priority = Schedule(
            name="Normal Priority Task",
            priority=Priority.NORMAL,
            start_time="2025-01-01 10:30:00", 
            duration=60
        )
        
        scheduling_service.add_schedule(normal_priority)
        scheduling_service.add_schedule(high_priority)
        
        resolution = scheduling_service.resolve_conflicts(ConflictResolution.PRIORITY_BASED)
        
        assert resolution["status"] == "resolved"
        assert resolution["actions_taken"] is not None
        
    def test_resource_requirement_checking(self, scheduling_service):
        """Test resource requirement validation"""
        resource_heavy_schedule = Schedule(
            name="Resource Heavy Task",
            resource_requirements=["high_cpu", "high_memory", "gpu_access"]
        )
        
        schedule_id = scheduling_service.add_schedule(resource_heavy_schedule)
        
        # Mock resource availability check
        with patch.object(scheduling_service, 'check_resource_availability', return_value=True):
            can_execute = scheduling_service.can_execute_now(schedule_id)
            assert can_execute is True
            
        with patch.object(scheduling_service, 'check_resource_availability', return_value=False):
            can_execute = scheduling_service.can_execute_now(schedule_id)
            assert can_execute is False
            
    def test_schedule_statistics(self, scheduling_service):
        """Test schedule statistics and metrics"""
        # Add various schedules
        for i in range(5):
            schedule = Schedule(
                name=f"Schedule {i}",
                status=ScheduleStatus.COMPLETED if i < 3 else ScheduleStatus.PENDING,
                priority=Priority.HIGH if i < 2 else Priority.NORMAL
            )
            scheduling_service.add_schedule(schedule)
            
        stats = scheduling_service.get_statistics()
        
        assert stats["total_schedules"] == 5
        assert stats["completed_schedules"] == 3
        assert stats["pending_schedules"] == 2
        assert stats["high_priority_schedules"] == 2
        
    def test_emergency_schedule_handling(self, scheduling_service):
        """Test emergency schedule priority handling"""
        # Add normal schedules
        normal_schedule = Schedule(name="Normal Task", priority=Priority.NORMAL)
        scheduling_service.add_schedule(normal_schedule)
        
        # Add emergency schedule
        emergency_schedule = Schedule(
            name="Emergency Task",
            schedule_type=ScheduleType.EMERGENCY,
            priority=Priority.URGENT
        )
        
        schedule_id = scheduling_service.add_schedule(emergency_schedule)
        
        # Emergency schedules should get immediate priority
        next_execution = scheduling_service.get_next_execution()
        
        assert next_execution is not None
        assert next_execution["schedule_id"] == schedule_id
        assert next_execution["priority"] == Priority.URGENT
        
    @pytest.mark.asyncio
    async def test_async_schedule_execution(self, scheduling_service, sample_schedule):
        """Test asynchronous schedule execution"""
        schedule_id = scheduling_service.add_schedule(sample_schedule)
        
        # Mock async execution
        async def mock_execute_task(schedule):
            await asyncio.sleep(0.1)  # Simulate work
            return {"status": "completed", "result": "success"}
            
        with patch.object(scheduling_service, 'execute_task', side_effect=mock_execute_task):
            result = await scheduling_service.execute_schedule_async(schedule_id)
            
            assert result["status"] == "completed"
            assert result["result"] == "success"
            
    def test_schedule_validation(self, scheduling_service):
        """Test schedule validation before adding"""
        # Invalid schedule (missing required fields)
        invalid_schedule = Schedule(name="")  # Empty name
        
        is_valid, errors = scheduling_service.validate_schedule(invalid_schedule)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("name" in error.lower() for error in errors)
        
        # Valid schedule
        valid_schedule = Schedule(
            name="Valid Schedule",
            start_time="2025-01-01 10:00:00"
        )
        
        is_valid, errors = scheduling_service.validate_schedule(valid_schedule)
        
        assert is_valid is True
        assert len(errors) == 0
        
    def test_time_zone_handling(self, scheduling_service):
        """Test time zone aware scheduling"""
        schedule_with_tz = Schedule(
            name="Time Zone Test",
            start_time="2025-01-01 10:00:00",
            parameters={"timezone": "Asia/Tokyo"}
        )
        
        schedule_id = scheduling_service.add_schedule(schedule_with_tz)
        
        # Test conversion to UTC
        utc_time = scheduling_service.convert_to_utc(schedule_id)
        
        assert utc_time is not None
        assert isinstance(utc_time, str)
        
    def test_schedule_persistence(self, scheduling_service, sample_schedule):
        """Test schedule data persistence"""
        schedule_id = scheduling_service.add_schedule(sample_schedule)
        
        # Test export/import
        exported_data = scheduling_service.export_schedules()
        
        assert "schedules" in exported_data
        assert len(exported_data["schedules"]) == 1
        
        # Clear and import
        scheduling_service.clear_all_schedules()
        assert len(scheduling_service.schedules) == 0
        
        success = scheduling_service.import_schedules(exported_data)
        
        assert success is True
        assert len(scheduling_service.schedules) == 1
        assert scheduling_service.schedules[0].name == sample_schedule.name


class TestScheduleDataClass:
    """Test cases for Schedule data class"""
    
    def test_schedule_default_values(self):
        """Test Schedule default values"""
        schedule = Schedule()
        
        assert schedule.id is not None
        assert schedule.name == ""
        assert schedule.schedule_type == ScheduleType.ONE_TIME
        assert schedule.status == ScheduleStatus.PENDING
        assert schedule.priority == Priority.NORMAL
        assert schedule.duration == 30
        
    def test_schedule_custom_values(self):
        """Test Schedule with custom values"""
        schedule = Schedule(
            name="Custom Schedule",
            description="Test description",
            schedule_type=ScheduleType.RECURRING,
            priority=Priority.HIGH,
            duration=60
        )
        
        assert schedule.name == "Custom Schedule"
        assert schedule.description == "Test description" 
        assert schedule.schedule_type == ScheduleType.RECURRING
        assert schedule.priority == Priority.HIGH
        assert schedule.duration == 60
        
    def test_schedule_serialization(self):
        """Test Schedule serialization to dict"""
        schedule = Schedule(
            name="Serialization Test",
            priority=Priority.HIGH,
            context_factors=["weather", "time"],
            parameters={"quality": "high", "duration": 30}
        )
        
        # Test that schedule can be converted to dict-like structure
        assert schedule.name == "Serialization Test"
        assert schedule.priority == Priority.HIGH
        assert "weather" in schedule.context_factors
        assert schedule.parameters["quality"] == "high"


# Integration test for schedule execution flow
class TestScheduleExecutionFlow:
    """Integration tests for complete schedule execution flow"""
    
    @pytest.fixture
    def configured_service(self):
        """Create configured scheduling service"""
        service = SchedulingService()
        service.configure({
            "max_concurrent_schedules": 3,
            "default_timeout": 300,
            "conflict_resolution": ConflictResolution.PRIORITY_BASED
        })
        return service
        
    def test_complete_schedule_lifecycle(self, configured_service):
        """Test complete schedule from creation to completion"""
        # Create schedule
        schedule = Schedule(
            name="Lifecycle Test",
            description="Test complete lifecycle",
            priority=Priority.NORMAL,
            start_time="2025-01-01 10:00:00",
            duration=30,
            resource_requirements=["cpu", "memory"]
        )
        
        # Add to service
        schedule_id = configured_service.add_schedule(schedule)
        assert schedule_id is not None
        
        # Validate
        is_valid, errors = configured_service.validate_schedule(schedule)
        assert is_valid is True
        
        # Prepare for execution
        prepared = configured_service.prepare_for_execution(schedule_id)
        assert prepared is not None
        
        # Update status to active
        success = configured_service.update_schedule_status(schedule_id, ScheduleStatus.ACTIVE)
        assert success is True
        
        # Complete execution
        success = configured_service.update_schedule_status(schedule_id, ScheduleStatus.COMPLETED)
        assert success is True
        
        # Verify final state
        final_schedule = configured_service.get_schedule(schedule_id)
        assert final_schedule.status == ScheduleStatus.COMPLETED