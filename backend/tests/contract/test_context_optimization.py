"""
Contract tests for context-based generation optimization - T252.
Tests MUST fail initially (RED phase), then pass after implementation (GREEN phase).
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestContextOptimizationContract:
    """Contract tests for T252: Context-based Generation Optimization"""
    
    def test_context_model_exists(self):
        """Test that ContextOptimization model exists"""
        from src.models.context_optimization import ContextOptimization
        
        # Test model creation
        context = ContextOptimization(
            optimization_id="opt_123",
            context_type="environmental",
            context_data={"temperature": 22, "humidity": 60, "lighting": "natural"},
            optimization_params={"style_weight": 0.8, "mood_weight": 0.7},
            performance_score=0.85
        )
        
        assert context.optimization_id == "opt_123"
        assert context.context_type == "environmental"
        assert context.context_data["temperature"] == 22
        assert context.performance_score == 0.85
    
    @pytest.mark.asyncio
    async def test_context_optimization_service_exists(self):
        """Test that ContextOptimizationService exists and works"""
        from src.ai.services.context_optimization_service import ContextOptimizationService
        
        # Create service
        service = ContextOptimizationService()
        
        # Test context analysis
        context_data = {
            "time_of_day": "evening",
            "weather": "rainy",
            "temperature": 18,
            "user_activity": "relaxing",
            "location": "living_room"
        }
        
        # Analyze context for optimization
        optimization = await service.analyze_context(context_data)
        assert optimization is not None
        assert "style_suggestions" in optimization
        assert "mood_adjustment" in optimization
        assert "color_palette" in optimization
        assert "optimization_score" in optimization
    
    @pytest.mark.asyncio
    async def test_multi_context_optimization(self):
        """Test optimization with multiple context sources"""
        from src.ai.services.context_optimization_service import ContextOptimizationService
        
        service = ContextOptimizationService()
        
        # Multiple context sources
        contexts = {
            "environmental": {
                "temperature": 25,
                "humidity": 45,
                "lighting": "artificial"
            },
            "temporal": {
                "time_of_day": "night",
                "day_of_week": "friday",
                "season": "summer"
            },
            "user": {
                "mood": "energetic",
                "activity": "party",
                "preference_profile": "vibrant"
            }
        }
        
        # Get optimized generation parameters
        params = await service.optimize_generation_params(contexts)
        
        assert params is not None
        assert params["style"] is not None
        assert params["energy_level"] > 0.5  # Party context should increase energy
        assert "color_temperature" in params
        assert params["optimization_confidence"] > 0
    
    @pytest.mark.asyncio
    async def test_context_based_prompt_optimization(self):
        """Test that prompts are optimized based on context"""
        from src.ai.services.context_optimization_service import ContextOptimizationService
        
        service = ContextOptimizationService()
        
        base_prompt = "A beautiful scene"
        context = {
            "time_of_day": "sunset",
            "weather": "clear",
            "season": "autumn",
            "user_mood": "peaceful"
        }
        
        # Optimize prompt based on context
        optimized_prompt = await service.optimize_prompt(base_prompt, context)
        
        assert optimized_prompt != base_prompt
        assert len(optimized_prompt) > len(base_prompt)
        # Should include context-relevant elements
        assert any(word in optimized_prompt.lower() for word in ["sunset", "autumn", "peaceful", "golden"])
    
    @pytest.mark.asyncio
    async def test_performance_tracking(self):
        """Test that optimization performance is tracked"""
        from src.ai.services.context_optimization_service import ContextOptimizationService
        
        service = ContextOptimizationService()
        
        # Record optimization result
        optimization_id = "opt_456"
        context = {"time_of_day": "morning", "weather": "sunny"}
        result = {
            "user_satisfaction": 0.9,
            "generation_quality": 0.85,
            "context_match": 0.95
        }
        
        # Track performance
        success = await service.track_optimization_performance(optimization_id, context, result)
        assert success == True
        
        # Get performance metrics
        metrics = await service.get_optimization_metrics()
        assert metrics is not None
        assert metrics["average_satisfaction"] > 0
        assert metrics["total_optimizations"] > 0
        assert "best_performing_contexts" in metrics
    
    @pytest.mark.asyncio
    async def test_adaptive_learning(self):
        """Test that the system learns and adapts from optimization results"""
        from src.ai.services.context_optimization_service import ContextOptimizationService
        
        service = ContextOptimizationService()
        
        # Simulate multiple optimization cycles
        context = {"time_of_day": "evening", "weather": "cloudy"}
        
        # First optimization
        params1 = await service.optimize_generation_params({"environmental": context})
        
        # Record feedback - need to track the optimization first
        cache_key = service._generate_cache_key(context)
        await service.track_optimization_performance("opt_1", context, {"user_satisfaction": 0.6})
        
        # Record specific feedback
        await service.record_feedback("opt_1", params1, {"satisfaction": 0.6})
        
        # Second optimization (should adapt based on feedback)
        params2 = await service.optimize_generation_params({"environmental": context})
        
        # Check that adaptation weights have been updated
        cache_key = service._generate_cache_key(context)
        initial_weight = 1.0
        current_weight = service.adaptation_weights.get(cache_key, 1.0)
        
        # Weight should be different from initial after feedback
        assert current_weight != initial_weight
        # Both should have optimization_confidence
        assert "optimization_confidence" in params2
        assert "optimization_confidence" in params1
    
    @pytest.mark.asyncio  
    async def test_context_caching(self):
        """Test that context optimizations are cached for performance"""
        from src.ai.services.context_optimization_service import ContextOptimizationService
        
        service = ContextOptimizationService()
        
        context = {"time_of_day": "noon", "weather": "sunny", "temperature": 28}
        
        # First call - should compute
        import time
        start = time.time()
        result1 = await service.analyze_context(context)
        time1 = time.time() - start
        
        # Second call - should use cache
        start = time.time()
        result2 = await service.analyze_context(context)
        time2 = time.time() - start
        
        # Results should be the same (except cache_hit flag)
        result1_copy = {k: v for k, v in result1.items() if k != "cache_hit"}
        result2_copy = {k: v for k, v in result2.items() if k != "cache_hit"}
        assert result1_copy == result2_copy
        # Second call should be from cache
        assert result1["cache_hit"] == False
        assert result2["cache_hit"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])