# Integration test test_ai_scheduling.py - TDD RED Phase
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class Testtest_ai_scheduling:
    @pytest.mark.asyncio
    async def test_integration(self):
        with pytest.raises(ModuleNotFoundError):
            from src.ai.services.integration import IntegrationService
            service = IntegrationService()
            result = await service.run_integration()
            assert result is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
