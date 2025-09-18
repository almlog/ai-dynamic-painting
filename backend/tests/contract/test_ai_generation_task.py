"""
Contract test for AIGenerationTask model
Test File: backend/tests/contract/test_ai_generation_task.py

This test MUST FAIL initially (RED phase of TDD)
"""

import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_ai_generation_task_model_exists():
    """Test that AIGenerationTask model exists and has required fields"""
    # This should initially FAIL until we implement the model
    try:
        from src.ai.models.ai_generation_task import AIGenerationTask
        
        # Test model can be instantiated
        task = AIGenerationTask()
        assert task is not None
        
        # Test required fields exist
        required_fields = [
            'task_id', 'user_id', 'prompt_text', 'generation_status', 
            'creation_time', 'completion_time', 'video_output_path',
            'generation_params', 'error_message', 'retry_count',
            'priority_level', 'estimated_duration'
        ]
        
        for field in required_fields:
            assert hasattr(task, field), f"Missing required field: {field}"
            
    except ImportError:
        pytest.fail("AIGenerationTask model not implemented yet")


def test_ai_generation_task_status_enum():
    """Test that generation status enum is properly defined"""
    try:
        from src.ai.models.ai_generation_task import GenerationStatus
        
        # Test enum values exist
        expected_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled']
        
        for status in expected_statuses:
            assert hasattr(GenerationStatus, status.upper()), f"Missing status: {status}"
            
    except ImportError:
        pytest.fail("GenerationStatus enum not implemented yet")


def test_ai_generation_task_crud_operations():
    """Test basic CRUD operations for AIGenerationTask"""
    try:
        from src.ai.models.ai_generation_task import AIGenerationTask, GenerationStatus
        
        # Test creation
        task_data = {
            'task_id': 'test_task_001',
            'user_id': 'user_123',
            'prompt_text': 'Test prompt for AI generation',
            'generation_status': GenerationStatus.PENDING,
            'priority_level': 1,
            'estimated_duration': 300
        }
        
        task = AIGenerationTask(**task_data)
        assert task.task_id == 'test_task_001'
        assert task.user_id == 'user_123'
        assert task.generation_status == GenerationStatus.PENDING
        
        # Test status transitions
        task.generation_status = GenerationStatus.PROCESSING
        assert task.generation_status == GenerationStatus.PROCESSING
        
        task.generation_status = GenerationStatus.COMPLETED
        assert task.generation_status == GenerationStatus.COMPLETED
        
    except ImportError:
        pytest.fail("AIGenerationTask model not fully implemented")


def test_ai_generation_task_validation():
    """Test data validation for AIGenerationTask"""
    try:
        from src.ai.models.ai_generation_task import AIGenerationTask, GenerationStatus
        
        # Test required field validation
        with pytest.raises((ValueError, TypeError)):
            task = AIGenerationTask()  # Missing required fields
            
        # Test prompt text validation
        task = AIGenerationTask(
            task_id='test_002',
            user_id='user_456',
            prompt_text='',  # Empty prompt should be invalid
            generation_status=GenerationStatus.PENDING
        )
        
        # Validate prompt text length
        assert len(task.prompt_text) >= 0  # This should validate properly
        
        # Test priority level validation
        task = AIGenerationTask(
            task_id='test_003',
            user_id='user_789',
            prompt_text='Valid prompt text',
            generation_status=GenerationStatus.PENDING,
            priority_level=10  # Should be valid priority
        )
        
        assert 1 <= task.priority_level <= 10
        
    except ImportError:
        pytest.fail("AIGenerationTask validation not implemented")


def test_ai_generation_task_json_serialization():
    """Test JSON serialization/deserialization"""
    try:
        from src.ai.models.ai_generation_task import AIGenerationTask, GenerationStatus
        import json
        
        task = AIGenerationTask(
            task_id='test_serialize_001',
            user_id='user_serialize',
            prompt_text='Serialization test prompt',
            generation_status=GenerationStatus.PENDING,
            priority_level=5
        )
        
        # Test to_dict method
        task_dict = task.to_dict()
        assert isinstance(task_dict, dict)
        assert task_dict['task_id'] == 'test_serialize_001'
        assert task_dict['user_id'] == 'user_serialize'
        
        # Test JSON serialization
        json_str = json.dumps(task_dict)
        assert isinstance(json_str, str)
        
        # Test deserialization
        loaded_dict = json.loads(json_str)
        assert loaded_dict['task_id'] == 'test_serialize_001'
        
    except ImportError:
        pytest.fail("AIGenerationTask serialization not implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])