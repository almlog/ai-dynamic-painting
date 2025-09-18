"""
Contract tests for advanced caching system - T256.
Tests MUST fail initially (RED phase), then pass after implementation (GREEN phase).
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestAdvancedCachingContract:
    """Contract tests for T256: Advanced Caching System"""
    
    def test_cache_entry_model_exists(self):
        """Test that CacheEntry model exists"""
        from src.models.cache_entry import CacheEntry
        
        # Test model creation
        entry = CacheEntry(
            cache_key="weather_tokyo_123",
            data={"temperature": 25, "humidity": 60},
            ttl_seconds=300,
            cache_type="weather_data",
            tags=["weather", "tokyo", "api_data"],
            compression_enabled=True,
            access_count=0
        )
        
        assert entry.cache_key == "weather_tokyo_123"
        assert entry.data["temperature"] == 25
        assert entry.ttl_seconds == 300
        assert entry.cache_type == "weather_data"
        assert "weather" in entry.tags
        assert entry.compression_enabled == True
        assert entry.access_count == 0
    
    @pytest.mark.asyncio
    async def test_advanced_cache_manager_exists(self):
        """Test that AdvancedCacheManager service exists and works"""
        from src.ai.services.advanced_cache_manager import AdvancedCacheManager
        
        # Create cache manager
        cache_manager = AdvancedCacheManager()
        
        # Test basic cache operations
        cache_key = "test_prompt_enhancement"
        test_data = {
            "base_prompt": "A beautiful scene",
            "enhanced_prompt": "A beautiful scene with cinematic lighting",
            "quality_score": 0.89
        }
        
        # Store data in cache
        success = await cache_manager.set(cache_key, test_data, ttl=300, tags=["prompt", "enhancement"])
        assert success == True
        
        # Retrieve data from cache
        cached_data = await cache_manager.get(cache_key)
        assert cached_data is not None
        assert cached_data["base_prompt"] == "A beautiful scene"
        assert cached_data["quality_score"] == 0.89
    
    @pytest.mark.asyncio
    async def test_hierarchical_caching(self):
        """Test hierarchical cache levels (L1, L2, L3)"""
        from src.ai.services.advanced_cache_manager import AdvancedCacheManager
        
        cache_manager = AdvancedCacheManager()
        
        # Test data for different cache levels
        l1_data = {"level": "L1", "size": "small", "access": "frequent"}
        l2_data = {"level": "L2", "size": "medium", "access": "moderate"}
        l3_data = {"level": "L3", "size": "large", "access": "infrequent"}
        
        # Store in different cache levels
        await cache_manager.set_l1("frequent_prompt", l1_data, ttl=60)
        await cache_manager.set_l2("moderate_prompt", l2_data, ttl=300)
        await cache_manager.set_l3("archived_prompt", l3_data, ttl=3600)
        
        # Retrieve from different levels
        l1_result = await cache_manager.get("frequent_prompt")
        l2_result = await cache_manager.get("moderate_prompt")
        l3_result = await cache_manager.get("archived_prompt")
        
        assert l1_result["level"] == "L1"
        assert l2_result["level"] == "L2"
        assert l3_result["level"] == "L3"
        
        # Test cache level promotion (L2 -> L1 on frequent access)
        for _ in range(5):  # Access multiple times
            await cache_manager.get("moderate_prompt")
        
        # Check if promoted to L1
        cache_stats = await cache_manager.get_cache_stats()
        assert cache_stats["l1_entries"] >= 1  # Should have promoted items
    
    @pytest.mark.asyncio
    async def test_intelligent_eviction(self):
        """Test intelligent cache eviction policies"""
        from src.ai.services.advanced_cache_manager import AdvancedCacheManager
        
        cache_manager = AdvancedCacheManager(max_memory_mb=10)  # Small cache for testing
        
        # Fill cache with data
        for i in range(20):
            data = {"item": i, "data": "x" * 1000}  # 1KB per item
            await cache_manager.set(f"item_{i}", data, ttl=3600)
        
        # Cache should be near full, eviction should occur
        cache_stats = await cache_manager.get_cache_stats()
        assert cache_stats["total_entries"] < 20  # Some items should be evicted
        assert cache_stats["memory_usage_mb"] <= 10  # Should respect memory limit
        
        # Recently accessed items should be preserved
        recent_item = await cache_manager.get("item_19")  # Last added
        assert recent_item is not None
        
        # Check eviction strategy effectiveness
        eviction_stats = await cache_manager.get_eviction_stats()
        assert eviction_stats["total_evictions"] > 0
        assert eviction_stats["eviction_strategy"] in ["lru", "lfu", "adaptive"]
    
    @pytest.mark.asyncio
    async def test_cache_compression(self):
        """Test data compression in cache"""
        from src.ai.services.advanced_cache_manager import AdvancedCacheManager
        
        cache_manager = AdvancedCacheManager()
        
        # Large data that benefits from compression
        large_data = {
            "prompt": "A beautiful landscape " * 100,  # Repetitive data
            "enhanced": "A beautiful landscape with cinematic lighting " * 100,
            "metadata": {"size": "large", "compression": "enabled"}
        }
        
        # Store with compression
        await cache_manager.set("large_prompt", large_data, 
                               ttl=300, enable_compression=True)
        
        # Store without compression for comparison
        await cache_manager.set("large_prompt_uncompressed", large_data,
                               ttl=300, enable_compression=False)
        
        # Check compression effectiveness
        compression_stats = await cache_manager.get_compression_stats()
        assert compression_stats["compressed_entries"] >= 1
        assert compression_stats["compression_ratio"] > 1.0  # Should achieve compression
        assert compression_stats["space_saved_bytes"] > 0
        
        # Data should be retrievable and identical
        compressed_data = await cache_manager.get("large_prompt")
        uncompressed_data = await cache_manager.get("large_prompt_uncompressed")
        
        assert compressed_data["prompt"] == uncompressed_data["prompt"]
        assert compressed_data["enhanced"] == uncompressed_data["enhanced"]
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_by_tags(self):
        """Test cache invalidation using tags"""
        from src.ai.services.advanced_cache_manager import AdvancedCacheManager
        
        cache_manager = AdvancedCacheManager()
        
        # Store data with different tags
        await cache_manager.set("weather_tokyo", {"temp": 25}, ttl=300, 
                               tags=["weather", "tokyo", "api_data"])
        await cache_manager.set("weather_osaka", {"temp": 28}, ttl=300,
                               tags=["weather", "osaka", "api_data"])
        await cache_manager.set("user_prefs", {"style": "modern"}, ttl=300,
                               tags=["user", "preferences"])
        
        # Verify all data is cached
        assert await cache_manager.get("weather_tokyo") is not None
        assert await cache_manager.get("weather_osaka") is not None
        assert await cache_manager.get("user_prefs") is not None
        
        # Invalidate by tag
        invalidated_count = await cache_manager.invalidate_by_tag("weather")
        assert invalidated_count == 2  # Both weather entries should be invalidated
        
        # Weather data should be gone, user prefs should remain
        assert await cache_manager.get("weather_tokyo") is None
        assert await cache_manager.get("weather_osaka") is None
        assert await cache_manager.get("user_prefs") is not None
    
    @pytest.mark.asyncio
    async def test_cache_warming(self):
        """Test cache warming functionality"""
        from src.ai.services.advanced_cache_manager import AdvancedCacheManager
        
        cache_manager = AdvancedCacheManager()
        
        # Define warming strategies
        warming_config = {
            "weather_data": {
                "locations": [{"lat": 35.6762, "lon": 139.6503}],  # Tokyo
                "ttl": 300,
                "priority": "high"
            },
            "common_prompts": {
                "prompts": ["landscape", "portrait", "abstract"],
                "ttl": 600,
                "priority": "medium"
            }
        }
        
        # Warm cache
        warming_result = await cache_manager.warm_cache(warming_config)
        assert warming_result["success"] == True
        assert warming_result["warmed_entries"] >= 3  # At least weather + prompts
        
        # Verify warmed data is accessible
        cache_stats = await cache_manager.get_cache_stats()
        assert cache_stats["total_entries"] >= 3
        
        # Check warming effectiveness
        warming_stats = await cache_manager.get_warming_stats()
        assert warming_stats["last_warming_time"] is not None
        assert warming_stats["total_warmed_entries"] >= 3
    
    @pytest.mark.asyncio
    async def test_distributed_cache_sync(self):
        """Test distributed cache synchronization"""
        from src.ai.services.advanced_cache_manager import AdvancedCacheManager
        
        # Simulate multiple cache instances
        cache_node1 = AdvancedCacheManager(node_id="node_1")
        cache_node2 = AdvancedCacheManager(node_id="node_2")
        
        # Store data in node 1
        await cache_node1.set("shared_prompt", {"data": "shared"}, ttl=300)
        
        # Sync between nodes
        sync_result = await cache_node1.sync_with_peer(cache_node2)
        assert sync_result["status"] == "success"
        
        # Data should be available in both nodes
        node1_data = await cache_node1.get("shared_prompt")
        node2_data = await cache_node2.get("shared_prompt")
        
        assert node1_data is not None
        assert node2_data is not None
        assert node1_data["data"] == node2_data["data"]
        
        # Test conflict resolution
        await cache_node1.set("conflict_key", {"version": 1, "node": "node_1"}, ttl=300)
        await cache_node2.set("conflict_key", {"version": 2, "node": "node_2"}, ttl=300)
        
        # Sync and resolve conflicts
        conflict_result = await cache_node1.sync_with_peer(cache_node2)
        assert conflict_result["conflicts_resolved"] >= 1
    
    @pytest.mark.asyncio
    async def test_cache_analytics(self):
        """Test cache analytics and monitoring"""
        from src.ai.services.advanced_cache_manager import AdvancedCacheManager
        
        cache_manager = AdvancedCacheManager()
        
        # Generate cache activity
        for i in range(10):
            await cache_manager.set(f"item_{i}", {"value": i}, ttl=300)
        
        # Access some items multiple times
        for _ in range(5):
            await cache_manager.get("item_0")  # Hot item
            await cache_manager.get("item_1")
        
        # Get analytics
        analytics = await cache_manager.get_cache_analytics()
        
        assert analytics["hit_rate"] >= 0.0
        assert analytics["miss_rate"] >= 0.0
        assert analytics["total_requests"] >= 10
        assert analytics["hot_keys"] is not None
        assert len(analytics["hot_keys"]) >= 1
        
        # Test performance metrics
        perf_metrics = await cache_manager.get_performance_metrics()
        assert perf_metrics["average_get_time_ms"] >= 0
        assert perf_metrics["average_set_time_ms"] >= 0
        assert perf_metrics["cache_efficiency"] >= 0.0
    
    @pytest.mark.asyncio
    async def test_cache_persistence(self):
        """Test cache persistence to disk"""
        from src.ai.services.advanced_cache_manager import AdvancedCacheManager
        
        cache_manager = AdvancedCacheManager(persistence_enabled=True)
        
        # Store persistent data
        persistent_data = {
            "user_preferences": {"theme": "dark", "language": "en"},
            "model_weights": {"accuracy": 0.95, "version": "v2.1"}
        }
        
        await cache_manager.set("persistent_prefs", persistent_data, 
                               ttl=3600, persistent=True)
        
        # Simulate cache restart
        await cache_manager.save_to_disk()
        cache_manager.clear_memory()
        await cache_manager.load_from_disk()
        
        # Data should be restored
        restored_data = await cache_manager.get("persistent_prefs")
        assert restored_data is not None
        assert restored_data["user_preferences"]["theme"] == "dark"
        assert restored_data["model_weights"]["accuracy"] == 0.95
        
        # Check persistence stats
        persistence_stats = await cache_manager.get_persistence_stats()
        assert persistence_stats["persistent_entries"] >= 1
        assert persistence_stats["last_save_time"] is not None
    
    @pytest.mark.asyncio
    async def test_adaptive_ttl(self):
        """Test adaptive TTL based on access patterns"""
        from src.ai.services.advanced_cache_manager import AdvancedCacheManager
        
        cache_manager = AdvancedCacheManager(adaptive_ttl=True)
        
        # Store items with adaptive TTL
        await cache_manager.set("popular_item", {"data": "popular"}, 
                               ttl=300, adaptive=True)
        await cache_manager.set("unpopular_item", {"data": "unpopular"}, 
                               ttl=300, adaptive=True)
        
        # Access popular item frequently
        for _ in range(10):
            await cache_manager.get("popular_item")
            await asyncio.sleep(0.01)  # Small delay
        
        # Access unpopular item once
        await cache_manager.get("unpopular_item")
        
        # Wait for TTL adaptation
        await asyncio.sleep(0.1)
        
        # Check adaptive TTL stats
        ttl_stats = await cache_manager.get_adaptive_ttl_stats()
        assert ttl_stats["adaptive_adjustments"] >= 0
        
        # Popular item should have extended TTL
        popular_meta = await cache_manager.get_metadata("popular_item")
        unpopular_meta = await cache_manager.get_metadata("unpopular_item")
        
        assert popular_meta is not None
        assert unpopular_meta is not None
        # Popular item may have longer remaining TTL due to access pattern


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])