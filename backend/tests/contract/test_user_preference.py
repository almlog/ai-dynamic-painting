"""
Contract test for UserPreference model
Test File: backend/tests/contract/test_user_preference.py

This test MUST FAIL initially (RED phase of TDD)
"""

import pytest
from pathlib import Path
import sys
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_user_preference_model_exists():
    """Test that UserPreference model exists and has required fields"""
    # This should initially FAIL until we implement the model
    try:
        from src.ai.models.user_preference import UserPreference
        
        # Test model can be instantiated
        preference = UserPreference()
        assert preference is not None
        
        # Test required fields exist
        required_fields = [
            'preference_id', 'user_id', 'preference_type', 'preference_value',
            'context', 'weight', 'confidence_score', 'learning_source',
            'creation_time', 'last_updated', 'usage_count', 'effectiveness_score',
            'is_active', 'metadata', 'tags'
        ]
        
        for field in required_fields:
            assert hasattr(preference, field), f"Missing required field: {field}"
            
    except ImportError:
        pytest.fail("UserPreference model not implemented yet")


def test_user_preference_type_enum():
    """Test that preference type enum is properly defined"""
    try:
        from src.ai.models.user_preference import PreferenceType
        
        # Test enum values exist
        expected_types = ['style', 'color', 'mood', 'time_of_day', 'weather', 'season', 'theme', 'content_type']
        
        for pref_type in expected_types:
            assert hasattr(PreferenceType, pref_type.upper()), f"Missing preference type: {pref_type}"
            
    except ImportError:
        pytest.fail("PreferenceType enum not implemented yet")


def test_user_preference_learning_source_enum():
    """Test that learning source enum is properly defined"""
    try:
        from src.ai.models.user_preference import LearningSource
        
        # Test enum values exist
        expected_sources = ['explicit', 'implicit', 'system', 'external']
        
        for source in expected_sources:
            assert hasattr(LearningSource, source.upper()), f"Missing learning source: {source}"
            
    except ImportError:
        pytest.fail("LearningSource enum not implemented yet")


def test_user_preference_crud_operations():
    """Test basic CRUD operations for UserPreference"""
    try:
        from src.ai.models.user_preference import UserPreference, PreferenceType, LearningSource
        
        # Test creation with required fields
        preference_data = {
            'preference_id': 'pref_001',
            'user_id': 'user_123',
            'preference_type': PreferenceType.STYLE,
            'preference_value': 'impressionist',
            'context': {'time_of_day': 'evening', 'season': 'autumn'},
            'weight': 0.8,
            'confidence_score': 0.75,
            'learning_source': LearningSource.EXPLICIT
        }
        
        preference = UserPreference(**preference_data)
        assert preference.preference_id == 'pref_001'
        assert preference.user_id == 'user_123'
        assert preference.preference_type == PreferenceType.STYLE
        assert preference.preference_value == 'impressionist'
        assert preference.weight == 0.8
        
        # Test context handling
        assert preference.get_context_value('time_of_day') == 'evening'
        preference.set_context_value('mood', 'relaxed')
        assert preference.get_context_value('mood') == 'relaxed'
        
    except ImportError:
        pytest.fail("UserPreference model not fully implemented")


def test_user_preference_validation():
    """Test data validation for UserPreference"""
    try:
        from src.ai.models.user_preference import UserPreference, PreferenceType, LearningSource
        
        # Test weight validation (0.0 to 1.0)
        preference = UserPreference(
            preference_id='test_002',
            user_id='user_456',
            preference_type=PreferenceType.COLOR,
            preference_value='blue',
            weight=1.5,  # Should be clamped to 1.0
            learning_source=LearningSource.IMPLICIT
        )
        
        assert 0.0 <= preference.weight <= 1.0
        
        # Test confidence score validation (0.0 to 1.0)
        preference.confidence_score = 0.5
        assert 0.0 <= preference.confidence_score <= 1.0
        
        # Test usage count validation
        preference.usage_count = 10
        assert preference.usage_count >= 0
        
    except ImportError:
        pytest.fail("UserPreference validation not implemented")


