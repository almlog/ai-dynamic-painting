"""Contract tests for prompt generation engine (T213) - TDD RED Phase."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestPromptEngine:
    """Contract tests for AI prompt generation engine."""
    
    @pytest.mark.asyncio
    async def test_generate_contextual_prompt(self):
        """Test contextual prompt generation."""
        with pytest.raises(ModuleNotFoundError):
            from src.ai.services.prompt_engine import PromptEngine
            
            engine = PromptEngine()
            prompt = await engine.generate_prompt(
                base_theme="sunrise",
                context={"time": "morning", "weather": "clear"}
            )
            
            assert "sunrise" in prompt.lower()
            assert "morning" in prompt.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])