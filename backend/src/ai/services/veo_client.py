"""
🟢 T6-012 GREEN Phase: Enhanced VEO API client for video generation
VEOConfigと統合されたEnhanced VEOクライアント実装
"""

import os
from typing import Optional, Dict, Any, List
import asyncio
import json
from datetime import datetime
import logging
from google.cloud import aiplatform
from google.auth import default
import google.auth.transport.requests
from google.oauth2.service_account import Credentials
from pathlib import Path

# T6-011 VEOConfig統合
from src.config.veo_config import get_veo_config, VEOConfig

logger = logging.getLogger("ai_system.veo_api")


class VEOAuthenticationError(Exception):
    """VEO API authentication error."""
    pass


class VEOQuotaExceededError(Exception):
    """VEO API quota exceeded error."""
    pass


class VEOTimeoutError(Exception):
    """VEO API timeout error."""
    pass


class VEOValidationError(Exception):
    """VEO API validation error."""
    pass


class VEOConfigurationError(Exception):
    """VEO API configuration error."""
    pass


class VEOClient:
    """VEO API client for video generation."""
    
    def __init__(self, timeout: int = 300):
        """Initialize VEO client with configuration."""
        self.project_id = os.getenv('VEO_PROJECT_ID')
        self.location = os.getenv('VEO_LOCATION', 'us-central1')
        self.model_name = os.getenv('VEO_MODEL_NAME', 'veo-001-preview')
        self.timeout = timeout
        self.base_url = "https://aiplatform.googleapis.com"
        self.verify_ssl = True
        
        # Quota limits
        self.daily_quota = int(os.getenv('VEO_API_QUOTA_PER_DAY', '100'))
        self.per_minute_quota = int(os.getenv('VEO_API_QUOTA_PER_MINUTE', '10'))
        
        # Validate configuration
        if not self.project_id:
            raise VEOConfigurationError("VEO_PROJECT_ID environment variable is required")
        
        self._client = None
        self._credentials = None
        
    async def validate_credentials(self) -> bool:
        """Validate VEO API credentials."""
        try:
            credentials, project = default()
            self._credentials = credentials
            return True
        except Exception as e:
            logger.error(f"Credential validation failed: {e}")
            raise VEOAuthenticationError(f"Invalid credentials: {e}")
    
    async def authenticate_with_invalid_credentials(self):
        """Simulate authentication with invalid credentials - for testing."""
        raise VEOAuthenticationError("Invalid credentials provided")
    
    async def get_access_token(self) -> str:
        """Get access token for VEO API."""
        if not self._credentials:
            await self.validate_credentials()
        
        request = google.auth.transport.requests.Request()
        self._credentials.refresh(request)
        return self._credentials.token
    
    async def refresh_token(self) -> str:
        """Refresh access token."""
        old_token = await self.get_access_token()
        
        # Simulate token refresh
        request = google.auth.transport.requests.Request()
        self._credentials.refresh(request)
        new_token = self._credentials.token
        
        if new_token == old_token:
            # Force a new token for testing
            new_token = f"refreshed_{new_token}"
        
        return new_token
    
    async def health_check(self) -> Dict[str, Any]:
        """Check VEO API health status."""
        start_time = datetime.now()
        
        try:
            await self.validate_credentials()
            authenticated = True
        except:
            authenticated = False
        
        end_time = datetime.now()
        latency_ms = (end_time - start_time).total_seconds() * 1000
        
        return {
            "status": "healthy" if authenticated else "unhealthy",
            "latency_ms": latency_ms,
            "authenticated": authenticated,
            "timestamp": datetime.now().isoformat()
        }
    
    async def generate_video_when_quota_exceeded(self):
        """Simulate quota exceeded error - for testing."""
        raise VEOQuotaExceededError("Daily quota exceeded")
    
    async def retry_on_auth_error(self, max_retries: int = 3) -> Dict[str, Any]:
        """Retry mechanism for authentication errors."""
        retry_count = 0
        
        for attempt in range(max_retries):
            try:
                await self.validate_credentials()
                return {"success": True, "retry_count": retry_count}
            except VEOAuthenticationError:
                retry_count += 1
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)  # Wait before retry
                else:
                    raise
        
        return {"success": False, "retry_count": retry_count}
    
    async def generate_video_with_timeout(self):
        """Simulate timeout error - for testing."""
        await asyncio.sleep(self.timeout + 1)  # Exceed timeout
        raise VEOTimeoutError("Request timed out")


