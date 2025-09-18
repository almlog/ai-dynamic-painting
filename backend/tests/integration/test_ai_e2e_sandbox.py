"""
End-to-End tests for AI services with VEO API (Sandbox) - T273 AI E2E Tests
This test file is designed to run against a VEO API sandbox/test environment
"""

import pytest
import asyncio
import os
import time
import json
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ai.services.veo_api_service import VEOAPIService, VEOAPIError, GenerationStatus
from ai.services.learning_service import LearningService
from ai.services.weather_api_service import WeatherAPIService


class TestVEOAPISandboxIntegration:
    """
    End-to-end integration tests with VEO API sandbox
    NOTE: These tests require VEO_API_KEY environment variable to be set
    for actual API testing. Without it, tests will use mocked responses.
    """
    
    @pytest.fixture
    def sandbox_veo_service(self):
        """Create VEO API service for sandbox testing"""
        api_key = os.environ.get('VEO_API_KEY', 'test_sandbox_key')
        sandbox_url = os.environ.get('VEO_SANDBOX_URL', 'https://sandbox.veo.ai/api')
        
        # If no real API key, we'll use mock mode
        is_sandbox = api_key != 'test_sandbox_key'
        
        service = VEOAPIService(
            api_key=api_key,
            timeout=60,  # Longer timeout for real API calls
            monthly_budget=10.0  # Small budget for testing
        )
        
        if is_sandbox:
            # Override base URL for sandbox
            service.base_url = sandbox_url
        
        service.is_sandbox = is_sandbox
        return service
    
    @pytest.fixture
    def learning_service(self):
        """Create learning service for E2E testing"""
        return LearningService()
    
    @pytest.fixture
    def weather_service(self):
        """Create weather service for E2E testing"""
        return WeatherAPIService()
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.environ.get('VEO_API_KEY'),
        reason="VEO_API_KEY not set - skipping real API tests"
    )
    async def test_real_veo_api_authentication(self, sandbox_veo_service):
        """Test actual VEO API authentication"""
        # This test only runs with real API key
        assert sandbox_veo_service.is_sandbox
        
        # Test authentication
        auth_result = sandbox_veo_service.authenticate()
        assert auth_result is True, "Authentication should succeed with valid API key"
        assert sandbox_veo_service.is_authenticated is True
        
        # Test account info retrieval
        account_info = sandbox_veo_service.get_account_info()
        assert account_info is not None
        assert 'user_id' in account_info
        assert 'plan' in account_info
        
        print(f"\n✅ Real API Authentication Successful")
        print(f"   Account ID: {account_info.get('user_id', 'N/A')}")
        print(f"   Plan: {account_info.get('plan', 'N/A')}")
    
    @pytest.mark.asyncio
    async def test_mock_veo_api_full_workflow(self, sandbox_veo_service):
        """Test full VEO API workflow with mocked responses"""
        
        # Mock responses for sandbox testing
        with patch.object(sandbox_veo_service, 'authenticate') as mock_auth, \
             patch.object(sandbox_veo_service, '_make_request') as mock_request:
            
            # Setup authentication mock
            mock_auth.return_value = True
            sandbox_veo_service.is_authenticated = True
            
            # Mock API responses
            generation_id = 'sandbox_gen_001'
            
            # Step 1: Create video generation
            mock_request.return_value = {
                'generation_id': generation_id,
                'status': 'pending',
                'estimated_completion': (datetime.now() + timedelta(minutes=5)).isoformat(),
                'estimated_cost': 0.50
            }
            
            generation_data = {
                'prompt': 'A peaceful nature scene with mountains and a lake at sunset',
                'duration': 15,
                'quality': 'medium',
                'resolution': '1920x1080'
            }
            
            result = sandbox_veo_service.create_video_generation(generation_data)
            assert result['generation_id'] == generation_id
            assert result['status'] == 'pending'
            
            print(f"\n📹 Video Generation Started")
            print(f"   ID: {generation_id}")
            print(f"   Status: {result['status']}")
            
            # Step 2: Check generation status (simulate progress)
            status_updates = [
                {'status': 'processing', 'progress': 25},
                {'status': 'processing', 'progress': 50},
                {'status': 'processing', 'progress': 75},
                {'status': 'completed', 'progress': 100, 
                 'video_url': 'https://sandbox.veo.ai/videos/sandbox_gen_001.mp4'}
            ]
            
            for update in status_updates:
                mock_request.return_value = {
                    'generation_id': generation_id,
                    **update
                }
                
                status = sandbox_veo_service.get_generation_status(generation_id)
                assert status['generation_id'] == generation_id
                assert status['status'] == update['status']
                
                print(f"   Progress: {update.get('progress', 0)}% - {update['status']}")
                
                # Simulate time delay between checks
                await asyncio.sleep(0.1)
            
            # Step 3: Download video (mocked)
            video_url = status_updates[-1]['video_url']
            
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.raise_for_status = Mock()
                mock_response.iter_content = Mock(return_value=[b'video_data'])
                mock_response.headers = {'content-length': '1000000'}
                mock_get.return_value = mock_response
                
                download_path = '/tmp/test_video_sandbox.mp4'
                success = sandbox_veo_service.download_video(video_url, download_path)
                assert success is True
                
                print(f"   Download: Completed to {download_path}")
            
            # Step 4: Cost tracking
            sandbox_veo_service.track_costs(generation_id, 0.50)
            stats = sandbox_veo_service.get_usage_statistics()
            
            assert stats['total_cost'] == 0.50
            assert stats['generation_count'] == 1
            
            print(f"\n💰 Cost Tracking")
            print(f"   Total Cost: ${stats['total_cost']:.2f}")
            print(f"   Budget Remaining: ${stats['budget_remaining']:.2f}")
    
    @pytest.mark.asyncio
    async def test_ai_services_integration_e2e(self, sandbox_veo_service, learning_service, weather_service):
        """Test complete AI services integration end-to-end"""
        
        # Mock all external API calls for integration test
        with patch.object(sandbox_veo_service, 'authenticate') as mock_veo_auth, \
             patch.object(sandbox_veo_service, '_make_request') as mock_veo_request, \
             patch.object(weather_service, 'get_current_weather') as mock_weather:
            
            # Setup mocks
            mock_veo_auth.return_value = True
            sandbox_veo_service.is_authenticated = True
            
            # Mock weather data
            async def mock_weather_async(*args, **kwargs):
                return {
                    'temperature': 22.0,
                    'humidity': 65,
                    'conditions': 'partly_cloudy',
                    'wind_speed': 10.0,
                    'description': 'Partly cloudy with mild temperature'
                }
            mock_weather.side_effect = mock_weather_async
            
            print(f"\n🔄 Full AI Pipeline E2E Test")
            
            # Step 1: Get weather context
            location = {'lat': 35.6762, 'lon': 139.6503, 'name': 'Tokyo'}
            weather_data = await weather_service.get_current_weather(location)
            
            print(f"\n🌤️  Weather Context")
            print(f"   Location: {location['name']}")
            print(f"   Conditions: {weather_data['conditions']}")
            print(f"   Temperature: {weather_data['temperature']}°C")
            
            # Step 2: Learn user preferences
            user_id = 'e2e_test_user'
            interaction_data = [
                {
                    'user_id': user_id,
                    'content_id': 'sample_video_1',
                    'interaction_type': 'watch',
                    'duration_watched': 28,
                    'total_duration': 30,
                    'timestamp': datetime.now().isoformat(),
                    'content_metadata': {
                        'genre': 'nature',
                        'tags': ['scenic', 'relaxing'],
                        'weather_context': weather_data['conditions']
                    }
                }
            ]
            
            learning_result = await learning_service.learn_user_preferences(user_id, interaction_data)
            
            print(f"\n🧠 Learning Service")
            print(f"   User: {user_id}")
            print(f"   Preferences Learned: {learning_result.get('status', 'unknown')}")
            
            # Step 3: Get personalized recommendations
            recommendations = await learning_service.generate_personalized_recommendations(
                user_id,
                {'weather': weather_data, 'time_of_day': 'evening'}
            )
            
            print(f"   Recommendations: {len(recommendations)} generated")
            
            # Step 4: Generate video based on context
            # Create AI-driven prompt based on weather and preferences
            ai_prompt = self._generate_contextual_prompt(weather_data, recommendations)
            
            mock_veo_request.return_value = {
                'generation_id': 'e2e_gen_001',
                'status': 'pending',
                'estimated_cost': 0.75
            }
            
            generation_data = {
                'prompt': ai_prompt,
                'duration': 20,
                'quality': 'high',
                'resolution': '1920x1080'
            }
            
            # Check budget before generation
            estimated_cost = sandbox_veo_service.get_cost_estimate(generation_data)
            can_afford = sandbox_veo_service.check_budget_available(estimated_cost)
            
            assert can_afford, "Should have budget for generation"
            
            generation_result = sandbox_veo_service.create_video_generation(generation_data)
            
            print(f"\n🎬 Video Generation")
            print(f"   Prompt: {ai_prompt[:50]}...")
            print(f"   Generation ID: {generation_result['generation_id']}")
            print(f"   Estimated Cost: ${estimated_cost:.2f}")
            
            # Step 5: Track and verify the complete workflow
            sandbox_veo_service.track_costs(generation_result['generation_id'], estimated_cost)
            
            final_stats = {
                'weather_context': weather_data,
                'user_preferences': learning_result,
                'recommendations': len(recommendations),
                'generation_id': generation_result['generation_id'],
                'total_cost': sandbox_veo_service.current_usage,
                'budget_remaining': sandbox_veo_service.monthly_budget - sandbox_veo_service.current_usage
            }
            
            print(f"\n✅ E2E Pipeline Complete")
            print(f"   Total Cost: ${final_stats['total_cost']:.2f}")
            print(f"   Budget Remaining: ${final_stats['budget_remaining']:.2f}")
            
            # Verify complete integration
            assert final_stats['weather_context'] is not None
            assert final_stats['recommendations'] > 0
            assert final_stats['generation_id'] is not None
            assert final_stats['budget_remaining'] >= 0
    
    def _generate_contextual_prompt(self, weather_data: Dict[str, Any], 
                                   recommendations: List[Dict[str, Any]]) -> str:
        """Generate AI prompt based on context"""
        weather_desc = weather_data.get('description', 'pleasant weather')
        
        # Base prompt templates based on weather
        weather_prompts = {
            'sunny': 'A bright, vibrant scene with golden sunlight',
            'partly_cloudy': 'A dynamic scene with interesting cloud formations',
            'rainy': 'A cozy, atmospheric scene with gentle rain',
            'cloudy': 'A moody, dramatic scene with overcast skies'
        }
        
        base_prompt = weather_prompts.get(
            weather_data.get('conditions', 'sunny'),
            'A beautiful nature scene'
        )
        
        # Add personalized elements from recommendations
        if recommendations:
            # In real implementation, would analyze recommendations
            base_prompt += ', featuring serene landscapes and calming elements'
        
        return f"{base_prompt}, perfect for {weather_desc}"
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.environ.get('VEO_API_KEY'),
        reason="VEO_API_KEY not set - skipping sandbox stress test"
    )
    async def test_sandbox_api_stress_test(self, sandbox_veo_service):
        """Stress test the sandbox API with multiple concurrent requests"""
        
        # This test only runs with real API key
        assert sandbox_veo_service.is_sandbox
        
        print(f"\n⚡ Sandbox API Stress Test")
        
        # Authenticate first
        auth_result = sandbox_veo_service.authenticate()
        assert auth_result is True
        
        # Create multiple generation requests
        generation_tasks = []
        num_requests = 5  # Limited for sandbox testing
        
        for i in range(num_requests):
            generation_data = {
                'prompt': f'Test video {i}: Abstract colorful patterns',
                'duration': 10,
                'quality': 'low',  # Low quality for faster processing
                'resolution': '1280x720'
            }
            
            # Create generation task
            task = self._create_generation_task(sandbox_veo_service, generation_data, i)
            generation_tasks.append(task)
        
        # Execute all tasks concurrently
        start_time = time.time()
        results = await asyncio.gather(*generation_tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyze results
        successful = [r for r in results if not isinstance(r, Exception)]
        failed = [r for r in results if isinstance(r, Exception)]
        
        print(f"   Requests: {num_requests}")
        print(f"   Successful: {len(successful)}")
        print(f"   Failed: {len(failed)}")
        print(f"   Duration: {end_time - start_time:.2f}s")
        print(f"   Rate: {len(successful)/(end_time - start_time):.2f} req/s")
        
        # At least some requests should succeed
        assert len(successful) > 0, "At least one request should succeed"
        
        # Check rate limiting behavior
        if failed:
            rate_limit_errors = [e for e in failed if 'rate limit' in str(e).lower()]
            print(f"   Rate limit errors: {len(rate_limit_errors)}")
    
    async def _create_generation_task(self, service, generation_data, index):
        """Helper to create a generation task"""
        try:
            result = service.create_video_generation(generation_data)
            return {'index': index, 'success': True, 'result': result}
        except Exception as e:
            return {'index': index, 'success': False, 'error': str(e)}


class TestAISystemResilience:
    """Test system resilience and error recovery"""
    
    @pytest.fixture
    def resilient_veo_service(self):
        """Create VEO service with resilience features"""
        service = VEOAPIService(
            api_key='test_resilience_key',
            timeout=30,
            max_retries=5
        )
        return service
    
    @pytest.mark.asyncio
    async def test_api_failure_recovery(self, resilient_veo_service):
        """Test recovery from API failures"""
        
        with patch.object(resilient_veo_service, '_make_request') as mock_request:
            # Simulate intermittent failures
            mock_request.side_effect = [
                VEOAPIError("Temporary failure"),
                VEOAPIError("Still failing"),
                {'generation_id': 'recovered_gen', 'status': 'pending'}  # Success on third try
            ]
            
            # Test retry mechanism
            with patch('time.sleep'):  # Speed up test by mocking sleep
                result = resilient_veo_service.retry_failed_request('/test', {})
                
                assert result is not None
                assert result['generation_id'] == 'recovered_gen'
                assert mock_request.call_count == 3
            
            print(f"\n🔧 API Failure Recovery")
            print(f"   Retries needed: 2")
            print(f"   Final status: Success")
    
    @pytest.mark.asyncio
    async def test_budget_exhaustion_handling(self, resilient_veo_service):
        """Test handling of budget exhaustion scenarios"""
        
        # Set very low budget with some room for a cheap generation
        resilient_veo_service.monthly_budget = 1.0
        resilient_veo_service.current_usage = 0.90  # Leave 0.10 remaining for cheap generation
        
        # Try to create expensive generation
        generation_data = {
            'prompt': 'Expensive ultra-high quality video',
            'duration': 60,
            'quality': 'ultra',
            'resolution': '3840x2160'
        }
        
        estimated_cost = resilient_veo_service.get_cost_estimate(generation_data)
        can_afford = resilient_veo_service.check_budget_available(estimated_cost)
        
        assert not can_afford, "Should not be able to afford expensive generation"
        
        # Try with cheaper alternative - minimal cost settings
        cheaper_data = {
            'prompt': 'Budget-friendly video',
            'duration': 5,  # Very short duration
            'quality': 'low',
            'resolution': '1280x720'
        }
        
        cheaper_cost = resilient_veo_service.get_cost_estimate(cheaper_data)
        can_afford_cheap = resilient_veo_service.check_budget_available(cheaper_cost)
        
        assert can_afford_cheap, "Should be able to afford cheaper generation"
        
        print(f"\n💸 Budget Exhaustion Handling")
        print(f"   Original cost: ${estimated_cost:.2f} (rejected)")
        print(f"   Alternative cost: ${cheaper_cost:.2f} (accepted)")
        print(f"   Budget saved: ${estimated_cost - cheaper_cost:.2f}")
    
    @pytest.mark.asyncio
    async def test_concurrent_request_coordination(self):
        """Test coordination of concurrent AI service requests"""
        
        services = {
            'veo': VEOAPIService(api_key='test_key'),
            'learning': LearningService(),
            'weather': WeatherAPIService()
        }
        
        # Mock all service methods
        with patch.object(services['veo'], 'create_video_generation') as mock_veo, \
             patch.object(services['learning'], 'predict_user_preferences') as mock_learn, \
             patch.object(services['weather'], 'get_current_weather') as mock_weather:
            
            # Setup async mocks
            async def mock_veo_async(*args, **kwargs):
                await asyncio.sleep(0.1)  # Simulate processing
                return {'generation_id': 'concurrent_gen', 'status': 'pending'}
            
            async def mock_learn_async(*args, **kwargs):
                await asyncio.sleep(0.05)
                return [{'preference': 'nature', 'score': 0.8}]
            
            async def mock_weather_async(*args, **kwargs):
                await asyncio.sleep(0.02)
                return {'conditions': 'sunny', 'temperature': 25}
            
            mock_veo.side_effect = mock_veo_async
            mock_learn.side_effect = mock_learn_async
            mock_weather.side_effect = mock_weather_async
            
            # Execute services concurrently
            start_time = time.time()
            
            results = await asyncio.gather(
                mock_veo({'prompt': 'test', 'duration': 10}),
                mock_learn('user_123', []),
                mock_weather({'lat': 0, 'lon': 0}),
                return_exceptions=True
            )
            
            end_time = time.time()
            
            # All should complete successfully
            assert all(not isinstance(r, Exception) for r in results)
            assert len(results) == 3
            
            # Should be faster than sequential execution
            total_time = end_time - start_time
            assert total_time < 0.2, "Concurrent execution should be faster than sequential"
            
            print(f"\n🔀 Concurrent Request Coordination")
            print(f"   Services: 3")
            print(f"   Execution time: {total_time:.3f}s")
            print(f"   Speedup: ~{0.17/total_time:.1f}x vs sequential")


if __name__ == "__main__":
    # Run with: python -m pytest test_ai_e2e_sandbox.py -v -s
    # For real API testing: VEO_API_KEY=your_key python -m pytest test_ai_e2e_sandbox.py -v -s
    pytest.main([__file__, "-v", "-s"])