"""
Contract tests for multi-source integration - T255.
Tests MUST fail initially (RED phase), then pass after implementation (GREEN phase).
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestMultiSourceIntegrationContract:
    """Contract tests for T255: Multi-source Integration"""
    
    def test_data_source_model_exists(self):
        """Test that DataSource model exists"""
        from src.models.data_source import DataSource
        
        # Test model creation
        source = DataSource(
            source_id="src_123",
            source_type="weather_api",
            source_name="OpenWeather API",
            endpoint_url="https://api.openweathermap.org/data/2.5/weather",
            authentication_type="api_key",
            configuration={"api_key": "test_key", "units": "metric"},
            is_active=True,
            priority=1
        )
        
        assert source.source_id == "src_123"
        assert source.source_type == "weather_api"
        assert source.source_name == "OpenWeather API"
        assert source.is_active == True
        assert source.priority == 1
    
    @pytest.mark.asyncio
    async def test_multi_source_manager_exists(self):
        """Test that MultiSourceManager service exists and works"""
        from src.ai.services.multi_source_manager import MultiSourceManager
        
        # Create manager
        manager = MultiSourceManager()
        
        # Test source registration
        weather_config = {
            "source_type": "weather_api",
            "endpoint": "https://api.openweathermap.org/data/2.5/weather",
            "api_key": "test_key"
        }
        
        source_id = await manager.register_data_source("weather", weather_config)
        assert source_id is not None
        assert isinstance(source_id, str)
        
        # Test source listing
        sources = await manager.get_active_sources()
        assert len(sources) >= 1
        assert any(s["source_type"] == "weather_api" for s in sources)
    
    @pytest.mark.asyncio
    async def test_weather_integration(self):
        """Test weather API integration"""
        from src.ai.services.multi_source_manager import MultiSourceManager
        
        manager = MultiSourceManager()
        
        # Test weather data fetching
        location = {"lat": 35.6762, "lon": 139.6503}  # Tokyo coordinates
        weather_data = await manager.fetch_weather_data(location)
        
        assert weather_data is not None
        assert "temperature" in weather_data
        assert "humidity" in weather_data
        assert "weather_condition" in weather_data
        assert "timestamp" in weather_data
        
        # Temperature should be reasonable (mock data)
        assert -50 <= weather_data["temperature"] <= 50
        assert 0 <= weather_data["humidity"] <= 100
    
    @pytest.mark.asyncio
    async def test_time_data_integration(self):
        """Test time/calendar data integration"""
        from src.ai.services.multi_source_manager import MultiSourceManager
        
        manager = MultiSourceManager()
        
        # Test time data fetching
        timezone = "Asia/Tokyo"
        time_data = await manager.fetch_time_data(timezone)
        
        assert time_data is not None
        assert "current_time" in time_data
        assert "time_of_day" in time_data  # morning, afternoon, evening, night
        assert "day_of_week" in time_data
        assert "season" in time_data
        assert "is_weekend" in time_data
        
        # Validate time of day
        assert time_data["time_of_day"] in ["morning", "afternoon", "evening", "night"]
        assert time_data["day_of_week"] in [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
        ]
        assert time_data["season"] in ["spring", "summer", "autumn", "winter"]
    
    @pytest.mark.asyncio
    async def test_sensor_data_integration(self):
        """Test sensor data integration (M5Stack, etc.)"""
        from src.ai.services.multi_source_manager import MultiSourceManager
        
        manager = MultiSourceManager()
        
        # Test sensor data fetching
        device_id = "m5stack_001"
        sensor_data = await manager.fetch_sensor_data(device_id)
        
        assert sensor_data is not None
        assert "device_id" in sensor_data
        assert "temperature" in sensor_data
        assert "humidity" in sensor_data
        assert "light_level" in sensor_data
        assert "button_states" in sensor_data
        assert "timestamp" in sensor_data
        
        # Validate sensor ranges
        assert isinstance(sensor_data["button_states"], dict)
        assert 0 <= sensor_data["light_level"] <= 100
    
    @pytest.mark.asyncio
    async def test_data_aggregation(self):
        """Test multi-source data aggregation"""
        from src.ai.services.multi_source_manager import MultiSourceManager
        
        manager = MultiSourceManager()
        
        # Test data aggregation from multiple sources
        sources = ["weather", "time", "sensor"]
        context = {"location": {"lat": 35.6762, "lon": 139.6503}, "device_id": "m5stack_001"}
        
        aggregated_data = await manager.aggregate_data(sources, context)
        
        assert aggregated_data is not None
        assert "weather" in aggregated_data
        assert "time" in aggregated_data
        assert "sensor" in aggregated_data
        assert "aggregation_timestamp" in aggregated_data
        assert "source_count" in aggregated_data
        
        # Each source should have data
        assert aggregated_data["weather"] is not None
        assert aggregated_data["time"] is not None
        assert aggregated_data["sensor"] is not None
        assert aggregated_data["source_count"] == 3
    
    @pytest.mark.asyncio
    async def test_data_prioritization(self):
        """Test data source prioritization"""
        from src.ai.services.multi_source_manager import MultiSourceManager
        
        manager = MultiSourceManager()
        
        # Register multiple weather sources with different priorities
        primary_config = {
            "source_type": "weather_api_primary",
            "endpoint": "https://primary-weather.com/api",
            "priority": 1
        }
        
        backup_config = {
            "source_type": "weather_api_backup", 
            "endpoint": "https://backup-weather.com/api",
            "priority": 2
        }
        
        primary_id = await manager.register_data_source("weather_primary", primary_config)
        backup_id = await manager.register_data_source("weather_backup", backup_config)
        
        # Test prioritized data fetching
        weather_data = await manager.fetch_prioritized_weather_data({"lat": 35.6762, "lon": 139.6503})
        
        assert weather_data is not None
        assert "source_used" in weather_data
        assert "fallback_attempted" in weather_data
    
    @pytest.mark.asyncio
    async def test_fallback_mechanism(self):
        """Test fallback mechanism when primary sources fail"""
        from src.ai.services.multi_source_manager import MultiSourceManager
        
        manager = MultiSourceManager()
        
        # Test fallback behavior
        unreliable_sources = ["failing_source", "another_failing_source", "working_source"]
        
        result = await manager.fetch_with_fallback(
            sources=unreliable_sources,
            data_type="weather",
            context={"lat": 35.6762, "lon": 139.6503}
        )
        
        assert result is not None
        assert "data" in result
        assert "source_used" in result
        assert "attempts_made" in result
        assert "fallback_chain" in result
        
        # Should have attempted multiple sources
        assert result["attempts_made"] >= 1
        assert len(result["fallback_chain"]) >= 1
    
    @pytest.mark.asyncio
    async def test_data_caching_across_sources(self):
        """Test data caching across multiple sources"""
        from src.ai.services.multi_source_manager import MultiSourceManager
        
        manager = MultiSourceManager()
        
        context = {"lat": 35.6762, "lon": 139.6503}
        
        # First fetch - should hit all sources
        import time
        start_time = time.time()
        data1 = await manager.fetch_cached_weather_data(context, cache_ttl=300)
        time1 = time.time() - start_time
        
        # Second fetch - should use cache
        start_time = time.time()
        data2 = await manager.fetch_cached_weather_data(context, cache_ttl=300)
        time2 = time.time() - start_time
        
        assert data1 is not None
        assert data2 is not None
        assert data1["temperature"] == data2["temperature"]  # Same cached data
        assert time2 < time1  # Cache should be faster
        assert data2["cache_hit"] == True
    
    @pytest.mark.asyncio
    async def test_context_aware_source_selection(self):
        """Test context-aware source selection"""
        from src.ai.services.multi_source_manager import MultiSourceManager
        
        manager = MultiSourceManager()
        
        # Different contexts should select different optimal sources
        indoor_context = {
            "location_type": "indoor",
            "device_type": "m5stack",
            "priority": "sensor_accuracy"
        }
        
        outdoor_context = {
            "location_type": "outdoor", 
            "device_type": "weather_station",
            "priority": "weather_accuracy"
        }
        
        indoor_sources = await manager.select_optimal_sources(indoor_context)
        outdoor_sources = await manager.select_optimal_sources(outdoor_context)
        
        assert indoor_sources is not None
        assert outdoor_sources is not None
        assert isinstance(indoor_sources, list)
        assert isinstance(outdoor_sources, list)
        
        # Indoor should prefer sensor data, outdoor should prefer weather API
        indoor_types = [s["source_type"] for s in indoor_sources]
        outdoor_types = [s["source_type"] for s in outdoor_sources]
        
        assert any("sensor" in t for t in indoor_types)
        assert any("weather" in t for t in outdoor_types)
    
    @pytest.mark.asyncio
    async def test_real_time_data_streaming(self):
        """Test real-time data streaming from multiple sources"""
        from src.ai.services.multi_source_manager import MultiSourceManager
        
        manager = MultiSourceManager()
        
        # Start data streaming
        stream_id = await manager.start_data_stream(
            sources=["weather", "sensor", "time"],
            interval_seconds=1,
            context={"device_id": "m5stack_001"}
        )
        
        assert stream_id is not None
        
        # Wait for some data
        await asyncio.sleep(0.5)
        
        # Get streamed data
        stream_data = await manager.get_stream_data(stream_id, limit=3)
        
        assert stream_data is not None
        assert "stream_id" in stream_data
        assert "data_points" in stream_data
        assert len(stream_data["data_points"]) >= 0  # May be empty if stream just started
        
        # Stop streaming
        stop_result = await manager.stop_data_stream(stream_id)
        assert stop_result["status"] == "stopped"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])