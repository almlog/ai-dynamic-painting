# Phase 2 Technical Research - AI Integration Technologies

**Phase**: 002-phase-2-ai  
**Created**: 2025-09-14  
**Research Focus**: VEO API統合、プロンプト最適化、学習システム技術選定  

---

## 🔍 VEO API Integration Research

### Google VEO API Overview
**Technology**: Google Vertex AI Video Generation API (Veo)  
**Capabilities**: Text-to-video generation, style control, duration control  
**Pricing Model**: Per-generation pricing + compute time billing  

#### API Key Features
- **Generation Models**: Veo 1, Veo 2 (different quality/speed trade-offs)
- **Video Specifications**: 720p-4K resolution, 5-60 seconds duration
- **Style Controls**: Cinematic, artistic, realistic, animated styles
- **Prompt Engineering**: Detailed scene descriptions, camera movement, lighting
- **Safety Features**: Content filtering, inappropriate content detection

#### Integration Architecture
```python
# Recommended VEO Client Pattern
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict

class VEOClient:
    def __init__(self, project_id: str, location: str, api_key: str):
        self.client = aiplatform.gapic.PredictionServiceClient()
        self.endpoint = f"projects/{project_id}/locations/{location}/endpoints/veo"
    
    async def generate_video(self, prompt: str, style: str = "cinematic", 
                           duration: int = 10) -> VideoGenerationResult:
        # Implementation with retry logic, error handling, cost tracking
        pass
```

### Cost Management Strategy  
**Cost Factors**: Generation requests, compute time, storage  
**Budget Planning**: ~$50-200/month for daily generation (estimated)  
**Optimization Techniques**:
- Prompt caching for similar contexts
- Generation batching for similar timeframes
- Quality vs cost trade-off configuration
- Failed generation retry limits

---

## 🌤️ Weather API Integration Research

### OpenWeatherMap API Selection
**Rationale**: Free tier available, comprehensive data, reliable uptime  
**Data Coverage**: Current weather, 5-day forecast, historical data  
**Update Frequency**: Real-time updates, 10-minute data refresh  

#### Integration Pattern
```python
import aiohttp
from dataclasses import dataclass
from typing import Optional

@dataclass
class WeatherContext:
    condition: str  # sunny, cloudy, rainy, snowy
    temperature: float
    season: str  # spring, summer, autumn, winter
    time_of_day: str  # morning, afternoon, evening, night
    
class WeatherService:
    BASE_URL = "http://api.openweathermap.org/data/2.5"
    
    async def get_current_weather(self, lat: float, lon: float) -> WeatherContext:
        # API call with caching, error handling, rate limiting
        pass
        
    def extract_prompt_context(self, weather: WeatherContext) -> dict:
        """Convert weather data to prompt generation context"""
        return {
            "lighting": self._weather_to_lighting(weather.condition),
            "mood": self._weather_to_mood(weather.condition),
            "colors": self._season_to_colors(weather.season),
            "atmosphere": self._time_to_atmosphere(weather.time_of_day)
        }
```

### Alternative Weather Services
- **AccuWeather**: More detailed forecast, higher accuracy
- **Weather.gov (NOAA)**: Free US government data, very reliable
- **Visual Crossing**: Historical weather data, good for ML training

---

## 🧠 Prompt Generation Engine Research

### Dynamic Prompt Engineering Techniques
**Base Strategy**: Template-based generation with context injection  
**Advanced Techniques**: Few-shot learning, prompt chaining, context weighting  

#### Prompt Template Architecture
```python
from jinja2 import Template
from enum import Enum

class PromptTheme(Enum):
    NATURE = "nature"
    URBAN = "urban" 
    ABSTRACT = "abstract"
    SEASONAL = "seasonal"

class PromptGenerator:
    TEMPLATES = {
        PromptTheme.NATURE: Template("""
        Create a beautiful {{season}} {{weather_condition}} scene in nature.
        {{time_of_day}} lighting with {{mood}} atmosphere.
        Style: {{style_preference}}. Camera: {{camera_movement}}.
        Colors: {{color_palette}}. Duration: {{duration}} seconds.
        """),
        # More templates...
    }
    
    def generate_prompt(self, context: WeatherContext, 
                       user_prefs: UserPreferences) -> str:
        template = self._select_template(context, user_prefs)
        return template.render(**self._build_context_vars(context, user_prefs))
```

