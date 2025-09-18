"""
Unit tests for VEOAPIService - T270 AI Unit Tests
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

from src.ai.services.veo_api_service import VEOAPIService, GenerationStatus, VEOAPIError


class TestVEOAPIService:
    """Unit tests for VEOAPIService"""
    
    @pytest.fixture
    def veo_service(self):
        """Create VEOAPIService instance for testing"""
        return VEOAPIService(api_key="test_key", timeout=10)
    
    @pytest.fixture
    def mock_generation_data(self):
        """Mock generation request data"""
        return {
            'prompt': 'A beautiful sunset over mountains',
            'duration': 30,
            'quality': 'high',
            'resolution': '1920x1080'
        }
    
    def test_service_initialization(self, veo_service):
        """Test VEOAPIService initialization"""
        assert veo_service is not None
        assert veo_service.api_key == "test_key"
        assert veo_service.timeout == 10
        assert veo_service.is_authenticated is False
        assert veo_service.generation_count == 0
        assert veo_service.current_usage == 0.0
    
    def test_service_initialization_with_defaults(self):
        """Test VEOAPIService initialization with defaults"""
        service = VEOAPIService()
        assert service.api_key == ''  # Default from environment
        assert service.timeout == 30
        assert service.max_retries == 3
        assert service.monthly_budget == 100.0
        assert service.requests_per_minute == 60
    
    def test_validate_api_key(self, veo_service):
        """Test API key validation"""
        # Valid API keys
        assert veo_service.validate_api_key("veo_12345678901234567890") is True
        assert veo_service.validate_api_key("sk_12345678901234567890") is True
        
        # Invalid API keys
        assert veo_service.validate_api_key("") is False
        assert veo_service.validate_api_key("short") is False
        assert veo_service.validate_api_key("invalid_prefix_123456789") is False
        assert veo_service.validate_api_key(None) is False
    
    def test_authentication(self, veo_service):
        """Test authentication process"""
        with patch.object(veo_service, '_make_request') as mock_request:
            # Successful authentication
            mock_request.return_value = {'authenticated': True}
            result = veo_service.authenticate()
            assert result is True
            assert veo_service.is_authenticated is True
            
            # Failed authentication
            mock_request.side_effect = VEOAPIError("Auth failed")
            result = veo_service.authenticate()
            assert result is False
            assert veo_service.is_authenticated is False
    
    def test_get_cost_estimate(self, veo_service, mock_generation_data):
        """Test cost estimation"""
        # Basic cost estimation
        cost = veo_service.get_cost_estimate(mock_generation_data)
        assert isinstance(cost, float)
        assert cost > 0
        
        # Test duration multiplier
        long_video = mock_generation_data.copy()
        long_video['duration'] = 60
        long_cost = veo_service.get_cost_estimate(long_video)
        assert long_cost > cost
        
        # Test quality multiplier
        high_quality = mock_generation_data.copy()
        high_quality['quality'] = 'ultra'
        hq_cost = veo_service.get_cost_estimate(high_quality)
        assert hq_cost > cost
        
        # Test resolution multiplier
        fourk_video = mock_generation_data.copy()
        fourk_video['resolution'] = '3840x2160'
        fourk_cost = veo_service.get_cost_estimate(fourk_video)
        assert fourk_cost > cost
    
    def test_check_budget_available(self, veo_service):
        """Test budget checking"""
        # Initially should have budget available
        assert veo_service.check_budget_available(10.0) is True
        
        # After using most budget
        veo_service.current_usage = 95.0
        assert veo_service.check_budget_available(10.0) is False
        assert veo_service.check_budget_available(5.0) is True
    
    def test_track_costs(self, veo_service):
        """Test cost tracking"""
        initial_usage = veo_service.current_usage
        veo_service.track_costs("gen_123", 5.50)
        
        assert veo_service.current_usage == initial_usage + 5.50
    
    def test_get_usage_statistics(self, veo_service):
        """Test usage statistics"""
        veo_service.current_usage = 25.0
        veo_service.generation_count = 10
        
        stats = veo_service.get_usage_statistics()
        
        assert stats['total_cost'] == 25.0
        assert stats['generation_count'] == 10
        assert stats['monthly_budget'] == 100.0
        assert stats['budget_remaining'] == 75.0
        assert stats['average_cost_per_generation'] == 2.5
    
    def test_create_video_generation_without_auth(self, veo_service, mock_generation_data):
        """Test video generation without authentication"""
        veo_service.is_authenticated = False
        
        with patch.object(veo_service, 'authenticate') as mock_auth:
            mock_auth.return_value = False
            
            with pytest.raises(VEOAPIError) as exc_info:
                veo_service.create_video_generation(mock_generation_data)
            
            assert "Authentication required" in str(exc_info.value)
    
    def test_create_video_generation_success(self, veo_service, mock_generation_data):
        """Test successful video generation"""
        with patch.object(veo_service, 'authenticate') as mock_auth, \
             patch.object(veo_service, '_make_request') as mock_request, \
             patch.object(veo_service, 'get_cost_estimate') as mock_cost, \
             patch.object(veo_service, 'check_budget_available') as mock_budget:
            
            mock_auth.return_value = True
            mock_cost.return_value = 5.0
            mock_budget.return_value = True
            mock_request.return_value = {
                'generation_id': 'gen_12345',
                'status': 'pending',
                'estimated_completion': '2025-01-15T12:30:00Z'
            }
            
            veo_service.is_authenticated = True
            result = veo_service.create_video_generation(mock_generation_data)
            
            assert result['generation_id'] == 'gen_12345'
            assert result['status'] == 'pending'
            assert veo_service.generation_count == 1
    
    def test_create_video_generation_missing_prompt(self, veo_service):
        """Test video generation with missing required fields"""
        veo_service.is_authenticated = True
        
        with pytest.raises(VEOAPIError) as exc_info:
            veo_service.create_video_generation({})
        
        assert "Missing required field: prompt" in str(exc_info.value)
    
    def test_create_video_generation_insufficient_budget(self, veo_service, mock_generation_data):
        """Test video generation with insufficient budget"""
        with patch.object(veo_service, 'authenticate') as mock_auth, \
             patch.object(veo_service, 'get_cost_estimate') as mock_cost, \
             patch.object(veo_service, 'check_budget_available') as mock_budget:
            
            mock_auth.return_value = True
            mock_cost.return_value = 150.0  # More than budget
            mock_budget.return_value = False
            
            veo_service.is_authenticated = True
            
            with pytest.raises(VEOAPIError) as exc_info:
                veo_service.create_video_generation(mock_generation_data)
            
            assert "Insufficient budget" in str(exc_info.value)
    
    def test_get_generation_status(self, veo_service):
        """Test generation status checking"""
        generation_id = "gen_12345"
        
        with patch.object(veo_service, '_make_request') as mock_request:
            # Successful status check
            mock_request.return_value = {
                'generation_id': generation_id,
                'status': 'completed',
                'progress': 100,
                'video_url': 'https://example.com/video.mp4'
            }
            
            status = veo_service.get_generation_status(generation_id)
            assert status['generation_id'] == generation_id
            assert status['status'] == 'completed'
            assert status['progress'] == 100
            
            # Failed status check
            mock_request.side_effect = VEOAPIError("Not found")
            status = veo_service.get_generation_status(generation_id)
            assert status is None
            
            # Empty generation ID
            status = veo_service.get_generation_status("")
            assert status is None
    
    def test_cancel_generation(self, veo_service):
        """Test generation cancellation"""
        generation_id = "gen_12345"
        
        with patch.object(veo_service, '_make_request') as mock_request:
            # Successful cancellation
            mock_request.return_value = {'cancelled': True}
            result = veo_service.cancel_generation(generation_id)
            assert result is True
            
            # Failed cancellation
            mock_request.side_effect = VEOAPIError("Cannot cancel")
            result = veo_service.cancel_generation(generation_id)
            assert result is False
    
    def test_download_video(self, veo_service, tmp_path):
        """Test video download functionality"""
        video_url = "https://example.com/video.mp4"
        local_path = tmp_path / "test_video.mp4"
        
        with patch('requests.get') as mock_get:
            # Mock successful download
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_content = Mock(return_value=[b'chunk1', b'chunk2'])
            mock_get.return_value = mock_response
            
            success = veo_service.download_video(video_url, str(local_path))
            assert success is True
            assert local_path.exists()
            
            # Test download failure
            mock_get.side_effect = Exception("Download failed")
            success = veo_service.download_video(video_url, "/tmp/fail.mp4")
            assert success is False
    
    def test_download_video_with_progress(self, veo_service, tmp_path):
        """Test video download with progress tracking"""
        video_url = "https://example.com/video.mp4"
        local_path = tmp_path / "test_video_progress.mp4"
        progress_calls = []
        
        def progress_callback(downloaded, total):
            progress_calls.append((downloaded, total))
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.headers = {'content-length': '100'}
            mock_response.iter_content = Mock(return_value=[b'chunk1', b'chunk2'])
            mock_get.return_value = mock_response
            
            success = veo_service.download_video_with_progress(
                video_url, str(local_path), progress_callback
            )
            
            assert success is True
            assert len(progress_calls) > 0
    
    def test_create_video_generation_safe(self, veo_service, mock_generation_data):
        """Test safe video generation with error handling"""
        with patch.object(veo_service, 'create_video_generation') as mock_create:
            # Successful generation
            mock_create.return_value = {'generation_id': 'gen_123'}
            result = veo_service.create_video_generation_safe(mock_generation_data)
            assert 'generation_id' in result
            
            # VEO API Error
            mock_create.side_effect = VEOAPIError("API Error")
            result = veo_service.create_video_generation_safe(mock_generation_data)
            assert 'error' in result
            assert result['error'] == "API Error"
            
            # Unexpected error
            mock_create.side_effect = Exception("Unexpected")
            result = veo_service.create_video_generation_safe(mock_generation_data)
            assert 'error' in result
            assert result['error'] == "Unexpected error occurred"
    
    def test_get_account_info(self, veo_service):
        """Test account information retrieval"""
        with patch.object(veo_service, '_make_request') as mock_request:
            # Successful account info
            mock_request.return_value = {
                'user_id': 'user_123',
                'plan': 'premium',
                'usage_limit': 1000,
                'usage_current': 250
            }
            
            info = veo_service.get_account_info()
            assert info['user_id'] == 'user_123'
            assert info['plan'] == 'premium'
            
            # API failure
            mock_request.side_effect = VEOAPIError("API unavailable")
            info = veo_service.get_account_info()
            assert info['user_id'] == 'unknown'
            assert info['plan'] == 'unknown'
    
    def test_check_api_health(self, veo_service):
        """Test API health checking"""
        with patch.object(veo_service, '_make_request') as mock_request:
            # Healthy API
            mock_request.return_value = {'status': 'healthy', 'uptime': '99.9%'}
            health = veo_service.check_api_health()
            assert health['status'] == 'healthy'
            
            # Unhealthy API
            mock_request.side_effect = VEOAPIError("API down")
            health = veo_service.check_api_health()
            assert health['status'] == 'unhealthy'
    
    def test_get_performance_metrics(self, veo_service):
        """Test performance metrics retrieval"""
        # No response times recorded
        metrics = veo_service.get_performance_metrics()
        assert metrics['response_times'] == []
        assert metrics['average_response_time'] == 0
        
        # With response times
        veo_service.response_times = [100, 150, 200, 120, 180]
        metrics = veo_service.get_performance_metrics()
        assert len(metrics['response_times']) == 5
        assert metrics['average_response_time'] == 150.0
        assert metrics['fastest_response'] == 100
        assert metrics['slowest_response'] == 200
    
    def test_validate_configuration(self, veo_service):
        """Test configuration validation"""
        # Valid configuration
        assert veo_service.validate_configuration() is True
        
        # Invalid configurations
        veo_service.api_key = ""
        assert veo_service.validate_configuration() is False
        
        veo_service.api_key = "test_key"
        veo_service.base_url = "http://insecure.com"
        assert veo_service.validate_configuration() is False
        
        veo_service.base_url = "https://api.veo.com"
        veo_service.timeout = -1
        assert veo_service.validate_configuration() is False
        
        veo_service.timeout = 30
        veo_service.max_retries = -1
        assert veo_service.validate_configuration() is False
        
        veo_service.max_retries = 3
        veo_service.monthly_budget = 0
        assert veo_service.validate_configuration() is False
    
    def test_update_configuration(self, veo_service):
        """Test configuration updates"""
        original_timeout = veo_service.timeout
        
        config_updates = {
            'timeout': 60,
            'max_retries': 5,
            'monthly_budget': 200.0
        }
        
        veo_service.update_configuration(config_updates)
        
        assert veo_service.timeout == 60
        assert veo_service.max_retries == 5
        assert veo_service.monthly_budget == 200.0
    
    def test_handle_rate_limits(self, veo_service):
        """Test rate limit handling"""
        with patch('time.sleep') as mock_sleep:
            result = veo_service.handle_rate_limits()
            assert result is True
            mock_sleep.assert_called_once()
    
    def test_retry_failed_request(self, veo_service):
        """Test request retry mechanism"""
        with patch.object(veo_service, '_make_request') as mock_request, \
             patch('time.sleep') as mock_sleep:
            
            # Successful retry
            mock_request.side_effect = [VEOAPIError("Temp fail"), {'success': True}]
            result = veo_service.retry_failed_request('/test', {'data': 'test'})
            assert result == {'success': True}
            assert mock_request.call_count == 2
            
            # Max retries exceeded
            mock_request.side_effect = VEOAPIError("Permanent fail")
            with pytest.raises(VEOAPIError):
                veo_service.retry_failed_request('/test', max_retries=2)
    
    def test_context_manager(self):
        """Test VEOAPIService as context manager"""
        with VEOAPIService(api_key="test") as service:
            assert service is not None
            assert hasattr(service, 'session')
        
        # Session should be closed after exiting context


class TestVEOAPIServiceHttpRequests:
    """Test HTTP request functionality"""
    
    @pytest.fixture
    def veo_service(self):
        return VEOAPIService(api_key="test_key")
    
    def test_make_request_get(self, veo_service):
        """Test GET request"""
        with patch.object(veo_service.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'result': 'success'}
            mock_get.return_value = mock_response
            
            result = veo_service._make_request('GET', '/test')
            assert result == {'result': 'success'}
    
    def test_make_request_post(self, veo_service):
        """Test POST request"""
        with patch.object(veo_service.session, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'id': '123'}
            mock_post.return_value = mock_response
            
            result = veo_service._make_request('POST', '/create', {'data': 'test'})
            assert result == {'id': '123'}
    
    def test_make_request_rate_limiting(self, veo_service):
        """Test rate limiting in requests"""
        with patch('time.time') as mock_time, \
             patch('time.sleep') as mock_sleep, \
             patch.object(veo_service.session, 'get') as mock_get:
            
            # Simulate rapid requests - need more values for all time.time() calls
            mock_time.side_effect = [0, 0.5, 0.5, 1.0, 1.0, 1.5]
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_get.return_value = mock_response
            
            veo_service._make_request('GET', '/test')
            mock_sleep.assert_called()
    
    def test_make_request_http_errors(self, veo_service):
        """Test HTTP error handling"""
        with patch.object(veo_service.session, 'get') as mock_get:
            mock_response = Mock()
            mock_get.return_value = mock_response
            
            # Test 429 Rate Limit
            mock_response.status_code = 429
            with pytest.raises(VEOAPIError) as exc_info:
                veo_service._make_request('GET', '/test')
            assert "Rate limit exceeded" in str(exc_info.value)
            
            # Test 401 Unauthorized
            mock_response.status_code = 401
            with pytest.raises(VEOAPIError) as exc_info:
                veo_service._make_request('GET', '/test')
            assert "Authentication failed" in str(exc_info.value)
            
            # Test 403 Forbidden
            mock_response.status_code = 403
            with pytest.raises(VEOAPIError) as exc_info:
                veo_service._make_request('GET', '/test')
            assert "Access forbidden" in str(exc_info.value)
            
            # Test generic 4xx error
            mock_response.status_code = 404
            mock_response.text = "Not found"
            with pytest.raises(VEOAPIError) as exc_info:
                veo_service._make_request('GET', '/test')
            assert "HTTP 404" in str(exc_info.value)
    
    def test_make_request_connection_errors(self, veo_service):
        """Test connection error handling"""
        import requests
        
        with patch.object(veo_service.session, 'get') as mock_get:
            # Test timeout
            mock_get.side_effect = requests.exceptions.Timeout()
            with pytest.raises(VEOAPIError) as exc_info:
                veo_service._make_request('GET', '/test')
            assert "Request timeout" in str(exc_info.value)
            
            # Test connection error
            mock_get.side_effect = requests.exceptions.ConnectionError()
            with pytest.raises(VEOAPIError) as exc_info:
                veo_service._make_request('GET', '/test')
            assert "Connection error" in str(exc_info.value)
            
            # Test generic request exception
            mock_get.side_effect = requests.exceptions.RequestException("Network error")
            with pytest.raises(VEOAPIError) as exc_info:
                veo_service._make_request('GET', '/test')
            assert "Request failed" in str(exc_info.value)


# Test utility functions
def test_create_veo_service():
    """Test convenience function for creating VEO service"""
    from src.ai.services.veo_api_service import create_veo_service
    
    service = create_veo_service(api_key="test_key", budget=50.0)
    assert service.api_key == "test_key"
    assert service.monthly_budget == 50.0


def test_estimate_generation_cost():
    """Test convenience function for cost estimation"""
    from src.ai.services.veo_api_service import estimate_generation_cost
    
    cost = estimate_generation_cost(duration=60, resolution='4K', quality='ultra')
    assert isinstance(cost, float)
    assert cost > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])