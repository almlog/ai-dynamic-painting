#!/usr/bin/env python3
"""
Real VEO API Video Generation Test
実際のVEO APIを使った動画生成テスト（小規模・低コスト）
"""

import os
import sys
import json
import time
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
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
    else:
        print(f"ℹ️  No .env file found at: {env_path}")
except ImportError:
    print("ℹ️  python-dotenv not installed, skipping .env file loading")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_real_veo_generation(project_id: str, location: str, test_prompt: str = "A beautiful sunset over mountains") -> bool:
    """
    実際のVEO APIを使った動画生成テスト
    
    Args:
        project_id: Google Cloud プロジェクトID
        location: リージョン
        test_prompt: 生成テスト用プロンプト
    
    Returns:
        True if generation successful, False otherwise
    """
    try:
        from google.cloud import aiplatform
        from google.cloud.aiplatform import gapic
        
        print(f"\n🎬 Real VEO API Video Generation Test")
        print(f"📍 Project: {project_id}")
        print(f"📍 Location: {location}")
        print(f"📝 Prompt: {test_prompt}")
        print(f"💰 Estimated Cost: $0.50-$2.00")
        
        # Warning confirmation
        print(f"\n⚠️  WARNING: This will make REAL API calls and incur costs!")
        print(f"   Continue? (y/N): ", end="")
        
        # For automated testing, skip confirmation
        # In real usage, you'd want user confirmation
        confirmation = os.getenv('VEO_TEST_CONFIRM', 'n').lower()
        print(confirmation)
        
        if confirmation != 'y':
            print("❌ Test cancelled by user")
            return False
        
        # Initialize Vertex AI
        aiplatform.init(
            project=project_id,
            location=location,
            credentials=None  # Use default credentials discovery
        )
        
        print("✅ Vertex AI initialized for real generation")
        
        # Prepare generation request
        # Note: This is a simplified example - actual VEO API might have different endpoints
        endpoint_name = f"projects/{project_id}/locations/{location}/publishers/google/models/imagegeneration@006"
        
        # Create prediction request
        instances = [
            {
                "prompt": test_prompt,
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": "16:9",
                    "outputType": "video",
                    "duration": "5s",  # Shortest duration to minimize cost
                    "quality": "draft"  # Lowest quality to minimize cost
                }
            }
        ]
        
        print(f"\n🔄 Sending generation request...")
        print(f"   Endpoint: {endpoint_name}")
        print(f"   Duration: 5s (minimum)")
        print(f"   Quality: draft (minimum cost)")
        
        # Try to make prediction
        try:
            # Get prediction client
            client_options = {"api_endpoint": f"{location}-aiplatform.googleapis.com"}
            client = gapic.PredictionServiceClient(client_options=client_options)
            
            # Make prediction request
            response = client.predict(
                endpoint=endpoint_name,
                instances=instances,
                parameters={}
            )
            
            print("✅ Generation request sent successfully!")
            print(f"📊 Response: {len(response.predictions)} predictions received")
            
            # Process response
            for i, prediction in enumerate(response.predictions):
                print(f"\n🎥 Video {i+1}:")
                
                if hasattr(prediction, 'bytesBase64Encoded') and prediction.bytesBase64Encoded:
                    # Save generated video
                    output_dir = Path(__file__).parent.parent / "generated_videos"
                    output_dir.mkdir(exist_ok=True)
                    
                    output_file = output_dir / f"veo_test_{int(time.time())}.mp4"
                    
                    import base64
                    video_data = base64.b64decode(prediction.bytesBase64Encoded)
                    
                    with open(output_file, 'wb') as f:
                        f.write(video_data)
                    
                    print(f"   ✅ Video saved: {output_file}")
                    print(f"   📊 Size: {len(video_data)} bytes")
                    
                elif hasattr(prediction, 'content'):
                    print(f"   📝 Content: {prediction.content}")
                else:
                    print(f"   📄 Raw prediction: {prediction}")
            
            print(f"\n🎉 Real VEO generation test SUCCESSFUL!")
            return True
            
        except Exception as api_error:
            error_str = str(api_error)
            
            if "403" in error_str or "permission" in error_str.lower():
                print(f"❌ Permission denied: {api_error}")
                print(f"   Possible causes:")
                print(f"   1. VEO/Imagen APIs not enabled")
                print(f"   2. Insufficient IAM permissions")
                print(f"   3. Billing not enabled")
                
            elif "404" in error_str or "not found" in error_str.lower():
                print(f"❌ Endpoint not found: {api_error}")
                print(f"   The VEO model might not be available in this region")
                print(f"   Try us-central1 or us-west1")
                
            elif "quota" in error_str.lower() or "rate" in error_str.lower():
                print(f"❌ Quota/Rate limit exceeded: {api_error}")
                print(f"   Wait a few minutes and try again")
                
            else:
                print(f"❌ API error: {api_error}")
            
            return False
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure google-cloud-aiplatform is installed")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_prerequisites() -> bool:
    """
    実VEO生成の前提条件チェック
    
    Returns:
        True if all prerequisites met, False otherwise
    """
    print("🔍 Checking prerequisites for real VEO generation...")
    
    # Check authentication
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path or not Path(credentials_path).exists():
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set or file not found")
        return False
    
    print(f"✅ Authentication: {credentials_path}")
    
    # Check environment variables
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("VEO_PROJECT_ID")
    if not project_id:
        print("❌ Project ID not set (GOOGLE_CLOUD_PROJECT or VEO_PROJECT_ID)")
        return False
    
    print(f"✅ Project ID: {project_id}")
    
    # Check billing warning acceptance
    daily_budget = os.getenv("DAILY_BUDGET_LIMIT", "10.00")
    print(f"✅ Daily budget limit: ${daily_budget}")
    
    return True


def main():
    """
    メイン実行関数
    """
    print("=" * 60)
    print("Real VEO API Video Generation Test")
    print("⚠️  This will incur actual costs!")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix issues above.")
        return 1
    
    # Get configuration
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("VEO_PROJECT_ID", "ai-dynamic-painting")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    test_prompt = "A peaceful mountain sunset with clouds, 5 seconds, cinematic"
    
    # Run real generation test
    success = test_real_veo_generation(project_id, location, test_prompt)
    
    # Summary
    print("\n" + "=" * 60)
    print("Real VEO Generation Test Summary")
    print("=" * 60)
    
    if success:
        print("🎉 SUCCESS: Real VEO video generation test completed!")
        print("\nNext steps:")
        print("1. Review generated video quality")
        print("2. Check actual billing costs in Google Cloud Console")
        print("3. Adjust generation parameters based on results")
        print("4. Implement production cost monitoring")
        return 0
    else:
        print("❌ FAILED: Real VEO generation test failed")
        print("   Check the error messages above for troubleshooting")
        return 1


if __name__ == "__main__":
    sys.exit(main())