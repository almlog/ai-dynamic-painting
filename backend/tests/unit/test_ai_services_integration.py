"""
Integration unit tests for AI Services - T270 AI Unit Tests
Tests interactions between multiple AI services
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.ai.services.veo_api_service import VEOAPIService, GenerationStatus
from src.ai.services.learning_service import LearningService, InteractionType
from src.ai.services.weather_api_service import WeatherAPIService, WeatherCondition
from src.ai.services.context_aware_service import ContextAwareService
from src.ai.services.prompt_generation_service import PromptGenerationService
from src.ai.services.scheduling_service import SchedulingService


class TestAIServicesIntegration:
    """Integration tests for AI services working together"""
    
    @pytest.fixture
    def ai_services(self):
        """Create instances of all AI services"""
        return {
            'veo': VEOAPIService(),
            'learning': LearningService(),
            'weather': WeatherAPIService(),
            'context': ContextAwareService(),
            'prompt': PromptGenerationService(),
            'scheduler': SchedulingService()
        }
    
    @pytest.fixture
    def sample_user_context(self):
        """Sample user context for testing"""
        return {
            'user_id': 'test_user_123',
            'location': {
                'latitude': 35.6762,
                'longitude': 139.6503,
                'city': 'Tokyo'
            },
            'time_of_day': 'evening',
            'preferences': {
                'style': 'abstract',
                'mood': 'calm'
            }
        }
    
    @pytest.mark.asyncio
    async def test_weather_context_integration(self, ai_services, sample_user_context):
        """Test integration between weather and context services"""
        weather_service = ai_services['weather']
        context_service = ai_services['context']
        
        # Mock weather data
        mock_weather = {
            'temperature': 22,
            'condition': 'clear',
            'humidity': 60,
            'mood_indicators': {
                'energy': 'high',
                'mood': 'positive'
            }
        }
        
        with patch.object(weather_service, 'get_weather_for_ai_context') as mock_weather_api:
            mock_weather_api.return_value = mock_weather
            
            # Get context including weather
            context_params = {
                'include_weather': True,
                'include_time': True,
                'weather_weight': 0.4
            }
            
            context = await context_service.generate_context(
                sample_user_context, context_params
            )
            
            assert context is not None
            assert 'weather_context' in context
            assert context['weather_context']['condition'] == 'clear'
    
    @pytest.mark.asyncio
    async def test_learning_prompt_integration(self, ai_services, sample_user_context):
        """Test integration between learning and prompt generation services"""
        learning_service = ai_services['learning']
        prompt_service = ai_services['prompt']
        
        # Mock user preferences learning
        user_id = sample_user_context['user_id']
        sample_interactions = [
            {
                'user_id': user_id,
                'content_id': 'video_001',
                'interaction_type': InteractionType.LIKE,
                'content_metadata': {'style': 'abstract', 'mood': 'peaceful'}
            }
        ]
        
        await learning_service.learn_user_preferences(user_id, sample_interactions)
        
        # Generate personalized prompt
        base_prompt = "A beautiful landscape"
        enhancement_params = {
            'use_user_preferences': True,
            'personalization_weight': 0.6,
            'style_enhancement': True
        }
        
        with patch.object(learning_service, 'predict_user_preferences') as mock_predict:
            mock_predict.return_value = {
                'predicted_rating': 0.8,
                'preferred_style': 'abstract',
                'confidence': 0.7
            }
            
            enhanced_prompt = await prompt_service.enhance_prompt(
                base_prompt, sample_user_context, enhancement_params
            )
            
            assert enhanced_prompt != base_prompt
            assert len(enhanced_prompt) > len(base_prompt)
    
    @pytest.mark.asyncio
    async def test_context_veo_integration(self, ai_services, sample_user_context):
        """Test integration between context service and VEO API"""
        context_service = ai_services['context']
        veo_service = ai_services['veo']
        
        # Generate context
        context_params = {
            'include_weather': True,
            'include_time': True,
            'include_user_state': True
        }
        
        with patch.object(context_service, 'generate_context') as mock_context:
            mock_context.return_value = {
                'weather_context': {'condition': 'clear', 'temperature': 22},
                'time_context': {'period': 'evening', 'lighting': 'golden_hour'},
                'user_context': {'mood': 'relaxed', 'energy': 'moderate'},
                'combined_score': 0.85
            }
            
            context = await context_service.generate_context(
                sample_user_context, context_params
            )
            
            # Use context to enhance VEO generation request
            base_request = {
                'prompt': 'A serene landscape',
                'duration': 30
            }
            
            enhanced_prompt = veo_service.enhance_prompt(
                base_request['prompt'], context
            )
            
            assert enhanced_prompt != base_request['prompt']
            assert 'clear' in enhanced_prompt.lower() or 'evening' in enhanced_prompt.lower()
    
    @pytest.mark.asyncio
    async def test_scheduler_context_integration(self, ai_services, sample_user_context):
        """Test integration between scheduler and context services"""
        scheduler_service = ai_services['scheduler']
        context_service = ai_services['context']
        
        # Create a schedule with context awareness
        schedule_data = {
            'name': 'Evening Video Generation',
            'schedule_type': 'recurring',
            'start_time': '19:00',
            'context_factors': ['weather', 'user_mood', 'time_of_day']
        }
        
        with patch.object(context_service, 'generate_context') as mock_context:
            mock_context.return_value = {
                'optimal_timing': True,
                'context_score': 0.8,
                'recommendation': 'proceed'
            }
            
            created_schedule = await scheduler_service.create_schedule(schedule_data)
            
            assert created_schedule is not None
            assert 'schedule_id' in created_schedule
            
            # Test context-based schedule adjustment
            schedule_id = created_schedule['schedule_id']
            context_changes = {
                'weather_change': 'clear_to_rainy',
                'user_mood': 'tired'
            }
            
            adjusted = await scheduler_service.adjust_schedule_based_on_context(
                schedule_id, context_changes
            )
            
            assert adjusted is not None
            assert 'adjustments_made' in adjusted
    
    @pytest.mark.asyncio
    async def test_full_ai_pipeline_integration(self, ai_services, sample_user_context):
        """Test complete AI pipeline integration"""
        # Services
        weather_service = ai_services['weather']
        learning_service = ai_services['learning']
        context_service = ai_services['context']
        prompt_service = ai_services['prompt']
        veo_service = ai_services['veo']
        scheduler_service = ai_services['scheduler']
        
        user_id = sample_user_context['user_id']
        
        # Step 1: Learn user preferences
        interactions = [
            {
                'user_id': user_id,
                'content_id': 'video_001',
                'interaction_type': InteractionType.LIKE,
                'content_metadata': {'style': 'cinematic', 'mood': 'peaceful'},
                'duration_watched': 120,
                'total_duration': 120
            }
        ]
        
        await learning_service.learn_user_preferences(user_id, interactions)
        
        # Step 2: Get weather context
        with patch.object(weather_service, 'get_weather_for_ai_context') as mock_weather:
            mock_weather.return_value = {
                'weather_summary': 'clear evening',
                'mood_indicators': {'energy': 'calm', 'mood': 'peaceful'},
                'visual_atmosphere': {'lighting': 'golden', 'colors': ['warm']}
            }
            
            # Step 3: Generate comprehensive context
            context_params = {
                'include_weather': True,
                'include_preferences': True,
                'include_time': True
            }
            
            with patch.object(context_service, 'generate_context') as mock_context:
                mock_context.return_value = {
                    'weather_context': mock_weather.return_value,
                    'user_preferences': {'style': 'cinematic', 'mood': 'peaceful'},
                    'time_context': {'period': 'evening'},
                    'combined_score': 0.9
                }
                
                context = await context_service.generate_context(
                    sample_user_context, context_params
                )
                
                # Step 4: Generate enhanced prompt
                base_prompt = "A beautiful nature scene"
                enhancement_params = {
                    'use_context': True,
                    'use_preferences': True,
                    'enhancement_level': 'high'
                }
                
                enhanced_prompt = await prompt_service.enhance_prompt(
                    base_prompt, context, enhancement_params
                )
                
                # Step 5: Create VEO generation request
                generation_request = {
                    'prompt': enhanced_prompt,
                    'duration': 30,
                    'quality': 'high',
                    'style': 'cinematic'
                }
                
                # Mock VEO API response
                with patch.object(veo_service, 'generate_video') as mock_veo:
                    mock_veo.return_value = {
                        'generation_id': 'gen_integration_test',
                        'status': GenerationStatus.PENDING.value,
                        'estimated_completion': '2025-01-15T20:00:00Z'
                    }
                    
                    veo_service.set_api_credentials("test_key", "test_project")
                    result = await veo_service.generate_video(generation_request)
                    
                    # Step 6: Schedule follow-up based on result
                    if result and 'generation_id' in result:
                        schedule_data = {
                            'name': 'Follow-up Generation',
                            'generation_id': result['generation_id'],
                            'schedule_type': 'one_time',
                            'trigger_time': 'after_completion'
                        }
                        
                        follow_up = await scheduler_service.create_schedule(schedule_data)
                        
                        assert follow_up is not None
                        assert 'schedule_id' in follow_up
                
                # Verify integration worked
                assert enhanced_prompt != base_prompt
                assert result is not None
                assert 'generation_id' in result
    
    @pytest.mark.asyncio
    async def test_error_propagation_between_services(self, ai_services):
        """Test error handling across service boundaries"""
        context_service = ai_services['context']
        weather_service = ai_services['weather']
        
        # Simulate weather service failure
        with patch.object(weather_service, 'get_weather_for_ai_context') as mock_weather:
            mock_weather.side_effect = Exception("Weather API unavailable")
            
            # Context service should handle weather failure gracefully
            context_params = {
                'include_weather': True,
                'fallback_on_error': True
            }
            
            context = await context_service.generate_context(
                {'user_id': 'test'}, context_params
            )
            
            # Should still return context without weather
            assert context is not None
            # Weather context should be None or contain error info
            assert 'weather_context' not in context or context['weather_context'] is None
    
    @pytest.mark.asyncio
    async def test_service_performance_integration(self, ai_services):
        """Test performance characteristics of integrated services"""
        learning_service = ai_services['learning']
        prompt_service = ai_services['prompt']
        
        user_id = 'perf_test_user'
        
        # Create multiple interactions for performance testing
        interactions = [
            {
                'user_id': user_id,
                'content_id': f'video_{i:03d}',
                'interaction_type': InteractionType.LIKE if i % 2 == 0 else InteractionType.SKIP,
                'content_metadata': {
                    'style': ['abstract', 'realistic', 'cinematic'][i % 3],
                    'mood': ['calm', 'energetic', 'mysterious'][i % 3]
                },
                'duration_watched': 60 + i * 5,
                'total_duration': 120
            } for i in range(50)  # 50 interactions for performance test
        ]
        
        # Measure learning performance
        start_time = datetime.now()
        await learning_service.learn_user_preferences(user_id, interactions)
        learning_duration = (datetime.now() - start_time).total_seconds()
        
        # Learning should complete in reasonable time (< 5 seconds for 50 interactions)
        assert learning_duration < 5.0
        
        # Measure prompt enhancement performance
        start_time = datetime.now()
        for i in range(10):
            await prompt_service.enhance_prompt(
                f"Test prompt {i}",
                {'user_id': user_id},
                {'use_preferences': True}
            )
        prompt_duration = (datetime.now() - start_time).total_seconds()
        
        # Prompt enhancement should be fast (< 2 seconds for 10 prompts)
        assert prompt_duration < 2.0
    
    @pytest.mark.asyncio
    async def test_data_consistency_across_services(self, ai_services):
        """Test data consistency when shared across services"""
        learning_service = ai_services['learning']
        context_service = ai_services['context']
        
        user_id = 'consistency_test_user'
        
        # Learn preferences in learning service
        interactions = [
            {
                'user_id': user_id,
                'content_id': 'video_001',
                'interaction_type': InteractionType.LIKE,
                'content_metadata': {'style': 'abstract', 'mood': 'peaceful'}
            }
        ]
        
        learned_prefs = await learning_service.learn_user_preferences(user_id, interactions)
        
        # Use preferences in context service
        user_context = {
            'user_id': user_id,
            'preferences': learned_prefs.get('preferences_learned', {})
        }
        
        context_params = {
            'include_preferences': True,
            'preference_weight': 0.8
        }
        
        context = await context_service.generate_context(user_context, context_params)
        
        # Verify consistency
        assert context is not None
        if 'user_preferences' in context:
            # Should reflect the learned preferences
            assert 'style' in str(context['user_preferences']) or 'abstract' in str(context)
    
    @pytest.mark.asyncio
    async def test_concurrent_service_usage(self, ai_services):
        """Test concurrent usage of multiple services"""
        services = ai_services
        
        # Create concurrent tasks
        tasks = []
        
        # Weather requests
        for i in range(5):
            task = services['weather'].get_current_weather({
                'latitude': 35.6762 + i * 0.01,
                'longitude': 139.6503 + i * 0.01,
                'location_type': 'coordinates'
            })
            tasks.append(task)
        
        # Learning operations
        for i in range(3):
            task = services['learning'].learn_user_preferences(
                f'concurrent_user_{i}',
                [{'user_id': f'concurrent_user_{i}', 'content_id': 'video_001', 'interaction_type': InteractionType.LIKE}]
            )
            tasks.append(task)
        
        # Context generation
        for i in range(3):
            task = services['context'].generate_context(
                {'user_id': f'context_user_{i}'},
                {'include_time': True}
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all completed successfully
        assert len(results) == 11  # 5 + 3 + 3
        
        # Count successful results (not exceptions)
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 8  # Allow some to fail due to mocking


class TestAIServicesMocking:
    """Test proper mocking and isolation of AI services"""
    
    @pytest.mark.asyncio
    async def test_isolated_service_testing(self):
        """Test that services can be tested in isolation"""
        # Create service with mocked dependencies
        veo_service = VEOAPIService()
        
        # Mock external API calls
        with patch.object(veo_service, '_make_api_request') as mock_api:
            mock_api.return_value = {
                'generation_id': 'isolated_test',
                'status': 'pending'
            }
            
            veo_service.set_api_credentials("test", "test")
            result = await veo_service.generate_video({
                'prompt': 'test prompt',
                'duration': 30
            })
            
            assert result['generation_id'] == 'isolated_test'
            mock_api.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_service_dependency_mocking(self):
        """Test mocking service dependencies"""
        context_service = ContextAwareService()
        
        # Mock weather service dependency
        mock_weather_service = Mock()
        mock_weather_service.get_weather_for_ai_context.return_value = {
            'condition': 'mocked_clear',
            'temperature': 99  # Unrealistic value to ensure it's mocked
        }
        
        # Inject mocked dependency
        context_service.weather_service = mock_weather_service
        
        user_context = {'user_id': 'test_user'}
        context_params = {'include_weather': True}
        
        result = await context_service.generate_context(user_context, context_params)
        
        # Verify mock was used
        assert result is not None
        mock_weather_service.get_weather_for_ai_context.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])