### Prompt Optimization Research
**Quality Factors**: Relevance, creativity, visual appeal, generation success rate  
**Optimization Methods**:
- A/B testing different prompt structures
- User feedback integration (Good/Bad ratings)
- Generation success rate tracking
- Cost per generation optimization

#### Context-Aware Prompt Enhancement
```python
CONTEXT_MODIFIERS = {
    "morning": {
        "lighting": "golden hour, soft morning light",
        "mood": "peaceful, awakening, fresh", 
        "colors": "warm yellows, soft oranges, pale blues"
    },
    "rainy": {
        "lighting": "diffused, moody, dramatic shadows",
        "mood": "contemplative, cozy, introspective",
        "colors": "cool grays, deep blues, muted greens"
    },
    # More context modifiers...
}
```

---

## 📚 User Learning System Research

### Machine Learning Approach Selection
**Chosen Method**: Simple collaborative filtering + weighted preference scoring  
**Rationale**: Interpretable, fast, works with limited data, privacy-friendly  
**Alternative Methods**: Neural networks, matrix factorization, deep learning  

#### Learning Algorithm Architecture
```python
import numpy as np
from sklearn.preprocessing import StandardScaler
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class UserRating:
    video_id: str
    theme: str
    weather_context: str
    time_context: str
    rating: float  # -1 (bad), 0 (skip), 1 (good)
    timestamp: datetime

class PreferenceLearningEngine:
    def __init__(self):
        self.theme_weights = {}
        self.context_weights = {}
        self.scaler = StandardScaler()
    
    def update_preferences(self, ratings: List[UserRating]) -> None:
        """Update preference model with new rating data"""
        # Weighted moving average for theme preferences
        # Context-aware preference adjustment
        # Temporal decay for old preferences
        pass
        
    def predict_preference_score(self, context: GenerationContext) -> float:
        """Predict user preference for given generation context"""
        theme_score = self.theme_weights.get(context.theme, 0.5)
        context_score = self._calculate_context_score(context)
        return np.clip(theme_score * 0.7 + context_score * 0.3, 0, 1)
```

### Learning Data Management
**Storage**: SQLite local storage (privacy-first approach)  
**Data Retention**: 6-month rolling window, aggregated older data  
**Privacy Protection**: No external data transmission, local-only processing  

#### Cold Start Problem Solutions
```python
DEFAULT_PREFERENCES = {
    "nature": 0.8,  # Most people like nature content
    "abstract": 0.3,  # More niche preference
    "urban": 0.5,   # Neutral starting point
    "seasonal": 0.7  # Generally appreciated
}

TIME_PREFERENCES = {
    "morning": {"nature": +0.2, "peaceful": +0.3},
    "evening": {"cozy": +0.2, "warm_colors": +0.1},
    # Context-specific adjustments
}
```

---

## ⚡ Background Processing & Scheduling Research

### Task Queue System Selection
**Chosen**: APScheduler (Advanced Python Scheduler)  
**Rationale**: Pure Python, no additional infrastructure, SQLite job store  
**Alternative**: Celery (more complex, requires Redis/RabbitMQ)  

#### Scheduling Architecture
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

class AIGenerationScheduler:
    def __init__(self, database_url: str):
        jobstores = {'default': SQLAlchemyJobStore(url=database_url)}
        executors = {'default': AsyncIOExecutor()}
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores, 
            executors=executors
        )
    
    def schedule_daily_generation(self, time: str = "06:00"):
        """Schedule daily AI video generation"""
        self.scheduler.add_job(
            self._generate_daily_content,
            trigger='cron',
            hour=6, minute=0,
            id='daily_generation',
            replace_existing=True
        )
    
    async def _generate_daily_content(self):
        # Weather check -> Prompt generation -> VEO API call -> Storage
        pass
```

### Priority-Based Generation Queue
```python
from enum import IntEnum
from heapq import heappush, heappop

