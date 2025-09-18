"""
Unit tests for LearningService - T270 AI Unit Tests
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.ai.services.learning_service import (
    LearningService, PreferenceType, InteractionType, LearningAlgorithm,
    UserPreference, InteractionRecord
)


class TestLearningService:
    """Unit tests for LearningService"""
    
    @pytest.fixture
    def learning_service(self):
        """Create LearningService instance for testing"""
        return LearningService()
    
    @pytest.fixture
    def sample_interaction_data(self):
        """Sample interaction data for testing"""
        return [
            {
                'user_id': 'user_123',
                'content_id': 'video_001',
                'interaction_type': InteractionType.LIKE,
                'duration_watched': 90,
                'total_duration': 120,
                'content_metadata': {
                    'style': 'abstract',
                    'mood': 'calm',
                    'weather': 'sunny'
                },
                'timestamp': datetime.now()
            },
            {
                'user_id': 'user_123',
                'content_id': 'video_002',
                'interaction_type': InteractionType.SKIP,
                'duration_watched': 15,
                'total_duration': 180,
                'content_metadata': {
                    'style': 'realistic',
                    'mood': 'energetic',
                    'weather': 'rainy'
                },
                'timestamp': datetime.now()
            }
        ]
    
    def test_service_initialization(self, learning_service):
        """Test LearningService initialization"""
        assert learning_service is not None
        assert isinstance(learning_service.user_preferences, dict)
        assert isinstance(learning_service.interaction_history, list)
        assert isinstance(learning_service.learning_models, dict)
        assert isinstance(learning_service.algorithm_weights, dict)
    
    def test_safe_get_preference_type(self, learning_service):
        """Test safe preference type conversion"""
        # Test valid preference type
        result = learning_service._safe_get_preference_type('style')
        assert result == PreferenceType.STYLE
        
        # Test mapping for unknown types
        result = learning_service._safe_get_preference_type('time_of_day')
        assert result == PreferenceType.TIMING
        
        result = learning_service._safe_get_preference_type('weather_condition')
        assert result == PreferenceType.WEATHER
        
        # Test default fallback
        result = learning_service._safe_get_preference_type('unknown_type')
        assert result == PreferenceType.CONTENT
    
    @pytest.mark.asyncio
    async def test_learn_user_preferences(self, learning_service, sample_interaction_data):
        """Test user preference learning"""
        user_id = 'user_123'
        
        result = await learning_service.learn_user_preferences(user_id, sample_interaction_data)
        
        assert result is not None
        assert 'preferences_learned' in result
        assert 'confidence_scores' in result
        assert 'interaction_count' in result
        assert result['interaction_count'] == len(sample_interaction_data)
        
        # Check if preferences were stored
        assert user_id in learning_service.user_preferences
        preferences = learning_service.user_preferences[user_id]
        assert len(preferences) > 0
    
    @pytest.mark.asyncio
    async def test_predict_user_preferences(self, learning_service, sample_interaction_data):
        """Test user preference prediction"""
        user_id = 'user_123'
        
        # First learn some preferences
        await learning_service.learn_user_preferences(user_id, sample_interaction_data)
        
        # Test prediction
        content_metadata = {
            'style': 'abstract',
            'mood': 'calm',
            'duration': 60
        }
        
        prediction = await learning_service.predict_user_preferences(user_id, content_metadata)
        
        assert prediction is not None
        assert 'predicted_rating' in prediction
        assert 'confidence' in prediction
        assert 'reasoning' in prediction
        assert 0.0 <= prediction['predicted_rating'] <= 1.0
        assert 0.0 <= prediction['confidence'] <= 1.0
    
    @pytest.mark.asyncio
    async def test_analyze_interaction_patterns(self, learning_service, sample_interaction_data):
        """Test interaction pattern analysis"""
        user_id = 'user_123'
        
        # Add interaction data
        await learning_service.learn_user_preferences(user_id, sample_interaction_data)
        
        analysis_params = {
            'time_window_days': 30,
            'pattern_types': ['temporal', 'content', 'behavioral'],
            'min_interactions': 1
        }
        
        patterns = await learning_service.analyze_interaction_patterns(user_id, analysis_params)
        
        assert patterns is not None
        assert 'temporal_patterns' in patterns
        assert 'content_patterns' in patterns
        assert 'behavioral_patterns' in patterns
        assert 'pattern_strength' in patterns
    
    @pytest.mark.asyncio
    async def test_generate_personalized_recommendations(self, learning_service, sample_interaction_data):
        """Test personalized recommendation generation"""
        user_id = 'user_123'
        
        # Learn preferences first
        await learning_service.learn_user_preferences(user_id, sample_interaction_data)
        
        content_pool = [
            {
                'content_id': 'video_003',
                'metadata': {'style': 'abstract', 'mood': 'calm'},
                'available': True
            },
            {
                'content_id': 'video_004', 
                'metadata': {'style': 'realistic', 'mood': 'energetic'},
                'available': True
            }
        ]
        
        context = {
            'time_of_day': 'evening',
            'weather': 'sunny',
            'user_mood': 'relaxed'
        }
        
        recommendations = await learning_service.generate_personalized_recommendations(
            user_id, content_pool, context
        )
        
        assert recommendations is not None
        assert 'recommended_content' in recommendations
        assert 'recommendation_scores' in recommendations
        assert 'personalization_factors' in recommendations
        assert len(recommendations['recommended_content']) <= len(content_pool)
    
    @pytest.mark.asyncio
    async def test_track_preference_evolution(self, learning_service):
        """Test preference evolution tracking"""
        user_id = 'user_123'
        tracking_params = {
            'time_window_days': 30,
            'evolution_metrics': ['preference_shift', 'stability', 'diversity'],
            'min_data_points': 2
        }
        
        # Mock some historical preferences
        learning_service.user_preferences[user_id] = {
            'style': UserPreference(
                user_id=user_id,
                preference_type=PreferenceType.STYLE,
                preference_value='abstract',
                confidence=0.8,
                context_factors={},
                last_updated=datetime.now()
            )
        }
        
        evolution = await learning_service.track_preference_evolution(user_id, tracking_params)
        
        assert evolution is not None
        assert 'evolution_summary' in evolution
        assert 'preference_changes' in evolution
        assert 'stability_metrics' in evolution
        assert 'trend_analysis' in evolution
    
    @pytest.mark.asyncio
    async def test_calculate_preference_confidence(self, learning_service, sample_interaction_data):
        """Test preference confidence calculation"""
        user_id = 'user_123'
        
        # Learn preferences
        await learning_service.learn_user_preferences(user_id, sample_interaction_data)
        
        confidence_params = {
            'confidence_factors': ['interaction_count', 'consistency', 'recency'],
            'weight_distribution': {'interaction_count': 0.4, 'consistency': 0.4, 'recency': 0.2}
        }
        
        confidence = await learning_service.calculate_preference_confidence(user_id, confidence_params)
        
        assert confidence is not None
        assert 'overall_confidence' in confidence
        assert 'confidence_breakdown' in confidence
        assert 'factors_analysis' in confidence
        assert 0.0 <= confidence['overall_confidence'] <= 1.0
    
    @pytest.mark.asyncio
    async def test_detect_preference_shifts(self, learning_service):
        """Test preference shift detection"""
        user_id = 'user_123'
        
        # Mock preference history
        old_preference = UserPreference(
            user_id=user_id,
            preference_type=PreferenceType.STYLE,
            preference_value='realistic',
            confidence=0.7,
            context_factors={},
            last_updated=datetime.now() - timedelta(days=15)
        )
        
        new_preference = UserPreference(
            user_id=user_id,
            preference_type=PreferenceType.STYLE,
            preference_value='abstract',
            confidence=0.8,
            context_factors={},
            last_updated=datetime.now()
        )
        
        learning_service.user_preferences[user_id] = {'style': new_preference}
        
        detection_params = {
            'sensitivity': 0.3,
            'time_window_days': 30,
            'shift_types': ['preference_value', 'confidence_level', 'context_dependency']
        }
        
        shifts = await learning_service.detect_preference_shifts(user_id, detection_params)
        
        assert shifts is not None
        assert 'shifts_detected' in shifts
        assert 'shift_details' in shifts
        assert 'shift_significance' in shifts
    
    @pytest.mark.asyncio
    async def test_cluster_similar_users(self, learning_service):
        """Test user clustering functionality"""
        user_id = 'user_123'
        
        # Mock multiple users with preferences
        for i, uid in enumerate(['user_123', 'user_456', 'user_789']):
            learning_service.user_preferences[uid] = {
                'style': UserPreference(
                    user_id=uid,
                    preference_type=PreferenceType.STYLE,
                    preference_value=['abstract', 'realistic', 'abstract'][i],
                    confidence=0.8,
                    context_factors={},
                    last_updated=datetime.now()
                )
            }
        
        clustering_params = {
            'similarity_threshold': 0.7,
            'min_cluster_size': 2,
            'max_clusters': 5,
            'feature_dimensions': ['style', 'mood']
        }
        
        clusters = await learning_service.cluster_similar_users(user_id, clustering_params)
        
        assert clusters is not None
        assert 'user_cluster_id' in clusters
        assert 'cluster_members' in clusters
        assert 'cluster_characteristics' in clusters
        assert 'similarity_scores' in clusters
    
    @pytest.mark.asyncio
    async def test_predict_engagement_score(self, learning_service, sample_interaction_data):
        """Test engagement score prediction"""
        user_id = 'user_123'
        
        # Learn preferences first
        await learning_service.learn_user_preferences(user_id, sample_interaction_data)
        
        content_candidates = [
            {
                'content_id': 'video_test',
                'metadata': {'style': 'abstract', 'mood': 'calm', 'duration': 90},
                'context': {'time_of_day': 'evening', 'weather': 'clear'}
            }
        ]
        
        prediction_params = {
            'prediction_model': 'hybrid',
            'context_weight': 0.3,
            'preference_weight': 0.7
        }
        
        scores = await learning_service.predict_engagement_score(
            user_id, content_candidates, prediction_params
        )
        
        assert scores is not None
        assert len(scores) == len(content_candidates)
        for score in scores:
            assert 'content_id' in score
            assert 'engagement_score' in score
            assert 'prediction_confidence' in score
            assert 0.0 <= score['engagement_score'] <= 1.0
    
    @pytest.mark.asyncio
    async def test_validate_learning_accuracy(self, learning_service):
        """Test learning accuracy validation"""
        user_id = 'user_123'
        
        validation_params = {
            'test_period_days': 7,
            'validation_metrics': ['precision', 'recall', 'f1_score'],
            'cross_validation_folds': 3
        }
        
        # Mock some training data
        learning_service.interaction_history = [
            InteractionRecord(
                user_id=user_id,
                content_id=f'video_{i}',
                interaction_type=InteractionType.LIKE if i % 2 == 0 else InteractionType.SKIP,
                duration_watched=60 + i * 10,
                total_duration=120,
                content_metadata={'style': 'abstract' if i % 2 == 0 else 'realistic'},
                timestamp=datetime.now() - timedelta(days=i),
                context={}
            ) for i in range(10)
        ]
        
        accuracy = await learning_service.validate_learning_accuracy(user_id, validation_params)
        
        assert accuracy is not None
        assert 'overall_accuracy' in accuracy
        assert 'metric_scores' in accuracy
        assert 'validation_details' in accuracy
        assert 0.0 <= accuracy['overall_accuracy'] <= 1.0
    
    @pytest.mark.asyncio
    async def test_adapt_to_feedback(self, learning_service):
        """Test feedback adaptation"""
        user_id = 'user_123'
        
        feedback_data = {
            'content_id': 'video_feedback_test',
            'feedback_type': 'rating',
            'feedback_value': 4.5,  # 5-star rating
            'feedback_context': {
                'recommendation_accuracy': 'high',
                'content_relevance': 'very_relevant',
                'timing_appropriateness': 'perfect'
            }
        }
        
        adaptation_params = {
            'learning_rate': 0.1,
            'feedback_weight': 0.8,
            'adaptation_scope': ['preferences', 'algorithms', 'parameters']
        }
        
        result = await learning_service.adapt_to_feedback(
            user_id, feedback_data, adaptation_params
        )
        
        assert result is not None
        assert 'adaptation_applied' in result
        assert 'updated_preferences' in result
        assert 'algorithm_adjustments' in result
        assert 'confidence_changes' in result
    
    @pytest.mark.asyncio
    async def test_export_import_user_profile(self, learning_service, sample_interaction_data):
        """Test user profile export and import"""
        user_id = 'user_123'
        
        # Learn some preferences
        await learning_service.learn_user_preferences(user_id, sample_interaction_data)
        
        # Test export
        export_options = {
            'include_preferences': True,
            'include_history': True,
            'include_models': False,
            'format': 'json',
            'anonymize': False
        }
        
        exported_profile = await learning_service.export_user_profile(user_id, export_options)
        
        assert exported_profile is not None
        assert 'user_id' in exported_profile
        assert 'preferences' in exported_profile
        assert 'export_metadata' in exported_profile
        
        # Test import
        import_options = {
            'merge_strategy': 'update',
            'validate_data': True,
            'backup_existing': True
        }
        
        import_result = await learning_service.import_user_profile(
            exported_profile, import_options
        )
        
        assert import_result is not None
        assert 'import_status' in import_result
        assert 'imported_preferences' in import_result
        assert import_result['import_status'] == 'success'
    
    @pytest.mark.asyncio
    async def test_reset_user_preferences(self, learning_service, sample_interaction_data):
        """Test user preference reset"""
        user_id = 'user_123'
        
        # Learn preferences first
        await learning_service.learn_user_preferences(user_id, sample_interaction_data)
        assert user_id in learning_service.user_preferences
        
        # Test selective reset
        reset_options = {
            'reset_scope': 'preferences_only',
            'preserve_history': True,
            'reset_confirmation': True
        }
        
        reset_result = await learning_service.reset_user_preferences(user_id, reset_options)
        
        assert reset_result is not None
        assert 'reset_status' in reset_result
        assert 'items_reset' in reset_result
        assert reset_result['reset_status'] == 'success'
        
        # Verify preferences were reset but history preserved
        assert len(learning_service.user_preferences.get(user_id, {})) == 0
    
    def test_calculate_preference_match_score(self, learning_service):
        """Test preference match score calculation"""
        user_id = 'user_123'
        
        # Mock user preferences
        learning_service.user_preferences[user_id] = {
            'style': UserPreference(
                user_id=user_id,
                preference_type=PreferenceType.STYLE,
                preference_value='abstract',
                confidence=0.8,
                context_factors={},
                last_updated=datetime.now()
            )
        }
        
        content_metadata = {
            'style': 'abstract',
            'mood': 'calm',
            'duration': 60
        }
        
        score = learning_service._calculate_preference_match_score(user_id, content_metadata)
        
        assert isinstance(score, (int, float))
        assert 0.0 <= score <= 1.0
    
    def test_calculate_novelty_score(self, learning_service):
        """Test novelty score calculation"""
        user_id = 'user_123'
        
        # Mock interaction history
        learning_service.interaction_history = [
            InteractionRecord(
                user_id=user_id,
                content_id='video_001',
                interaction_type=InteractionType.LIKE,
                duration_watched=90,
                total_duration=120,
                content_metadata={'style': 'abstract'},
                timestamp=datetime.now(),
                context={}
            )
        ]
        
        content_data = {
            'content_id': 'video_new',
            'metadata': {'style': 'realistic'}  # Different from history
        }
        
        novelty_score = learning_service._calculate_novelty_score(user_id, content_data)
        
        assert isinstance(novelty_score, (int, float))
        assert 0.0 <= novelty_score <= 1.0


class TestLearningServiceAdvanced:
    """Advanced unit tests for LearningService machine learning features"""
    
    @pytest.fixture
    def learning_service_with_data(self):
        """Create LearningService with sample data"""
        service = LearningService()
        
        # Add sample users and preferences
        for i, user_id in enumerate(['user_1', 'user_2', 'user_3']):
            service.user_preferences[user_id] = {
                'style': UserPreference(
                    user_id=user_id,
                    preference_type=PreferenceType.STYLE,
                    preference_value=['abstract', 'realistic', 'cinematic'][i],
                    confidence=0.7 + i * 0.1,
                    context_factors={},
                    last_updated=datetime.now()
                )
            }
        
        return service
    
    def test_create_user_feature_vector(self, learning_service_with_data):
        """Test user feature vector creation"""
        user_id = 'user_1'
        feature_dimensions = ['style', 'mood', 'timing']
        
        vector = learning_service_with_data._create_user_feature_vector(user_id, feature_dimensions)
        
        assert vector is not None
        assert isinstance(vector, (list, np.ndarray))
        assert len(vector) > 0
    
    def test_calculate_user_similarity(self, learning_service_with_data):
        """Test user similarity calculation"""
        user1_id = 'user_1'
        user2_id = 'user_2'
        
        similarity = learning_service_with_data._calculate_user_similarity(user1_id, user2_id)
        
        assert isinstance(similarity, (int, float))
        assert 0.0 <= similarity <= 1.0
    
    @pytest.mark.asyncio
    async def test_optimize_learning_parameters(self, learning_service_with_data):
        """Test learning parameter optimization"""
        user_id = 'user_1'
        
        optimization_config = {
            'algorithm': LearningAlgorithm.HYBRID,
            'learning_rate': 0.01,
            'regularization': 0.1,
            'feature_weights': {
                'temporal': 0.3,
                'content': 0.4,
                'contextual': 0.3
            },
            'optimization_objective': 'maximize_engagement'
        }
        
        optimized = await learning_service_with_data.optimize_learning_parameters(
            user_id, optimization_config
        )
        
        assert optimized is not None
        assert 'optimized_algorithm' in optimized
        assert 'optimized_learning_rate' in optimized
        assert 'optimized_weights' in optimized
        assert 'performance_improvement' in optimized


if __name__ == "__main__":
    pytest.main([__file__, "-v"])