def test_user_preference_learning_operations():
    """Test learning and adaptation operations"""
    try:
        from src.ai.models.user_preference import UserPreference, PreferenceType, LearningSource
        
        preference = UserPreference(
            preference_id='learn_test_001',
            user_id='user_learning',
            preference_type=PreferenceType.MOOD,
            preference_value='bright',
            weight=0.5,
            confidence_score=0.3,
            learning_source=LearningSource.IMPLICIT,
            usage_count=0,
            effectiveness_score=0.0
        )
        
        # Test positive feedback
        initial_weight = preference.weight
        preference.apply_positive_feedback(0.1)
        assert preference.weight > initial_weight
        assert preference.confidence_score > 0.3
        
        # Test negative feedback
        current_weight = preference.weight
        preference.apply_negative_feedback(0.05)
        assert preference.weight < current_weight
        
        # Test usage tracking
        initial_usage = preference.usage_count
        preference.record_usage()
        assert preference.usage_count == initial_usage + 1
        
    except ImportError:
        pytest.fail("UserPreference learning operations not implemented")


def test_user_preference_similarity_calculation():
    """Test preference similarity and matching"""
    try:
        from src.ai.models.user_preference import UserPreference, PreferenceType
        
        # Create two similar preferences
        pref1 = UserPreference(
            preference_id='sim_test_001',
            user_id='user_sim',
            preference_type=PreferenceType.STYLE,
            preference_value='impressionist',
            context={'time_of_day': 'evening'},
            weight=0.8
        )
        
        pref2 = UserPreference(
            preference_id='sim_test_002',
            user_id='user_sim',
            preference_type=PreferenceType.STYLE,
            preference_value='impressionist',
            context={'time_of_day': 'evening'},
            weight=0.7
        )
        
        # Test similarity calculation
        similarity = pref1.calculate_similarity(pref2)
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.8  # Should be high similarity
        
        # Test context matching
        context_match = pref1.matches_context({'time_of_day': 'evening', 'season': 'autumn'})
        assert context_match == True
        
    except ImportError:
        pytest.fail("UserPreference similarity calculation not implemented")


def test_user_preference_aggregation():
    """Test preference aggregation and ranking"""
    try:
        from src.ai.models.user_preference import UserPreference, PreferenceType
        
        preferences = []
        for i in range(3):
            pref = UserPreference(
                preference_id=f'agg_test_{i:03d}',
                user_id='user_agg',
                preference_type=PreferenceType.COLOR,
                preference_value=f'color_{i}',
                weight=0.5 + (i * 0.1),
                usage_count=i * 5,
                effectiveness_score=0.6 + (i * 0.1)
            )
            preferences.append(pref)
        
        # Test ranking by weight
        sorted_by_weight = UserPreference.rank_by_weight(preferences)
        assert len(sorted_by_weight) == 3
        assert sorted_by_weight[0].weight >= sorted_by_weight[1].weight
        
        # Test ranking by effectiveness
        sorted_by_effectiveness = UserPreference.rank_by_effectiveness(preferences)
        assert len(sorted_by_effectiveness) == 3
        assert sorted_by_effectiveness[0].effectiveness_score >= sorted_by_effectiveness[1].effectiveness_score
        
    except ImportError:
        pytest.fail("UserPreference aggregation not implemented")


def test_user_preference_json_serialization():
    """Test JSON serialization/deserialization"""
    try:
        from src.ai.models.user_preference import UserPreference, PreferenceType, LearningSource
        import json
        
        preference = UserPreference(
            preference_id='serialize_test_001',
            user_id='user_serialize',
            preference_type=PreferenceType.THEME,
            preference_value='nature',
            context={'season': 'spring', 'weather': 'sunny'},
            weight=0.9,
            confidence_score=0.85,
            learning_source=LearningSource.EXPLICIT,
            usage_count=25,
            effectiveness_score=0.88,
            metadata={'source': 'user_feedback'},
            tags=['outdoor', 'peaceful']
        )
        
        # Test to_dict method
        preference_dict = preference.to_dict()
        assert isinstance(preference_dict, dict)
        assert preference_dict['preference_id'] == 'serialize_test_001'
        assert preference_dict['user_id'] == 'user_serialize'
        assert preference_dict['weight'] == 0.9
        
        # Test JSON serialization
        json_str = json.dumps(preference_dict)
        assert isinstance(json_str, str)
        
        # Test deserialization
        loaded_dict = json.loads(json_str)
        assert loaded_dict['preference_id'] == 'serialize_test_001'
        
    except ImportError:
        pytest.fail("UserPreference serialization not implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])