class GenerationPriority(IntEnum):
    LOW = 3      # Bulk generation, off-peak
    NORMAL = 2   # Scheduled daily generation
    HIGH = 1     # User-requested, weather-triggered
    URGENT = 0   # Manual override, system recovery

class GenerationQueue:
    def __init__(self):
        self._queue = []
        self._counter = 0
    
    def add_task(self, task: GenerationTask, priority: GenerationPriority):
        heappush(self._queue, (priority.value, self._counter, task))
        self._counter += 1
    
    async def process_queue(self):
        while self._queue:
            _, _, task = heappop(self._queue)
            await self._execute_generation(task)
```

---

## 🔧 Performance & Resource Management Research

### System Resource Optimization
**CPU Management**: Background process nice priority, CPU affinity  
**Memory Management**: Generation result streaming, cache size limits  
**Storage Management**: Automatic cleanup, compression, archive policies  

#### Resource Monitoring
```python
import psutil
from dataclasses import dataclass

@dataclass
class SystemResources:
    cpu_percent: float
    memory_percent: float  
    disk_usage_percent: float
    network_io: dict

class ResourceMonitor:
    def __init__(self, max_cpu: float = 70.0, max_memory: float = 80.0):
        self.max_cpu = max_cpu
        self.max_memory = max_memory
    
    def should_throttle_generation(self) -> bool:
        """Check if system resources require AI throttling"""
        resources = self.get_current_resources()
        return (resources.cpu_percent > self.max_cpu or 
                resources.memory_percent > self.max_memory)
    
    async def adaptive_generation_control(self):
        """Dynamically adjust generation frequency based on resources"""
        if self.should_throttle_generation():
            # Reduce generation frequency, defer low-priority tasks
            pass
```

### Cache Strategy Research
**Cache Type**: LRU Cache with TTL for generation results  
**Storage**: File system cache + Redis optional for distributed setup  
**Eviction Policy**: Size-based + time-based + usage-based  

```python
from functools import lru_cache
import aioredis
from typing import Optional

class GenerationCache:
    def __init__(self, max_size: int = 100, ttl: int = 3600 * 24):
        self.max_size = max_size
        self.ttl = ttl
        self._cache = {}
    
    def cache_key(self, prompt: str, context: dict) -> str:
        """Generate stable cache key for similar contexts"""
        return hashlib.md5(f"{prompt}:{sorted(context.items())}".encode()).hexdigest()
    
    async def get_cached_generation(self, prompt: str, context: dict) -> Optional[str]:
        """Get cached video if similar generation exists"""
        key = self.cache_key(prompt, context)
        # Check file system cache, return video path if exists
        pass
```

---

## 🔐 Security & Privacy Research

### API Security Best Practices
**Authentication**: Service account keys, token refresh, secure storage  
**Data Protection**: API key rotation, environment variable management  
**Network Security**: HTTPS only, request signing, rate limiting  

#### Secure Configuration Management
```python
import os
from cryptography.fernet import Fernet
from pydantic import BaseSettings

class AIServiceConfig(BaseSettings):
    veo_api_key: str
    weather_api_key: str
    encryption_key: str = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

class SecureConfigManager:
    def __init__(self):
        self.cipher = Fernet(os.environ.get('ENCRYPTION_KEY').encode())
    
    def encrypt_api_key(self, key: str) -> str:
        return self.cipher.encrypt(key.encode()).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        return self.cipher.decrypt(encrypted_key.encode()).decode()
```

### Privacy-First Learning Design
**Principles**: Local-only data, no external transmission, user control  
**Implementation**: SQLite storage, encrypted preferences, data export/deletion  

---

## 📊 Testing Strategy Research

### AI Component Testing Approaches
**Unit Testing**: Mock VEO API responses, prompt generation validation  
**Integration Testing**: End-to-end generation pipeline, weather integration  
**Performance Testing**: Load testing, resource usage, cache effectiveness  

#### AI-Specific Test Patterns
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
async def mock_veo_client():
    with patch('ai_service.VEOClient') as mock:
        mock.return_value.generate_video = AsyncMock(
            return_value=VideoGenerationResult(
                video_url="test_video.mp4",
                generation_id="test_123",
                cost=0.50
            )
        )
        yield mock

async def test_generation_pipeline(mock_veo_client, weather_service):
    """Test complete AI generation pipeline"""
    context = WeatherContext(condition="sunny", temperature=22.0, season="spring")
    prompt_generator = PromptGenerator()
    
    prompt = prompt_generator.generate_prompt(context, default_preferences)
    result = await ai_service.generate_video(prompt)
    
    assert result.success
    assert result.cost <= expected_max_cost
    assert "spring" in result.metadata["context"]
```

