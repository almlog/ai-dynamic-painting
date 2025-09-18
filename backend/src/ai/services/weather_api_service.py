"""Weather API Service for external weather data integration."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import math
from statistics import mean, median
import aiohttp
import time
from collections import defaultdict

logger = logging.getLogger("ai_system.weather")


class WeatherProvider(Enum):
    """Enumeration for weather API providers"""
    OPENWEATHER = "openweather"
    ACCUWEATHER = "accuweather" 
    WEATHERAPI = "weatherapi"
    NOAA = "noaa"
    BACKUP = "backup"


class WeatherCondition(Enum):
    """Enumeration for weather conditions"""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    SNOWY = "snowy"
    STORMY = "stormy"
    FOGGY = "foggy"
    WINDY = "windy"


class WeatherSeverity(Enum):
    """Enumeration for weather severity levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


class ForecastType(Enum):
    """Enumeration for forecast types"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    EXTENDED = "extended"


class LocationType(Enum):
    """Enumeration for location types"""
    COORDINATES = "coordinates"
    CITY_NAME = "city_name"
    ZIP_CODE = "zip_code"
    IP_ADDRESS = "ip_address"


class CacheStrategy(Enum):
    """Enumeration for caching strategies"""
    NONE = "none"
    BASIC = "basic"
    INTELLIGENT = "intelligent"
    AGGRESSIVE = "aggressive"


@dataclass
class WeatherData:
    """Data class for weather information"""
    temperature: float
    condition: WeatherCondition
    humidity: int
    pressure: float
    wind_speed: float
    visibility: float
    timestamp: datetime
    location_info: Dict[str, Any]
    provider: WeatherProvider = WeatherProvider.OPENWEATHER
    confidence: float = 1.0


@dataclass 
class WeatherAlert:
    """Data class for weather alerts"""
    alert_id: str
    alert_type: str
    severity: WeatherSeverity
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    affected_areas: List[str]
    instructions: str = ""


class WeatherAPIService:
    """Weather API service for external weather data integration"""
    
    def __init__(self):
        """Initialize the weather API service"""
        self.providers = {
            WeatherProvider.OPENWEATHER: {
                'base_url': 'https://api.openweathermap.org/data/2.5',
                'api_key': None,
                'rate_limit': 1000,  # requests per day
                'timeout': 10
            },
            WeatherProvider.WEATHERAPI: {
                'base_url': 'https://api.weatherapi.com/v1',
                'api_key': None,
                'rate_limit': 1000000,
                'timeout': 10
            }
        }
        
        self.cache = {}
        self.cache_ttl = 900  # 15 minutes default
        self.active_providers = [WeatherProvider.OPENWEATHER]
        self.request_counts = defaultdict(int)
        self.last_request_time = defaultdict(float)
        
        logger.info("WeatherAPIService initialized")

    async def get_current_weather(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get current weather for a location"""
        try:
            # Extract location information
            if location_data.get('location_type') == LocationType.COORDINATES:
                lat = location_data['latitude']
                lon = location_data['longitude']
                location_key = f"current_{lat}_{lon}"
            elif location_data.get('location_type') == LocationType.CITY_NAME:
                city = location_data['city']
                country = location_data.get('country', '')
                location_key = f"current_{city}_{country}"
                # Convert to coordinates for API call
                lat, lon = await self._geocode_city(city, country)
            else:
                raise ValueError("Unsupported location type")
            
            # Check cache first
            if self._is_cache_valid(location_key):
                logger.info(f"Using cached weather data for {location_key}")
                return self.cache[location_key]['data']
            
            # Make API request
            weather_data = await self._fetch_current_weather(lat, lon)
            
            # Format response
            current_weather = {
                'temperature': weather_data.temperature,
                'condition': weather_data.condition.value,
                'humidity': weather_data.humidity,
                'pressure': weather_data.pressure,
                'wind_speed': weather_data.wind_speed,
                'visibility': weather_data.visibility,
                'timestamp': weather_data.timestamp.isoformat(),
                'location_info': weather_data.location_info,
                'provider': weather_data.provider.value,
                'confidence': weather_data.confidence
            }
            
            # Cache the result
            self._cache_data(location_key, current_weather)
            
            logger.info(f"Retrieved current weather for {location_key}")
            return current_weather
            
        except Exception as e:
            logger.error(f"Error getting current weather: {e}")
            return await self._get_fallback_weather(location_data)

    async def get_weather_forecast(self, location_data: Dict[str, Any], 
                                 forecast_params: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather forecast for a location"""
        try:
            lat = location_data.get('latitude', 35.6762)
            lon = location_data.get('longitude', 139.6503)
            
            forecast_type = forecast_params.get('forecast_type', ForecastType.DAILY)
            days = forecast_params.get('days', 7)
            hours = forecast_params.get('hours', 24)
            
            # Generate mock forecast data
            forecast_data = []
            
            if forecast_type == ForecastType.DAILY:
                for i in range(min(days, 7)):
                    future_date = datetime.now() + timedelta(days=i)
                    forecast_data.append({
                        'date': future_date.date().isoformat(),
                        'temperature_high': 25 + (i * 2) % 10,
                        'temperature_low': 15 + (i * 2) % 8,
                        'condition': ['clear', 'cloudy', 'partly_cloudy'][i % 3],
                        'precipitation_chance': min(20 + (i * 10), 80),
                        'humidity': 60 + (i * 5) % 30,
                        'wind_speed': 10 + (i * 2) % 15
                    })
            elif forecast_type == ForecastType.HOURLY:
                for i in range(min(hours, 48)):
                    future_time = datetime.now() + timedelta(hours=i)
                    forecast_data.append({
                        'time': future_time.isoformat(),
                        'temperature': 20 + (i * 0.5) % 15,
                        'condition': ['clear', 'cloudy'][i % 2],
                        'precipitation_chance': (i * 5) % 60,
                        'humidity': 50 + (i * 2) % 40
                    })
            
            return {
                'forecast_data': forecast_data,
                'forecast_type': forecast_type.value,
                'forecast_period': f"{days} days" if forecast_type == ForecastType.DAILY else f"{hours} hours",
                'location_info': {
                    'latitude': lat,
                    'longitude': lon,
                    'name': 'Tokyo'  # Default for demo
                },
                'generated_at': datetime.now().isoformat(),
                'provider': WeatherProvider.OPENWEATHER.value
            }
            
        except Exception as e:
            logger.error(f"Error getting weather forecast: {e}")
            return {
                'forecast_data': [],
                'forecast_type': forecast_type.value,
                'error': str(e)
            }

    async def get_historical_weather(self, location_data: Dict[str, Any], 
                                   time_range: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical weather data"""
        try:
            start_date = time_range.get('start_date')
            end_date = time_range.get('end_date')
            
            # Generate mock historical data
            historical_data = []
            current_date = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date
            end = datetime.fromisoformat(end_date) if isinstance(end_date, str) else end_date
            
            while current_date <= end:
                historical_data.append({
                    'date': current_date.date().isoformat(),
                    'temperature_avg': 20 + (hash(str(current_date.date())) % 20),
                    'temperature_high': 25 + (hash(str(current_date.date())) % 15),
                    'temperature_low': 15 + (hash(str(current_date.date())) % 10),
                    'condition': ['clear', 'cloudy', 'rainy'][hash(str(current_date.date())) % 3],
                    'precipitation': max(0, (hash(str(current_date.date())) % 50) - 30),
                    'humidity': 50 + (hash(str(current_date.date())) % 40)
                })
                current_date += timedelta(days=1)
            
            return {
                'historical_data': historical_data,
                'location_info': location_data,
                'time_range': time_range,
                'data_source': WeatherProvider.OPENWEATHER.value
            }
            
        except Exception as e:
            logger.error(f"Error getting historical weather: {e}")
            return {'historical_data': [], 'error': str(e)}

    async def get_weather_alerts(self, location_data: Dict[str, Any], 
                               alert_params: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather alerts for a location"""
        try:
            severity_filter = alert_params.get('severity_filter', [])
            time_range_hours = alert_params.get('time_range_hours', 24)
            
            # Generate mock alerts (usually there are none)
            active_alerts = []
            
            # Occasionally generate a sample alert for demo purposes
            if hash(str(datetime.now().date())) % 10 == 0:
                sample_alert = WeatherAlert(
                    alert_id=str(uuid.uuid4()),
                    alert_type="thunderstorm",
                    severity=WeatherSeverity.MODERATE,
                    title="Thunderstorm Watch",
                    description="Thunderstorms possible in the afternoon",
                    start_time=datetime.now() + timedelta(hours=2),
                    end_time=datetime.now() + timedelta(hours=8),
                    affected_areas=["Tokyo Metropolitan Area"],
                    instructions="Stay indoors during active storms"
                )
                
                if not severity_filter or sample_alert.severity in severity_filter:
                    active_alerts.append({
                        'alert_id': sample_alert.alert_id,
                        'alert_type': sample_alert.alert_type,
                        'severity': sample_alert.severity.value,
                        'title': sample_alert.title,
                        'description': sample_alert.description,
                        'start_time': sample_alert.start_time.isoformat(),
                        'end_time': sample_alert.end_time.isoformat(),
                        'affected_areas': sample_alert.affected_areas,
                        'instructions': sample_alert.instructions
                    })
            
            return {
                'active_alerts': active_alerts,
                'alert_count': len(active_alerts),
                'severity_summary': {
                    'high_severity': sum(1 for alert in active_alerts if alert.get('severity') == 'high'),
                    'moderate_severity': sum(1 for alert in active_alerts if alert.get('severity') == 'moderate'),
                    'low_severity': sum(1 for alert in active_alerts if alert.get('severity') == 'low')
                },
                'location_info': location_data,
                'query_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting weather alerts: {e}")
            return {'active_alerts': [], 'alert_count': 0, 'error': str(e)}

    async def get_weather_summary(self, location_data: Dict[str, Any], 
                                summary_params: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather summary for a location and time period"""
        try:
            time_period = summary_params.get('time_period', 'current')
            include_trends = summary_params.get('include_trends', True)
            
            current_weather = await self.get_current_weather(location_data)
            
            summary = {
                'current_conditions': {
                    'temperature': current_weather['temperature'],
                    'condition': current_weather['condition'],
                    'description': self._get_weather_description(current_weather)
                },
                'comfort_level': self._calculate_comfort_level(current_weather),
                'activity_recommendations': self._get_activity_recommendations(current_weather),
                'summary_text': self._generate_summary_text(current_weather),
                'location_info': current_weather['location_info'],
                'generated_at': datetime.now().isoformat()
            }
            
            if include_trends:
                forecast = await self.get_weather_forecast(location_data, {'days': 3})
                summary['trends'] = self._analyze_weather_trends(forecast['forecast_data'])
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting weather summary: {e}")
            return {'error': str(e)}

    async def validate_api_connection(self) -> Dict[str, Any]:
        """Validate connection to weather API providers"""
        try:
            validation_results = {
                'connection_status': 'connected',
                'api_providers': {},
                'response_times': {},
                'rate_limits': {}
            }
            
            for provider in self.active_providers:
                start_time = time.time()
                
                # Mock validation (would normally make actual API call)
                await asyncio.sleep(0.1)  # Simulate network latency
                
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                validation_results['api_providers'][provider.value] = {
                    'status': 'active',
                    'version': '2.5',
                    'last_check': datetime.now().isoformat()
                }
                validation_results['response_times'][provider.value] = response_time
                validation_results['rate_limits'][provider.value] = {
                    'limit': self.providers[provider]['rate_limit'],
                    'used': self.request_counts[provider],
                    'reset_time': datetime.now() + timedelta(days=1)
                }
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating API connection: {e}")
            return {
                'connection_status': 'error',
                'error': str(e)
            }

    async def configure_weather_providers(self, provider_config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure weather API providers"""
        try:
            primary_provider = provider_config.get('primary_provider')
            fallback_providers = provider_config.get('fallback_providers', [])
            api_keys = provider_config.get('api_keys', {})
            
            # Update provider configuration
            if primary_provider:
                self.active_providers = [primary_provider] + fallback_providers
            
            # Update API keys
            for provider_name, api_key in api_keys.items():
                for provider in self.providers:
                    if provider.value == provider_name:
                        self.providers[provider]['api_key'] = api_key
            
            # Update timeouts and retry settings
            timeout = provider_config.get('request_timeout_seconds', 10)
            for provider in self.providers:
                self.providers[provider]['timeout'] = timeout
            
            return {
                'configuration_status': 'success',
                'active_providers': [p.value for p in self.active_providers],
                'provider_capabilities': {
                    provider.value: {
                        'current_weather': True,
                        'forecast': True,
                        'historical': True,
                        'alerts': True
                    } for provider in self.active_providers
                },
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error configuring weather providers: {e}")
            return {
                'configuration_status': 'error',
                'error': str(e)
            }

    async def get_location_weather(self, location_query: str) -> Dict[str, Any]:
        """Get weather for a location query (city, coordinates, etc.)"""
        try:
            # Parse location query
            if ',' in location_query and all(part.replace('.', '').replace('-', '').isdigit() 
                                           for part in location_query.split(',')):
                # Coordinates format: "lat,lon"
                lat, lon = map(float, location_query.split(','))
                location_data = {
                    'latitude': lat,
                    'longitude': lon,
                    'location_type': LocationType.COORDINATES
                }
            else:
                # City name
                location_data = {
                    'city': location_query,
                    'location_type': LocationType.CITY_NAME
                }
            
            return await self.get_current_weather(location_data)
            
        except Exception as e:
            logger.error(f"Error getting location weather: {e}")
            return {'error': str(e)}

    async def cache_weather_data(self, location_data: Dict[str, Any], 
                               cache_config: Dict[str, Any]) -> Dict[str, Any]:
        """Cache weather data with specified configuration"""
        try:
            cache_strategy = cache_config.get('cache_strategy', CacheStrategy.BASIC)
            cache_duration = cache_config.get('cache_duration_minutes', 15)
            
            # Get current weather to cache
            weather_data = await self.get_current_weather(location_data)
            
            # Create cache key
            lat = location_data.get('latitude', 0)
            lon = location_data.get('longitude', 0)
            cache_key = f"weather_{lat}_{lon}"
            
            # Cache the data
            cache_entry = {
                'data': weather_data,
                'timestamp': datetime.now(),
                'ttl': cache_duration * 60,  # Convert to seconds
                'strategy': cache_strategy.value
            }
            
            self.cache[cache_key] = cache_entry
            
            return {
                'cache_status': 'cached',
                'cached_data_types': ['current_weather'],
                'cache_expiry': (datetime.now() + timedelta(minutes=cache_duration)).isoformat(),
                'cache_key': cache_key,
                'strategy_used': cache_strategy.value
            }
            
        except Exception as e:
            logger.error(f"Error caching weather data: {e}")
            return {'cache_status': 'error', 'error': str(e)}

    async def get_weather_trends(self, location_data: Dict[str, Any], 
                               trend_params: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather trends and patterns"""
        try:
            time_period = trend_params.get('time_period_days', 30)
            
            # Generate mock trend data
            trends = {
                'temperature_trend': {
                    'direction': 'increasing',
                    'rate_per_day': 0.2,
                    'confidence': 0.75
                },
                'precipitation_trend': {
                    'direction': 'stable',
                    'rate_per_day': 0.0,
                    'confidence': 0.85
                },
                'seasonal_indicators': {
                    'season': 'autumn',
                    'seasonal_progression': 0.6,
                    'typical_for_season': True
                },
                'patterns_detected': [
                    'afternoon_thunderstorms',
                    'morning_fog',
                    'evening_clearing'
                ],
                'location_info': location_data,
                'analysis_period': f"{time_period} days",
                'generated_at': datetime.now().isoformat()
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting weather trends: {e}")
            return {'error': str(e)}

    async def get_seasonal_patterns(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get seasonal weather patterns for a location"""
        try:
            patterns = {
                'spring': {
                    'avg_temperature': 18,
                    'precipitation_days': 12,
                    'dominant_conditions': ['partly_cloudy', 'rainy'],
                    'characteristics': ['mild', 'variable', 'growing_season']
                },
                'summer': {
                    'avg_temperature': 28,
                    'precipitation_days': 8,
                    'dominant_conditions': ['clear', 'hot'],
                    'characteristics': ['hot', 'humid', 'thunderstorms']
                },
                'autumn': {
                    'avg_temperature': 20,
                    'precipitation_days': 10,
                    'dominant_conditions': ['clear', 'cool'],
                    'characteristics': ['crisp', 'colorful', 'comfortable']
                },
                'winter': {
                    'avg_temperature': 8,
                    'precipitation_days': 6,
                    'dominant_conditions': ['clear', 'cold'],
                    'characteristics': ['cold', 'dry', 'clear_skies']
                },
                'location_info': location_data,
                'climate_zone': 'temperate',
                'data_source': 'historical_averages'
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error getting seasonal patterns: {e}")
            return {'error': str(e)}

    async def get_weather_for_ai_context(self, location_data: Dict[str, Any], 
                                       ai_params: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather data optimized for AI context generation"""
        try:
            include_mood = ai_params.get('include_mood_indicators', True)
            include_activities = ai_params.get('include_activity_suitability', True)
            include_atmosphere = ai_params.get('include_visual_atmosphere', True)
            simplify = ai_params.get('simplify_for_prompts', True)
            
            current_weather = await self.get_current_weather(location_data)
            
            ai_weather = {
                'weather_summary': f"{current_weather['condition']} at {current_weather['temperature']}°C",
                'basic_conditions': {
                    'temperature': current_weather['temperature'],
                    'condition': current_weather['condition'],
                    'humidity': current_weather['humidity']
                }
            }
            
            if include_mood:
                ai_weather['mood_indicators'] = self._get_weather_mood_indicators(current_weather)
            
            if include_activities:
                ai_weather['activity_suggestions'] = self._get_activity_suggestions(current_weather)
            
            if include_atmosphere:
                ai_weather['visual_atmosphere'] = self._get_visual_atmosphere(current_weather)
            
            if simplify:
                ai_weather['prompt_friendly_description'] = self._create_prompt_description(current_weather)
            
            return ai_weather
            
        except Exception as e:
            logger.error(f"Error getting weather for AI context: {e}")
            return {'error': str(e)}

    async def monitor_weather_changes(self, location_data: Dict[str, Any], 
                                    monitoring_config: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor weather changes based on configuration"""
        try:
            monitor_params = monitoring_config.get('monitor_parameters', [])
            thresholds = monitoring_config.get('change_thresholds', {})
            
            current_conditions = await self.get_current_weather(location_data)
            
            # For demo purposes, simulate change detection
            change_detection = {
                'changes_detected': False,
                'change_details': [],
                'alert_level': 'none'
            }
            
            # Simulate occasional changes
            if datetime.now().minute % 10 == 0:  # Every 10 minutes for demo
                change_detection = {
                    'changes_detected': True,
                    'change_details': [
                        {
                            'parameter': 'temperature',
                            'old_value': current_conditions['temperature'] - 2,
                            'new_value': current_conditions['temperature'],
                            'change_magnitude': 2.0,
                            'significance': 'minor'
                        }
                    ],
                    'alert_level': 'low'
                }
            
            return {
                'monitoring_status': 'active',
                'current_conditions': current_conditions,
                'change_detection': change_detection,
                'monitoring_config': monitoring_config,
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error monitoring weather changes: {e}")
            return {'monitoring_status': 'error', 'error': str(e)}

    async def get_weather_impact_score(self, location_data: Dict[str, Any], 
                                     impact_params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate weather impact score for activities or mood"""
        try:
            activity_type = impact_params.get('activity_type', 'general')
            user_preferences = impact_params.get('user_preferences', {})
            
            current_weather = await self.get_current_weather(location_data)
            
            # Calculate impact score based on weather conditions
            base_score = 0.5  # Neutral
            condition = current_weather['condition']
            temperature = current_weather['temperature']
            
            # Adjust based on weather condition
            condition_scores = {
                'clear': 0.9,
                'cloudy': 0.7,
                'partly_cloudy': 0.8,
                'rainy': 0.3,
                'stormy': 0.1,
                'foggy': 0.4,
                'snowy': 0.6 if activity_type == 'winter_sports' else 0.3
            }
            
            score = condition_scores.get(condition, 0.5)
            
            # Adjust based on temperature comfort
            if 18 <= temperature <= 25:  # Comfortable range
                temp_modifier = 1.0
            elif 10 <= temperature < 18 or 25 < temperature <= 30:
                temp_modifier = 0.8
            else:
                temp_modifier = 0.5
            
            final_score = score * temp_modifier
            
            # Apply user preferences
            preferred_weather = user_preferences.get('preferred_weather', [])
            avoid_weather = user_preferences.get('avoid_weather', [])
            
            if condition in preferred_weather:
                final_score = min(1.0, final_score * 1.2)
            elif condition in avoid_weather:
                final_score = max(0.0, final_score * 0.5)
            
            reasoning = []
            if condition in ['clear', 'partly_cloudy']:
                reasoning.append("Good weather conditions")
            elif condition in ['rainy', 'stormy']:
                reasoning.append("Adverse weather conditions")
            
            if 18 <= temperature <= 25:
                reasoning.append("Comfortable temperature")
            elif temperature < 10 or temperature > 30:
                reasoning.append("Extreme temperature")
            
            recommendations = []
            if final_score >= 0.7:
                recommendations.append("Great weather for outdoor activities")
            elif final_score >= 0.4:
                recommendations.append("Moderate conditions, some activities suitable")
            else:
                recommendations.append("Consider indoor alternatives")
            
            return {
                'impact_score': round(final_score, 2),
                'reasoning': reasoning,
                'recommendations': recommendations,
                'weather_factors': {
                    'condition': condition,
                    'temperature': temperature,
                    'condition_score': score,
                    'temperature_modifier': temp_modifier
                },
                'activity_type': activity_type,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating weather impact score: {e}")
            return {'impact_score': 0.5, 'error': str(e)}

    async def bulk_weather_request(self, locations: List[Dict[str, Any]], 
                                 bulk_params: Dict[str, Any]) -> Dict[str, Any]:
        """Process multiple weather requests efficiently"""
        try:
            data_types = bulk_params.get('data_types', ['current'])
            max_concurrent = bulk_params.get('max_concurrent', 5)
            optimize_requests = bulk_params.get('optimize_requests', True)
            
            results = []
            success_count = 0
            error_count = 0
            
            # Process requests in batches
            for i in range(0, len(locations), max_concurrent):
                batch = locations[i:i + max_concurrent]
                batch_tasks = []
                
                for location in batch:
                    if 'current' in data_types:
                        task = self.get_current_weather(location)
                        batch_tasks.append(task)
                
                # Execute batch concurrently
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for j, result in enumerate(batch_results):
                    location = batch[j]
                    if isinstance(result, Exception):
                        results.append({
                            'location': location,
                            'success': False,
                            'error': str(result)
                        })
                        error_count += 1
                    else:
                        results.append({
                            'location': location,
                            'success': True,
                            'data': result
                        })
                        success_count += 1
            
            return {
                'results': results,
                'success_count': success_count,
                'error_count': error_count,
                'total_processed': len(locations),
                'processing_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing bulk weather request: {e}")
            return {
                'results': [],
                'success_count': 0,
                'error_count': len(locations),
                'error': str(e)
            }

    async def get_weather_recommendations(self, location_data: Dict[str, Any], 
                                        recommendation_params: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather-based recommendations"""
        try:
            focus_area = recommendation_params.get('focus_area', 'general')
            time_horizon = recommendation_params.get('time_horizon_hours', 24)
            
            current_weather = await self.get_current_weather(location_data)
            forecast = await self.get_weather_forecast(location_data, {'hours': time_horizon})
            
            recommendations = {
                'current_recommendations': self._get_current_recommendations(current_weather),
                'upcoming_recommendations': self._get_forecast_recommendations(forecast),
                'focus_area': focus_area,
                'generated_at': datetime.now().isoformat()
            }
            
            if focus_area == 'photography':
                recommendations['photography_tips'] = self._get_photography_recommendations(current_weather)
            elif focus_area == 'outdoor_activities':
                recommendations['activity_tips'] = self._get_activity_recommendations(current_weather)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting weather recommendations: {e}")
            return {'error': str(e)}

    # Helper methods
    
    async def _fetch_current_weather(self, lat: float, lon: float) -> WeatherData:
        """Fetch current weather from API (mock implementation)"""
        # Mock weather data generation
        await asyncio.sleep(0.1)  # Simulate API delay
        
        conditions = list(WeatherCondition)
        condition = conditions[hash(f"{lat}{lon}{datetime.now().hour}") % len(conditions)]
        
        return WeatherData(
            temperature=20 + (hash(f"{lat}{lon}") % 20),
            condition=condition,
            humidity=50 + (hash(f"{lat}{lon}") % 40),
            pressure=1013 + (hash(f"{lat}{lon}") % 50),
            wind_speed=5 + (hash(f"{lat}{lon}") % 15),
            visibility=10.0,
            timestamp=datetime.now(),
            location_info={
                'latitude': lat,
                'longitude': lon,
                'name': 'Sample Location',
                'country': 'Japan'
            },
            provider=WeatherProvider.OPENWEATHER,
            confidence=0.95
        )

    async def _geocode_city(self, city: str, country: str) -> Tuple[float, float]:
        """Convert city name to coordinates (mock implementation)"""
        # Mock geocoding - return Tokyo coordinates as default
        city_coords = {
            'tokyo': (35.6762, 139.6503),
            'new york': (40.7128, -74.0060),
            'london': (51.5074, -0.1278),
            'paris': (48.8566, 2.3522)
        }
        
        city_key = city.lower()
        return city_coords.get(city_key, (35.6762, 139.6503))

    async def _get_fallback_weather(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback weather data when API fails"""
        return {
            'temperature': 20,
            'condition': 'partly_cloudy',
            'humidity': 60,
            'pressure': 1013,
            'wind_speed': 5,
            'visibility': 10.0,
            'timestamp': datetime.now().isoformat(),
            'location_info': location_data,
            'provider': 'fallback',
            'confidence': 0.3,
            'fallback': True
        }

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_entry = self.cache[cache_key]
        age = (datetime.now() - cache_entry['timestamp']).total_seconds()
        return age < cache_entry['ttl']

    def _cache_data(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Cache weather data"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now(),
            'ttl': self.cache_ttl
        }

    def _get_weather_description(self, weather_data: Dict[str, Any]) -> str:
        """Generate human-readable weather description"""
        condition = weather_data['condition']
        temp = weather_data['temperature']
        
        descriptions = {
            'clear': f"Clear skies with {temp}°C",
            'cloudy': f"Cloudy with {temp}°C",
            'rainy': f"Rainy conditions with {temp}°C",
            'snowy': f"Snow with {temp}°C",
            'stormy': f"Stormy weather with {temp}°C"
        }
        
        return descriptions.get(condition, f"{condition} with {temp}°C")

    def _calculate_comfort_level(self, weather_data: Dict[str, Any]) -> str:
        """Calculate comfort level based on weather conditions"""
        temp = weather_data['temperature']
        condition = weather_data['condition']
        humidity = weather_data['humidity']
        
        if condition in ['stormy', 'heavy_rain']:
            return 'uncomfortable'
        elif 18 <= temp <= 25 and humidity < 70:
            return 'very_comfortable'
        elif 15 <= temp <= 30 and humidity < 80:
            return 'comfortable'
        else:
            return 'moderate'

    def _get_activity_recommendations(self, weather_data: Dict[str, Any]) -> List[str]:
        """Get activity recommendations based on weather"""
        condition = weather_data['condition']
        temp = weather_data['temperature']
        
        recommendations = []
        
        if condition == 'clear' and 20 <= temp <= 25:
            recommendations.extend(['outdoor photography', 'picnic', 'hiking', 'cycling'])
        elif condition == 'cloudy' and temp > 15:
            recommendations.extend(['museum visit', 'city walking', 'shopping'])
        elif condition == 'rainy':
            recommendations.extend(['indoor activities', 'reading', 'cooking', 'movie watching'])
        elif temp < 10:
            recommendations.extend(['warm indoor activities', 'hot drinks', 'cozy atmosphere'])
        
        return recommendations

    def _generate_summary_text(self, weather_data: Dict[str, Any]) -> str:
        """Generate a summary text for weather conditions"""
        condition = weather_data['condition']
        temp = weather_data['temperature']
        humidity = weather_data['humidity']
        
        summary_parts = []
        summary_parts.append(f"Currently {condition} with {temp}°C")
        
        if humidity > 80:
            summary_parts.append("high humidity")
        elif humidity < 30:
            summary_parts.append("low humidity")
        
        if temp > 30:
            summary_parts.append("quite hot")
        elif temp < 5:
            summary_parts.append("very cold")
        
        return ", ".join(summary_parts)

    def _analyze_weather_trends(self, forecast_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in forecast data"""
        if not forecast_data:
            return {'trend': 'no_data'}
        
        temps = [day.get('temperature_high', 20) for day in forecast_data]
        
        if len(temps) >= 2:
            trend = 'increasing' if temps[-1] > temps[0] else 'decreasing' if temps[-1] < temps[0] else 'stable'
        else:
            trend = 'stable'
        
        return {
            'temperature_trend': trend,
            'avg_temperature': sum(temps) / len(temps),
            'temperature_range': {'min': min(temps), 'max': max(temps)}
        }

    def _get_weather_mood_indicators(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get mood indicators based on weather"""
        condition = weather_data['condition']
        temp = weather_data['temperature']
        
        mood_map = {
            'clear': {'energy': 'high', 'mood': 'positive', 'alertness': 'alert'},
            'cloudy': {'energy': 'moderate', 'mood': 'neutral', 'alertness': 'calm'},
            'rainy': {'energy': 'low', 'mood': 'contemplative', 'alertness': 'relaxed'},
            'stormy': {'energy': 'dynamic', 'mood': 'intense', 'alertness': 'heightened'}
        }
        
        return mood_map.get(condition, {'energy': 'moderate', 'mood': 'neutral', 'alertness': 'calm'})

    def _get_activity_suggestions(self, weather_data: Dict[str, Any]) -> List[str]:
        """Get activity suggestions based on current weather"""
        return self._get_activity_recommendations(weather_data)

    def _get_visual_atmosphere(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get visual atmosphere description for AI"""
        condition = weather_data['condition']
        
        atmosphere_map = {
            'clear': {
                'lighting': 'bright',
                'colors': ['blue', 'white', 'golden'],
                'atmosphere': 'crisp',
                'visibility': 'excellent'
            },
            'cloudy': {
                'lighting': 'diffused',
                'colors': ['grey', 'silver', 'muted'],
                'atmosphere': 'soft',
                'visibility': 'good'
            },
            'rainy': {
                'lighting': 'dim',
                'colors': ['grey', 'blue-grey', 'dark'],
                'atmosphere': 'moody',
                'visibility': 'limited'
            }
        }
        
        return atmosphere_map.get(condition, {
            'lighting': 'neutral',
            'colors': ['natural'],
            'atmosphere': 'calm',
            'visibility': 'normal'
        })

    def _create_prompt_description(self, weather_data: Dict[str, Any]) -> str:
        """Create AI prompt-friendly weather description"""
        condition = weather_data['condition']
        temp = weather_data['temperature']
        
        temp_desc = 'warm' if temp > 25 else 'cool' if temp < 15 else 'mild'
        
        return f"{condition} weather, {temp_desc} temperature at {temp}°C"

    def _get_current_recommendations(self, weather_data: Dict[str, Any]) -> List[str]:
        """Get recommendations for current weather"""
        return self._get_activity_recommendations(weather_data)

    def _get_forecast_recommendations(self, forecast_data: Dict[str, Any]) -> List[str]:
        """Get recommendations based on forecast"""
        forecast_list = forecast_data.get('forecast_data', [])
        if not forecast_list:
            return ['Check weather before planning activities']
        
        # Analyze first few hours/days
        upcoming_conditions = [item.get('condition', 'unknown') for item in forecast_list[:3]]
        
        if 'rainy' in upcoming_conditions:
            return ['Plan indoor alternatives', 'Bring umbrella', 'Waterproof gear recommended']
        elif 'clear' in upcoming_conditions:
            return ['Great for outdoor plans', 'Good visibility expected', 'Enjoy outdoor activities']
        else:
            return ['Variable conditions', 'Check forecast regularly', 'Plan flexible activities']

    def _get_photography_recommendations(self, weather_data: Dict[str, Any]) -> List[str]:
        """Get photography-specific recommendations"""
        condition = weather_data['condition']
        
        photo_tips = {
            'clear': ['Golden hour photography', 'Sharp shadows available', 'Blue sky backgrounds'],
            'cloudy': ['Soft, even lighting', 'Good for portraits', 'Dramatic sky potential'],
            'rainy': ['Reflection photography', 'Moody atmosphere', 'Use weather protection'],
            'foggy': ['Atmospheric shots', 'Minimalist compositions', 'Soft, dreamy lighting']
        }
        
        return photo_tips.get(condition, ['Standard photography conditions'])