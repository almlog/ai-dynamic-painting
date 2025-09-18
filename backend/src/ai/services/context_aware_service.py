"""Context Aware Service for intelligent environment analysis and adaptation."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import asyncio
from statistics import mean, median
import math
import uuid

logger = logging.getLogger("ai_system.context_aware")


class TimeContext(Enum):
    """Enumeration for time-based contexts"""
    DAWN = "dawn"
    MORNING = "morning"
    MIDDAY = "midday"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    DUSK = "dusk"
    NIGHT = "night"
    LATE_NIGHT = "late_night"


class WeatherType(Enum):
    """Enumeration for weather types"""
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    OVERCAST = "overcast"
    RAINY = "rainy"
    STORMY = "stormy"
    SNOWY = "snowy"
    FOGGY = "foggy"
    WINDY = "windy"
    HUMID = "humid"
    DRY = "dry"


class SeasonType(Enum):
    """Enumeration for season types"""
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"
    EARLY_SPRING = "early_spring"
    LATE_SPRING = "late_spring"
    EARLY_SUMMER = "early_summer"
    LATE_SUMMER = "late_summer"
    EARLY_AUTUMN = "early_autumn"
    LATE_AUTUMN = "late_autumn"
    EARLY_WINTER = "early_winter"
    LATE_WINTER = "late_winter"


class SensorType(Enum):
    """Enumeration for sensor types"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    LIGHT = "light"
    MOTION = "motion"
    NOISE = "noise"
    AIR_QUALITY = "air_quality"
    PRESSURE = "pressure"
    PROXIMITY = "proximity"
    VIBRATION = "vibration"


class UserBehaviorPattern(Enum):
    """Enumeration for user behavior patterns"""
    MORNING_ROUTINE = "morning_routine"
    WORK_FOCUSED = "work_focused"
    RELAXATION = "relaxation"
    ENTERTAINMENT = "entertainment"
    SLEEP_PREP = "sleep_prep"
    ACTIVE = "active"
    PASSIVE = "passive"
    ENGAGED = "engaged"
    ABSENT = "absent"
    ROUTINE = "routine"
    IRREGULAR = "irregular"
    FOCUSED = "focused"
    DISTRACTED = "distracted"


