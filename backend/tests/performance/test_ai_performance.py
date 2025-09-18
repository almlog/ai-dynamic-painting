"""
Performance tests for AI services - T271 AI Performance Tests
"""

import pytest
import asyncio
import time
import threading
import psutil
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ai.services.veo_api_service import VEOAPIService, VEOAPIError
from ai.services.learning_service import LearningService
from ai.services.weather_api_service import WeatherAPIService


class PerformanceTracker:
    """Helper class to track performance metrics"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.memory_usage = []
        self.cpu_usage = []
        self.process = psutil.Process(os.getpid())
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        self.memory_usage = []
        self.cpu_usage = []
        
        # Initial readings
        self.memory_usage.append(self.process.memory_info().rss / 1024 / 1024)  # MB
        self.cpu_usage.append(self.process.cpu_percent())
    
    def record_metrics(self):
        """Record current performance metrics"""
        if self.start_time:
            self.memory_usage.append(self.process.memory_info().rss / 1024 / 1024)  # MB
            self.cpu_usage.append(self.process.cpu_percent())
    
    def stop_monitoring(self):
        """Stop performance monitoring and return results"""
        self.end_time = time.time()
        
        # Final readings
        self.memory_usage.append(self.process.memory_info().rss / 1024 / 1024)  # MB
        self.cpu_usage.append(self.process.cpu_percent())
        
        return {
            'execution_time': self.end_time - self.start_time,
            'memory_usage': {
                'max': max(self.memory_usage),
                'min': min(self.memory_usage),
                'avg': sum(self.memory_usage) / len(self.memory_usage),
                'samples': self.memory_usage
            },
            'cpu_usage': {
                'max': max(self.cpu_usage),
                'min': min(self.cpu_usage),
                'avg': sum(self.cpu_usage) / len(self.cpu_usage),
                'samples': self.cpu_usage
            }
        }


class TestVEOAPIServicePerformance:
    """Performance tests for VEO API Service"""
    
    @pytest.fixture
    def veo_service(self):
        """Create VEO API service for performance testing"""
        return VEOAPIService(api_key="test_key", timeout=30)
    
    @pytest.fixture
    def mock_generation_data(self):
        """Mock video generation data"""
        return {
            'prompt': 'A beautiful sunset over mountains with birds flying',
            'duration': 30,
            'quality': 'high',
            'resolution': '1920x1080'
        }
    
    def test_single_video_generation_performance(self, veo_service, mock_generation_data):
        """Test performance of single video generation"""
        tracker = PerformanceTracker()
        
        with patch.object(veo_service, 'authenticate') as mock_auth, \
             patch.object(veo_service, '_make_request') as mock_request, \
             patch.object(veo_service, 'get_cost_estimate') as mock_cost, \
             patch.object(veo_service, 'check_budget_available') as mock_budget:
            
            # Setup mocks
            mock_auth.return_value = True
            mock_cost.return_value = 2.5
            mock_budget.return_value = True
            mock_request.return_value = {
                'generation_id': 'gen_perf_test',
                'status': 'pending',
                'estimated_completion': '2025-01-15T12:30:00Z'
            }
            
            veo_service.is_authenticated = True
            
            # Performance test
            tracker.start_monitoring()
            
            for i in range(10):  # Generate 10 videos sequentially
                result = veo_service.create_video_generation(mock_generation_data)
                assert 'generation_id' in result
                tracker.record_metrics()
            
            metrics = tracker.stop_monitoring()
            
            # Performance assertions
            assert metrics['execution_time'] < 5.0, f"Sequential generation too slow: {metrics['execution_time']:.2f}s"
            assert metrics['memory_usage']['max'] < 200, f"Memory usage too high: {metrics['memory_usage']['max']:.2f}MB"
            
            print(f"\n🔥 Single Generation Performance:")
            print(f"   Execution time: {metrics['execution_time']:.3f}s")
            print(f"   Memory peak: {metrics['memory_usage']['max']:.2f}MB")
            print(f"   CPU peak: {metrics['cpu_usage']['max']:.1f}%")
    
    def test_concurrent_video_generation_performance(self, veo_service, mock_generation_data):
        """Test performance of concurrent video generations"""
        tracker = PerformanceTracker()
        
        with patch.object(veo_service, 'authenticate') as mock_auth, \
             patch.object(veo_service, '_make_request') as mock_request, \
             patch.object(veo_service, 'get_cost_estimate') as mock_cost, \
             patch.object(veo_service, 'check_budget_available') as mock_budget:
            
            # Setup mocks
            mock_auth.return_value = True
            mock_cost.return_value = 2.5
            mock_budget.return_value = True
            mock_request.return_value = {
                'generation_id': 'gen_concurrent',
                'status': 'pending'
            }
            
            veo_service.is_authenticated = True
            
            # Concurrent performance test
            tracker.start_monitoring()
            
            def generate_video(index):
                data = mock_generation_data.copy()
                data['prompt'] = f"Test video {index}: {data['prompt']}"
                return veo_service.create_video_generation(data)
            
            # Test with 20 concurrent requests
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(generate_video, i) for i in range(20)]
                
                results = []
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    tracker.record_metrics()
            
            metrics = tracker.stop_monitoring()
            
            # Performance assertions
            assert len(results) == 20, "Not all concurrent requests completed"
            assert metrics['execution_time'] < 10.0, f"Concurrent generation too slow: {metrics['execution_time']:.2f}s"
            assert metrics['memory_usage']['max'] < 300, f"Memory usage too high during concurrent operations: {metrics['memory_usage']['max']:.2f}MB"
            
            print(f"\n⚡ Concurrent Generation Performance (20 requests):")
            print(f"   Execution time: {metrics['execution_time']:.3f}s")
            print(f"   Throughput: {20/metrics['execution_time']:.1f} req/s")
            print(f"   Memory peak: {metrics['memory_usage']['max']:.2f}MB")
            print(f"   CPU peak: {metrics['cpu_usage']['max']:.1f}%")
    
    def test_cost_calculation_performance(self, veo_service):
        """Test performance of cost calculation operations"""
        tracker = PerformanceTracker()
        
        # Test data variations
        test_cases = []
        for duration in [15, 30, 60, 120]:
            for quality in ['low', 'medium', 'high', 'ultra']:
                for resolution in ['1920x1080', '2560x1440', '3840x2160']:
                    test_cases.append({
                        'duration': duration,
                        'quality': quality,
                        'resolution': resolution,
                        'prompt': f'Test video {duration}s {quality} {resolution}'
                    })
        
        tracker.start_monitoring()
        
        # Calculate costs for all combinations (48 calculations)
        costs = []
        for case in test_cases:
            cost = veo_service.get_cost_estimate(case)
            costs.append(cost)
            
            if len(costs) % 10 == 0:  # Record every 10 calculations
                tracker.record_metrics()
        
        metrics = tracker.stop_monitoring()
        
        # Performance assertions
        assert len(costs) == len(test_cases), "Not all cost calculations completed"
        assert metrics['execution_time'] < 1.0, f"Cost calculation too slow: {metrics['execution_time']:.3f}s"
        assert all(cost > 0 for cost in costs), "All costs should be positive"
        
        print(f"\n💰 Cost Calculation Performance ({len(test_cases)} calculations):")
        print(f"   Execution time: {metrics['execution_time']:.3f}s")
        print(f"   Rate: {len(test_cases)/metrics['execution_time']:.1f} calc/s")
        print(f"   Memory usage: {metrics['memory_usage']['max']:.2f}MB")
    
    def test_large_batch_operations_performance(self, veo_service):
        """Test performance with large batch operations"""
        tracker = PerformanceTracker()
        
        # Simulate large batch of status checks
        generation_ids = [f"gen_batch_{i:04d}" for i in range(100)]
        
        with patch.object(veo_service, '_make_request') as mock_request:
            mock_request.return_value = {
                'generation_id': 'gen_test',
                'status': 'completed',
                'progress': 100,
                'video_url': 'https://example.com/video.mp4'
            }
            
            tracker.start_monitoring()
            
            # Batch status checking
            statuses = []
            for gen_id in generation_ids:
                status = veo_service.get_generation_status(gen_id)
                statuses.append(status)
                
                if len(statuses) % 20 == 0:  # Record every 20 operations
                    tracker.record_metrics()
            
            metrics = tracker.stop_monitoring()
            
            # Performance assertions
            assert len(statuses) == 100, "Not all status checks completed"
            assert metrics['execution_time'] < 5.0, f"Batch operations too slow: {metrics['execution_time']:.2f}s"
            
            print(f"\n📊 Batch Operations Performance (100 status checks):")
            print(f"   Execution time: {metrics['execution_time']:.3f}s")
            print(f"   Rate: {100/metrics['execution_time']:.1f} ops/s")
            print(f"   Memory peak: {metrics['memory_usage']['max']:.2f}MB")


class TestLearningServicePerformance:
    """Performance tests for Learning Service"""
    
    @pytest.fixture
    def learning_service(self):
        """Create Learning service for performance testing"""
        return LearningService()
    
    def test_preference_learning_performance(self, learning_service):
        """Test performance of preference learning operations"""
        tracker = PerformanceTracker()
        
        # Generate test user data
        user_data = {
            'user_id': 'perf_test_user',
            'interactions': []
        }
        
        # Generate 1000 mock interactions
        for i in range(1000):
            interaction = {
                'timestamp': time.time() - (1000 - i) * 3600,  # 1 hour intervals
                'video_id': f'video_{i % 50}',  # 50 different videos
                'watch_duration': 20 + (i % 40),  # 20-60 seconds
                'rating': (i % 5) + 1,  # 1-5 rating
                'skip_count': i % 3,  # 0-2 skips
                'replay_count': i % 2,  # 0-1 replays
                'context': {
                    'time_of_day': (i % 24),
                    'day_of_week': (i % 7),
                    'weather': ['sunny', 'cloudy', 'rainy'][i % 3]
                }
            }
            user_data['interactions'].append(interaction)
        
        tracker.start_monitoring()
        
        # Performance test
        with patch.object(learning_service, '_save_user_data') as mock_save:
            # Test preference learning
            learning_service.learn_user_preferences(user_data)
            tracker.record_metrics()
            
            # Test preference prediction
            for i in range(10):
                preferences = learning_service.predict_user_preferences('perf_test_user')
                tracker.record_metrics()
        
        metrics = tracker.stop_monitoring()
        
        # Performance assertions
        assert metrics['execution_time'] < 10.0, f"Learning operations too slow: {metrics['execution_time']:.2f}s"
        
        print(f"\n🧠 Learning Performance (1000 interactions):")
        print(f"   Execution time: {metrics['execution_time']:.3f}s")
        print(f"   Memory peak: {metrics['memory_usage']['max']:.2f}MB")
        print(f"   CPU peak: {metrics['cpu_usage']['max']:.1f}%")
    
    def test_user_clustering_performance(self, learning_service):
        """Test performance of user clustering operations"""
        tracker = PerformanceTracker()
        
        # Generate test users
        users_data = []
        for user_id in range(50):  # 50 users
            user_preferences = {
                'colors': [f'color_{i}' for i in range(user_id % 10)],
                'styles': [f'style_{i}' for i in range(user_id % 5)],
                'moods': [f'mood_{i}' for i in range(user_id % 3)],
                'engagement_scores': [0.1 + (i * 0.1) for i in range(user_id % 8)]
            }
            users_data.append({
                'user_id': f'user_{user_id}',
                'preferences': user_preferences
            })
        
        tracker.start_monitoring()
        
        # Performance test
        with patch.object(learning_service, '_load_all_users') as mock_load:
            mock_load.return_value = users_data
            
            # Test clustering
            clusters = learning_service.cluster_similar_users(num_clusters=5)
            tracker.record_metrics()
            
            # Test similarity calculations
            for i in range(10):
                similarity = learning_service.calculate_user_similarity('user_1', 'user_2')
                tracker.record_metrics()
        
        metrics = tracker.stop_monitoring()
        
        # Performance assertions  
        assert metrics['execution_time'] < 15.0, f"Clustering too slow: {metrics['execution_time']:.2f}s"
        
        print(f"\n👥 Clustering Performance (50 users):")
        print(f"   Execution time: {metrics['execution_time']:.3f}s")
        print(f"   Memory peak: {metrics['memory_usage']['max']:.2f}MB")


class TestWeatherAPIServicePerformance:
    """Performance tests for Weather API Service"""
    
    @pytest.fixture
    def weather_service(self):
        """Create Weather API service for performance testing"""
        return WeatherAPIService()
    
    def test_weather_data_retrieval_performance(self, weather_service):
        """Test performance of weather data retrieval"""
        tracker = PerformanceTracker()
        
        # Test locations
        locations = [
            {'lat': 35.6762, 'lon': 139.6503, 'name': 'Tokyo'},
            {'lat': 40.7128, 'lon': -74.0060, 'name': 'New York'},
            {'lat': 51.5074, 'lon': -0.1278, 'name': 'London'},
            {'lat': 48.8566, 'lon': 2.3522, 'name': 'Paris'},
            {'lat': -33.8688, 'lon': 151.2093, 'name': 'Sydney'}
        ]
        
        with patch.object(weather_service, '_fetch_current_weather') as mock_request:
            from src.ai.services.weather_api_service import WeatherData
            mock_weather_data = WeatherData(
                temperature=22.5,
                humidity=65,
                conditions='partly_cloudy',
                wind_speed=15.2,
                pressure=1013.25,
                description='Partly cloudy',
                location='Test Location',
                timestamp=int(time.time())
            )
            mock_request.return_value = mock_weather_data
            
            tracker.start_monitoring()
            
            # Test concurrent weather requests
            async def get_weather_async(location):
                return await weather_service.get_current_weather(location)
            
            def get_weather(location):
                import asyncio
                return asyncio.run(get_weather_async(location))
            
            results = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                
                # Make 10 requests for each location (50 total)
                for location in locations:
                    for _ in range(10):
                        future = executor.submit(get_weather, location)
                        futures.append(future)
                
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    
                    if len(results) % 10 == 0:
                        tracker.record_metrics()
            
            metrics = tracker.stop_monitoring()
            
            # Performance assertions
            assert len(results) == 50, "Not all weather requests completed"
            assert metrics['execution_time'] < 8.0, f"Weather retrieval too slow: {metrics['execution_time']:.2f}s"
            
            print(f"\n🌤️  Weather API Performance (50 requests):")
            print(f"   Execution time: {metrics['execution_time']:.3f}s")
            print(f"   Throughput: {50/metrics['execution_time']:.1f} req/s")
            print(f"   Memory peak: {metrics['memory_usage']['max']:.2f}MB")


class TestIntegratedAIPerformance:
    """Integrated AI services performance tests"""
    
    @pytest.fixture
    def ai_services(self):
        """Create all AI services for integrated testing"""
        return {
            'veo': VEOAPIService(api_key="test_key"),
            'learning': LearningService(),
            'weather': WeatherAPIService()
        }
    
    def test_full_ai_pipeline_performance(self, ai_services):
        """Test performance of full AI pipeline"""
        tracker = PerformanceTracker()
        
        # Mock all external dependencies
        with patch.object(ai_services['weather'], 'get_current_weather') as mock_weather, \
             patch.object(ai_services['veo'], 'authenticate') as mock_veo_auth, \
             patch.object(ai_services['veo'], '_make_request') as mock_veo_request, \
             patch.object(ai_services['veo'], 'get_cost_estimate') as mock_cost, \
             patch.object(ai_services['veo'], 'check_budget_available') as mock_budget, \
             patch.object(ai_services['learning'], 'learn_user_preferences') as mock_learn, \
             patch.object(ai_services['learning'], 'predict_user_preferences') as mock_predict:
            
            # Setup mocks for async calls
            async def mock_weather_async(*args, **kwargs):
                return {
                    'temperature': 25.0,
                    'humidity': 60,
                    'conditions': 'sunny',
                    'wind_speed': 5.0,
                    'pressure': 1013.25,
                    'description': 'Clear sky'
                }
            
            async def mock_learn_async(*args, **kwargs):
                return {'status': 'success', 'preferences_updated': True}
            
            async def mock_predict_async(*args, **kwargs):
                return [{'type': 'nature', 'confidence': 0.8}]
            
            mock_weather.side_effect = mock_weather_async
            mock_learn.side_effect = mock_learn_async
            mock_predict.side_effect = mock_predict_async
            
            mock_veo_auth.return_value = True
            mock_cost.return_value = 3.0
            mock_budget.return_value = True
            mock_veo_request.return_value = {
                'generation_id': 'gen_pipeline',
                'status': 'pending'
            }
            
            ai_services['veo'].is_authenticated = True
            
            tracker.start_monitoring()
            
            # Simulate full AI pipeline for 5 users
            import asyncio
            
            async def run_pipeline():
                for user_id in range(5):
                    # 1. Get weather context
                    weather = await ai_services['weather'].get_current_weather({
                        'lat': 35.6762 + user_id, 'lon': 139.6503 + user_id
                    })
                    tracker.record_metrics()
                    
                    # 2. Learn user preferences
                    interaction_data = [
                        {
                            'timestamp': time.time(),
                            'video_id': f'video_{user_id}',
                            'rating': 4 + (user_id % 2),
                            'watch_duration': 30 + user_id * 5
                        }
                    ]
                    await ai_services['learning'].learn_user_preferences(f'pipeline_user_{user_id}', interaction_data)
                    tracker.record_metrics()
                    
                    # 3. Predict preferences
                    preferences = await ai_services['learning'].predict_user_preferences(f'pipeline_user_{user_id}', [])
                    tracker.record_metrics()
                    
                    # 4. Generate video based on context
                    generation_data = {
                        'prompt': f'Video for user {user_id} based on weather {weather.get("conditions", "unknown") if isinstance(weather, dict) else getattr(weather, "conditions", "unknown")}',
                        'duration': 30,
                        'quality': 'medium'
                    }
                    result = ai_services['veo'].create_video_generation(generation_data)
                    tracker.record_metrics()
            
            # Run the async pipeline
            asyncio.run(run_pipeline())
            
            metrics = tracker.stop_monitoring()
            
            # Performance assertions
            assert metrics['execution_time'] < 15.0, f"Full pipeline too slow: {metrics['execution_time']:.2f}s"
            assert metrics['memory_usage']['max'] < 400, f"Pipeline memory usage too high: {metrics['memory_usage']['max']:.2f}MB"
            
            print(f"\n🔄 Full AI Pipeline Performance (5 users):")
            print(f"   Execution time: {metrics['execution_time']:.3f}s")
            print(f"   Users/second: {5/metrics['execution_time']:.1f}")
            print(f"   Memory peak: {metrics['memory_usage']['max']:.2f}MB")
            print(f"   CPU peak: {metrics['cpu_usage']['max']:.1f}%")
    
    def test_memory_leak_detection(self, ai_services):
        """Test for memory leaks in AI services"""
        import gc
        
        # Get initial memory baseline
        gc.collect()
        initial_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        
        memory_samples = [initial_memory]
        
        with patch.object(ai_services['veo'], 'authenticate') as mock_auth, \
             patch.object(ai_services['veo'], '_make_request') as mock_request, \
             patch.object(ai_services['veo'], 'get_cost_estimate') as mock_cost, \
             patch.object(ai_services['veo'], 'check_budget_available') as mock_budget:
            
            mock_auth.return_value = True
            mock_cost.return_value = 2.0
            mock_budget.return_value = True
            mock_request.return_value = {'generation_id': 'leak_test', 'status': 'pending'}
            
            ai_services['veo'].is_authenticated = True
            
            # Run operations in batches and check memory
            for batch in range(10):  # 10 batches
                for i in range(20):  # 20 operations per batch
                    # Generate video
                    result = ai_services['veo'].create_video_generation({
                        'prompt': f'Memory test video {batch}_{i}',
                        'duration': 15
                    })
                    
                    # Check status
                    status = ai_services['veo'].get_generation_status(result['generation_id'])
                    
                    # Cost calculation
                    cost = ai_services['veo'].get_cost_estimate({'duration': 30, 'quality': 'high'})
                
                # Force garbage collection and measure memory
                gc.collect()
                current_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)
                
                print(f"   Batch {batch + 1}: {current_memory:.1f}MB")
        
        # Analyze memory growth
        memory_growth = memory_samples[-1] - memory_samples[0]
        max_memory = max(memory_samples)
        
        # Memory leak assertions
        assert memory_growth < 50, f"Potential memory leak detected: {memory_growth:.1f}MB growth"
        assert max_memory < initial_memory + 100, f"Memory usage too high: {max_memory:.1f}MB"
        
        print(f"\n🔍 Memory Leak Detection (200 operations):")
        print(f"   Initial memory: {initial_memory:.1f}MB")
        print(f"   Final memory: {memory_samples[-1]:.1f}MB")
        print(f"   Memory growth: {memory_growth:.1f}MB")
        print(f"   Peak memory: {max_memory:.1f}MB")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to see print statements