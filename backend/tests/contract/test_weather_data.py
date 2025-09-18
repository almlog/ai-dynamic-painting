"""
Contract test for WeatherData model
Test File: backend/tests/contract/test_weather_data.py

This test MUST FAIL initially (RED phase of TDD)
"""

import pytest
from pathlib import Path
import sys
from datetime import datetime, timedelta
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_weather_data_model_exists():
    """Test that WeatherData model exists and has required fields"""
    # This should initially FAIL until we implement the model
    try:
        from src.ai.models.weather_data import WeatherData
        
        # Test model can be instantiated
        weather = WeatherData()
        assert weather is not None
        
        # Test required fields exist
        required_fields = [
            'weather_id', 'location', 'timestamp', 'temperature_celsius',
            'humidity_percent', 'weather_condition', 'weather_description',
            'wind_speed_kmh', 'pressure_hpa', 'visibility_km', 'uv_index',
            'sunrise_time', 'sunset_time', 'data_source', 'is_current'
        ]
        
        for field in required_fields:
            assert hasattr(weather, field), f"Missing required field: {field}"
            
    except ImportError:
        pytest.fail("WeatherData model not implemented yet")


def test_weather_condition_enum():
    """Test that weather condition enum is properly defined"""
    try:
        from src.ai.models.weather_data import WeatherCondition
        
        # Test enum values exist
        expected_conditions = ['sunny', 'cloudy', 'partly_cloudy', 'rainy', 'stormy', 'snowy', 'foggy', 'windy']
        
        for condition in expected_conditions:
            assert hasattr(WeatherCondition, condition.upper()), f"Missing weather condition: {condition}"
            
    except ImportError:
        pytest.fail("WeatherCondition enum not implemented yet")


def test_weather_data_source_enum():
    """Test that data source enum is properly defined"""
    try:
        from src.ai.models.weather_data import DataSource
        
        # Test enum values exist
        expected_sources = ['openweathermap', 'manual', 'sensor', 'forecast']
        
        for source in expected_sources:
            assert hasattr(DataSource, source.upper()), f"Missing data source: {source}"
            
    except ImportError:
        pytest.fail("DataSource enum not implemented yet")


def test_weather_data_crud_operations():
    """Test basic CRUD operations for WeatherData"""
    try:
        from src.ai.models.weather_data import WeatherData, WeatherCondition, DataSource
        
        # Test creation with required fields
        weather_data = {
            'weather_id': 'weather_001',
            'location': 'Tokyo, Japan',
            'temperature_celsius': 25.5,
            'humidity_percent': 60,
            'weather_condition': WeatherCondition.PARTLY_CLOUDY,
            'weather_description': 'Partly cloudy with gentle breeze',
            'wind_speed_kmh': 12.3,
            'pressure_hpa': 1013.25,
            'data_source': DataSource.OPENWEATHERMAP
        }
        
        weather = WeatherData(**weather_data)
        assert weather.weather_id == 'weather_001'
        assert weather.location == 'Tokyo, Japan'
        assert weather.temperature_celsius == 25.5
        assert weather.weather_condition == WeatherCondition.PARTLY_CLOUDY
        
        # Test temperature conversion
        temp_f = weather.get_temperature_fahrenheit()
        assert abs(temp_f - 77.9) < 0.1  # 25.5°C ≈ 77.9°F
        
    except ImportError:
        pytest.fail("WeatherData model not fully implemented")


def test_weather_data_validation():
    """Test data validation for WeatherData"""
    try:
        from src.ai.models.weather_data import WeatherData, WeatherCondition, DataSource
        
        # Test temperature validation
        weather = WeatherData(
            weather_id='test_002',
            location='Test Location',
            temperature_celsius=-50,  # Extreme cold but valid
            humidity_percent=150,     # Should be clamped to 0-100
            weather_condition=WeatherCondition.SNOWY,
            data_source=DataSource.SENSOR
        )
        
        # Humidity should be clamped
        assert 0 <= weather.humidity_percent <= 100
        
        # Wind speed should be non-negative
        weather.wind_speed_kmh = -5
        assert weather.wind_speed_kmh >= 0
        
        # UV index should be 0-11+
        weather.uv_index = -1
        assert weather.uv_index >= 0
        
    except ImportError:
        pytest.fail("WeatherData validation not implemented")


