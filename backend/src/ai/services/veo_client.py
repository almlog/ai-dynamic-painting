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


# =====================================
# T6-012: Enhanced VEO Client with VEOConfig Integration
# =====================================

class EnhancedVEOClient:
    """
    Enhanced VEO API client with VEOConfig integration
    T6-011で作成したVEOConfigを使用した堅牢なVEOクライアント
    """
    
    def __init__(self, config: Optional[VEOConfig] = None, timeout: int = 300, 
                 max_retries: int = 3, retry_delay: float = 1.0,
                 model: Optional[Any] = None):
        """
        Initialize Enhanced VEO client with Dependency Injection
        
        Args:
            config: VEOConfig instance (if None, will use get_veo_config())
            timeout: API request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
            retry_delay: Delay between retry attempts in seconds
            model: Optional GenerativeModel instance for dependency injection
            
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
        
        # Dependency injection for model
        self.model = model
        if self.model is None:
            # 実際のAPIを初期化
            aiplatform.init(
                project=self.project_id,
                location=self.location,
                credentials=self.get_credentials()
            )
            self.model = aiplatform.GenerativeModel(self.model_name)
        
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
        Internal method for VEO API calls using the actual SDK.

        Args:
            request_data: API request parameters including prompt, style, and image_bytes.

        Returns:
            Dict containing parsed API response.

        Raises:
            VEOValidationError: If the prompt is missing or invalid.
            Exception: For other API-related errors.
        """
        prompt = request_data.get('prompt')
        if not prompt:
            raise VEOValidationError("Prompt is required for VEO API call")

        generation_config = {
            "duration_secs": request_data.get('duration_seconds', 8),
            "resolution": request_data.get('resolution', '1920x1080'),
            "fps": request_data.get('fps', 24),
        }

        contents = [prompt]
        if 'image_bytes' in request_data and request_data['image_bytes']:
            from google.cloud.aiplatform_v1.types import content
            image_part = content.Part(inline_data=content.Blob(mime_type="image/png", data=request_data['image_bytes']))
            contents.append(image_part)

        try:
            response = await self.model.generate_content_async(
                contents,
                generation_config=generation_config
            )

            # Assuming the first part of the first candidate is the video response
            video_response_part = response.candidates[0].content.parts[0]
            video_uri = video_response_part.video_metadata.video_uri
            
            # This is a simplified parser. The actual response structure might be more complex.
            return {
                "status": "completed",
                "video_data": {
                    "video_url": video_uri,
                    "video_id": f"veo_{datetime.now().timestamp()}", # Placeholder
                    "duration_seconds": generation_config["duration_secs"],
                    "resolution": generation_config["resolution"]
                },
                "generation_time_ms": 50000, # Placeholder
                "metadata": {
                    "prompt": prompt,
                    "style": request_data.get('style'),
                    "model_version": self.model_name
                }
            }
        except Exception as e:
            logger.error(f"Error calling VEO API: {e}")
            # Re-raise the exception to be handled by the caller's error handling logic
            raise
    
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