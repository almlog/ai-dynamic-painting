
import pytest
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add backend to path to allow for src imports

from src.ai.services.veo_client import VEOGenerationService, VEOConfigurationError, VEOValidationError

import base64

# 1x1 transparent PNG bytes, a valid image format
FAKE_IMAGE_BYTES = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")

# Mock environment variables for all tests in this file
@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-api-key")
    monkeypatch.setenv("VEO_PROJECT_ID", "fake-project-id")

@pytest.fixture
def mock_generative_model():
    """Fixture to mock the genai.GenerativeModel and its response."""
    # Create a mock for the response object structure
    mock_response = MagicMock()
    mock_part = MagicMock()
    mock_part.blob.data = b'fake_video_bytes'
    mock_response.candidates = [MagicMock()]
    mock_response.candidates[0].content.parts = [mock_part]

    # Patch 'google.generativeai.GenerativeModel' and make its instance return the mock response
    with patch('google.generativeai.GenerativeModel') as mock_model_class:
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance
        yield mock_model_instance

@pytest.mark.asyncio
async def test_generate_video_image_to_video_success(mock_generative_model):
    """
    T-V004 (Green Phase): Tests the success case for image-to-video generation.
    """
    service = VEOGenerationService()
    service.model = mock_generative_model # Inject the mock model

    prompt = "Animate this image"
    fake_image_bytes = FAKE_IMAGE_BYTES

    result = await service.generate_video(
        prompt=prompt,
        image_bytes=fake_image_bytes
    )

    # Assert that the mock model's generate_content was called
    mock_generative_model.generate_content.assert_called_once()
    
    # Assert that the contents passed to the model include the image
    call_args, call_kwargs = mock_generative_model.generate_content.call_args
    assert len(call_kwargs['contents']) == 2
    # NOTE: The test can't easily assert the type of the PIL Image object,
    # but we can check that the prompt is in the correct place.
    assert call_kwargs['contents'][1] == prompt

    # Assert that the result from the service is correct
    assert result["status"] == "completed"
    assert result["video_bytes"] == b'fake_video_bytes'
    print("\n✅ T-V004: Image-to-Video test passed.")

@pytest.mark.asyncio
async def test_generate_video_text_to_video_success(mock_generative_model):
    """
    T-V004 (Green Phase): Tests the success case for text-to-video generation.
    """
    service = VEOGenerationService()
    service.model = mock_generative_model # Inject the mock model

    prompt = "A beautiful sunset"

    result = await service.generate_video(prompt=prompt)

    # Assert that the mock model's generate_content was called
    mock_generative_model.generate_content.assert_called_once()
    
    # Assert that the contents passed to the model are just the prompt
    call_args, call_kwargs = mock_generative_model.generate_content.call_args
    assert call_kwargs['contents'] == [prompt]

    # Assert that the result from the service is correct
    assert result["status"] == "completed"
    assert result["video_bytes"] == b'fake_video_bytes'
    print("\n✅ T-V004: Text-to-Video test passed.")

@pytest.mark.asyncio
async def test_generate_video_fails_on_empty_prompt():
    """
    Tests that validation prevents calls with an empty prompt.
    """
    service = VEOGenerationService()
    with pytest.raises(VEOValidationError) as excinfo:
        await service.generate_video(prompt="   ")
    assert "Prompt cannot be empty" in str(excinfo.value)
    print("\n✅ T-V004: Empty prompt validation test passed.")
