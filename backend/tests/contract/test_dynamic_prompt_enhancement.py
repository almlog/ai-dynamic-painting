"""
Contract tests for dynamic prompt enhancement - T253.
Tests MUST fail initially (RED phase), then pass after implementation (GREEN phase).
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestDynamicPromptEnhancementContract:
    """Contract tests for T253: Dynamic Prompt Enhancement"""
    
    def test_prompt_enhancement_model_exists(self):
        """Test that PromptEnhancement model exists"""
        from src.models.prompt_enhancement import PromptEnhancement
        
        # Test model creation
        enhancement = PromptEnhancement(
            enhancement_id="enh_123",
            base_prompt="A beautiful landscape",
            enhanced_prompt="A beautiful landscape, in impressionist style, with golden hour lighting",
            enhancement_type="style_injection",
            enhancement_params={"style": "impressionist", "lighting": "golden_hour"},
            quality_score=0.89
        )
        
        assert enhancement.enhancement_id == "enh_123"
        assert enhancement.base_prompt == "A beautiful landscape"
        assert "impressionist" in enhancement.enhanced_prompt
        assert enhancement.quality_score == 0.89
    
    @pytest.mark.asyncio
    async def test_dynamic_prompt_service_exists(self):
        """Test that DynamicPromptService exists and works"""
        from src.ai.services.dynamic_prompt_service import DynamicPromptService
        
        # Create service
        service = DynamicPromptService()
        
        # Test basic prompt enhancement
        base_prompt = "A serene mountain scene"
        enhancement_config = {
            "target_style": "cinematic",
            "mood": "peaceful",
            "technical_quality": "high_resolution",
            "artistic_elements": ["depth_of_field", "atmospheric_perspective"]
        }
        
        # Enhance prompt
        enhanced_prompt = await service.enhance_prompt(base_prompt, enhancement_config)
        
        assert enhanced_prompt != base_prompt
        assert len(enhanced_prompt) > len(base_prompt)
        assert "cinematic" in enhanced_prompt.lower()
        assert "peaceful" in enhanced_prompt.lower()
    
    @pytest.mark.asyncio
    async def test_contextual_enhancement(self):
        """Test prompt enhancement based on context"""
        from src.ai.services.dynamic_prompt_service import DynamicPromptService
        
        service = DynamicPromptService()
        
        base_prompt = "A city street"
        context = {
            "time_of_day": "night",
            "weather": "rainy",
            "season": "winter",
            "mood": "noir"
        }
        
        # Enhance with context
        enhanced_prompt = await service.enhance_with_context(base_prompt, context)
        
        assert enhanced_prompt != base_prompt
        # Should include contextual elements
        context_words = ["night", "rain", "winter", "noir", "dark", "wet", "cold"]
        assert any(word in enhanced_prompt.lower() for word in context_words)
    
    @pytest.mark.asyncio
    async def test_multi_layer_enhancement(self):
        """Test multi-layer prompt enhancement"""
        from src.ai.services.dynamic_prompt_service import DynamicPromptService
        
        service = DynamicPromptService()
        
        base_prompt = "A forest"
        enhancement_layers = [
            {"layer": "style", "params": {"style": "fantasy", "intensity": 0.8}},
            {"layer": "lighting", "params": {"lighting": "magical", "time": "dusk"}},
            {"layer": "details", "params": {"details": ["ancient_trees", "mystical_fog"]}},
            {"layer": "technical", "params": {"quality": "8k", "render": "hyperrealistic"}}
        ]
        
        # Apply multi-layer enhancement
        enhanced_prompt = await service.apply_enhancement_layers(base_prompt, enhancement_layers)
        
        assert enhanced_prompt != base_prompt
        # Should include elements from all layers
        assert "fantasy" in enhanced_prompt.lower()
        assert any(word in enhanced_prompt.lower() for word in ["magical", "dusk"])
        assert any(word in enhanced_prompt.lower() for word in ["ancient", "mystical"])
        assert any(word in enhanced_prompt.lower() for word in ["8k", "hyperrealistic"])
    
    @pytest.mark.asyncio
    async def test_enhancement_quality_scoring(self):
        """Test that enhancement quality is scored"""
        from src.ai.services.dynamic_prompt_service import DynamicPromptService
        
        service = DynamicPromptService()
        
        base_prompt = "A flower"
        enhanced_prompt = "A delicate cherry blossom in full bloom, bathed in soft morning light, with dewdrops glistening on pink petals, shot with shallow depth of field, hyperrealistic 8k photography"
        
        # Score enhancement quality
        quality_score = await service.score_enhancement_quality(base_prompt, enhanced_prompt)
        
        assert 0.0 <= quality_score <= 1.0
        assert quality_score > 0.5  # Should be good quality
    
    @pytest.mark.asyncio
    async def test_style_transfer_enhancement(self):
        """Test style transfer enhancement"""
        from src.ai.services.dynamic_prompt_service import DynamicPromptService
        
        service = DynamicPromptService()
        
        base_prompt = "A portrait of a woman"
        target_styles = ["Van_Gogh", "Picasso", "Monet", "Dali"]
        
        enhanced_prompts = {}
        for style in target_styles:
            enhanced = await service.apply_style_transfer(base_prompt, style)
            enhanced_prompts[style] = enhanced
            
            assert enhanced != base_prompt
            assert style.lower().replace("_", " ") in enhanced.lower()
        
        # All enhanced prompts should be different
        unique_prompts = set(enhanced_prompts.values())
        assert len(unique_prompts) == len(target_styles)
    
    @pytest.mark.asyncio
    async def test_technical_optimization(self):
        """Test technical prompt optimization"""
        from src.ai.services.dynamic_prompt_service import DynamicPromptService
        
        service = DynamicPromptService()
        
        base_prompt = "A photo"
        technical_params = {
            "resolution": "4k",
            "camera": "professional_dslr",
            "lens": "85mm",
            "lighting": "studio_lighting",
            "composition": "rule_of_thirds"
        }
        
        # Apply technical optimization
        optimized_prompt = await service.optimize_technical_aspects(base_prompt, technical_params)
        
        assert optimized_prompt != base_prompt
        # Should include technical terms
        tech_terms = ["4k", "dslr", "85mm", "studio", "composition"]
        assert any(term in optimized_prompt.lower() for term in tech_terms)
    
    @pytest.mark.asyncio
    async def test_enhancement_history_tracking(self):
        """Test that enhancement history is tracked"""
        from src.ai.services.dynamic_prompt_service import DynamicPromptService
        
        service = DynamicPromptService()
        
        base_prompt = "A sunset"
        user_id = "user_123"
        
        # Perform multiple enhancements
        enhancements = []
        for i in range(3):
            enhanced = await service.enhance_prompt(
                base_prompt, 
                {"style": f"style_{i}", "mood": "dramatic"},
                user_id=user_id
            )
            enhancements.append(enhanced)
        
        # Get enhancement history
        history = await service.get_enhancement_history(user_id)
        
        assert history is not None
        assert len(history) >= 3
        assert all("enhancement_id" in item for item in history)
        assert all("timestamp" in item for item in history)
    
    @pytest.mark.asyncio
    async def test_adaptive_enhancement_learning(self):
        """Test that system learns from enhancement performance"""
        from src.ai.services.dynamic_prompt_service import DynamicPromptService
        
        service = DynamicPromptService()
        
        base_prompt = "A landscape"
        enhancement_config = {"style": "photorealistic", "mood": "serene"}
        
        # First enhancement
        enhanced1 = await service.enhance_prompt(base_prompt, enhancement_config)
        
        # Provide feedback
        await service.record_enhancement_feedback("enh_1", {
            "user_satisfaction": 0.9,
            "technical_quality": 0.85,
            "style_accuracy": 0.95
        })
        
        # Second enhancement (should be improved based on feedback)
        enhanced2 = await service.enhance_prompt(base_prompt, enhancement_config)
        
        # Enhancement should be refined
        assert enhanced1 != enhanced2
        
        # Get adaptation metrics
        metrics = await service.get_adaptation_metrics()
        assert "learning_rate" in metrics
        assert "improvement_trend" in metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])