
import pytest
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add backend to path to allow for src imports
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from src.services.master_generation_service import MasterGenerationService
from src.services.gemini_service import GeminiService
from src.ai.services.veo_client import VEOGenerationService

# Mock environment variables for all tests in this file
@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-api-key")
    monkeypatch.setenv("VEO_PROJECT_ID", "fake-project-id")

@pytest.fixture
def mock_services():
    """Fixture to mock dependent services for MasterGenerationService."""
    with patch('src.services.gemini_service.GeminiService') as MockGeminiService, \
         patch('src.ai.services.veo_client.VEOGenerationService') as MockVEOGenerationService:
        
        mock_gemini_instance = MockGeminiService.return_value
        mock_gemini_instance.generate_image.return_value = b'fake_image_bytes'
        mock_gemini_instance.generate_image_instructions.return_value = {"success": True, "instructions": "fake detailed instructions"}

        # Configure mock VEOGenerationService
        mock_veo_instance = MockVEOGenerationService.return_value
        mock_veo_instance.generate_video.return_value = {"status": "completed", "video_bytes": b'fake_video_bytes', "video_id": "fake_video_id"}

        yield {
            "gemini_service": mock_gemini_instance,
            "veo_service": mock_veo_instance
        }

@pytest.mark.asyncio
async def test_create_masterpiece_flow_red_phase(mock_services):
    """
    T-V006 (Red Phase): Tests that the MasterGenerationService.create_masterpiece_flow
    initially returns the placeholder message, indicating the orchestration logic is not yet implemented.
    """
    service = MasterGenerationService()

    prompt = "A futuristic city at sunset"
    result = await service.create_masterpiece_flow(prompt=prompt)

    # Assert that the result is the placeholder message
    assert result == {"status": "processing", "message": "Orchestration logic not yet implemented."}
    print("\n✅ T-V006 Red Phase: Test correctly passed, indicating orchestration logic is not yet implemented.")