### Cost Testing & Simulation
```python
class CostSimulator:
    def __init__(self, daily_generations: int = 3, cost_per_generation: float = 0.50):
        self.daily_generations = daily_generations
        self.cost_per_generation = cost_per_generation
    
    def simulate_monthly_cost(self, success_rate: float = 0.85) -> float:
        """Simulate monthly API costs with generation success rate"""
        monthly_attempts = self.daily_generations * 30
        successful_generations = monthly_attempts * success_rate
        return successful_generations * self.cost_per_generation
    
    def cost_optimization_scenarios(self) -> dict:
        """Test different cost optimization strategies"""
        scenarios = {
            "baseline": self.simulate_monthly_cost(),
            "cache_50%": self.simulate_monthly_cost() * 0.5,  # 50% cache hit
            "reduced_frequency": (self.daily_generations * 0.7) * 30 * 0.85 * self.cost_per_generation
        }
        return scenarios
```

---

## 🚀 Deployment & Operations Research

### Production Environment Considerations
**Scaling**: Horizontal scaling for generation workers  
**Monitoring**: AI-specific metrics, cost tracking, generation quality  
**Maintenance**: Model updates, API version management, cache cleanup  

#### Monitoring & Alerting
```python
import logging
from prometheus_client import Counter, Histogram, Gauge

# Metrics for AI system monitoring
generation_requests = Counter('ai_generation_requests_total', 'Total AI generation requests')
generation_latency = Histogram('ai_generation_duration_seconds', 'AI generation duration')
api_cost_gauge = Gauge('ai_api_cost_daily', 'Daily AI API cost')

class AISystemMonitor:
    def __init__(self):
        self.logger = logging.getLogger('ai_system')
    
    async def track_generation_metrics(self, result: GenerationResult):
        generation_requests.inc()
        api_cost_gauge.set(self.calculate_daily_cost())
        
        if not result.success:
            self.logger.error(f"Generation failed: {result.error}")
            # Send alert if error rate exceeds threshold
```

---

## 🎯 Technology Selection Summary

### Final Technology Stack
```yaml
AI Integration:
  - VEO API Client: Google Cloud AI Platform SDK
  - Prompt Engine: Jinja2 + Custom Context System
  - Cost Tracking: Custom implementation with PostgreSQL/SQLite

External Data:
  - Weather: OpenWeatherMap API with aiohttp
  - Time/Season: Python datetime + custom seasonal logic
  - Caching: File system + optional Redis

Background Processing:
  - Scheduler: APScheduler with SQLite job store
  - Queue: Custom priority queue implementation
  - Resource Monitoring: psutil + custom metrics

Machine Learning:
  - User Preferences: Custom weighted scoring algorithm
  - Data Storage: SQLite with encrypted sensitive data
  - Privacy: Local-only processing, no external ML services

Testing & Monitoring:
  - Unit Tests: pytest with async support
  - AI Mocking: Custom VEO API mock responses
  - Metrics: Prometheus + Grafana (optional)
  - Cost Simulation: Custom testing framework
```

### Implementation Priority
1. **Week 1-2**: VEO API client + basic prompt generation
2. **Week 3-4**: Weather integration + context-aware prompts
3. **Week 5-6**: Scheduling system + background processing
4. **Week 7-8**: User learning system + preference engine
5. **Week 9-10**: Performance optimization + production readiness

---

**Next Actions**:
1. Set up VEO API development account and test generation
2. Implement basic prompt templates for major themes
3. Research optimal caching strategies for video generation
4. Design database schema extensions for AI features

---

*Generated with SuperClaude Framework - Technical Research for AI Dynamic Painting System Phase 2*