def test_weather_data_time_operations():
    """Test time-based operations and calculations"""
    try:
        from src.ai.models.weather_data import WeatherData, WeatherCondition
        
        now = datetime.now()
        sunrise = now.replace(hour=6, minute=0, second=0, microsecond=0)
        sunset = now.replace(hour=18, minute=0, second=0, microsecond=0)
        
        weather = WeatherData(
            weather_id='time_test_001',
            location='Time Test City',
            timestamp=now,
            temperature_celsius=20.0,
            weather_condition=WeatherCondition.SUNNY,
            sunrise_time=sunrise,
            sunset_time=sunset
        )
        
        # Test daylight calculation
        daylight_hours = weather.calculate_daylight_hours()
        assert daylight_hours == 12.0  # 6 AM to 6 PM = 12 hours
        
        # Test if it's currently day or night
        noon = now.replace(hour=12, minute=0, second=0, microsecond=0)
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        assert weather.is_daytime(noon) == True
        assert weather.is_daytime(midnight) == False
        
        # Test data freshness
        assert weather.is_data_fresh(max_age_hours=1) == True
        
        old_weather = WeatherData(
            weather_id='old_001',
            location='Old City',
            timestamp=now - timedelta(hours=5),
            temperature_celsius=15.0,
            weather_condition=WeatherCondition.CLOUDY
        )
        assert old_weather.is_data_fresh(max_age_hours=1) == False
        
    except ImportError:
        pytest.fail("WeatherData time operations not implemented")


def test_weather_data_comfort_analysis():
    """Test comfort and suitability analysis"""
    try:
        from src.ai.models.weather_data import WeatherData, WeatherCondition
        
        # Comfortable weather
        comfortable_weather = WeatherData(
            weather_id='comfort_001',
            location='Comfort City',
            temperature_celsius=22.0,
            humidity_percent=50,
            weather_condition=WeatherCondition.SUNNY,
            wind_speed_kmh=5.0,
            uv_index=3
        )
        
        # Test comfort assessment
        assert comfortable_weather.is_comfortable_temperature() == True
        assert comfortable_weather.is_good_visibility() == True
        
        # Uncomfortable weather
        hot_weather = WeatherData(
            weather_id='hot_001',
            location='Hot City',
            temperature_celsius=38.0,
            humidity_percent=85,
            weather_condition=WeatherCondition.SUNNY,
            uv_index=10
        )
        
        assert hot_weather.is_comfortable_temperature() == False
        assert hot_weather.is_high_uv() == True
        
        # Test outdoor activity suitability
        assert comfortable_weather.is_suitable_for_outdoor_activity() == True
        assert hot_weather.is_suitable_for_outdoor_activity() == False
        
    except ImportError:
        pytest.fail("WeatherData comfort analysis not implemented")


def test_weather_data_context_generation():
    """Test weather context generation for AI prompts"""
    try:
        from src.ai.models.weather_data import WeatherData, WeatherCondition
        
        weather = WeatherData(
            weather_id='context_001',
            location='Context City',
            temperature_celsius=28.0,
            humidity_percent=70,
            weather_condition=WeatherCondition.PARTLY_CLOUDY,
            weather_description='Warm afternoon with scattered clouds',
            wind_speed_kmh=8.0,
            uv_index=6
        )
        
        # Test mood generation
        mood = weather.generate_mood_context()
        assert isinstance(mood, str)
        assert len(mood) > 0
        
        # Test color palette suggestion
        colors = weather.suggest_color_palette()
        assert isinstance(colors, list)
        assert len(colors) > 0
        
        # Test prompt context
        prompt_context = weather.generate_prompt_context()
        assert isinstance(prompt_context, dict)
        assert 'temperature_feel' in prompt_context
        assert 'weather_mood' in prompt_context
        assert 'lighting_condition' in prompt_context
        
    except ImportError:
        pytest.fail("WeatherData context generation not implemented")


def test_weather_data_json_serialization():
    """Test JSON serialization/deserialization"""
    try:
        from src.ai.models.weather_data import WeatherData, WeatherCondition, DataSource
        import json
        
        now = datetime.now()
        
        weather = WeatherData(
            weather_id='serialize_test_001',
            location='Serialize City',
            timestamp=now,
            temperature_celsius=18.5,
            humidity_percent=65,
            weather_condition=WeatherCondition.RAINY,
            weather_description='Light rain with cool temperatures',
            wind_speed_kmh=15.2,
            pressure_hpa=1008.5,
            visibility_km=8.0,
            uv_index=2,
            data_source=DataSource.OPENWEATHERMAP,
            is_current=True
        )
        
        # Test to_dict method
        weather_dict = weather.to_dict()
        assert isinstance(weather_dict, dict)
        assert weather_dict['weather_id'] == 'serialize_test_001'
        assert weather_dict['location'] == 'Serialize City'
        assert weather_dict['temperature_celsius'] == 18.5
        
        # Test JSON serialization
        json_str = json.dumps(weather_dict)
        assert isinstance(json_str, str)
        
        # Test deserialization
        loaded_dict = json.loads(json_str)
        assert loaded_dict['weather_id'] == 'serialize_test_001'
        
    except ImportError:
        pytest.fail("WeatherData serialization not implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])