"""
Gemini APIサービス
画像生成用の高品質AIプロンプト生成および画像生成
"""

import os
import requests
from typing import Dict, Any, Optional
import json
import base64
import logging

from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

# Logger setup
logger = logging.getLogger(__name__)


class GeminiService:
    """Gemini API統合サービス"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.project_id = os.getenv("VEO_PROJECT_ID")
        self.location = "us-central1"  # As per documentation, this is a common default
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        if not self.project_id:
            logger.error("VEO_PROJECT_ID environment variable is not set.")
        
        # Initialize AI Platform client
        try:
            aiplatform.init(project=self.project_id, location=self.location)
            logger.info(f"Vertex AI initialized for project '{self.project_id}' in '{self.location}'")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")


    def generate_image(self, prompt: str, quality: str = "standard", aspect_ratio: str = "1:1", negative_prompt: Optional[str] = None, style_preset: Optional[str] = None, seed: Optional[int] = None, sample_count: int = 1) -> Optional[bytes]:
        """
        Generates an image from a text prompt using Google Cloud's Imagen 2 API.

        Args:
            prompt: The text prompt to guide image generation.
            quality: The desired quality of the image ("standard" or "hd").
            aspect_ratio: The aspect ratio of the image (e.g., "1:1", "16:9").
            negative_prompt: An optional prompt of things to avoid in the image.
            style_preset: An optional style preset (e.g., "anime", "photographic", "digital-art").
            seed: An optional seed value for reproducible image generation.
            sample_count: The number of images to generate.

        Returns:
            The image data as bytes if successful, otherwise None.
        """
        logger.info(f"Starting image generation with prompt: {prompt[:80]}...")
        
        try:
            client_options = {"api_endpoint": f"{self.location}-aiplatform.googleapis.com"}
            prediction_service_client = aiplatform.gapic.PredictionServiceClient(
                client_options=client_options
            )

            endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/imagegeneration@006"

            instance = json_format.ParseDict({"prompt": prompt}, Value())
            
            # Build parameters based on quality
            image_size = "2K" if quality == "hd" else "1K"
            
            parameters_dict = {
                "sampleCount": sample_count,
                "sampleImageSize": image_size,
                "aspectRatio": aspect_ratio
            }
            if negative_prompt:
                parameters_dict["negativePrompt"] = negative_prompt
            if style_preset:
                parameters_dict["stylePreset"] = style_preset
            if seed is not None:
                parameters_dict["seed"] = seed

            parameters = json_format.ParseDict(parameters_dict, Value())
            
            response = prediction_service_client.predict(
                endpoint=endpoint, instances=[instance], parameters=parameters
            )

            if not response.predictions:
                logger.error("Image generation API returned no predictions.")
                return None

            # The generated image is base64 encoded
            image_bytes = base64.b64decode(response.predictions[0]["bytesBase64Encoded"])
            logger.info(f"Successfully generated image, {len(image_bytes)} bytes.")
            return image_bytes

        except Exception as e:
            logger.error(f"An error occurred during image generation: {e}")
            return None

    def generate_image_instructions(
        self, 
        prompt: str,
        model: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        top_k: int = 40,
        top_p: float = 0.95,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Gemini APIで画像生成指示を取得
        
        Args:
            prompt: 入力プロンプト
            model: 使用モデル
            temperature: Temperature設定
            top_k: Top-K設定
            top_p: Top-P設定
            max_tokens: 最大トークン数
            
        Returns:
            生成結果
        """
        
        if not self.api_key:
            return {
                "success": False,
                "error": "GEMINI_API_KEY not configured"
            }
        
        # エンハンスプロンプト
        enhanced_prompt = f"""
あなたは世界的に有名な美術ディレクターです。以下の指示に従って、
最高品質の絵画制作の詳細な指示書を作成してください：

{prompt}

【出力フォーマット】
1. 構図の詳細説明（前景・中景・背景）
2. 色彩とライティングの具体的指示
3. 質感と筆致の表現方法
4. 特徴的な要素の描き方
5. 全体の芸術的印象と雰囲気

美術館に展示できるレベルの高品質作品となるよう、
印象派の巨匠が描いたような詳細な指示を提供してください。
        """
        
        # API URL
        url = f"{self.base_url}/{model}:generateContent?key={self.api_key}"
        
        # リクエストボディ
        headers = {
            'Content-Type': 'application/json',
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": enhanced_prompt
                }]
            }],
            "generationConfig": {
                "temperature": temperature,
                "topK": top_k,
                "topP": top_p,
                "maxOutputTokens": max_tokens
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    
                    return {
                        "success": True,
                        "instructions": content,
                        "model": model,
                        "parameters": {
                            "temperature": temperature,
                            "top_k": top_k,
                            "top_p": top_p,
                            "max_tokens": max_tokens
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": "No response from Gemini API"
                    }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception: {str(e)}"
            }
    
    def validate_api_key(self) -> bool:
        """APIキーの有効性確認"""
        if not self.api_key:
            return False
            
        # 簡単なテストリクエスト
        url = f"{self.base_url}/gemini-1.5-flash:generateContent?key={self.api_key}"
        
        data = {
            "contents": [{
                "parts": [{
                    "text": "Hello"
                }]
            }]
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except:
            return False