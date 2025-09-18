"""
Unit tests for WeatherAPIService - T270 AI Unit Tests
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

from src.ai.services.weather_api_service import (
    WeatherAPIService, WeatherProvider, WeatherCondition, WeatherSeverity,
    ForecastType, LocationType, CacheStrategy, WeatherData, WeatherAlert
)


class TestWeatherAPIService:
    """Unit tests for WeatherAPIService"""
    
    @pytest.fixture
    def weather_service(self):
        """Create WeatherAPIService instance for testing"""
        return WeatherAPIService()
    
    @pytest.fixture
    def sample_location_data(self):
        """Sample location data for testing"""
        return {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'location_type': LocationType.COORDINATES
        }
    
    @pytest.fixture
    def sample_weather_data(self):
        """Sample weather data for testing"""
        return WeatherData(
            temperature=22.5,
            condition=WeatherCondition.CLEAR,
            humidity=65,
            pressure=1013.2,
            wind_speed=8.5,
            visibility=10.0,
            timestamp=datetime.now(),
            location_info={
                'latitude': 35.6762,
                'longitude': 139.6503,
                'name': 'Tokyo'
            },
            provider=WeatherProvider.OPENWEATHER,
            confidence=0.95
        )
    
    def test_service_initialization(self, weather_service):
        """Test WeatherAPIService initialization"""
        assert weather_service is not None
        assert isinstance(weather_service.providers, dict)
        assert isinstance(weather_service.cache, dict)
        assert weather_service.cache_ttl == 900  # 15 minutes
        assert isinstance(weather_service.active_providers, list)
        assert len(weather_service.active_providers) > 0
    
    def test_weather_enum_values(self):
        """Test weather enum values"""
        # Test WeatherProvider enum
        assert WeatherProvider.OPENWEATHER.value == "openweather"
        assert WeatherProvider.WEATHERAPI.value == "weatherapi"
        
        # Test WeatherCondition enum
        assert WeatherCondition.CLEAR.value == "clear"
        assert WeatherCondition.RAINY.value == "rainy"
        
        # Test WeatherSeverity enum
        assert WeatherSeverity.LOW.value == "low"
        assert WeatherSeverity.EXTREME.value == "extreme"
        
        # Test ForecastType enum
        assert ForecastType.HOURLY.value == "hourly"
        assert ForecastType.DAILY.value == "daily"
    
    @pytest.mark.asyncio
    async def test_get_current_weather_coordinates(self, weather_service, sample_location_data):
        """Test getting current weather by coordinates"""
        with patch.object(weather_service, '_fetch_current_weather') as mock_fetch:
            mock_weather = WeatherData(
                temperature=25.0,
                condition=WeatherCondition.CLEAR,
                humidity=60,
                pressure=1013.0,
                wind_speed=5.0,
                visibility=10.0,
                timestamp=datetime.now(),
                location_info=sample_location_data,
                provider=WeatherProvider.OPENWEATHER
            )
            mock_fetch.return_value = mock_weather
            
            result = await weather_service.get_current_weather(sample_location_data)
            
            assert result is not None
            assert 'temperature' in result
            assert 'condition' in result
            assert 'humidity' in result
            assert result['temperature'] == 25.0
            assert result['condition'] == 'clear'
    
    @pytest.mark.asyncio
    async def test_get_current_weather_city_name(self, weather_service):
        """Test getting current weather by city name"""
        city_location = {
            'city': 'Tokyo',
            'country': 'Japan',
            'location_type': LocationType.CITY_NAME
        }
        
        with patch.object(weather_service, '_geocode_city') as mock_geocode, \
             patch.object(weather_service, '_fetch_current_weather') as mock_fetch:
            
            mock_geocode.return_value = (35.6762, 139.6503)
            mock_weather = WeatherData(
                temperature=20.0,
                condition=WeatherCondition.CLOUDY,
                humidity=70,
                pressure=1015.0,
                wind_speed=3.0,
                visibility=8.0,
                timestamp=datetime.now(),
                location_info={'city': 'Tokyo'},
                provider=WeatherProvider.OPENWEATHER
            )
            mock_fetch.return_value = mock_weather
            
            result = await weather_service.get_current_weather(city_location)
            
            assert result is not None
            assert result['temperature'] == 20.0
            mock_geocode.assert_called_once_with('Tokyo', 'Japan')
    
    @pytest.mark.asyncio
    async def test_get_weather_forecast_daily(self, weather_service, sample_location_data):
        """Test getting daily weather forecast"""
        forecast_params = {
            'forecast_type': ForecastType.DAILY,
            'days': 5,
            'include_hourly': False,
            'include_alerts': True
        }
        
        result = await weather_service.get_weather_forecast(sample_location_data, forecast_params)
        
        assert result is not None
        assert 'forecast_data' in result
        assert 'forecast_type' in result
        assert 'forecast_period' in result
        assert result['forecast_type'] == ForecastType.DAILY.value
        
        forecast_data = result['forecast_data']
        assert isinstance(forecast_data, list)
        assert len(forecast_data) <= 5
        
        # Check structure of forecast entries
        if forecast_data:
            day_forecast = forecast_data[0]
            assert 'date' in day_forecast
            assert 'temperature_high' in day_forecast
            assert 'temperature_low' in day_forecast
            assert 'condition' in day_forecast
    
    @pytest.mark.asyncio
    async def test_get_weather_forecast_hourly(self, weather_service, sample_location_data):
        """Test getting hourly weather forecast"""
        forecast_params = {
            'forecast_type': ForecastType.HOURLY,
            'hours': 12,
            'include_detailed': True
        }
        
        result = await weather_service.get_weather_forecast(sample_location_data, forecast_params)
        
        assert result is not None
        assert result['forecast_type'] == ForecastType.HOURLY.value
        
        forecast_data = result['forecast_data']
        assert len(forecast_data) <= 12
        
        if forecast_data:
            hour_forecast = forecast_data[0]
            assert 'time' in hour_forecast
            assert 'temperature' in hour_forecast
            assert 'condition' in hour_forecast
    
    @pytest.mark.asyncio
    async def test_get_historical_weather(self, weather_service, sample_location_data):
        """Test getting historical weather data"""
        time_range = {
            'start_date': datetime.now() - timedelta(days=7),
            'end_date': datetime.now() - timedelta(days=1)
        }
        
        result = await weather_service.get_historical_weather(sample_location_data, time_range)
        
        assert result is not None
        assert 'historical_data' in result
        assert 'location_info' in result
        assert 'time_range' in result
        
        historical_data = result['historical_data']
        assert isinstance(historical_data, list)
        assert len(historical_data) > 0
        
        # Check structure of historical entries
        if historical_data:
            day_data = historical_data[0]
            assert 'date' in day_data
            assert 'temperature_avg' in day_data
            assert 'condition' in day_data
    
    @pytest.mark.asyncio
    async def test_get_weather_alerts(self, weather_service, sample_location_data):
        """Test getting weather alerts"""
        alert_params = {
            'severity_filter': [WeatherSeverity.HIGH, WeatherSeverity.EXTREME],
            'alert_types': ['storm', 'flood'],
            'time_range_hours': 24
        }
        
        result = await weather_service.get_weather_alerts(sample_location_data, alert_params)
        
        assert result is not None
        assert 'active_alerts' in result
        assert 'alert_count' in result
        assert 'severity_summary' in result
        assert isinstance(result['active_alerts'], list)
        assert isinstance(result['alert_count'], int)
    
    @pytest.mark.asyncio
    async def test_get_weather_summary(self, weather_service, sample_location_data):
        """Test getting weather summary"""
        summary_params = {
            'time_period': 'current',
            'include_trends': True
        }
        
        with patch.object(weather_service, 'get_current_weather') as mock_current, \
             patch.object(weather_service, 'get_weather_forecast') as mock_forecast:
            
            mock_current.return_value = {
                'temperature': 22,
                'condition': 'clear',
                'humidity': 65,
                'location_info': sample_location_data
            }
            
            mock_forecast.return_value = {
                'forecast_data': [
                    {'temperature_high': 25, 'temperature_low': 18},
                    {'temperature_high': 27, 'temperature_low': 20}
                ]
            }
            
            result = await weather_service.get_weather_summary(sample_location_data, summary_params)
            
            assert result is not None
            assert 'current_conditions' in result
            assert 'comfort_level' in result
            assert 'activity_recommendations' in result
            assert 'summary_text' in result
            assert 'trends' in result  # Because include_trends=True
    
    @pytest.mark.asyncio
    async def test_validate_api_connection(self, weather_service):
        """Test API connection validation"""
        result = await weather_service.validate_api_connection()
        
        assert result is not None
        assert 'connection_status' in result
        assert 'api_providers' in result
        assert 'response_times' in result
        assert 'rate_limits' in result
        
        # Check provider information
        for provider in weather_service.active_providers:
            assert provider.value in result['api_providers']
            assert provider.value in result['response_times']
    
    @pytest.mark.asyncio
    async def test_configure_weather_providers(self, weather_service):
        """Test weather provider configuration"""
        provider_config = {
            'primary_provider': WeatherProvider.OPENWEATHER,
            'fallback_providers': [WeatherProvider.WEATHERAPI],
            'api_keys': {
                'openweather': 'test_key_ow',
                'weatherapi': 'test_key_wa'
            },
            'request_timeout_seconds': 15,
            'retry_attempts': 2
        }
        
        result = await weather_service.configure_weather_providers(provider_config)
        
        assert result is not None
        assert 'configuration_status' in result
        assert 'active_providers' in result
        assert 'provider_capabilities' in result
        assert result['configuration_status'] == 'success'
        
        # Verify configuration was applied
        assert WeatherProvider.OPENWEATHER in weather_service.active_providers
        assert weather_service.providers[WeatherProvider.OPENWEATHER]['api_key'] == 'test_key_ow'
    
    @pytest.mark.asyncio
    async def test_get_location_weather_coordinates(self, weather_service):
        """Test getting weather by location query (coordinates)"""
        location_query = "35.6762,139.6503"
        
        with patch.object(weather_service, 'get_current_weather') as mock_get_weather:
            mock_get_weather.return_value = {'temperature': 20, 'condition': 'clear'}
            
            result = await weather_service.get_location_weather(location_query)
            
            assert result is not None
            mock_get_weather.assert_called_once()
            
            # Check the location data passed to get_current_weather
            call_args = mock_get_weather.call_args[0][0]
            assert call_args['latitude'] == 35.6762
            assert call_args['longitude'] == 139.6503
            assert call_args['location_type'] == LocationType.COORDINATES
    
    @pytest.mark.asyncio
    async def test_get_location_weather_city(self, weather_service):
        """Test getting weather by location query (city name)"""
        location_query = "Tokyo"
        
        with patch.object(weather_service, 'get_current_weather') as mock_get_weather:
            mock_get_weather.return_value = {'temperature': 20, 'condition': 'clear'}
            
            result = await weather_service.get_location_weather(location_query)
            
            assert result is not None
            mock_get_weather.assert_called_once()
            
            # Check the location data passed to get_current_weather
            call_args = mock_get_weather.call_args[0][0]
            assert call_args['city'] == 'Tokyo'
            assert call_args['location_type'] == LocationType.CITY_NAME
    
    @pytest.mark.asyncio
    async def test_cache_weather_data(self, weather_service, sample_location_data):
        """Test weather data caching"""
        cache_config = {
            'cache_strategy': CacheStrategy.INTELLIGENT,
            'cache_duration_minutes': 30,
            'cache_location_radius_km': 10,
            'auto_refresh': True
        }
        
        with patch.object(weather_service, 'get_current_weather') as mock_get_weather:
            mock_get_weather.return_value = {
                'temperature': 22,
                'condition': 'clear',
                'timestamp': datetime.now().isoformat()
            }
            
            result = await weather_service.cache_weather_data(sample_location_data, cache_config)
            
            assert result is not None
            assert 'cache_status' in result
            assert 'cached_data_types' in result
            assert 'cache_expiry' in result
            assert result['cache_status'] == 'cached'
    
    @pytest.mark.asyncio
    async def test_get_weather_trends(self, weather_service, sample_location_data):
        """Test weather trends analysis"""
        trend_params = {
            'time_period_days': 14,
            'analysis_type': 'comprehensive'
        }
        
        result = await weather_service.get_weather_trends(sample_location_data, trend_params)
        
        assert result is not None
        assert 'temperature_trend' in result
        assert 'precipitation_trend' in result
        assert 'seasonal_indicators' in result
        assert 'patterns_detected' in result
        
        # Check trend structure
        temp_trend = result['temperature_trend']
        assert 'direction' in temp_trend
        assert 'confidence' in temp_trend
        assert 0.0 <= temp_trend['confidence'] <= 1.0
    
    @pytest.mark.asyncio
    async def test_get_seasonal_patterns(self, weather_service, sample_location_data):
        """Test seasonal pattern retrieval"""
        result = await weather_service.get_seasonal_patterns(sample_location_data)
        
        assert result is not None
        seasons = ['spring', 'summer', 'autumn', 'winter']
        
        for season in seasons:
            assert season in result
            season_data = result[season]
            assert 'avg_temperature' in season_data
            assert 'precipitation_days' in season_data
            assert 'dominant_conditions' in season_data
            assert 'characteristics' in season_data
    
    @pytest.mark.asyncio
    async def test_get_weather_for_ai_context(self, weather_service, sample_location_data):
        """Test weather data for AI context"""
        ai_params = {
            'include_mood_indicators': True,
            'include_activity_suitability': True,
            'include_visual_atmosphere': True,
            'simplify_for_prompts': True
        }
        
        with patch.object(weather_service, 'get_current_weather') as mock_get_weather:
            mock_get_weather.return_value = {
                'temperature': 22,
                'condition': 'clear',
                'humidity': 60
            }
            
            result = await weather_service.get_weather_for_ai_context(sample_location_data, ai_params)
            
            assert result is not None
            assert 'weather_summary' in result
            assert 'basic_conditions' in result
            assert 'mood_indicators' in result
            assert 'activity_suggestions' in result
            assert 'visual_atmosphere' in result
            assert 'prompt_friendly_description' in result
    
    @pytest.mark.asyncio
    async def test_monitor_weather_changes(self, weather_service, sample_location_data):
        """Test weather change monitoring"""
        monitoring_config = {
            'monitor_parameters': ['temperature', 'condition'],
            'change_thresholds': {
                'temperature_change': 5,
                'condition_change': True
            },
            'monitoring_interval_minutes': 15
        }
        
        with patch.object(weather_service, 'get_current_weather') as mock_get_weather:
            mock_get_weather.return_value = {
                'temperature': 22,
                'condition': 'clear'
            }
            
            result = await weather_service.monitor_weather_changes(sample_location_data, monitoring_config)
            
            assert result is not None
            assert 'monitoring_status' in result
            assert 'current_conditions' in result
            assert 'change_detection' in result
            assert result['monitoring_status'] == 'active'
    
    @pytest.mark.asyncio
    async def test_get_weather_impact_score(self, weather_service, sample_location_data):
        """Test weather impact score calculation"""
        impact_params = {
            'activity_type': 'outdoor_photography',
            'user_preferences': {
                'preferred_weather': ['clear', 'partly_cloudy'],
                'avoid_weather': ['rainy', 'stormy']
            }
        }
        
        with patch.object(weather_service, 'get_current_weather') as mock_get_weather:
            mock_get_weather.return_value = {
                'temperature': 22,
                'condition': 'clear',
                'humidity': 60
            }
            
            result = await weather_service.get_weather_impact_score(sample_location_data, impact_params)
            
            assert result is not None
            assert 'impact_score' in result
            assert 'reasoning' in result
            assert 'recommendations' in result
            assert 'weather_factors' in result
            assert 0.0 <= result['impact_score'] <= 1.0
    
    @pytest.mark.asyncio
    async def test_bulk_weather_request(self, weather_service):
        """Test bulk weather requests"""
        locations = [
            {'latitude': 35.6762, 'longitude': 139.6503, 'name': 'Tokyo'},
            {'latitude': 40.7128, 'longitude': -74.0060, 'name': 'New York'},
            {'latitude': 51.5074, 'longitude': -0.1278, 'name': 'London'}
        ]
        
        bulk_params = {
            'data_types': ['current'],
            'optimize_requests': True,
            'max_concurrent': 2
        }
        
        with patch.object(weather_service, 'get_current_weather') as mock_get_weather:
            mock_get_weather.return_value = {'temperature': 20, 'condition': 'clear'}
            
            result = await weather_service.bulk_weather_request(locations, bulk_params)
            
            assert result is not None
            assert 'results' in result
            assert 'success_count' in result
            assert 'error_count' in result
            assert 'total_processed' in result
            assert len(result['results']) == len(locations)
    
    @pytest.mark.asyncio
    async def test_get_weather_recommendations(self, weather_service, sample_location_data):
        """Test weather-based recommendations"""
        recommendation_params = {
            'focus_area': 'photography',
            'time_horizon_hours': 12
        }
        
        with patch.object(weather_service, 'get_current_weather') as mock_current, \
             patch.object(weather_service, 'get_weather_forecast') as mock_forecast:
            
            mock_current.return_value = {'temperature': 22, 'condition': 'clear'}
            mock_forecast.return_value = {'forecast_data': []}
            
            result = await weather_service.get_weather_recommendations(
                sample_location_data, recommendation_params
            )
            
            assert result is not None
            assert 'current_recommendations' in result
            assert 'upcoming_recommendations' in result
            assert 'focus_area' in result
            assert 'photography_tips' in result  # Because focus_area is 'photography'
    
    def test_cache_functionality(self, weather_service):
        """Test cache validity and data management"""
        cache_key = "test_cache_key"
        test_data = {'temperature': 20, 'condition': 'clear'}
        
        # Test cache miss
        assert not weather_service._is_cache_valid(cache_key)
        
        # Cache data
        weather_service._cache_data(cache_key, test_data)
        
        # Test cache hit
        assert weather_service._is_cache_valid(cache_key)
        assert weather_service.cache[cache_key]['data'] == test_data
    
    def test_weather_description_generation(self, weather_service):
        """Test weather description generation"""
        weather_data = {
            'condition': 'clear',
            'temperature': 22
        }
        
        description = weather_service._get_weather_description(weather_data)
        
        assert isinstance(description, str)
        assert '22' in description
        assert 'clear' in description.lower()
    
    def test_comfort_level_calculation(self, weather_service):
        """Test comfort level calculation"""
        # Test comfortable conditions
        comfortable_weather = {
            'temperature': 22,
            'condition': 'clear',
            'humidity': 50
        }
        
        comfort = weather_service._calculate_comfort_level(comfortable_weather)
        assert comfort in ['very_comfortable', 'comfortable']
        
        # Test uncomfortable conditions
        uncomfortable_weather = {
            'temperature': 40,
            'condition': 'stormy',
            'humidity': 90
        }
        
        comfort = weather_service._calculate_comfort_level(uncomfortable_weather)
        assert comfort in ['uncomfortable', 'moderate']
    
    def test_activity_recommendations(self, weather_service):
        """Test activity recommendation generation"""
        good_weather = {
            'temperature': 22,
            'condition': 'clear'
        }
        
        recommendations = weather_service._get_activity_recommendations(good_weather)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Should include outdoor activities for good weather
        outdoor_activities = ['outdoor photography', 'picnic', 'hiking', 'cycling']
        assert any(activity in ' '.join(recommendations) for activity in outdoor_activities)
    
    @pytest.mark.asyncio
    async def test_geocode_city(self, weather_service):
        """Test city name to coordinates conversion"""
        lat, lon = await weather_service._geocode_city('Tokyo', 'Japan')
        
        assert isinstance(lat, float)
        assert isinstance(lon, float)
        # Tokyo coordinates should be around these values
        assert 35.0 <= lat <= 36.0
        assert 139.0 <= lon <= 140.0
    
    @pytest.mark.asyncio
    async def test_fallback_weather(self, weather_service, sample_location_data):
        """Test fallback weather when API fails"""
        fallback_weather = await weather_service._get_fallback_weather(sample_location_data)
        
        assert fallback_weather is not None
        assert 'temperature' in fallback_weather
        assert 'condition' in fallback_weather
        assert 'fallback' in fallback_weather
        assert fallback_weather['fallback'] is True
        assert fallback_weather['confidence'] < 1.0


class TestWeatherAPIServiceErrorHandling:
    """Test error handling in WeatherAPIService"""
    
    @pytest.fixture
    def weather_service(self):
        return WeatherAPIService()
    
    @pytest.mark.asyncio
    async def test_invalid_location_type(self, weather_service):
        """Test handling of invalid location type"""
        invalid_location = {
            'location_type': 'invalid_type',
            'some_data': 'test'
        }
        
        result = await weather_service.get_current_weather(invalid_location)
        
        # Should return fallback weather
        assert result is not None
        assert 'fallback' in result or 'error' in str(result)
    
    @pytest.mark.asyncio
    async def test_api_request_failure(self, weather_service, sample_location_data):
        """Test handling of API request failures"""
        with patch.object(weather_service, '_fetch_current_weather') as mock_fetch:
            mock_fetch.side_effect = Exception("API connection failed")
            
            result = await weather_service.get_current_weather(sample_location_data)
            
            # Should return fallback weather
            assert result is not None
            assert 'fallback' in result
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, weather_service):
        """Test handling of missing required fields"""
        incomplete_location = {}  # Missing latitude, longitude, etc.
        
        result = await weather_service.get_current_weather(incomplete_location)
        
        # Should handle gracefully
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])