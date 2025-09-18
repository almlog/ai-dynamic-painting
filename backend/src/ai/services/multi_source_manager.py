"""
Multi-source data integration manager for AI operations.
Handles weather APIs, sensor data, time information, and data aggregation.
"""

import uuid
import time
import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import aiohttp
import random

from src.models.data_source import (
    DataSource,
    DataSourceConfig,
    SourceData,
    AggregatedData,
    StreamConfig,
    WeatherData,
    TimeData,
    SensorData,
    SourceType,
    AuthType
)


class MultiSourceManager:
    """Service for managing multiple data sources and integration"""
    
    def __init__(self, db_url: str = "sqlite:///ai_dynamic_painting.db"):
        self.engine = create_engine(db_url)
        self.session_factory = sessionmaker(bind=self.engine)
        
        # Data caching
        self.cache = {}
        self.cache_timestamps = {}
        
        # Active streams
        self.active_streams = {}
        
        # Source configurations
        self.registered_sources = {}
        
        # Mock data for testing
        self.mock_mode = True  # Set to False for real API calls
        
    async def register_data_source(self, source_name: str, 
                                 config: Dict[str, Any]) -> str:
        """Register a new data source"""
        source_id = f"src_{uuid.uuid4().hex[:8]}"
        
        # For testing, store in memory only
        source_data = {
            "source_id": source_id,
            "source_type": config.get("source_type", "unknown"),
            "source_name": source_name,
            "endpoint_url": config.get("endpoint", ""),
            "authentication_type": config.get("auth_type", "none"),
            "configuration": config,
            "is_active": True,
            "priority": config.get("priority", 1),
            "created_at": datetime.now()
        }
        
        # Store in memory for quick access
        self.registered_sources[source_id] = source_data
        
        return source_id
    
    async def get_active_sources(self) -> List[Dict[str, Any]]:
        """Get list of active data sources"""
        result = []
        for source_data in self.registered_sources.values():
            if source_data.get("is_active", True):
                result.append({
                    "source_id": source_data["source_id"],
                    "source_type": source_data["source_type"],
                    "source_name": source_data["source_name"],
                    "priority": source_data.get("priority", 1),
                    "success_rate": source_data.get("success_rate", 1.0),
                    "last_success": source_data.get("last_success")
                })
        
        # Sort by priority
        result.sort(key=lambda x: x["priority"])
        return result
    
    async def fetch_weather_data(self, location: Dict[str, float]) -> Dict[str, Any]:
        """Fetch weather data for given location"""
        if self.mock_mode:
            # Mock weather data for testing
            await asyncio.sleep(0.05)  # Simulate API call
            return {
                "temperature": random.uniform(15, 35),
                "humidity": random.randint(30, 90),
                "weather_condition": random.choice(["sunny", "cloudy", "rainy", "snowy"]),
                "wind_speed": random.uniform(0, 15),
                "pressure": random.uniform(990, 1030),
                "visibility": random.uniform(5, 20),
                "timestamp": datetime.now().isoformat(),
                "location": location
            }
        
        # Real API implementation would go here
        cache_key = f"weather_{location['lat']}_{location['lon']}"
        cached_data = self._get_cached_data(cache_key, ttl=300)
        if cached_data:
            return cached_data
        
        # Simulate API call
        weather_data = {
            "temperature": 22.5,
            "humidity": 65,
            "weather_condition": "partly_cloudy",
            "timestamp": datetime.now().isoformat(),
            "location": location
        }
        
        self._cache_data(cache_key, weather_data)
        return weather_data
    
    async def fetch_time_data(self, timezone: str = "UTC") -> Dict[str, Any]:
        """Fetch time and calendar data"""
        now = datetime.now()
        
        # Determine time of day
        hour = now.hour
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        # Determine season (simplified for Northern Hemisphere)
        month = now.month
        if month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        elif month in [9, 10, 11]:
            season = "autumn"
        else:
            season = "winter"
        
        return {
            "current_time": now.isoformat(),
            "time_of_day": time_of_day,
            "day_of_week": now.strftime("%A"),
            "season": season,
            "is_weekend": now.weekday() >= 5,
            "is_holiday": False,  # Simplified
            "timezone": timezone
        }
    
    async def fetch_sensor_data(self, device_id: str) -> Dict[str, Any]:
        """Fetch sensor data from M5Stack or other devices"""
        if self.mock_mode:
            # Mock sensor data
            await asyncio.sleep(0.02)  # Simulate device communication
            return {
                "device_id": device_id,
                "temperature": random.uniform(18, 28),
                "humidity": random.randint(40, 80),
                "light_level": random.randint(10, 90),
                "button_states": {
                    "button_a": random.choice([True, False]),
                    "button_b": random.choice([True, False]),
                    "button_c": random.choice([True, False])
                },
                "battery_level": random.randint(20, 100),
                "wifi_signal": random.randint(50, 100),
                "timestamp": datetime.now().isoformat()
            }
        
        # Real device communication would go here
        # For now, return mock data
        return await self.fetch_sensor_data(device_id)
    
    async def aggregate_data(self, sources: List[str], 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate data from multiple sources"""
        aggregation_id = f"agg_{uuid.uuid4().hex[:8]}"
        aggregated_data = {}
        failed_sources = []
        successful_count = 0
        
        for source_type in sources:
            try:
                if source_type == "weather":
                    location = context.get("location", {"lat": 35.6762, "lon": 139.6503})
                    data = await self.fetch_weather_data(location)
                    aggregated_data["weather"] = data
                    successful_count += 1
                    
                elif source_type == "time":
                    timezone = context.get("timezone", "UTC")
                    data = await self.fetch_time_data(timezone)
                    aggregated_data["time"] = data
                    successful_count += 1
                    
                elif source_type == "sensor":
                    device_id = context.get("device_id", "default_device")
                    data = await self.fetch_sensor_data(device_id)
                    aggregated_data["sensor"] = data
                    successful_count += 1
                    
                else:
                    failed_sources.append(source_type)
                    
            except Exception as e:
                failed_sources.append(source_type)
        
        quality_score = successful_count / len(sources) if sources else 0
        
        return {
            "aggregation_id": aggregation_id,
            "weather": aggregated_data.get("weather"),
            "time": aggregated_data.get("time"),
            "sensor": aggregated_data.get("sensor"),
            "aggregation_timestamp": datetime.now().isoformat(),
            "source_count": successful_count,
            "failed_sources": failed_sources,
            "quality_score": quality_score
        }
    
    async def fetch_prioritized_weather_data(self, location: Dict[str, float]) -> Dict[str, Any]:
        """Fetch weather data using source prioritization"""
        # Get weather sources ordered by priority
        weather_sources = []
        for source_data in self.registered_sources.values():
            if ("weather" in source_data["source_type"] and 
                source_data.get("is_active", True)):
                weather_sources.append(source_data)
        
        # Sort by priority
        weather_sources.sort(key=lambda x: x.get("priority", 1))
        
        for source in weather_sources:
            try:
                # Attempt to fetch from this source
                data = await self.fetch_weather_data(location)
                data["source_used"] = source["source_id"]
                data["fallback_attempted"] = False
                return data
            except Exception:
                continue
        
        # All sources failed, return mock data
        data = await self.fetch_weather_data(location)
        data["source_used"] = "fallback_mock"
        data["fallback_attempted"] = True
        return data
    
    async def fetch_with_fallback(self, sources: List[str], data_type: str,
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data with fallback mechanism"""
        fallback_chain = []
        attempts_made = 0
        
        for source in sources:
            attempts_made += 1
            fallback_chain.append(source)
            
            try:
                if source == "working_source":
                    # Simulate successful source
                    if data_type == "weather":
                        data = await self.fetch_weather_data(context)
                    else:
                        data = {"mock_data": True, "type": data_type}
                    
                    return {
                        "data": data,
                        "source_used": source,
                        "attempts_made": attempts_made,
                        "fallback_chain": fallback_chain,
                        "success": True
                    }
                else:
                    # Simulate failing source
                    raise Exception(f"Source {source} failed")
                    
            except Exception:
                continue
        
        # All sources failed
        return {
            "data": None,
            "source_used": None,
            "attempts_made": attempts_made,
            "fallback_chain": fallback_chain,
            "success": False
        }
    
    async def fetch_cached_weather_data(self, context: Dict[str, Any], 
                                      cache_ttl: int = 300) -> Dict[str, Any]:
        """Fetch weather data with caching"""
        cache_key = f"weather_{context['lat']}_{context['lon']}"
        
        # Check cache
        cached_data = self._get_cached_data(cache_key, cache_ttl)
        if cached_data:
            # Create a copy to avoid modifying original cached data
            result = cached_data.copy()
            result["cache_hit"] = True
            return result
        
        # Fetch fresh data
        data = await self.fetch_weather_data(context)
        data["cache_hit"] = False
        
        # Cache the data
        self._cache_data(cache_key, data)
        
        return data
    
    async def select_optimal_sources(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Select optimal sources based on context"""
        location_type = context.get("location_type", "unknown")
        priority = context.get("priority", "balanced")
        
        sources = []
        
        if location_type == "indoor":
            # Prefer sensor data for indoor
            sources.append({
                "source_type": "sensor_device",
                "priority": 1,
                "reason": "indoor_environment"
            })
            sources.append({
                "source_type": "time_api",
                "priority": 2,
                "reason": "time_context"
            })
            
        elif location_type == "outdoor":
            # Prefer weather API for outdoor
            sources.append({
                "source_type": "weather_api",
                "priority": 1,
                "reason": "outdoor_environment"
            })
            sources.append({
                "source_type": "sensor_device",
                "priority": 2,
                "reason": "local_conditions"
            })
        
        else:
            # Balanced approach
            sources.append({
                "source_type": "weather_api",
                "priority": 1,
                "reason": "general_context"
            })
            sources.append({
                "source_type": "time_api",
                "priority": 2,
                "reason": "temporal_context"
            })
        
        return sources
    
    async def start_data_stream(self, sources: List[str], interval_seconds: int,
                              context: Dict[str, Any]) -> str:
        """Start real-time data streaming"""
        stream_id = f"stream_{uuid.uuid4().hex[:8]}"
        
        self.active_streams[stream_id] = {
            "sources": sources,
            "interval": interval_seconds,
            "context": context,
            "data_buffer": [],
            "is_running": True,
            "start_time": time.time()
        }
        
        # Start background streaming task
        asyncio.create_task(self._stream_data(stream_id))
        
        return stream_id
    
    async def get_stream_data(self, stream_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get data from active stream"""
        if stream_id not in self.active_streams:
            return {"error": "Stream not found"}
        
        stream = self.active_streams[stream_id]
        data_points = stream["data_buffer"][-limit:] if stream["data_buffer"] else []
        
        return {
            "stream_id": stream_id,
            "data_points": data_points,
            "buffer_size": len(stream["data_buffer"]),
            "is_running": stream["is_running"]
        }
    
    async def stop_data_stream(self, stream_id: str) -> Dict[str, str]:
        """Stop data streaming"""
        if stream_id in self.active_streams:
            self.active_streams[stream_id]["is_running"] = False
            # Clean up after a delay
            asyncio.create_task(self._cleanup_stream(stream_id))
            return {"status": "stopped", "stream_id": stream_id}
        
        return {"status": "not_found", "stream_id": stream_id}
    
    def _get_cached_data(self, cache_key: str, ttl: int) -> Optional[Dict[str, Any]]:
        """Get data from cache if not expired"""
        if cache_key in self.cache:
            cache_time = self.cache_timestamps.get(cache_key, 0)
            if time.time() - cache_time < ttl:
                return self.cache[cache_key]
            else:
                # Expired
                del self.cache[cache_key]
                del self.cache_timestamps[cache_key]
        
        return None
    
    def _cache_data(self, cache_key: str, data: Dict[str, Any]):
        """Cache data with timestamp"""
        self.cache[cache_key] = data
        self.cache_timestamps[cache_key] = time.time()
    
    async def _stream_data(self, stream_id: str):
        """Background task for streaming data"""
        stream = self.active_streams.get(stream_id)
        if not stream:
            return
        
        while stream.get("is_running", False):
            try:
                # Fetch data from all sources
                aggregated = await self.aggregate_data(
                    stream["sources"], 
                    stream["context"]
                )
                
                # Add to buffer
                stream["data_buffer"].append({
                    "timestamp": datetime.now().isoformat(),
                    "data": aggregated
                })
                
                # Limit buffer size
                if len(stream["data_buffer"]) > 100:
                    stream["data_buffer"] = stream["data_buffer"][-50:]
                
                await asyncio.sleep(stream["interval"])
                
            except Exception:
                # Continue streaming even if individual fetch fails
                await asyncio.sleep(stream["interval"])
    
    async def _cleanup_stream(self, stream_id: str):
        """Clean up stream after delay"""
        await asyncio.sleep(5)  # Wait 5 seconds before cleanup
        if stream_id in self.active_streams:
            del self.active_streams[stream_id]