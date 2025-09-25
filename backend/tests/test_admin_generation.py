
import pytest
from fastapi.testclient import TestClient
import time
import os
import base64
from pathlib import Path

# Add backend to path to allow for src imports
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.main import app
from src.services.gemini_service import GeminiService
from src.models.admin import GenerationStatus

# 1x1 transparent PNG bytes
FAKE_IMAGE_BYTES = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")

@pytest.fixture
def client():
    """Pytest fixture to create a TestClient."""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def mock_gemini_service(monkeypatch):
    """Pytest fixture to mock the GeminiService.generate_image method."""
    def mock_generate_image(*args, **kwargs):
        print("Mocked GeminiService.generate_image called")
        return FAKE_IMAGE_BYTES

    monkeypatch.setattr(GeminiService, "generate_image", mock_generate_image)

def test_generate_image_workflow(client, mock_gemini_service):
    """
    Tests the full image generation workflow from the admin API.
    1. Creates a prompt template.
    2. Triggers image generation.
    3. Polls for completion status.
    4. Verifies the image file is created.
    5. Cleans up the generated file.
    """
    generated_image_path = None

    try:
        # 1. Create a prompt template
        template_payload = {
            "name": "Test Template",
            "template": "A painting of a {subject} in the style of {artist}.",
            "description": "A test prompt template."
        }
        response = client.post("/api/admin/prompts", json=template_payload)
        assert response.status_code == 201
        template = response.json()
        template_id = template["id"]
        assert template_id is not None

        # 2. Trigger image generation
        generation_request_payload = {
            "prompt_template_id": template_id,
            "variables": {
                "subject": "robot cat",
                "artist": "van Gogh"
            },
            "model": "imagegeneration@006",
            "temperature": 0.8
        }
        response = client.post("/api/admin/generate", json=generation_request_payload)
        assert response.status_code == 202
        generation_response = response.json()
        generation_id = generation_response["generation_id"]
        assert generation_id is not None
        assert generation_response["status"] == GenerationStatus.PROCESSING

        # 3. Poll for completion status
        start_time = time.time()
        timeout = 30  # 30 seconds timeout
        final_status_response = None

        while time.time() - start_time < timeout:
            response = client.get(f"/api/admin/generate/status/{generation_id}")
            assert response.status_code == 200
            status_data = response.json()
            if status_data["status"] != GenerationStatus.PROCESSING:
                final_status_response = status_data
                break
            time.sleep(1)  # Wait 1 second before polling again

        assert final_status_response is not None, "Generation did not complete within timeout."

        # 4. Verify the result
        assert final_status_response["status"] == GenerationStatus.COMPLETED
        assert "error_message" not in final_status_response or final_status_response["error_message"] is None
        
        generated_image_path = final_status_response.get("image_path")
        assert generated_image_path is not None
        
        abs_image_path = generated_image_path
        
        print(f"Verifying existence of file: {abs_image_path}")
        assert os.path.exists(abs_image_path), f"Generated image file not found at {abs_image_path}"
        
        # Verify file content is not empty
        assert os.path.getsize(abs_image_path) > 0

    finally:
        # 5. Clean up the generated file
        if generated_image_path:
            if os.path.exists(generated_image_path):
                os.remove(generated_image_path)
                print(f"Cleaned up generated file: {generated_image_path}")

def test_generate_image_template_not_found(client):
    """Tests that generation fails if the prompt template does not exist."""
    generation_request_payload = {
        "prompt_template_id": "non-existent-template-id",
        "variables": {},
        "model": "imagegeneration@006"
    }
    response = client.post("/api/admin/generate", json=generation_request_payload)
    assert response.status_code == 202 # The task is accepted
    generation_id = response.json()["generation_id"]

    # Poll for status
    time.sleep(2) # Give it a moment to fail
    response = client.get(f"/api/admin/generate/status/{generation_id}")
    assert response.status_code == 200
    status_data = response.json()

    assert status_data["status"] == GenerationStatus.FAILED
    assert "Template not found" in status_data["error_message"]
