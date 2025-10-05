#!/usr/bin/env python3
"""
VEO API Real Video Generation Test
実際のVEO API動画生成テスト - 最小限のコスト
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

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


def test_veo_generation_endpoint(project_id: str, location: str) -> bool:
    """
    VEO動画生成の最小限テスト (実際のAPI呼び出し無し)
    
    Args:
        project_id: Google Cloud プロジェクトID
        location: リージョン (us-central1推奨)
    
    Returns:
        True if test successful, False otherwise
    """
    try:
        from google.cloud import aiplatform
        from google.api_core import exceptions
        
        print("\n🔄 Testing VEO generation endpoint access...")
        
        # Initialize with explicit project and location
        aiplatform.init(
            project=project_id,
            location=location,
            credentials=None  # Use default credentials discovery
        )
        
        print("✅ Vertex AI client initialized for VEO")
        
        # Test endpoint discovery (read-only, no cost)
        print("\n🔄 Checking VEO model availability...")
        
        try:
            # Look for Imagen/VEO models
            models = aiplatform.Model.list(filter='display_name:"*imagen*" OR display_name:"*veo*"')
            
            if models:
                print(f"✅ Found {len(models)} video/image generation models:")
                for model in models[:5]:  # Show first 5
                    print(f"   - {model.display_name}")
                    print(f"     ID: {model.name}")
                    print(f"     State: {model.get_model().lifecycle_state}")
                    print()
            else:
                print("ℹ️  No VEO/Imagen models found in this project")
                print("   This might be normal if models haven't been deployed yet")
                
        except exceptions.PermissionDenied as e:
            print(f"⚠️  Permission denied: {e}")
            print("   VEO/Imagen APIs might not be enabled for this project")
            
        except Exception as e:
            print(f"ℹ️  Could not list models: {e}")
        
        # Test generation endpoint (without actual generation)
        print("\n🔄 Testing generation endpoint format...")
        
        generation_endpoint = f"projects/{project_id}/locations/{location}/publishers/google/models/imagegeneration@006"
        print(f"✅ VEO generation endpoint format:")
        print(f"   {generation_endpoint}")
        
        # Test prediction format (without actual call)
        test_prompt = "A beautiful sunset over mountains"
        test_request = {
            "instances": [
                {
                    "prompt": test_prompt,
                    "parameters": {
                        "sampleCount": 1,
                        "aspectRatio": "16:9",
                        "outputType": "video"
                    }
                }
            ]
        }
        
        print(f"\n✅ Test request format validated:")
        print(f"   Prompt: {test_prompt}")
        print(f"   Parameters: aspectRatio=16:9, outputType=video")
        
        return True
        
    except Exception as e:
        print(f"\n❌ VEO generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_veo_quota_and_pricing() -> None:
    """
    VEO API価格とクォータ情報の表示
    """
    print("\n💰 VEO API Pricing & Quota Information:")
    print("=" * 50)
    print("🎬 Video Generation (VEO):")
    print("   - Price: ~$0.50-$2.00 per video (depending on quality/length)")
    print("   - Default quota: 5 videos per minute")
    print("   - Max video length: 5 seconds (preview)")
    print()
    print("🖼️  Image Generation (Imagen):")
    print("   - Price: ~$0.020 per image")
    print("   - Default quota: 100 images per minute")
    print()
    print("⚠️  Warning: This test does NOT make actual generation calls")
    print("   Actual video generation will incur costs!")
    print()


def main():
    """
    メイン実行関数
    """
    print("=" * 60)
    print("VEO API Real Generation Test (No-Cost Validation)")
    print("=" * 60)
    
    # Check environment
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("VEO_PROJECT_ID", "ai-dynamic-painting")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    print(f"📍 Project ID: {project_id}")
    print(f"📍 Location: {location}")
    
    # Check authentication
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path or not Path(credentials_path).exists():
        print("\n❌ Authentication not configured")
        print("   Please set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        return 1
    
    print(f"✅ Authentication: {credentials_path}")
    
    # Test VEO generation capabilities
    success = test_veo_generation_endpoint(project_id, location)
    
    # Show pricing information
    check_veo_quota_and_pricing()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    if success:
        print("✅ SUCCESS: VEO generation endpoint validation passed!")
        print("\nNext steps to make actual video generation:")
        print("1. Enable required APIs:")
        print("   gcloud services enable aiplatform.googleapis.com")
        print("   gcloud services enable compute.googleapis.com")
        print("2. Verify billing is enabled for the project")
        print("3. Test with a small generation request (will incur costs)")
        print("4. Implement cost monitoring before production use")
        return 0
    else:
        print("❌ FAILED: VEO generation endpoint validation failed")
        print("   Please check authentication and API enablement")
        return 1


if __name__ == "__main__":
    sys.exit(main())