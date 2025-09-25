"""
Cache entry model for advanced caching system.
Stores cache data with metadata, TTL, compression, and analytics.
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON, LargeBinary
from sqlalchemy.orm import declarative_base
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import json
import gzip
import hashlib

Base = declarative_base()


class CacheEntry(Base):
    """SQLAlchemy model for storing cache entries"""
    __tablename__ = "cache_entries"
    
    id = Column(Integer, primary_key=True)
    cache_key = Column(String(255), nullable=False, unique=True, index=True)
    data = Column(JSON)  # Uncompressed data storage
    compressed_data = Column(LargeBinary)  # Compressed data storage
    ttl_seconds = Column(Integer, nullable=False)
    cache_type = Column(String(100), nullable=False)  # prompt, weather, user_data, etc.
    tags = Column(JSON)  # JSON array of tags for grouping/invalidation
    compression_enabled = Column(Boolean, default=False)
    compression_ratio = Column(Float, default=1.0)
    original_size_bytes = Column(Integer, default=0)
    compressed_size_bytes = Column(Integer, default=0)
    
    # Access and analytics
    access_count = Column(Integer, default=0)
    last_access = Column(DateTime)
    hit_count = Column(Integer, default=0)
    miss_count = Column(Integer, default=0)
    
    # Cache level and priority
    cache_level = Column(String(10), default="L1")  # L1, L2, L3
    priority = Column(Integer, default=1)  # 1=highest priority
    is_persistent = Column(Boolean, default=False)
    
    # Adaptive TTL
    original_ttl = Column(Integer)  # Original TTL before adaptation
    adaptive_factor = Column(Float, default=1.0)  # TTL multiplication factor
    access_frequency = Column(Float, default=0.0)  # Accesses per hour
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    expires_at = Column(DateTime)
    
    def __init__(self, cache_key: str, data: Any, ttl_seconds: int,
                 cache_type: str = "general", tags: List[str] = None,
                 compression_enabled: bool = False, access_count: int = 0):
        self.cache_key = cache_key
        self.ttl_seconds = ttl_seconds
        self.original_ttl = ttl_seconds
        self.cache_type = cache_type
        self.tags = tags or []
        self.compression_enabled = compression_enabled
        self.access_count = access_count
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        
        # Store data with optional compression
        if compression_enabled:
            self.set_compressed_data(data)
        else:
            self.data = data
            self.original_size_bytes = len(json.dumps(data).encode('utf-8'))
    
    def set_compressed_data(self, data: Any):
        """Store data with compression"""
        json_data = json.dumps(data)
        original_bytes = json_data.encode('utf-8')
        compressed_bytes = gzip.compress(original_bytes)
        
        self.compressed_data = compressed_bytes
        self.original_size_bytes = len(original_bytes)
        self.compressed_size_bytes = len(compressed_bytes)
        self.compression_ratio = len(original_bytes) / len(compressed_bytes) if compressed_bytes else 1.0
        self.compression_enabled = True
    
    def get_data(self) -> Any:
        """Retrieve data with decompression if needed"""
        if self.compression_enabled and self.compressed_data:
            decompressed_bytes = gzip.decompress(self.compressed_data)
            json_data = decompressed_bytes.decode('utf-8')
            return json.loads(json_data)
        else:
            return self.data
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.now() > self.expires_at
    
    def update_access(self):
        """Update access statistics"""
        self.access_count += 1
        self.hit_count += 1
        self.last_access = datetime.now()
        
        # Update access frequency (accesses per hour)
        time_since_creation = (datetime.now() - self.created_at).total_seconds() / 3600
        if time_since_creation > 0:
            self.access_frequency = self.access_count / time_since_creation
        
        self.updated_at = datetime.now()
    
    def extend_ttl(self, factor: float = 1.5):
        """Extend TTL based on access patterns (adaptive TTL)"""
        self.adaptive_factor *= factor
        new_ttl = int(self.original_ttl * self.adaptive_factor)
        self.ttl_seconds = new_ttl
        self.expires_at = datetime.now() + timedelta(seconds=new_ttl)
        self.updated_at = datetime.now()
    
    def promote_cache_level(self):
        """Promote cache entry to higher level"""
        if self.cache_level == "L3":
            self.cache_level = "L2"
        elif self.cache_level == "L2":
            self.cache_level = "L1"
        self.updated_at = datetime.now()
    
    def demote_cache_level(self):
        """Demote cache entry to lower level"""
        if self.cache_level == "L1":
            self.cache_level = "L2"
        elif self.cache_level == "L2":
            self.cache_level = "L3"
        self.updated_at = datetime.now()


class CacheConfig(BaseModel):
    """Pydantic model for cache configuration"""
    max_memory_mb: int = Field(100, ge=10, le=1000, description="Maximum memory usage in MB")
    max_entries: int = Field(10000, ge=100, le=100000, description="Maximum cache entries")
    default_ttl_seconds: int = Field(300, ge=60, le=86400, description="Default TTL")
    compression_threshold_bytes: int = Field(1024, ge=512, description="Compression threshold")
    adaptive_ttl_enabled: bool = Field(True, description="Enable adaptive TTL")
    persistence_enabled: bool = Field(False, description="Enable disk persistence")
    eviction_strategy: str = Field("lru", description="Eviction strategy (lru, lfu, adaptive)")
    cache_levels: List[str] = Field(["L1", "L2", "L3"], description="Cache hierarchy levels")
    
    class Config:
        from_attributes = True


class CacheStats(BaseModel):
    """Pydantic model for cache statistics"""
    total_entries: int
    l1_entries: int
    l2_entries: int
    l3_entries: int
    memory_usage_mb: float
    hit_rate: float
    miss_rate: float
    compression_ratio: float
    eviction_count: int
    expired_count: int
    
    class Config:
        from_attributes = True


class CacheAnalytics(BaseModel):
    """Pydantic model for cache analytics"""
    hit_rate: float
    miss_rate: float
    total_requests: int
    hot_keys: List[str]
    cold_keys: List[str]
    access_patterns: Dict[str, Any]
    performance_metrics: Dict[str, float]
    
    class Config:
        from_attributes = True


class EvictionStats(BaseModel):
    """Pydantic model for eviction statistics"""
    total_evictions: int
    eviction_strategy: str
    evicted_by_ttl: int
    evicted_by_memory: int
    evicted_by_lru: int
    evicted_by_lfu: int
    average_entry_lifetime_seconds: float
    
    class Config:
        from_attributes = True


class CompressionStats(BaseModel):
    """Pydantic model for compression statistics"""
    compressed_entries: int
    uncompressed_entries: int
    compression_ratio: float
    space_saved_bytes: int
    compression_time_ms: float
    decompression_time_ms: float
    
    class Config:
        from_attributes = True


class WarmingConfig(BaseModel):
    """Pydantic model for cache warming configuration"""
    strategies: Dict[str, Dict[str, Any]] = Field(..., description="Warming strategies")
    priority: str = Field("medium", description="Warming priority level")
    parallel_workers: int = Field(3, ge=1, le=10, description="Parallel warming workers")
    
    class Config:
        from_attributes = True


class SyncResult(BaseModel):
    """Pydantic model for cache synchronization results"""
    status: str
    synced_entries: int
    conflicts_resolved: int
    sync_time_ms: int
    peer_node_id: str
    
    class Config:
        from_attributes = True


class PersistenceStats(BaseModel):
    """Pydantic model for persistence statistics"""
    persistent_entries: int
    last_save_time: Optional[str]
    last_load_time: Optional[str]
    disk_usage_mb: float
    save_time_ms: float
    load_time_ms: float
    
    class Config:
        from_attributes = True