class ContextPriority(Enum):
    """Enumeration for context priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"


class RecommendationType(Enum):
    """Enumeration for recommendation types"""
    CONTENT_OPTIMIZATION = "content_optimization"
    TIMING_ADJUSTMENT = "timing_adjustment"
    ENVIRONMENT_CHANGE = "environment_change"
    USER_NOTIFICATION = "user_notification"
    SYSTEM_ADAPTATION = "system_adaptation"
    LEARNING_OPPORTUNITY = "learning_opportunity"


class ContextAwareError(Exception):
    """Custom exception for context-aware service errors"""
    pass


@dataclass
class EnvironmentContext:
    """Current environment context data."""
    temperature: float
    humidity: float
    light_level: int
    motion_detected: bool
    noise_level: float
    time_of_day: str
    season: str
    weather_condition: str
    user_presence: bool = False
    last_interaction: Optional[datetime] = None


@dataclass 
class HistoricalPattern:
    """Historical usage and environment patterns."""
    average_temperature: float
    temperature_trend: str  # increasing, decreasing, stable
    activity_peaks: List[int]  # Hours of high activity
    preferred_conditions: Dict[str, Any]
    usage_frequency: float
    seasonal_preferences: Dict[str, str]


@dataclass
class ContextPrediction:
    """Predicted context for future time periods."""
    predicted_time: datetime
    expected_temperature: float
    expected_humidity: float
    expected_activity_level: str
    recommended_generation_time: bool
    confidence_score: float


class ContextAwareService:
    """Service for intelligent context analysis and prediction."""
    
    def __init__(self, history_days: int = 30):
        self.history_days = history_days
        self.sensor_history: List[EnvironmentContext] = []
        self.pattern_cache: Optional[HistoricalPattern] = None
        self.last_analysis_time: Optional[datetime] = None
        
    def update_sensor_data(self, sensor_data: Dict[str, Any]) -> EnvironmentContext:
        """Update current sensor data and return environment context."""
        
        current_time = datetime.now()
        
        context = EnvironmentContext(
            temperature=float(sensor_data.get("temperature", 20.0)),
            humidity=float(sensor_data.get("humidity", 50.0)),
            light_level=int(sensor_data.get("light_level", 100)),
            motion_detected=bool(sensor_data.get("motion_detected", False)),
            noise_level=float(sensor_data.get("noise_level", 30.0)),
            time_of_day=self._get_time_period(current_time),
            season=self._get_season(current_time),
            weather_condition=self._infer_weather(sensor_data),
            user_presence=bool(sensor_data.get("user_presence", False)),
            last_interaction=current_time if sensor_data.get("user_interaction") else None
        )
        
        # Add to history
        self.sensor_history.append(context)
        
        # Maintain history limit
        cutoff_time = current_time - timedelta(days=self.history_days)
        self.sensor_history = [
            ctx for ctx in self.sensor_history 
            if ctx.last_interaction is None or ctx.last_interaction > cutoff_time
        ]
        
        logger.info(f"Context updated: T={context.temperature}°C, H={context.humidity}%, "
                   f"Motion={context.motion_detected}, Period={context.time_of_day}")
        
        return context
    
    def _get_time_period(self, dt: datetime) -> str:
        """Get time period from datetime."""
        hour = dt.hour
        if 5 <= hour < 7:
            return "dawn"
        elif 7 <= hour < 12:
            return "morning"
        elif hour == 12:
            return "midday"
        elif 13 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 20:
            return "evening"
        elif 20 <= hour < 24:
            return "night"
        else:  # 0-4 hours
            return "late_night"
    
    def _calculate_energy_level(self, hour: int) -> float:
        """Calculate energy level based on time of day (0.0-1.0)"""
        # Energy peaks around 10am and 4pm, lowest at night
        if 9 <= hour <= 11:
            return 0.9  # Morning peak
        elif 15 <= hour <= 17:
            return 0.8  # Afternoon peak
        elif 7 <= hour <= 9 or 12 <= hour <= 15:
            return 0.7  # Good energy
        elif 17 <= hour <= 20:
            return 0.6  # Evening decline
        elif 5 <= hour <= 7 or 20 <= hour <= 22:
            return 0.4  # Low energy
        else:  # Night/late night
            return 0.2  # Lowest energy
    
    def _get_activity_recommendations(self, time_period: str) -> List[str]:
        """Get activity recommendations based on time period"""
        recommendations = {
            "dawn": ["meditation", "light exercise", "planning"],
            "morning": ["focused work", "learning", "important tasks"],
            "midday": ["break", "light meal", "social interaction"],
            "afternoon": ["collaborative work", "meetings", "creative tasks"],
            "evening": ["relaxation", "family time", "entertainment"],
            "night": ["wind down", "reading", "reflection"],
            "late_night": ["sleep preparation", "quiet activities"]
        }
        return recommendations.get(time_period, ["general activities"])
    
    def _get_lighting_context(self, hour: int) -> str:
        """Get lighting context based on hour"""
        if 6 <= hour <= 18:
            return "natural_light"
        elif 18 <= hour <= 22:
            return "evening_light"
        else:
            return "artificial_light"
    
    def _get_season(self, dt: datetime) -> str:
        """Get season from datetime."""
        month = dt.month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"
    
    def _infer_weather(self, sensor_data: Dict[str, Any]) -> str:
        """Infer weather conditions from sensor data."""
        temperature = sensor_data.get("temperature", 20)
        humidity = sensor_data.get("humidity", 50)
        light_level = sensor_data.get("light_level", 100)
        
        if temperature < 0:
            return "snowy"
        elif humidity > 80 and light_level < 50:
            return "rainy"
        elif humidity > 70:
            return "cloudy"
        elif light_level > 150 and humidity < 40:
            return "clear"
        else:
            return "partly_cloudy"
    
    def analyze_historical_patterns(self) -> HistoricalPattern:
        """Analyze historical data to identify patterns."""
        
        if len(self.sensor_history) < 10:
            logger.warning("Insufficient historical data for pattern analysis")
            return self._get_default_pattern()
        
        # Calculate averages and trends
        temperatures = [ctx.temperature for ctx in self.sensor_history[-168:]]  # Last week
        humidities = [ctx.humidity for ctx in self.sensor_history[-168:]]
        
        avg_temp = mean(temperatures)
        temp_trend = self._calculate_trend(temperatures)
        
        # Identify activity peaks
        activity_by_hour = {}
        for ctx in self.sensor_history[-168:]:
            if ctx.last_interaction:
                hour = ctx.last_interaction.hour
                activity_by_hour[hour] = activity_by_hour.get(hour, 0) + 1
        
        activity_peaks = sorted(activity_by_hour.keys(), 
                               key=lambda h: activity_by_hour[h], reverse=True)[:3]
        
        # Determine preferred conditions
        comfortable_contexts = [
            ctx for ctx in self.sensor_history 
            if ctx.user_presence and 18 <= ctx.temperature <= 26 and 40 <= ctx.humidity <= 60
        ]
        
        if comfortable_contexts:
            preferred_temp = mean([ctx.temperature for ctx in comfortable_contexts])
            preferred_humidity = mean([ctx.humidity for ctx in comfortable_contexts])
        else:
            preferred_temp = avg_temp
            preferred_humidity = mean(humidities)
        
        preferred_conditions = {
            "temperature": preferred_temp,
            "humidity": preferred_humidity,
            "light_level": 100,  # Default comfortable level
            "time_periods": self._get_preferred_time_periods()
        }
        
        # Seasonal preferences
        seasonal_prefs = self._analyze_seasonal_preferences()
        
        # Usage frequency
        interactions = len([ctx for ctx in self.sensor_history if ctx.user_presence])
        usage_frequency = interactions / max(len(self.sensor_history), 1)
        
        pattern = HistoricalPattern(
            average_temperature=avg_temp,
            temperature_trend=temp_trend,
            activity_peaks=activity_peaks,
            preferred_conditions=preferred_conditions,
            usage_frequency=usage_frequency,
            seasonal_preferences=seasonal_prefs
        )
        
        self.pattern_cache = pattern
        self.last_analysis_time = datetime.now()
        
        logger.info(f"Historical pattern analyzed: avg_temp={avg_temp:.1f}°C, "
                   f"trend={temp_trend}, peaks={activity_peaks}")
        
        return pattern
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from list of values."""
        if len(values) < 5:
            return "stable"
        
        # Simple linear trend calculation
        n = len(values)
        x_vals = list(range(n))
        
        # Linear regression slope
        x_mean = mean(x_vals)
        y_mean = mean(values)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, values))
        denominator = sum((x - x_mean) ** 2 for x in x_vals)
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _get_preferred_time_periods(self) -> List[str]:
        """Identify preferred time periods for activity."""
        period_activity = {}
        
        for ctx in self.sensor_history:
            if ctx.user_presence:
                period = ctx.time_of_day
                period_activity[period] = period_activity.get(period, 0) + 1
        
        # Sort by activity count
        sorted_periods = sorted(period_activity.items(), 
                               key=lambda x: x[1], reverse=True)
        
        return [period for period, count in sorted_periods[:2]]  # Top 2 periods
    
    def _analyze_seasonal_preferences(self) -> Dict[str, str]:
        """Analyze seasonal weather preferences."""
        seasonal_weather = {}
        
        for ctx in self.sensor_history:
            if ctx.user_presence:
                season = ctx.season
                weather = ctx.weather_condition
                
                if season not in seasonal_weather:
                    seasonal_weather[season] = {}
                
                seasonal_weather[season][weather] = seasonal_weather[season].get(weather, 0) + 1
        
        # Get most preferred weather for each season
        preferences = {}
        for season, weather_counts in seasonal_weather.items():
            if weather_counts:
                preferred = max(weather_counts.items(), key=lambda x: x[1])
                preferences[season] = preferred[0]
        
        return preferences
    
    def _get_default_pattern(self) -> HistoricalPattern:
        """Get default pattern when insufficient data."""
        return HistoricalPattern(
            average_temperature=22.0,
            temperature_trend="stable",
            activity_peaks=[9, 14, 19],  # 9am, 2pm, 7pm
            preferred_conditions={
                "temperature": 22.0,
                "humidity": 50.0,
                "light_level": 100,
                "time_periods": ["morning", "evening"]
            },
            usage_frequency=0.3,
            seasonal_preferences={
                "spring": "clear",
                "summer": "clear", 
                "autumn": "partly_cloudy",
                "winter": "clear"
            }
        )
    
    def predict_future_context(
        self,
        target_time: datetime,
        hours_ahead: int = 1
    ) -> ContextPrediction:
        """Predict context for future time period."""
        
        if not self.pattern_cache:
            self.analyze_historical_patterns()
        
        pattern = self.pattern_cache
        current_time = datetime.now()
        
        # Temperature prediction based on time of day and historical pattern
        target_hour = target_time.hour
        
        # Simple temperature model: daily cycle + trend
        daily_temp_variation = 5 * math.sin((target_hour - 6) * math.pi / 12)  # Peak at 18:00
        base_temp = pattern.average_temperature
        
        # Apply trend if predicting far ahead
        if hours_ahead > 12:
            trend_adjustment = 0.1 * hours_ahead if pattern.temperature_trend == "increasing" else 0
            trend_adjustment = -0.1 * hours_ahead if pattern.temperature_trend == "decreasing" else trend_adjustment
        else:
            trend_adjustment = 0
        
        predicted_temp = base_temp + daily_temp_variation + trend_adjustment
        
        # Humidity prediction (inverse relationship with temperature)
        base_humidity = pattern.preferred_conditions["humidity"]
        humidity_variation = -2 * daily_temp_variation  # Higher temp = lower humidity
        predicted_humidity = base_humidity + humidity_variation
        predicted_humidity = max(20, min(90, predicted_humidity))  # Clamp
        
        # Activity level prediction
        target_period = self._get_time_period(target_time)
        preferred_periods = pattern.preferred_conditions.get("time_periods", [])
        
        if target_hour in pattern.activity_peaks:
            activity_level = "high"
        elif target_period in preferred_periods:
            activity_level = "medium"
        else:
            activity_level = "low"
        
        # Generation recommendation
        recommended = (
            activity_level in ["medium", "high"] and
            18 <= predicted_temp <= 26 and
            target_period in preferred_periods
        )
        
        # Confidence based on data quality
        data_points = len(self.sensor_history)
        confidence = min(0.9, data_points / 168)  # Up to 90% confidence with week of data
        
        prediction = ContextPrediction(
            predicted_time=target_time,
            expected_temperature=predicted_temp,
            expected_humidity=predicted_humidity,
            expected_activity_level=activity_level,
            recommended_generation_time=recommended,
            confidence_score=confidence
        )
        
        logger.info(f"Context prediction for {target_time}: T={predicted_temp:.1f}°C, "
                   f"Activity={activity_level}, Recommended={recommended}")
        
        return prediction
    
    def get_optimal_generation_times(
        self,
        date: datetime,
        count: int = 4
    ) -> List[Tuple[datetime, float]]:
        """Get optimal times for video generation based on context analysis."""
        
        if not self.pattern_cache:
            self.analyze_historical_patterns()
        
        pattern = self.pattern_cache
        optimal_times = []
        
        # Check each hour of the target date
        for hour in range(24):
            target_time = date.replace(hour=hour, minute=0, second=0)
            prediction = self.predict_future_context(target_time)
            
            # Score based on multiple factors
            score = 0.0
            
            # Activity level score
            if prediction.expected_activity_level == "high":
                score += 3.0
            elif prediction.expected_activity_level == "medium":
                score += 2.0
            else:
                score += 0.5
            
            # Time period preference
            time_period = self._get_time_period(target_time)
            preferred_periods = pattern.preferred_conditions.get("time_periods", [])
            if time_period in preferred_periods:
                score += 2.0
            
            # Temperature comfort score
            temp_diff = abs(prediction.expected_temperature - pattern.preferred_conditions["temperature"])
            temp_score = max(0, 2.0 - (temp_diff / 5.0))
            score += temp_score
            
            # Peak hours bonus
            if hour in pattern.activity_peaks:
                score += 1.5
            
            # Confidence factor
            score *= prediction.confidence_score
            
            optimal_times.append((target_time, score))
        
        # Sort by score and return top candidates
        optimal_times.sort(key=lambda x: x[1], reverse=True)
        
        return optimal_times[:count]
    
    def should_generate_now(self, current_context: EnvironmentContext) -> Tuple[bool, str]:
        """Determine if now is a good time for video generation."""
        
        if not self.pattern_cache:
            self.analyze_historical_patterns()
        
        pattern = self.pattern_cache
        
        # Check multiple factors
        factors = []
        score = 0
        
        # User presence
        if current_context.user_presence:
            score += 3
            factors.append("user_present")
        
        # Comfortable temperature
        preferred_temp = pattern.preferred_conditions["temperature"]
        temp_diff = abs(current_context.temperature - preferred_temp)
        if temp_diff < 3:
            score += 2
            factors.append("comfortable_temp")
        
        # Preferred time period
        preferred_periods = pattern.preferred_conditions.get("time_periods", [])
        if current_context.time_of_day in preferred_periods:
            score += 2
            factors.append("preferred_time")
        
        # Activity peak hour
        current_hour = datetime.now().hour
        if current_hour in pattern.activity_peaks:
            score += 1.5
            factors.append("peak_activity")
        
        # Environmental conditions
        if (40 <= current_context.humidity <= 70 and 
            current_context.light_level > 50):
            score += 1
            factors.append("good_conditions")
        
        # Decision threshold
        should_generate = score >= 4.0
        
        reason = f"Score: {score:.1f}, Factors: {', '.join(factors) if factors else 'none'}"
        
        logger.info(f"Generation recommendation: {should_generate}, {reason}")
        
        return should_generate, reason
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get comprehensive context summary for debugging/monitoring."""
        
        current_time = datetime.now()
        recent_contexts = self.sensor_history[-24:] if len(self.sensor_history) >= 24 else self.sensor_history
        
        if not recent_contexts:
            return {"status": "no_data", "message": "No context data available"}
        
        latest_context = recent_contexts[-1]
        
        # Calculate recent trends
        if len(recent_contexts) >= 5:
            recent_temps = [ctx.temperature for ctx in recent_contexts[-5:]]
            recent_humidity = [ctx.humidity for ctx in recent_contexts[-5:]]
            temp_trend = self._calculate_trend(recent_temps)
            avg_humidity = mean(recent_humidity)
        else:
            temp_trend = "unknown"
            avg_humidity = latest_context.humidity
        
        summary = {
            "current_context": {
                "temperature": latest_context.temperature,
                "humidity": latest_context.humidity,
                "time_period": latest_context.time_of_day,
                "season": latest_context.season,
                "weather": latest_context.weather_condition,
                "user_present": latest_context.user_presence
            },
            "trends": {
                "temperature_trend": temp_trend,
                "average_humidity_24h": avg_humidity,
                "data_points": len(self.sensor_history)
            },
            "patterns": self.pattern_cache.__dict__ if self.pattern_cache else None,
            "last_analysis": self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            "next_optimal_times": []
        }
        
        # Add next optimal generation times
        try:
            optimal_times = self.get_optimal_generation_times(current_time + timedelta(hours=1), 3)
            summary["next_optimal_times"] = [
                {
                    "time": time.isoformat(),
                    "score": round(score, 2)
                }
                for time, score in optimal_times
            ]
        except Exception as e:
            logger.error(f"Error calculating optimal times: {e}")
        
        return summary
    
    # Contract test required methods
    async def analyze_time_context(self, timestamp=None):
        """Analyze time-based context factors"""
        if timestamp is None:
            timestamp = datetime.now()
        
        time_period = self._get_time_period(timestamp)
        
        return {
            'time_context': TimeContext(time_period),
            'time_category': TimeContext(time_period),
            'energy_level': self._calculate_energy_level(timestamp.hour),
            'activity_recommendations': self._get_activity_recommendations(time_period),
            'lighting_context': self._get_lighting_context(timestamp.hour),
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'is_weekend': timestamp.weekday() >= 5,
            'circadian_phase': self._get_circadian_phase(timestamp.hour),
            'productivity_score': self._calculate_productivity_score(timestamp)
        }
    
    async def analyze_weekly_pattern(self, timestamp=None):
        """Analyze weekly pattern context"""
        if timestamp is None:
            timestamp = datetime.now()
        
        day_of_week = timestamp.weekday()
        is_weekend = day_of_week >= 5
        
        return {
            'day_of_week': day_of_week,
            'weekend_factor': 1.0 if is_weekend else 0.0,
            'work_day_probability': 0.1 if is_weekend else 0.9,
            'day_name': timestamp.strftime('%A'),
            'is_weekend': is_weekend
        }
    
    async def analyze_monthly_pattern(self, timestamp=None):
        """Analyze monthly pattern context"""
        if timestamp is None:
            timestamp = datetime.now()
        
        month = timestamp.month
        day_of_month = timestamp.day
        days_in_month = 31  # Simplified
        
        return {
            'month_progression': day_of_month / days_in_month,
            'seasonal_transition': self._get_seasonal_transition_factor(month),
            'daylight_duration': self._estimate_daylight_duration(month),
            'month': month,
            'season': self._get_season(timestamp)
        }
    
    def _get_seasonal_transition_factor(self, month: int) -> float:
        """Get seasonal transition factor (0.0-1.0)"""
        # Peak transitions around solstices and equinoxes
        transition_months = {3: 0.8, 6: 0.9, 9: 0.8, 12: 0.9}
        return transition_months.get(month, 0.3)
    
    def _estimate_daylight_duration(self, month: int) -> float:
        """Estimate daylight duration in hours"""
        # Simplified daylight estimation for mid-latitudes
        base_hours = 12.0
        if month in [12, 1, 2]:  # Winter
            return base_hours - 2.5
        elif month in [6, 7, 8]:  # Summer
            return base_hours + 2.5
        else:  # Spring/Fall
            return base_hours
    
    def _calculate_comfort_index(self, temperature: float, humidity: float, wind_speed: float) -> float:
        """Calculate weather comfort index (0.0-1.0)"""
        # Optimal: 20-25°C, 40-60% humidity, <10 km/h wind
        temp_comfort = 1.0 - abs(temperature - 22.5) / 30.0
        humidity_comfort = 1.0 - abs(humidity - 50) / 50.0
        wind_comfort = 1.0 - min(wind_speed / 20.0, 1.0)
        
        return max(0.0, min(1.0, (temp_comfort + humidity_comfort + wind_comfort) / 3.0))
    
    def _calculate_mood_influence(self, weather_type: WeatherType, temperature: float, season) -> Dict[str, Any]:
        """Calculate detailed mood influence"""
        base_moods = {
            WeatherType.SUNNY: {'energy_impact': 0.8, 'emotional_tone': 'uplifting', 'alertness_factor': 0.9},
            WeatherType.CLOUDY: {'energy_impact': 0.6, 'emotional_tone': 'calm', 'alertness_factor': 0.7},
            WeatherType.RAINY: {'energy_impact': 0.4, 'emotional_tone': 'contemplative', 'alertness_factor': 0.6},
            WeatherType.STORMY: {'energy_impact': 0.3, 'emotional_tone': 'dramatic', 'alertness_factor': 0.8},
            WeatherType.SNOWY: {'energy_impact': 0.5, 'emotional_tone': 'peaceful', 'alertness_factor': 0.5},
            WeatherType.FOGGY: {'energy_impact': 0.4, 'emotional_tone': 'mysterious', 'alertness_factor': 0.6},
            WeatherType.WINDY: {'energy_impact': 0.7, 'emotional_tone': 'energetic', 'alertness_factor': 0.8}
        }
        return base_moods.get(weather_type, {'energy_impact': 0.5, 'emotional_tone': 'neutral', 'alertness_factor': 0.6})
    
    def _determine_activity_suitability(self, weather_type: WeatherType, temperature: float, wind_speed: float) -> Dict[str, Any]:
        """Determine activity suitability"""
        outdoor_conditions = {
            WeatherType.SUNNY: 0.9,
            WeatherType.CLOUDY: 0.7,
            WeatherType.RAINY: 0.2,
            WeatherType.STORMY: 0.1,
            WeatherType.SNOWY: 0.4,
            WeatherType.FOGGY: 0.3,
            WeatherType.WINDY: 0.6
        }
        
        outdoor_viability = outdoor_conditions.get(weather_type, 0.5)
        if temperature < 5 or temperature > 35:
            outdoor_viability *= 0.5
        if wind_speed > 15:
            outdoor_viability *= 0.7
        
        indoor_preference = 1.0 - outdoor_viability
        
        # Activity recommendations
        if outdoor_viability > 0.7:
            activities = ['outdoor sports', 'walking', 'gardening', 'picnic']
        elif outdoor_viability > 0.4:
            activities = ['light outdoor activities', 'covered outdoor spaces']
        else:
            activities = ['indoor activities', 'reading', 'crafts', 'cooking']
        
        return {
            'indoor_preference': indoor_preference,
            'outdoor_viability': outdoor_viability,
            'recommended_activities': activities
        }
    
    def _get_visual_characteristics(self, weather_type: WeatherType, visibility: str) -> Dict[str, Any]:
        """Get visual characteristics of weather"""
        characteristics = {
            WeatherType.SUNNY: {'lighting': 'bright', 'contrast': 'high', 'color_saturation': 'vivid'},
            WeatherType.CLOUDY: {'lighting': 'diffused', 'contrast': 'medium', 'color_saturation': 'muted'},
            WeatherType.RAINY: {'lighting': 'dim', 'contrast': 'low', 'color_saturation': 'saturated'},
            WeatherType.STORMY: {'lighting': 'dramatic', 'contrast': 'high', 'color_saturation': 'intense'},
            WeatherType.SNOWY: {'lighting': 'bright_diffused', 'contrast': 'low', 'color_saturation': 'minimal'},
            WeatherType.FOGGY: {'lighting': 'muted', 'contrast': 'very_low', 'color_saturation': 'desaturated'},
            WeatherType.WINDY: {'lighting': 'variable', 'contrast': 'medium', 'color_saturation': 'clear'}
        }
        
        result = characteristics.get(weather_type, {'lighting': 'neutral', 'contrast': 'medium', 'color_saturation': 'normal'})
        result['visibility'] = visibility
        return result
    
    def _calculate_atmospheric_pressure_effect(self, weather_type: WeatherType, humidity: float) -> Dict[str, Any]:
        """Calculate atmospheric pressure effects"""
        pressure_effects = {
            WeatherType.SUNNY: {'pressure_trend': 'stable', 'health_impact': 'positive'},
            WeatherType.CLOUDY: {'pressure_trend': 'slight_drop', 'health_impact': 'neutral'},
            WeatherType.RAINY: {'pressure_trend': 'dropping', 'health_impact': 'mild_negative'},
            WeatherType.STORMY: {'pressure_trend': 'rapid_drop', 'health_impact': 'notable_negative'},
            WeatherType.SNOWY: {'pressure_trend': 'dropping', 'health_impact': 'mild_negative'},
            WeatherType.FOGGY: {'pressure_trend': 'stable_low', 'health_impact': 'mild_negative'},
            WeatherType.WINDY: {'pressure_trend': 'variable', 'health_impact': 'variable'}
        }
        
        result = pressure_effects.get(weather_type, {'pressure_trend': 'stable', 'health_impact': 'neutral'})
        result['humidity_effect'] = 'high' if humidity > 70 else 'normal' if humidity > 40 else 'low'
        return result
    
    async def analyze_weather_context(self, weather_data):
        """Analyze weather-based context factors"""
        if not weather_data:
            return {'weather_type': WeatherType.SUNNY, 'mood_influence': 'neutral'}
        
        condition = weather_data.get('condition', 'sunny')
        
        # Handle both enum and string conditions
        if isinstance(condition, WeatherType):
            weather_type = condition
        else:
            condition_str = condition.lower() if isinstance(condition, str) else 'sunny'
            # Map to weather type
            weather_type = WeatherType.SUNNY
            for wtype in WeatherType:
                if wtype.value in condition_str:
                    weather_type = wtype
                    break
        
        # Calculate mood influence
        mood_mapping = {
            WeatherType.SUNNY: 'positive',
            WeatherType.CLOUDY: 'calm',
            WeatherType.RAINY: 'contemplative',
            WeatherType.STORMY: 'dramatic',
            WeatherType.SNOWY: 'peaceful'
        }
        
        # Extract weather data
        temperature = weather_data.get('temperature', 20)
        humidity = weather_data.get('humidity', 50)
        wind_speed = weather_data.get('wind_speed', 0)
        visibility = weather_data.get('visibility', 'good')
        season = weather_data.get('season', SeasonType.SPRING)
        
        # Calculate comfort index
        comfort_index = self._calculate_comfort_index(temperature, humidity, wind_speed)
        
        # Calculate mood influence
        mood_influence = self._calculate_mood_influence(weather_type, temperature, season)
        
        # Determine activity suitability
        activity_suitability = self._determine_activity_suitability(weather_type, temperature, wind_speed)
        
        # Get visual characteristics
        visual_characteristics = self._get_visual_characteristics(weather_type, visibility)
        
        # Calculate atmospheric pressure effect
        atmospheric_pressure_effect = self._calculate_atmospheric_pressure_effect(weather_type, humidity)
        
        return {
            'weather_type': weather_type,
            'comfort_index': comfort_index,
            'mood_influence': mood_influence,
            'activity_suitability': activity_suitability,
            'visual_characteristics': visual_characteristics,
            'atmospheric_pressure_effect': atmospheric_pressure_effect,
            'temperature': temperature,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'visibility': visibility,
            'season': season
        }
    
    async def process_sensor_data(self, sensor_readings):
        """Process environmental sensor data"""
        processed_data = {}
        
        for sensor_type, value in sensor_readings.items():
            try:
                sensor_enum = SensorType(sensor_type.lower())
                processed_data[sensor_enum.value] = {
                    'value': value,
                    'normalized': self._normalize_sensor_value(sensor_type, value),
                    'status': self._evaluate_sensor_status(sensor_type, value),
                    'timestamp': datetime.now().isoformat()
                }
            except ValueError:
                logger.warning(f"Unknown sensor type: {sensor_type}")
        
        return processed_data
    
    async def recognize_user_patterns(self, user_id=None):
        """Recognize user behavior patterns"""
        if not self.sensor_history:
            return {'pattern': UserBehaviorPattern.IRREGULAR, 'confidence': 0.0}
        
        recent_activity = self.sensor_history[-168:]  # Last week
        
        # Analyze activity patterns
        activity_hours = [ctx.last_interaction.hour for ctx in recent_activity 
                         if ctx.last_interaction and ctx.user_presence]
        
        if len(activity_hours) < 5:
            pattern = UserBehaviorPattern.IRREGULAR
            confidence = 0.3
        else:
            # Check for routine patterns
            common_hours = set(activity_hours)
            if len(common_hours) <= 4:  # Very consistent times
                pattern = UserBehaviorPattern.ROUTINE
                confidence = 0.9
            elif any(activity_hours.count(h) >= 3 for h in common_hours):
                pattern = UserBehaviorPattern.ENGAGED
                confidence = 0.7
            else:
                pattern = UserBehaviorPattern.ACTIVE
                confidence = 0.6
        
        return {
            'pattern': pattern,
            'confidence': confidence,
            'activity_hours': list(set(activity_hours)),
            'total_interactions': len(activity_hours)
        }
    
    async def predict_context_changes(self, horizon_hours=24):
        """Predict context changes over time horizon"""
        predictions = []
        current_time = datetime.now()
        
        for hour in range(1, horizon_hours + 1):
            future_time = current_time + timedelta(hours=hour)
            prediction = self.predict_future_context(future_time)
            
            predictions.append({
                'timestamp': future_time.isoformat(),
                'temperature': prediction.expected_temperature,
                'humidity': prediction.expected_humidity,
                'activity_level': prediction.expected_activity_level,
                'confidence': prediction.confidence_score,
                'recommended_generation': prediction.recommended_generation_time
            })
        
        return predictions
    
    async def generate_recommendations(self, context_data, priority=ContextPriority.MEDIUM):
        """Generate context-aware recommendations"""
        recommendations = []
        
        current_context = self.update_sensor_data(context_data)
        should_generate, reason = self.should_generate_now(current_context)
        
        if should_generate:
            recommendations.append({
                'type': RecommendationType.CONTENT_OPTIMIZATION,
                'priority': priority,
                'action': 'generate_content_now',
                'reason': reason,
                'confidence': 0.8
            })
        else:
            # Find next optimal time
            optimal_times = self.get_optimal_generation_times(datetime.now(), 1)
            if optimal_times:
                next_time, score = optimal_times[0]
                recommendations.append({
                    'type': RecommendationType.TIMING_ADJUSTMENT,
                    'priority': priority,
                    'action': f'schedule_for_{next_time.hour}h',
                    'reason': f'Optimal time with score {score:.1f}',
                    'confidence': score / 10.0
                })
        
        return recommendations
    
    async def track_context_history(self, duration_days=30):
        """Track and analyze context history"""
        cutoff_time = datetime.now() - timedelta(days=duration_days)
        relevant_history = [
            ctx for ctx in self.sensor_history
            if ctx.last_interaction and ctx.last_interaction > cutoff_time
        ]
        
        if not relevant_history:
            return {'status': 'insufficient_data', 'days_tracked': 0}
        
        return {
            'status': 'active',
            'days_tracked': duration_days,
            'total_entries': len(relevant_history),
            'average_temperature': mean([ctx.temperature for ctx in relevant_history]),
            'average_humidity': mean([ctx.humidity for ctx in relevant_history]),
            'activity_pattern': await self.recognize_user_patterns(),
            'most_active_hours': self._find_peak_hours(relevant_history)
        }
    
    async def fuse_multi_context(self, context_sources):
        """Fuse multiple context sources into unified analysis"""
        fused_context = {
            'timestamp': datetime.now().isoformat(),
            'sources': list(context_sources.keys()),
            'confidence': 1.0,
            'context_factors': {}
        }
        
        # Weight different context sources
        weights = {
            'time': 0.3,
            'weather': 0.2,
            'sensors': 0.3,
            'user_behavior': 0.2
        }
        
        total_weight = 0
        weighted_confidence = 0
        
        for source, data in context_sources.items():
            if source in weights:
                weight = weights[source]
                source_confidence = data.get('confidence', 0.5)
                weighted_confidence += weight * source_confidence
                total_weight += weight
                
                fused_context['context_factors'][source] = {
                    'data': data,
                    'weight': weight,
                    'confidence': source_confidence
                }
        
        if total_weight > 0:
            fused_context['confidence'] = weighted_confidence / total_weight
        
        return fused_context
    
    async def optimize_context_weights(self, feedback_data):
        """Optimize context fusion weights based on feedback"""
        # Simple optimization based on feedback success rate
        current_weights = {
            'time': 0.3,
            'weather': 0.2,
            'sensors': 0.3,
            'user_behavior': 0.2
        }
        
        success_rate = feedback_data.get('success_rate', 0.5)
        
        if success_rate > 0.8:
            # Current weights are working well
            return current_weights
        elif success_rate < 0.4:
            # Adjust weights to emphasize user behavior
            return {
                'time': 0.2,
                'weather': 0.15,
                'sensors': 0.25,
                'user_behavior': 0.4
            }
        else:
            # Moderate adjustment
            return {
                'time': 0.25,
                'weather': 0.2,
                'sensors': 0.35,
                'user_behavior': 0.3
            }
    
    async def analyze_seasonal_patterns(self, year_data=None):
        """Analyze seasonal behavior patterns"""
        if not year_data:
            # Use available history
            seasonal_data = {}
            for ctx in self.sensor_history:
                season = ctx.season
                if season not in seasonal_data:
                    seasonal_data[season] = []
                seasonal_data[season].append({
                    'temperature': ctx.temperature,
                    'humidity': ctx.humidity,
                    'user_presence': ctx.user_presence
                })
        else:
            seasonal_data = year_data
        
        patterns = {}
        for season, data in seasonal_data.items():
            if data:
                patterns[season] = {
                    'average_temperature': mean([d['temperature'] for d in data]),
                    'average_humidity': mean([d['humidity'] for d in data]),
                    'activity_level': sum([d['user_presence'] for d in data]) / len(data),
                    'data_points': len(data)
                }
        
        return patterns
    
    async def detect_context_anomalies(self, threshold=2.0):
        """Detect anomalies in context patterns"""
        if len(self.sensor_history) < 10:
            return {'anomalies': [], 'status': 'insufficient_data'}
        
        recent = self.sensor_history[-50:]  # Last 50 readings
        anomalies = []
        
        # Calculate baselines
        temp_mean = mean([ctx.temperature for ctx in recent])
        temp_std = self._calculate_std([ctx.temperature for ctx in recent])
        
        humidity_mean = mean([ctx.humidity for ctx in recent])
        humidity_std = self._calculate_std([ctx.humidity for ctx in recent])
        
        # Check for anomalies
        for i, ctx in enumerate(recent[-10:], len(recent)-10):
            temp_z = abs(ctx.temperature - temp_mean) / max(temp_std, 1.0)
            humidity_z = abs(ctx.humidity - humidity_mean) / max(humidity_std, 1.0)
            
            if temp_z > threshold:
                anomalies.append({
                    'type': 'temperature',
                    'value': ctx.temperature,
                    'expected': temp_mean,
                    'severity': temp_z,
                    'timestamp': ctx.last_interaction.isoformat() if ctx.last_interaction else None
                })
            
            if humidity_z > threshold:
                anomalies.append({
                    'type': 'humidity',
                    'value': ctx.humidity,
                    'expected': humidity_mean,
                    'severity': humidity_z,
                    'timestamp': ctx.last_interaction.isoformat() if ctx.last_interaction else None
                })
        
        return {
            'anomalies': anomalies,
            'threshold': threshold,
            'status': 'analyzed'
        }
    
    async def adapt_to_user_behavior(self, behavior_data):
        """Adapt system based on user behavior analysis"""
        behavior_pattern = behavior_data.get('pattern', UserBehaviorPattern.IRREGULAR)
        
        adaptations = {
            'generation_frequency': 'normal',
            'content_complexity': 'medium',
            'notification_timing': 'standard',
            'learning_rate': 0.1
        }
        
        if behavior_pattern == UserBehaviorPattern.ROUTINE:
            adaptations.update({
                'generation_frequency': 'predictable',
                'notification_timing': 'scheduled',
                'learning_rate': 0.05
            })
        elif behavior_pattern == UserBehaviorPattern.ACTIVE:
            adaptations.update({
                'generation_frequency': 'high',
                'content_complexity': 'high',
                'learning_rate': 0.15
            })
        elif behavior_pattern == UserBehaviorPattern.PASSIVE:
            adaptations.update({
                'generation_frequency': 'low',
                'content_complexity': 'simple',
                'learning_rate': 0.08
            })
        
        return adaptations
    
    async def get_context_analytics(self):
        """Get comprehensive context analytics"""
        if not self.sensor_history:
            return {'status': 'no_data'}
        
        recent_week = self.sensor_history[-168:] if len(self.sensor_history) >= 168 else self.sensor_history
        
        analytics = {
            'data_coverage': {
                'total_readings': len(self.sensor_history),
                'recent_week_readings': len(recent_week),
                'coverage_percentage': min(100, len(recent_week) / 168 * 100)
            },
            'environmental_stats': {
                'temperature_range': [
                    min([ctx.temperature for ctx in recent_week]),
                    max([ctx.temperature for ctx in recent_week])
                ],
                'humidity_range': [
                    min([ctx.humidity for ctx in recent_week]),
                    max([ctx.humidity for ctx in recent_week])
                ],
                'most_common_weather': self._most_common([ctx.weather_condition for ctx in recent_week])
            },
            'user_activity': {
                'total_interactions': sum([1 for ctx in recent_week if ctx.user_presence]),
                'activity_by_hour': self._activity_by_hour(recent_week),
                'most_active_day': self._most_active_day(recent_week)
            },
            'patterns': await self.recognize_user_patterns(),
            'anomalies': await self.detect_context_anomalies()
        }
        
        return analytics
    
    async def update_context_model(self, learning_data):
        """Update context model with new learning data"""
        if not learning_data:
            return {'status': 'no_update', 'reason': 'insufficient_data'}
        
        # Update pattern cache with new insights
        if self.pattern_cache:
            # Adjust preferred conditions based on successful interactions
            success_rate = learning_data.get('success_rate', 0.5)
            
            if success_rate > 0.8:
                # Reinforce current preferences
                current_temp = learning_data.get('temperature')
                if current_temp:
                    self.pattern_cache.preferred_conditions['temperature'] = (
                        self.pattern_cache.preferred_conditions['temperature'] * 0.9 + 
                        current_temp * 0.1
                    )
            
            # Update activity peaks
            successful_hours = learning_data.get('successful_hours', [])
            for hour in successful_hours:
                if hour not in self.pattern_cache.activity_peaks:
                    self.pattern_cache.activity_peaks.append(hour)
        
        return {
            'status': 'updated',
            'learning_rate': learning_data.get('learning_rate', 0.1),
            'improvements': learning_data.get('improvements', [])
        }
    
    async def get_predictive_insights(self, timeframe='week'):
        """Get predictive insights for future context"""
        insights = {
            'timeframe': timeframe,
            'predictions': [],
            'recommendations': [],
            'confidence': 0.0
        }
        
        if timeframe == 'week':
            hours_ahead = 168
        elif timeframe == 'day':
            hours_ahead = 24
        else:
            hours_ahead = 72  # 3 days default
        
        # Generate hourly predictions
        predictions = await self.predict_context_changes(min(hours_ahead, 72))
        insights['predictions'] = predictions
        
        # Generate recommendations based on predictions
        high_score_times = [p for p in predictions if p.get('confidence', 0) > 0.7]
        
        if high_score_times:
            insights['recommendations'] = [
                {
                    'type': 'optimal_timing',
                    'message': f"Best generation time: {high_score_times[0]['timestamp']}",
                    'confidence': high_score_times[0]['confidence']
                }
            ]
            insights['confidence'] = mean([p['confidence'] for p in high_score_times])
        
        return insights
    
    async def calibrate_sensor_readings(self, calibration_data):
        """Calibrate sensor readings for accuracy"""
        calibration_results = {}
        
        for sensor_type, calibration_values in calibration_data.items():
            reference_value = calibration_values.get('reference')
            measured_value = calibration_values.get('measured')
            
            if reference_value and measured_value:
                offset = reference_value - measured_value
                calibration_results[sensor_type] = {
                    'offset': offset,
                    'accuracy': 1.0 - abs(offset) / max(reference_value, 1.0),
                    'status': 'calibrated'
                }
            else:
                calibration_results[sensor_type] = {
                    'status': 'insufficient_data'
                }
        
        return calibration_results
    
    async def learn_from_feedback(self, feedback_data):
        """Learn from user feedback to improve context understanding"""
        feedback_type = feedback_data.get('type', 'general')
        rating = feedback_data.get('rating', 3)  # 1-5 scale
        context_id = feedback_data.get('context_id')
        
        learning_update = {
            'feedback_type': feedback_type,
            'rating': rating,
            'timestamp': datetime.now().isoformat(),
            'improvements': []
        }
        
        if rating >= 4:  # Positive feedback
            learning_update['improvements'].append('reinforce_current_patterns')
            if context_id:
                learning_update['improvements'].append(f'boost_context_{context_id}')
        elif rating <= 2:  # Negative feedback
            learning_update['improvements'].append('adjust_prediction_weights')
            learning_update['improvements'].append('explore_alternative_patterns')
        
        # Update model with feedback
        await self.update_context_model(learning_update)
        
        return learning_update
    
    async def export_context_data(self, format_type='json'):
        """Export context data for analysis or backup"""
        if format_type == 'json':
            export_data = {
                'metadata': {
                    'export_timestamp': datetime.now().isoformat(),
                    'total_records': len(self.sensor_history),
                    'history_days': self.history_days
                },
                'sensor_history': [
                    {
                        'temperature': ctx.temperature,
                        'humidity': ctx.humidity,
                        'light_level': ctx.light_level,
                        'motion_detected': ctx.motion_detected,
                        'noise_level': ctx.noise_level,
                        'time_of_day': ctx.time_of_day,
                        'season': ctx.season,
                        'weather_condition': ctx.weather_condition,
                        'user_presence': ctx.user_presence,
                        'timestamp': ctx.last_interaction.isoformat() if ctx.last_interaction else None
                    }
                    for ctx in self.sensor_history
                ],
                'patterns': self.pattern_cache.__dict__ if self.pattern_cache else None
            }
            return export_data
        else:
            return {'error': f'Unsupported format: {format_type}'}
    
    # Helper methods for new functionality
    def _get_circadian_phase(self, hour):
        """Get circadian rhythm phase for given hour"""
        if 6 <= hour < 10:
            return 'morning_rise'
        elif 10 <= hour < 14:
            return 'midday_peak'
        elif 14 <= hour < 18:
            return 'afternoon_active'
        elif 18 <= hour < 22:
            return 'evening_wind_down'
        elif 22 <= hour or hour < 2:
            return 'night_rest'
        else:
            return 'deep_sleep'
    
    def _calculate_productivity_score(self, timestamp):
        """Calculate productivity score based on time"""
        hour = timestamp.hour
        # Typical productivity curve
        if 9 <= hour <= 11:
            return 0.9  # Morning peak
        elif 14 <= hour <= 16:
            return 0.8  # Afternoon peak
        elif 19 <= hour <= 21:
            return 0.6  # Evening moderate
        else:
            return 0.3  # Low productivity times
    
    def _calculate_weather_comfort(self, weather_data):
        """Calculate comfort level based on weather"""
        temp = weather_data.get('temperature', 20)
        humidity = weather_data.get('humidity', 50)
        
        # Comfort index based on temperature and humidity
        if 18 <= temp <= 24 and 40 <= humidity <= 60:
            return 'excellent'
        elif 15 <= temp <= 27 and 30 <= humidity <= 70:
            return 'good'
        elif 10 <= temp <= 30 and 20 <= humidity <= 80:
            return 'acceptable'
        else:
            return 'poor'
    
    def _normalize_sensor_value(self, sensor_type, value):
        """Normalize sensor value to 0-1 range"""
        ranges = {
            'temperature': (-10, 50),
            'humidity': (0, 100),
            'light': (0, 1000),
            'noise': (0, 120),
            'pressure': (950, 1050)
        }
        
        if sensor_type in ranges:
            min_val, max_val = ranges[sensor_type]
            return max(0, min(1, (value - min_val) / (max_val - min_val)))
        return 0.5  # Default normalized value
    
    def _evaluate_sensor_status(self, sensor_type, value):
        """Evaluate sensor status as good/warning/critical"""
        # Define acceptable ranges
        if sensor_type == 'temperature':
            if 18 <= value <= 26:
                return 'good'
            elif 10 <= value <= 35:
                return 'warning'
            else:
                return 'critical'
        elif sensor_type == 'humidity':
            if 40 <= value <= 60:
                return 'good'
            elif 20 <= value <= 80:
                return 'warning'
            else:
                return 'critical'
        else:
            return 'good'  # Default status
    
    def _find_peak_hours(self, history):
        """Find most active hours from history"""
        hour_counts = {}
        for ctx in history:
            if ctx.user_presence and ctx.last_interaction:
                hour = ctx.last_interaction.hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        return sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    def _most_common(self, items):
        """Find most common item in list"""
        if not items:
            return None
        return max(set(items), key=items.count)
    
    def _activity_by_hour(self, history):
        """Calculate activity distribution by hour"""
        hour_activity = {hour: 0 for hour in range(24)}
        for ctx in history:
            if ctx.user_presence and ctx.last_interaction:
                hour_activity[ctx.last_interaction.hour] += 1
        return hour_activity
    
    def _most_active_day(self, history):
        """Find most active day of week"""
        day_counts = {day: 0 for day in range(7)}
        for ctx in history:
            if ctx.user_presence and ctx.last_interaction:
                day_counts[ctx.last_interaction.weekday()] += 1
        
        most_active = max(day_counts.items(), key=lambda x: x[1])
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[most_active[0]]
    
    def _calculate_std(self, values):
        """Calculate standard deviation"""
        if len(values) < 2:
            return 1.0
        mean_val = mean(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        return math.sqrt(variance)