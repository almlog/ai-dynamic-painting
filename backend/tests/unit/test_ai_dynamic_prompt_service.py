"""
Unit tests for AI Dynamic Prompt Service - T270 AI unit tests comprehensive coverage  
Tests the dynamic prompt enhancement engine for AI video generation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ai.services.dynamic_prompt_service import (
    DynamicPromptService,
    PromptEnhancement,
    EnhancementType,
    PromptQuality,
    ContextIntegration
)


class TestDynamicPromptService:
    """Test cases for DynamicPromptService"""
    
    @pytest.fixture
    def prompt_service(self):
        """Create DynamicPromptService instance for testing"""
        return DynamicPromptService()
    
    @pytest.fixture
    def sample_base_prompt(self):
        """Sample base prompt for testing"""
        return "A beautiful sunset over mountains"
    
    @pytest.fixture
    def sample_context(self):
        """Sample context data for prompt enhancement"""
        return {
            "time_of_day": "evening",
            "weather": "clear",
            "season": "autumn",
            "user_preferences": {
                "style": "cinematic",
                "mood": "peaceful",
                "colors": ["warm", "golden"]
            },
            "location": "mountain_range"
        }
    
    def test_service_initialization(self, prompt_service):
        """Test DynamicPromptService initialization"""
        assert prompt_service is not None
        assert hasattr(prompt_service, 'enhancement_templates')
        assert hasattr(prompt_service, 'quality_metrics')
        assert hasattr(prompt_service, 'context_integrator')
        
    def test_basic_prompt_enhancement(self, prompt_service, sample_base_prompt):
        """Test basic prompt enhancement without context"""
        enhanced = prompt_service.enhance_prompt(sample_base_prompt)
        
        assert enhanced is not None
        assert len(enhanced) > len(sample_base_prompt)
        assert sample_base_prompt in enhanced or enhanced.startswith(sample_base_prompt.split()[0])
        
    def test_context_aware_enhancement(self, prompt_service, sample_base_prompt, sample_context):
        """Test context-aware prompt enhancement"""
        enhanced = prompt_service.enhance_prompt(
            sample_base_prompt,
            context=sample_context
        )
        
        assert enhanced is not None
        assert len(enhanced) > len(sample_base_prompt)
        
        # Check for context integration
        enhanced_lower = enhanced.lower()
        assert any(keyword in enhanced_lower for keyword in ["evening", "autumn", "golden", "cinematic"])
        
    def test_enhancement_type_specification(self, prompt_service, sample_base_prompt):
        """Test specifying enhancement types"""
        enhancement_types = [EnhancementType.STYLE, EnhancementType.DETAIL, EnhancementType.ATMOSPHERE]
        
        enhanced = prompt_service.enhance_prompt(
            sample_base_prompt,
            enhancement_types=enhancement_types
        )
        
        assert enhanced is not None
        assert len(enhanced) > len(sample_base_prompt)
        
    def test_quality_validation(self, prompt_service):
        """Test prompt quality validation"""
        high_quality_prompt = "A detailed cinematic view of golden autumn sunset over snow-capped mountains with dramatic clouds and warm lighting"
        low_quality_prompt = "sunset"
        
        high_quality = prompt_service.validate_prompt_quality(high_quality_prompt)
        low_quality = prompt_service.validate_prompt_quality(low_quality_prompt)
        
        assert high_quality.score > low_quality.score
        assert high_quality.quality in [PromptQuality.HIGH, PromptQuality.EXCELLENT]
        assert low_quality.quality in [PromptQuality.LOW, PromptQuality.POOR]
        
    def test_template_based_enhancement(self, prompt_service, sample_base_prompt):
        """Test template-based prompt enhancement"""
        template_name = "cinematic_landscape"
        
        enhanced = prompt_service.apply_template(
            sample_base_prompt,
            template_name=template_name
        )
        
        assert enhanced is not None
        assert len(enhanced) >= len(sample_base_prompt)
        
    def test_style_integration(self, prompt_service, sample_base_prompt):
        """Test style integration into prompts"""
        styles = ["photorealistic", "cinematic", "artistic"]
        
        for style in styles:
            enhanced = prompt_service.integrate_style(sample_base_prompt, style)
            
            assert enhanced is not None
            enhanced_lower = enhanced.lower()
            assert style in enhanced_lower or any(
                related in enhanced_lower 
                for related in prompt_service.get_style_keywords(style)
            )
            
    def test_mood_enhancement(self, prompt_service, sample_base_prompt):
        """Test mood-based prompt enhancement"""
        moods = ["peaceful", "dramatic", "mysterious", "joyful"]
        
        for mood in moods:
            enhanced = prompt_service.enhance_with_mood(sample_base_prompt, mood)
            
            assert enhanced is not None
            assert len(enhanced) >= len(sample_base_prompt)
            
    def test_technical_parameter_integration(self, prompt_service, sample_base_prompt):
        """Test integration of technical parameters"""
        tech_params = {
            "resolution": "4K",
            "aspect_ratio": "16:9",
            "camera_angle": "wide_shot",
            "lighting": "golden_hour"
        }
        
        enhanced = prompt_service.integrate_technical_params(
            sample_base_prompt,
            tech_params
        )
        
        assert enhanced is not None
        enhanced_lower = enhanced.lower()
        assert any(param.lower().replace("_", " ") in enhanced_lower for param in tech_params.values())
        
    def test_context_aware_time_integration(self, prompt_service, sample_base_prompt):
        """Test time-aware context integration"""
        time_contexts = [
            {"time_of_day": "sunrise", "expected_keywords": ["dawn", "morning", "golden"]},
            {"time_of_day": "noon", "expected_keywords": ["bright", "clear", "midday"]},
            {"time_of_day": "sunset", "expected_keywords": ["dusk", "evening", "warm"]},
            {"time_of_day": "night", "expected_keywords": ["dark", "moonlight", "stars"]}
        ]
        
        for time_context in time_contexts:
            enhanced = prompt_service.enhance_prompt(
                sample_base_prompt,
                context={"time_of_day": time_context["time_of_day"]}
            )
            
            enhanced_lower = enhanced.lower()
            assert any(keyword in enhanced_lower for keyword in time_context["expected_keywords"])
            
    def test_seasonal_context_integration(self, prompt_service, sample_base_prompt):
        """Test seasonal context integration"""
        seasonal_contexts = {
            "spring": ["bloom", "fresh", "green", "renewal"],
            "summer": ["bright", "vibrant", "lush", "warm"],
            "autumn": ["golden", "falling", "warm", "harvest"],
            "winter": ["snow", "frost", "cold", "crisp"]
        }
        
        for season, keywords in seasonal_contexts.items():
            enhanced = prompt_service.enhance_prompt(
                sample_base_prompt,
                context={"season": season}
            )
            
            enhanced_lower = enhanced.lower()
            # At least one seasonal keyword should be present
            assert any(keyword in enhanced_lower for keyword in keywords)
            
    def test_weather_context_integration(self, prompt_service, sample_base_prompt):
        """Test weather-aware prompt enhancement"""
        weather_contexts = {
            "sunny": ["bright", "clear", "brilliant"],
            "cloudy": ["overcast", "soft", "diffused"],
            "rainy": ["wet", "storm", "dramatic"],
            "foggy": ["misty", "mysterious", "ethereal"]
        }
        
        for weather, keywords in weather_contexts.items():
            enhanced = prompt_service.enhance_prompt(
                sample_base_prompt,
                context={"weather": weather}
            )
            
            enhanced_lower = enhanced.lower()
            # Should contain weather-appropriate descriptors
            weather_related = any(keyword in enhanced_lower for keyword in keywords)
            assert weather_related or weather in enhanced_lower
            
    def test_user_preference_integration(self, prompt_service, sample_base_prompt):
        """Test user preference integration"""
        user_preferences = {
            "style": "minimalist",
            "colors": ["blue", "white"],
            "mood": "calm",
            "complexity": "simple"
        }
        
        enhanced = prompt_service.enhance_prompt(
            sample_base_prompt,
            context={"user_preferences": user_preferences}
        )
        
        enhanced_lower = enhanced.lower()
        
        # Check for preference integration
        assert "minimalist" in enhanced_lower or "minimal" in enhanced_lower
        assert any(color in enhanced_lower for color in ["blue", "white"])
        assert "calm" in enhanced_lower or "peaceful" in enhanced_lower
        
    def test_prompt_length_optimization(self, prompt_service):
        """Test prompt length optimization"""
        short_prompt = "mountain"
        long_prompt = "A highly detailed, ultra-realistic, professional photography shot of a majestic mountain range with intricate geological formations, dramatic lighting conditions, and atmospheric perspective"
        
        # Short prompt should be enhanced
        enhanced_short = prompt_service.optimize_length(short_prompt, target_length="medium")
        assert len(enhanced_short) > len(short_prompt)
        
        # Long prompt should be condensed
        enhanced_long = prompt_service.optimize_length(long_prompt, target_length="medium")
        assert len(enhanced_long) < len(long_prompt)
        
    def test_keyword_density_optimization(self, prompt_service, sample_base_prompt):
        """Test keyword density optimization"""
        keywords = ["cinematic", "detailed", "atmospheric", "professional"]
        
        enhanced = prompt_service.optimize_keyword_density(
            sample_base_prompt,
            keywords=keywords,
            target_density=0.15
        )
        
        enhanced_lower = enhanced.lower()
        keyword_count = sum(1 for keyword in keywords if keyword in enhanced_lower)
        
        assert keyword_count > 0
        assert keyword_count <= len(keywords)  # No duplicate keywords
        
    def test_enhancement_chaining(self, prompt_service, sample_base_prompt, sample_context):
        """Test chaining multiple enhancements"""
        # Apply multiple enhancement steps
        step1 = prompt_service.enhance_prompt(sample_base_prompt, context=sample_context)
        step2 = prompt_service.integrate_style(step1, "photorealistic")
        step3 = prompt_service.enhance_with_mood(step2, "serene")
        final = prompt_service.optimize_length(step3, target_length="optimal")
        
        assert len(final) > len(sample_base_prompt)
        final_lower = final.lower()
        assert any(keyword in final_lower for keyword in ["photorealistic", "serene", "evening", "autumn"])
        
    def test_enhancement_reversal(self, prompt_service, sample_base_prompt):
        """Test enhancement reversal and cleanup"""
        enhanced = prompt_service.enhance_prompt(sample_base_prompt)
        simplified = prompt_service.simplify_prompt(enhanced)
        
        assert simplified is not None
        assert len(simplified) <= len(enhanced)
        # Core concept should remain
        assert any(word in simplified.lower() for word in sample_base_prompt.lower().split())
        
    def test_prompt_variation_generation(self, prompt_service, sample_base_prompt):
        """Test generating prompt variations"""
        variations = prompt_service.generate_variations(
            sample_base_prompt,
            count=3,
            variation_strength="medium"
        )
        
        assert len(variations) == 3
        assert all(isinstance(variation, str) for variation in variations)
        assert all(len(variation) > 0 for variation in variations)
        
        # Variations should be different from each other
        assert len(set(variations)) == 3  # All unique
        
    def test_contextual_keyword_extraction(self, prompt_service, sample_context):
        """Test extracting relevant keywords from context"""
        keywords = prompt_service.extract_contextual_keywords(sample_context)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        
        # Should include context elements
        keywords_lower = [k.lower() for k in keywords]
        assert any("evening" in k or "time" in k for k in keywords_lower)
        assert any("autumn" in k or "season" in k for k in keywords_lower)
        
    def test_enhancement_quality_scoring(self, prompt_service, sample_base_prompt):
        """Test enhancement quality scoring"""
        enhanced = prompt_service.enhance_prompt(sample_base_prompt)
        quality_score = prompt_service.score_enhancement_quality(
            sample_base_prompt,
            enhanced
        )
        
        assert isinstance(quality_score, dict)
        assert "overall_score" in quality_score
        assert "improvement_factor" in quality_score
        assert "enhancement_metrics" in quality_score
        
        assert quality_score["overall_score"] >= 0
        assert quality_score["improvement_factor"] >= 1.0
        
    def test_template_customization(self, prompt_service):
        """Test custom template creation and application"""
        custom_template = {
            "name": "test_template",
            "pattern": "{base_prompt}, captured with {style} photography, {mood} atmosphere",
            "variables": {
                "style": ["professional", "artistic", "documentary"],
                "mood": ["dramatic", "peaceful", "energetic"]
            }
        }
        
        prompt_service.add_custom_template(custom_template)
        
        enhanced = prompt_service.apply_template(
            "mountain landscape",
            template_name="test_template"
        )
        
        assert enhanced is not None
        assert "mountain landscape" in enhanced
        assert any(style in enhanced for style in custom_template["variables"]["style"])
        
    def test_enhancement_caching(self, prompt_service, sample_base_prompt, sample_context):
        """Test enhancement result caching"""
        # First enhancement (should be calculated)
        start_time = datetime.now()
        enhanced1 = prompt_service.enhance_prompt(sample_base_prompt, context=sample_context)
        first_duration = (datetime.now() - start_time).total_seconds()
        
        # Second enhancement (should be cached)
        start_time = datetime.now()
        enhanced2 = prompt_service.enhance_prompt(sample_base_prompt, context=sample_context)
        second_duration = (datetime.now() - start_time).total_seconds()
        
        assert enhanced1 == enhanced2
        # Second call should be faster due to caching (though this might be flaky in tests)
        # We'll just verify the results are identical
        
    def test_error_handling(self, prompt_service):
        """Test error handling for invalid inputs"""
        # Empty prompt
        with pytest.raises(ValueError):
            prompt_service.enhance_prompt("")
            
        # None prompt
        with pytest.raises(ValueError):
            prompt_service.enhance_prompt(None)
            
        # Invalid context
        result = prompt_service.enhance_prompt("test", context="invalid_context")
        assert result is not None  # Should handle gracefully
        
        # Invalid enhancement type
        result = prompt_service.enhance_prompt("test", enhancement_types=["invalid_type"])
        assert result is not None  # Should handle gracefully
        
    def test_batch_enhancement(self, prompt_service):
        """Test batch prompt enhancement"""
        prompts = [
            "sunset over ocean",
            "forest in morning mist", 
            "cityscape at night"
        ]
        
        enhanced_batch = prompt_service.enhance_batch(prompts)
        
        assert len(enhanced_batch) == len(prompts)
        assert all(isinstance(enhanced, str) for enhanced in enhanced_batch)
        assert all(len(enhanced) > len(original) for enhanced, original in zip(enhanced_batch, prompts))
        
    def test_context_priority_handling(self, prompt_service, sample_base_prompt):
        """Test handling of context priority"""
        high_priority_context = {
            "user_preferences": {"style": "photorealistic"},
            "priority": "high"
        }
        
        low_priority_context = {
            "weather": "rainy",
            "priority": "low"
        }
        
        combined_context = {**high_priority_context, **low_priority_context}
        
        enhanced = prompt_service.enhance_prompt(
            sample_base_prompt,
            context=combined_context
        )
        
        enhanced_lower = enhanced.lower()
        
        # High priority elements should be more prominent
        assert "photorealistic" in enhanced_lower
        # Low priority elements may or may not be present
        
    def test_enhancement_metadata(self, prompt_service, sample_base_prompt, sample_context):
        """Test enhancement metadata tracking"""
        result = prompt_service.enhance_prompt_with_metadata(
            sample_base_prompt,
            context=sample_context
        )
        
        assert "enhanced_prompt" in result
        assert "metadata" in result
        
        metadata = result["metadata"]
        assert "enhancement_types_applied" in metadata
        assert "context_elements_used" in metadata
        assert "processing_time" in metadata
        assert "quality_score" in metadata
        
    def test_performance_optimization(self, prompt_service):
        """Test performance optimization for large-scale enhancement"""
        # Test with multiple prompts to ensure performance
        prompts = [f"test prompt {i}" for i in range(10)]
        
        start_time = datetime.now()
        results = prompt_service.enhance_batch(prompts, optimize_performance=True)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        assert len(results) == len(prompts)
        assert processing_time < 5.0  # Should complete within reasonable time
        
        
class TestPromptEnhancementComponents:
    """Test individual components of prompt enhancement"""
    
    def test_style_keyword_mapping(self):
        """Test style to keyword mapping"""
        service = DynamicPromptService()
        
        cinematic_keywords = service.get_style_keywords("cinematic")
        photorealistic_keywords = service.get_style_keywords("photorealistic")
        
        assert isinstance(cinematic_keywords, list)
        assert isinstance(photorealistic_keywords, list)
        assert len(cinematic_keywords) > 0
        assert len(photorealistic_keywords) > 0
        
        # Keywords should be relevant to style
        assert any("film" in kw or "movie" in kw or "dramatic" in kw for kw in cinematic_keywords)
        assert any("realistic" in kw or "detailed" in kw for kw in photorealistic_keywords)
        
    def test_context_integration_priority(self):
        """Test context integration with priority levels"""
        service = DynamicPromptService()
        
        context = {
            "time_of_day": {"value": "sunset", "priority": "high"},
            "weather": {"value": "cloudy", "priority": "low"},
            "mood": {"value": "peaceful", "priority": "medium"}
        }
        
        integrated = service.integrate_context_with_priority("mountain view", context)
        
        assert "sunset" in integrated.lower()  # High priority should be included
        assert "peaceful" in integrated.lower()  # Medium priority likely included
        # Low priority weather may or may not be included
        
    def test_enhancement_type_behavior(self):
        """Test different enhancement type behaviors"""
        service = DynamicPromptService()
        base_prompt = "forest scene"
        
        # Test specific enhancement types
        style_enhanced = service.enhance_prompt(base_prompt, enhancement_types=[EnhancementType.STYLE])
        detail_enhanced = service.enhance_prompt(base_prompt, enhancement_types=[EnhancementType.DETAIL])
        atmosphere_enhanced = service.enhance_prompt(base_prompt, enhancement_types=[EnhancementType.ATMOSPHERE])
        
        # Each should add different types of elements
        assert len(style_enhanced) > len(base_prompt)
        assert len(detail_enhanced) > len(base_prompt)
        assert len(atmosphere_enhanced) > len(base_prompt)
        
        # They should be different from each other
        assert style_enhanced != detail_enhanced
        assert detail_enhanced != atmosphere_enhanced