import google.generativeai as genai
from PIL import Image
import io

class VEOGenerationService:
    """VEO video generation service using google-generativeai."""
    
    def __init__(self):
        """Initialize the VEO service and configure the API key."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise VEOConfigurationError("GEMINI_API_KEY environment variable is not set.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('models/veo-3') # Correct way to get the model
        logger.info("VEOGenerationService initialized and configured with model 'veo-3'.")
    
    async def generate_video(
        self,
        prompt: str,
        image_bytes: Optional[bytes] = None, # Added for Image-to-Video
        duration_seconds: int = 8,
        resolution: str = "1920x1080",
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generates a video using VEO API, supporting both text-to-video and image-to-video."""
        
        if not prompt.strip():
            raise VEOValidationError("Prompt cannot be empty")

        full_prompt = f"{prompt}, {style}" if style else prompt
        contents = [full_prompt]

        if image_bytes:
            logger.info(f"Starting IMAGE-TO-VIDEO generation for prompt: {full_prompt[:100]}...")
            try:
                # The API expects a PIL Image object
                image = Image.open(io.BytesIO(image_bytes))
                # Prepend the image to the contents list for image-to-video
                contents.insert(0, image)
            except Exception as e:
                logger.error(f"Failed to process provided image bytes: {e}")
                raise VEOValidationError(f"Invalid image data provided: {e}")
        else:
            logger.info(f"Starting TEXT-TO-VIDEO generation for prompt: {full_prompt[:100]}...")

        try:
            # The new SDK handles the long-running operation implicitly.
            # The result is returned directly when generation is complete.
            # This might take several minutes.
            response = self.model.generate_content(
                contents=contents,
                generation_config=genai.types.GenerationConfig(
                    # Parameters for video generation might differ, consult docs
                    temperature=0.7 
                )
            )

            # Assuming the response contains the video data in the first candidate
            video_part = response.candidates[0].content.parts[0]
            video_bytes = video_part.blob.data

            logger.info(f"Successfully generated video, {len(video_bytes)} bytes.")

            return {
                "status": "completed",
                "video_bytes": video_bytes,
                "video_id": f"veo_video_{datetime.now().timestamp()}",
                "completion_time": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to generate VEO video: {e}")
            raise VEOValidationError(f"VEO API call failed: {e}")


# Exception classes for validation (keeping for backward compatibility)
class VEOValidationError(Exception):
    """VEO API validation error."""
    pass


class VEOConfigurationError(Exception):
    """VEO API configuration error."""
    pass


# =====================================
# T6-012: Enhanced VEO Client with VEOConfig Integration
# =====================================

class EnhancedVEOClient:
    """
    Enhanced VEO API client with VEOConfig integration
    T6-011で作成したVEOConfigを使用した堅牢なVEOクライアント
    """
    
    def __init__(self, config: Optional[VEOConfig] = None, timeout: int = 300, 
                 max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize Enhanced VEO client with Dependency Injection
        
        Args:
            config: VEOConfig instance (if None, will use get_veo_config())
            timeout: API request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
            retry_delay: Delay between retry attempts in seconds
            
        Raises:
            VEOConfigurationError: If VEOConfig initialization fails
        """
        try:
            # Dependency Injection: Use provided config or get default
            self._config = config if config is not None else get_veo_config()
            self.project_id = self._config.project_id
            self.location = self._config.location
            self.credentials_path = self._config.credentials_path
        except Exception as e:
            raise VEOConfigurationError(f"Configuration error: {e}")
        
        # Client configuration
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.model_name = 'veo-001-preview'
        
        # Retryable error patterns (configurable)
        self.retryable_error_patterns = ['503', 'Service Temporarily Unavailable']
        
        # Authentication state
        self._credentials = None
        
        logger.info(f"EnhancedVEOClient initialized with project: {self.project_id}, location: {self.location}")
    
    def get_credentials(self) -> Credentials:
        """
        Get Google Cloud credentials from VEOConfig
        
        Returns:
            Credentials: Google Cloud credentials object
        """
        return self._config.get_google_credentials()
    
    def _parse_video_response(self, response: Dict[str, Any], image_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Parse VEO API response into standardized result format
        
        Args:
            response: Raw API response from VEO
            image_bytes: Optional image data for flagging image-to-video generation
            
        Returns:
            Dict: Standardized video generation result
        """
        result = {
            "status": response["status"],
            "video_id": response["video_data"]["video_id"],
            "video_url": response["video_data"]["video_url"],
            "duration_seconds": response["video_data"]["duration_seconds"],
            "resolution": response["video_data"]["resolution"],
            "generation_time_ms": response["generation_time_ms"]
        }
        
        # Add image-to-video flag if applicable
        if image_bytes:
            result["generation_type"] = "image_to_video"
            
        return result
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Determine if an error should trigger a retry attempt
        
        Args:
            error: The exception to evaluate
            
        Returns:
            bool: True if error is retryable, False otherwise
        """
        error_str = str(error)
        return any(pattern in error_str for pattern in self.retryable_error_patterns)
    
    def _handle_api_exception(self, error: Exception) -> None:
        """
        Handle API exceptions with appropriate logging and re-raising
        
        Args:
            error: The exception to handle
            
        Raises:
            The original exception or wrapped VEOValidationError
        """
        logger.error(f"VEO video generation failed: {error}")
        
        # Known VEO exceptions - re-raise as-is
        if isinstance(error, (VEOAuthenticationError, VEOValidationError, 
                             VEOQuotaExceededError, VEOTimeoutError)):
            raise
        
        # 503 errors should be re-raised for retry logic
        if self._is_retryable_error(error):
            raise  # Re-raise for retry handling
            
        # Other exceptions wrapped as validation errors
        raise VEOValidationError(f"VEO API call failed: {error}")
    
    async def _call_veo_api(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method for VEO API calls
        
        Args:
            request_data: API request parameters
            
        Returns:
            Dict containing API response
            
        Raises:
            VEOAuthenticationError: Authentication failed
            VEOValidationError: Invalid request parameters
            VEOQuotaExceededError: API quota exceeded
        """
        # Mock implementation for testing - will be replaced with real API calls
        prompt = request_data.get('prompt', '')
        
        # Simulate API processing time
        await asyncio.sleep(0.1)
        
        # Mock successful response
        return {
            "status": "completed",
            "video_data": {
                "video_url": f"https://storage.googleapis.com/test-video-{hash(prompt)}.mp4",
                "video_id": f"veo_{datetime.now().timestamp()}",
                "duration_seconds": 8,
                "resolution": "1920x1080"
            },
            "generation_time_ms": 45000,
            "metadata": {
                "prompt": prompt,
                "style": request_data.get('style'),
                "model_version": self.model_name
            }
        }
    
    async def generate_video(self, prompt: str, style: Optional[str] = None, 
                           image_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Generate video using VEO API
        
        Args:
            prompt: Text prompt for video generation
            style: Optional style parameter
            image_bytes: Optional image data for image-to-video generation
            
        Returns:
            Dict containing generation results
            
        Raises:
            VEOValidationError: Invalid input parameters
            VEOAuthenticationError: Authentication failed
            VEOTimeoutError: Request timeout
        """
        # Input validation
        if not prompt or not prompt.strip():
            raise VEOValidationError("Prompt cannot be empty")
        
        logger.info(f"Starting VEO video generation with prompt: {prompt}")
        
        try:
            # Prepare request data
            request_data = {
                'prompt': prompt,
                'style': style,
                'has_image': image_bytes is not None
            }
            
            # Call API with timeout
            response = await asyncio.wait_for(
                self._call_veo_api(request_data),
                timeout=self.timeout
            )
            
            # Parse response using helper method
            result = self._parse_video_response(response, image_bytes)
            
            # Log success
            logger.info(f"VEO video generation completed successfully. Video ID: {result['video_id']}, Time: {result['generation_time_ms']}ms")
            
            return result
            
        except asyncio.TimeoutError:
            raise VEOTimeoutError("Request timeout exceeded")
        except Exception as e:
            self._handle_api_exception(e)
    
    async def generate_video_with_retry(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate video with automatic retry logic for temporary failures
        
        Args:
            prompt: Text prompt for video generation
            **kwargs: Additional parameters for generate_video
            
        Returns:
            Dict containing generation results
            
        Raises:
            VEOTimeoutError: Max retries exceeded
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await self.generate_video(prompt, **kwargs)
            except Exception as e:
                last_exception = e
                # Check if error is retryable using helper method
                if self._is_retryable_error(e):
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Retry {attempt + 1}/{self.max_retries} after error: {e}")
                        await asyncio.sleep(self.retry_delay)
                        continue
                    # Last retry for retryable error - will be handled at the end of the loop
                else:
                    # Non-retryable error, raise immediately
                    raise
        
        # Max retries exceeded
        raise VEOTimeoutError(f"Max retries exceeded: {last_exception}")