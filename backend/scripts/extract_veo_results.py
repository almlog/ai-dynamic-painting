#!/usr/bin/env python3
"""
VEO API Response Extractor
VEO APIレスポンスから動画データを抽出する詳細解析スクリプト
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

# Add parent directory to path for module imports
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Environment variables loaded from: {env_path}")
except ImportError:
    print("ℹ️  python-dotenv not installed, skipping .env file loading")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_veo_response_detailed(project_id: str, location: str) -> bool:
    """
    VEO APIレスポンスの詳細解析
    
    Args:
        project_id: Google Cloud プロジェクトID
        location: リージョン
    
    Returns:
        True if analysis successful, False otherwise
    """
    try:
        from google.cloud import aiplatform
        from google.cloud.aiplatform import gapic
        import google.protobuf.json_format as json_format
        
        print(f"\n🔍 Detailed VEO API Response Analysis")
        print(f"📍 Project: {project_id}")
        print(f"📍 Location: {location}")
        
        # Initialize Vertex AI
        aiplatform.init(
            project=project_id,
            location=location,
            credentials=None
        )
        
        print("✅ Vertex AI initialized for detailed analysis")
        
        # Create enhanced test request
        endpoint_name = f"projects/{project_id}/locations/{location}/publishers/google/models/imagegeneration@006"
        
        test_instances = [
            {
                "prompt": "A serene mountain landscape at golden hour",
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": "16:9",
                    "outputType": "video",
                    "duration": "3s",
                    "quality": "draft"
                }
            }
        ]
        
        print(f"\n🔄 Sending detailed generation request...")
        
        # Get prediction client
        client_options = {"api_endpoint": f"{location}-aiplatform.googleapis.com"}
        client = gapic.PredictionServiceClient(client_options=client_options)
        
        # Make prediction request
        response = client.predict(
            endpoint=endpoint_name,
            instances=test_instances,
            parameters={}
        )
        
        print("✅ Detailed generation request completed!")
        print(f"📊 Received {len(response.predictions)} predictions")
        
        # Detailed response analysis
        for i, prediction in enumerate(response.predictions):
            print(f"\n🎥 Analyzing Prediction {i+1}:")
            print(f"   Type: {type(prediction)}")
            
            # Convert to dict for detailed inspection
            try:
                prediction_dict = dict(prediction)
                print(f"   Keys: {list(prediction_dict.keys())}")
                
                for key, value in prediction_dict.items():
                    print(f"   {key}: {type(value)} = {str(value)[:100]}...")
                    
                    # Check for common video data fields
                    if key in ['bytesBase64Encoded', 'videoData', 'content', 'data']:
                        if isinstance(value, str) and len(value) > 100:
                            print(f"     🎬 Potential video data found! Length: {len(value)}")
                            
                            # Try to save as video
                            try:
                                output_dir = Path(__file__).parent.parent / "generated_videos"
                                output_dir.mkdir(exist_ok=True)
                                
                                if key == 'bytesBase64Encoded':
                                    import base64
                                    video_data = base64.b64decode(value)
                                    output_file = output_dir / f"veo_detailed_{int(time.time())}_{i}.mp4"
                                    
                                    with open(output_file, 'wb') as f:
                                        f.write(video_data)
                                    
                                    print(f"     ✅ Video saved: {output_file}")
                                    print(f"     📊 Size: {len(video_data)} bytes")
                                    
                                else:
                                    # Save raw data for analysis
                                    output_file = output_dir / f"veo_raw_{int(time.time())}_{i}_{key}.txt"
                                    
                                    with open(output_file, 'w') as f:
                                        f.write(str(value))
                                    
                                    print(f"     📄 Raw data saved: {output_file}")
                                    
                            except Exception as save_error:
                                print(f"     ❌ Save error: {save_error}")
                
            except Exception as dict_error:
                print(f"   ❌ Dict conversion error: {dict_error}")
                
                # Try alternative access methods
                try:
                    # Check for attributes
                    attrs = [attr for attr in dir(prediction) if not attr.startswith('_')]
                    print(f"   Available attributes: {attrs}")
                    
                    for attr in attrs:
                        try:
                            value = getattr(prediction, attr)
                            if not callable(value):
                                print(f"   {attr}: {type(value)} = {str(value)[:100]}...")
                        except Exception:
                            pass
                            
                except Exception as attr_error:
                    print(f"   ❌ Attribute access error: {attr_error}")
        
        # Check response metadata
        print(f"\n📋 Response Metadata:")
        print(f"   Response type: {type(response)}")
        
        if hasattr(response, 'model_version'):
            print(f"   Model version: {response.model_version}")
        if hasattr(response, 'model_display_name'):
            print(f"   Model name: {response.model_display_name}")
        if hasattr(response, 'deployed_model_id'):
            print(f"   Deployed model ID: {response.deployed_model_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Detailed analysis error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """
    メイン実行関数
    """
    print("=" * 60)
    print("VEO API Response Detailed Extractor")
    print("=" * 60)
    
    # Get configuration
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("VEO_PROJECT_ID", "ai-dynamic-painting")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    # Run detailed analysis
    success = analyze_veo_response_detailed(project_id, location)
    
    # Summary
    print("\n" + "=" * 60)
    print("VEO Response Analysis Summary")
    print("=" * 60)
    
    if success:
        print("✅ SUCCESS: VEO response analysis completed!")
        print("\nCheck the generated_videos/ directory for extracted content")
        return 0
    else:
        print("❌ FAILED: VEO response analysis failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())