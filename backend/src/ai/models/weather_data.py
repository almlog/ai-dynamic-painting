"""Weather Data model for contextual AI generation."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum
import json
import uuid

Base = declarative_base()


class WeatherCondition(Enum):
    """Enumeration for weather conditions"""
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    PARTLY_CLOUDY = "partly_cloudy"
    RAINY = "rainy"
    STORMY = "stormy"
    SNOWY = "snowy"
    FOGGY = "foggy"
    WINDY = "windy"


class DataSource(Enum):
    """Enumeration for weather data sources"""
    OPENWEATHERMAP = "openweathermap"
    MANUAL = "manual"
    SENSOR = "sensor"
    FORECAST = "forecast"


class WeatherData:
    """Simple WeatherData class for contract test compatibility"""
    
    def __init__(self, weather_id=None, location=None, timestamp=None, 
                 temperature_celsius=20.0, humidity_percent=50, 
                 weather_condition=None, weather_description=None,
                 wind_speed_kmh=0.0, pressure_hpa=1013.25, visibility_km=10.0,
                 uv_index=0, sunrise_time=None, sunset_time=None,
                 data_source=None, is_current=True):
        
        # Allow default constructor for testing
        if weather_id is None and location is None:
            location = "default_location"
            
        self.weather_id = weather_id or f"weather_{uuid.uuid4().hex[:8]}"
        self.location = location
        self.timestamp = timestamp or datetime.now()
        self.temperature_celsius = temperature_celsius
        self.humidity_percent = max(0, min(100, humidity_percent))  # Clamp to 0-100
        self.weather_condition = weather_condition or WeatherCondition.SUNNY
        self.weather_description = weather_description or "Clear weather"
        self._wind_speed_kmh = max(0.0, wind_speed_kmh)  # Non-negative (private)
        self.pressure_hpa = pressure_hpa
        self.visibility_km = visibility_km
        self._uv_index = max(0, uv_index)  # Non-negative (private)
        self.sunrise_time = sunrise_time
        self.sunset_time = sunset_time
        self.data_source = data_source or DataSource.MANUAL
        self.is_current = is_current
    
    @property
    def wind_speed_kmh(self):
        """Get wind speed"""
        return self._wind_speed_kmh
    
    @wind_speed_kmh.setter
    def wind_speed_kmh(self, value):
        """Set wind speed with validation"""
        self._wind_speed_kmh = max(0.0, value)
    
    @property
    def uv_index(self):
        """Get UV index"""
        return self._uv_index
    
    @uv_index.setter  
    def uv_index(self, value):
        """Set UV index with validation"""
        self._uv_index = max(0, value)
    
    def get_temperature_fahrenheit(self):
        """Convert temperature to Fahrenheit"""
        return (self.temperature_celsius * 9/5) + 32
    
    def calculate_daylight_hours(self):
        """Calculate daylight hours if sunrise/sunset times are available"""
        if not self.sunrise_time or not self.sunset_time:
            return 12.0  # Default assumption
        
        time_diff = self.sunset_time - self.sunrise_time
        return time_diff.total_seconds() / 3600  # Convert to hours
    
    def is_daytime(self, check_time):
        """Check if given time is during daytime"""
        if not self.sunrise_time or not self.sunset_time:
            # Default daytime hours: 6 AM to 6 PM
            hour = check_time.hour
            return 6 <= hour < 18
        
        return self.sunrise_time <= check_time <= self.sunset_time
    
    def is_data_fresh(self, max_age_hours=6):
        """Check if weather data is fresh within given hours"""
        if not self.timestamp:
            return False
        
        age = datetime.now() - self.timestamp
        return age.total_seconds() / 3600 <= max_age_hours
    
    def is_comfortable_temperature(self, min_temp=15, max_temp=30):
        """Check if temperature is in comfortable range"""
        return min_temp <= self.temperature_celsius <= max_temp
    
    def is_good_visibility(self, min_visibility_km=5.0):
        """Check if visibility is good"""
        return self.visibility_km >= min_visibility_km
    
    def is_high_uv(self, uv_threshold=8):
        """Check if UV index is high"""
        return self.uv_index >= uv_threshold
    
    def is_suitable_for_outdoor_activity(self):
        """Determine if weather is suitable for outdoor activities"""
        # Check multiple factors
        comfortable_temp = self.is_comfortable_temperature()
        good_visibility = self.is_good_visibility()
        not_stormy = self.weather_condition not in [WeatherCondition.STORMY, WeatherCondition.RAINY]
        not_too_windy = self.wind_speed_kmh < 25  # Less than 25 km/h
        not_high_uv = not self.is_high_uv()
        
        return all([comfortable_temp, good_visibility, not_stormy, not_too_windy, not_high_uv])
    
    def generate_mood_context(self):
        """Generate mood context based on weather for AI prompts"""
        mood_map = {
            WeatherCondition.SUNNY: "bright and cheerful",
            WeatherCondition.CLOUDY: "calm and contemplative", 
            WeatherCondition.PARTLY_CLOUDY: "dynamic and changeable",
            WeatherCondition.RAINY: "cozy and introspective",
            WeatherCondition.STORMY: "dramatic and intense",
            WeatherCondition.SNOWY: "peaceful and serene",
            WeatherCondition.FOGGY: "mysterious and atmospheric",
            WeatherCondition.WINDY: "energetic and flowing"
        }
        
        base_mood = mood_map.get(self.weather_condition, "neutral")
        
        # Modify based on temperature
        if self.temperature_celsius > 30:
            base_mood = f"warm {base_mood}"
        elif self.temperature_celsius < 5:
            base_mood = f"cool {base_mood}"
        
        return base_mood
    
    def suggest_color_palette(self):
        """Suggest color palette based on weather conditions"""
        color_palettes = {
            WeatherCondition.SUNNY: ["golden yellow", "sky blue", "warm orange", "bright white"],
            WeatherCondition.CLOUDY: ["soft gray", "muted blue", "pearl white", "silver"],
            WeatherCondition.PARTLY_CLOUDY: ["azure blue", "cotton white", "light gray", "sunshine yellow"],
            WeatherCondition.RAINY: ["deep blue", "gray", "sage green", "charcoal"],
            WeatherCondition.STORMY: ["dark gray", "electric blue", "purple", "black"],
            WeatherCondition.SNOWY: ["pure white", "ice blue", "silver", "pale gray"],
            WeatherCondition.FOGGY: ["misty gray", "soft white", "lavender", "pale blue"],
            WeatherCondition.WINDY: ["dynamic blue", "flowing white", "steel gray", "cyan"]
        }
        
        return color_palettes.get(self.weather_condition, ["neutral gray", "soft white"])
    
    def generate_prompt_context(self):
        """Generate comprehensive context for AI prompt generation"""
        # Temperature feel
        if self.temperature_celsius > 30:
            temp_feel = "hot"
        elif self.temperature_celsius > 20:
            temp_feel = "warm"
        elif self.temperature_celsius > 10:
            temp_feel = "mild"
        elif self.temperature_celsius > 0:
            temp_feel = "cool"
        else:
            temp_feel = "cold"
        
        # Lighting condition
        if self.weather_condition == WeatherCondition.SUNNY:
            lighting = "bright natural light"
        elif self.weather_condition == WeatherCondition.CLOUDY:
            lighting = "soft diffused light"
        elif self.weather_condition == WeatherCondition.PARTLY_CLOUDY:
            lighting = "dynamic light and shadow"
        elif self.weather_condition in [WeatherCondition.RAINY, WeatherCondition.STORMY]:
            lighting = "moody overcast light"
        elif self.weather_condition == WeatherCondition.FOGGY:
            lighting = "hazy filtered light"
        else:
            lighting = "natural ambient light"
        
        return {
            'temperature_feel': temp_feel,
            'weather_mood': self.generate_mood_context(),
            'lighting_condition': lighting,
            'weather_condition': self.weather_condition.value,
            'humidity_level': 'humid' if self.humidity_percent > 70 else 'dry' if self.humidity_percent < 30 else 'moderate',
            'wind_condition': 'windy' if self.wind_speed_kmh > 15 else 'calm',
            'visibility': 'clear' if self.visibility_km > 10 else 'limited' if self.visibility_km > 5 else 'poor',
            'color_palette': self.suggest_color_palette(),
            'time_context': 'daytime' if self.is_daytime(datetime.now()) else 'nighttime'
        }
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'weather_id': self.weather_id,
            'location': self.location,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'temperature_celsius': self.temperature_celsius,
            'temperature_fahrenheit': self.get_temperature_fahrenheit(),
            'humidity_percent': self.humidity_percent,
            'weather_condition': self.weather_condition.value if isinstance(self.weather_condition, WeatherCondition) else str(self.weather_condition),
            'weather_description': self.weather_description,
            'wind_speed_kmh': self.wind_speed_kmh,
            'pressure_hpa': self.pressure_hpa,
            'visibility_km': self.visibility_km,
            'uv_index': self.uv_index,
            'sunrise_time': self.sunrise_time.isoformat() if self.sunrise_time else None,
            'sunset_time': self.sunset_time.isoformat() if self.sunset_time else None,
            'data_source': self.data_source.value if isinstance(self.data_source, DataSource) else str(self.data_source),
            'is_current': self.is_current,
            'daylight_hours': self.calculate_daylight_hours(),
            'is_comfortable': self.is_comfortable_temperature(),
            'outdoor_suitable': self.is_suitable_for_outdoor_activity(),
            'prompt_context': self.generate_prompt_context()
        }


class WeatherDataDB(Base):
    """SQLAlchemy model for weather data."""
    
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    weather_id = Column(String, unique=True, nullable=False, index=True)
    location = Column(String, nullable=False, index=True)
    
    # Time information
    timestamp = Column(DateTime, nullable=False, index=True)
    sunrise_time = Column(DateTime, nullable=True)
    sunset_time = Column(DateTime, nullable=True)
    
    # Weather conditions
    temperature_celsius = Column(Float, nullable=False)
    humidity_percent = Column(Integer, nullable=False)
    weather_condition = Column(String, nullable=False)  # sunny, cloudy, rainy, etc.
    weather_description = Column(Text, nullable=True)
    
    # Wind and atmospheric
    wind_speed_kmh = Column(Float, default=0.0)
    pressure_hpa = Column(Float, default=1013.25)
    visibility_km = Column(Float, default=10.0)
    uv_index = Column(Integer, default=0)
    
    # Data source and status
    data_source = Column(String, nullable=False)  # openweathermap, manual, sensor
    is_current = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WeatherDataCreate(BaseModel):
    """Pydantic model for creating weather data."""
    
    location: str = Field(..., min_length=1, description="Location name")
    temperature_celsius: float = Field(..., description="Temperature in Celsius")
    humidity_percent: int = Field(..., ge=0, le=100, description="Humidity percentage")
    weather_condition: str = Field(..., description="Weather condition")
    weather_description: Optional[str] = Field(None, description="Detailed weather description")
    wind_speed_kmh: Optional[float] = Field(0.0, ge=0, description="Wind speed in km/h")
    pressure_hpa: Optional[float] = Field(1013.25, description="Atmospheric pressure in hPa")
    visibility_km: Optional[float] = Field(10.0, ge=0, description="Visibility in kilometers")
    uv_index: Optional[int] = Field(0, ge=0, description="UV index")
    sunrise_time: Optional[datetime] = Field(None, description="Sunrise time")
    sunset_time: Optional[datetime] = Field(None, description="Sunset time")
    data_source: str = Field(..., description="Data source")
    is_current: Optional[bool] = Field(True, description="Is current weather")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WeatherDataUpdate(BaseModel):
    """Pydantic model for updating weather data."""
    
    temperature_celsius: Optional[float] = None
    humidity_percent: Optional[int] = Field(None, ge=0, le=100)
    weather_condition: Optional[str] = None
    weather_description: Optional[str] = None
    wind_speed_kmh: Optional[float] = Field(None, ge=0)
    pressure_hpa: Optional[float] = None
    visibility_km: Optional[float] = Field(None, ge=0)
    uv_index: Optional[int] = Field(None, ge=0)
    sunrise_time: Optional[datetime] = None
    sunset_time: Optional[datetime] = None
    is_current: Optional[bool] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WeatherDataResponse(BaseModel):
    """Pydantic model for weather data responses."""
    
    id: int
    weather_id: str
    location: str
    timestamp: datetime
    temperature_celsius: float
    humidity_percent: int
    weather_condition: str
    weather_description: Optional[str] = None
    wind_speed_kmh: float = 0.0
    pressure_hpa: float = 1013.25
    visibility_km: float = 10.0
    uv_index: int = 0
    sunrise_time: Optional[datetime] = None
    sunset_time: Optional[datetime] = None
    data_source: str
    is_current: bool = False
    created_at: datetime
    updated_at: datetime
    
    # Calculated properties
    temperature_fahrenheit: float = 0.0
    is_comfortable: bool = False
    outdoor_suitable: bool = False
    is_fresh: bool = False
    daylight_hours: float = 12.0
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def from_db(cls, db_weather: WeatherDataDB) -> "WeatherDataResponse":
        """Create response model from database model."""
        
        # Calculate derived values
        temp_fahrenheit = (db_weather.temperature_celsius * 9/5) + 32
        is_comfortable = 15 <= db_weather.temperature_celsius <= 30
        
        # Calculate daylight hours
        daylight_hours = 12.0
        if db_weather.sunrise_time and db_weather.sunset_time:
            time_diff = db_weather.sunset_time - db_weather.sunrise_time
            daylight_hours = time_diff.total_seconds() / 3600
        
        # Check if data is fresh (within 6 hours)
        is_fresh = False
        if db_weather.timestamp:
            age = datetime.utcnow() - db_weather.timestamp
            is_fresh = age.total_seconds() / 3600 <= 6
        
        # Determine outdoor suitability
        outdoor_suitable = (
            is_comfortable and
            db_weather.visibility_km >= 5.0 and
            db_weather.weather_condition not in ['stormy', 'rainy'] and
            db_weather.wind_speed_kmh < 25 and
            db_weather.uv_index < 8
        )
        
        return cls(
            id=db_weather.id,
            weather_id=db_weather.weather_id,
            location=db_weather.location,
            timestamp=db_weather.timestamp,
            temperature_celsius=db_weather.temperature_celsius,
            humidity_percent=db_weather.humidity_percent,
            weather_condition=db_weather.weather_condition,
            weather_description=db_weather.weather_description,
            wind_speed_kmh=db_weather.wind_speed_kmh,
            pressure_hpa=db_weather.pressure_hpa,
            visibility_km=db_weather.visibility_km,
            uv_index=db_weather.uv_index,
            sunrise_time=db_weather.sunrise_time,
            sunset_time=db_weather.sunset_time,
            data_source=db_weather.data_source,
            is_current=db_weather.is_current,
            created_at=db_weather.created_at,
            updated_at=db_weather.updated_at,
            temperature_fahrenheit=temp_fahrenheit,
            is_comfortable=is_comfortable,
            outdoor_suitable=outdoor_suitable,
            is_fresh=is_fresh,
            daylight_hours=daylight_hours
        )


class WeatherDataStats(BaseModel):
    """Statistics for weather data."""
    
    total_records: int = 0
    current_records: int = 0
    unique_locations: int = 0
    
    # Temperature statistics
    average_temperature: float = 0.0
    min_temperature: float = 0.0
    max_temperature: float = 0.0
    
    # Condition distribution
    sunny_count: int = 0
    cloudy_count: int = 0
    rainy_count: int = 0
    stormy_count: int = 0
    snowy_count: int = 0
    other_condition_count: int = 0
    
    # Data source distribution
    api_data_count: int = 0
    manual_data_count: int = 0
    sensor_data_count: int = 0
    forecast_data_count: int = 0
    
    # Data freshness
    fresh_data_count: int = 0  # Within 6 hours
    stale_data_count: int = 0  # Older than 6 hours
    
    class Config:
        json_encoders = {
            float: lambda v: round(v, 2)
        }