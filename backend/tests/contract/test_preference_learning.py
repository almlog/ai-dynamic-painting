"""
Contract tests for preference learning system - T251.
Tests MUST fail initially (RED phase), then pass after implementation (GREEN phase).
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestPreferenceLearningContract:
    """Contract tests for T251: Advanced Preference Learning"""
    
    def test_preference_model_exists(self):
        """Test that PreferenceModel exists"""
        from src.models.preference_model import PreferenceModel
        
        # Test model creation
        preference = PreferenceModel(
            user_id="user_123",
            preference_type="style",
            preference_value="abstract",
            confidence_score=0.85,
            interaction_count=10
        )
        
        assert preference.user_id == "user_123"
        assert preference.preference_type == "style"
        assert preference.preference_value == "abstract"
        assert preference.confidence_score == 0.85
        assert preference.interaction_count == 10
    
    def test_user_interaction_model_exists(self):
        """Test that UserInteraction model exists"""
        from src.models.user_interaction import UserInteraction
        
        # Test interaction tracking
        interaction = UserInteraction(
            user_id="user_123",
            video_id="video_456",
            interaction_type="like",
            duration_seconds=120,
            timestamp=datetime.now()
        )
        
        assert interaction.user_id == "user_123"
        assert interaction.video_id == "video_456"
        assert interaction.interaction_type == "like"
        assert interaction.duration_seconds == 120
    
    @pytest.mark.asyncio
    async def test_preference_learning_service_exists(self):
        """Test that PreferenceLearningService exists and works"""
        from src.ai.services.preference_learning_service import PreferenceLearningService
        
        # Create service
        service = PreferenceLearningService()
        
        # Test preference tracking
        interaction_data = {
            "user_id": "user_123",
            "video_id": "video_456",
            "interaction_type": "like",
            "duration_seconds": 180,
            "prompt_style": "abstract",
            "time_of_day": "evening",
            "weather": "rainy"
        }
        
        # Record interaction
        success = await service.record_interaction(interaction_data)
        assert success == True
        
        # Get learned preferences
        preferences = await service.get_user_preferences("user_123")
        assert preferences is not None
        assert "style_preferences" in preferences
        assert "time_preferences" in preferences
        assert "weather_preferences" in preferences
        assert "confidence_scores" in preferences
    
    @pytest.mark.asyncio
    async def test_preference_based_prompt_adjustment(self):
        """Test that prompts can be adjusted based on learned preferences"""
        from src.ai.services.preference_learning_service import PreferenceLearningService
        
        service = PreferenceLearningService()
        
        # Set up user preferences
        user_id = "user_123"
        base_prompt = "A beautiful landscape"
        
        # Record multiple interactions to build preference profile
        interactions = [
            {"user_id": user_id, "interaction_type": "like", "prompt_style": "impressionist", "duration_seconds": 200},
            {"user_id": user_id, "interaction_type": "like", "prompt_style": "impressionist", "duration_seconds": 180},
            {"user_id": user_id, "interaction_type": "skip", "prompt_style": "realistic", "duration_seconds": 10},
        ]
        
        for interaction in interactions:
            await service.record_interaction(interaction)
        
        # Get adjusted prompt based on preferences
        adjusted_prompt = await service.adjust_prompt_for_user(user_id, base_prompt)
        
        assert adjusted_prompt != base_prompt
        assert "impressionist" in adjusted_prompt.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
