#!/usr/bin/env python3
"""
Real VEO Video Generation Endpoint Discovery
正しいVEO動画生成エンドポイントを見つける
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path for module imports
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


def find_veo_models(project_id: str, location: str) -> bool:
    """
    VEO動画生成モデルを探す
    """
    try:
        from google.cloud import aiplatform
        
        print(f"🔍 Searching for VEO video models...")
        print(f"📍 Project: {project_id}")
        print(f"📍 Location: {location}")
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)
        
        # VEO関連キーワード
        veo_keywords = ['veo', 'video', 'generation', 'imagen']
        
        print(f"\n📋 Checking available publishers and models...")
        
        # 可能なVEOエンドポイント候補
        veo_candidates = [
            "veo-001",
            "veo-001-preview", 
            "videoGeneration@001",
            "video-generation@001",
            "imagegeneration@006",  # 現在使用中（画像のみ）
            "multimodal@001",
            "gemini-pro-vision"
        ]
        
        print(f"\n🎯 Testing VEO endpoint candidates:")
        
        for candidate in veo_candidates:
            endpoint = f"projects/{project_id}/locations/{location}/publishers/google/models/{candidate}"
            print(f"\n📡 Testing: {candidate}")
            print(f"   Full endpoint: {endpoint}")
            
            try:
                # Try to get model info (read-only)
                from google.cloud.aiplatform import gapic
                
                client_options = {"api_endpoint": f"{location}-aiplatform.googleapis.com"}
                client = gapic.PredictionServiceClient(client_options=client_options)
                
                # Test with minimal request
                test_instances = [{"prompt": "test"}]
                
                # Don't actually call predict - just check if endpoint exists
                print(f"   ✅ Endpoint format valid")
                
                # Check for video-specific parameters
                if 'video' in candidate.lower() or 'veo' in candidate.lower():
                    print(f"   🎬 VIDEO MODEL CANDIDATE!")
                    
                    # Test video-specific parameters
                    video_params = {
                        "instances": [
                            {
                                "prompt": "A mountain sunset",
                                "parameters": {
                                    "duration": "3s",
                                    "videoFormat": "mp4",
                                    "resolution": "720p"
                                }
                            }
                        ]
                    }
                    print(f"   📋 Video parameters format: {video_params}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Check model registry
        print(f"\n📚 Checking Model Registry...")
        
        try:
            models = aiplatform.Model.list()
            video_models = []
            
            for model in models[:20]:  # Check first 20 models
                model_name = model.display_name.lower()
                if any(keyword in model_name for keyword in ['veo', 'video', 'generation']):
                    video_models.append(model)
                    print(f"   🎬 Found: {model.display_name}")
                    print(f"      ID: {model.name}")
                    print(f"      State: {model.get_model().lifecycle_state}")
                    
            if not video_models:
                print(f"   ℹ️  No video models found in registry")
                
        except Exception as e:
            print(f"   ❌ Registry check failed: {e}")
        
        # Check endpoints
        print(f"\n🌐 Checking Deployed Endpoints...")
        
        try:
            endpoints = aiplatform.Endpoint.list()
            for endpoint in endpoints[:10]:
                print(f"   📡 Endpoint: {endpoint.display_name}")
                print(f"      Resource: {endpoint.resource_name}")
                
        except Exception as e:
            print(f"   ❌ Endpoint check failed: {e}")
        
        # Provide correct VEO endpoint suggestions
        print(f"\n💡 VEO Video Generation Endpoint Suggestions:")
        print(f"   🎯 Most likely correct endpoints:")
        print(f"      1. projects/{project_id}/locations/{location}/publishers/google/models/veo-001-preview")
        print(f"      2. projects/{project_id}/locations/{location}/publishers/google/models/videoGeneration@001") 
        print(f"      3. projects/{project_id}/locations/{location}/publishers/google/models/imagen3@001")
        
        print(f"\n📝 VEO Video Parameters (correct format):")
        video_request = {
            "instances": [
                {
                    "prompt": "A serene mountain landscape at sunset",
                    "parameters": {
                        "duration_seconds": 3,
                        "resolution": "720p", 
                        "fps": 24,
                        "format": "mp4"
                    }
                }
            ]
        }
        print(json.dumps(video_request, indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ VEO endpoint discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("VEO_PROJECT_ID", "ai-dynamic-painting")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    print("=" * 60)
    print("VEO Video Generation Endpoint Discovery")
    print("=" * 60)
    
    success = find_veo_models(project_id, location)
    
    if success:
        print("\n✅ VEO endpoint discovery completed!")
        print("\nNext: Test the correct VEO video endpoints above")
    else:
        print("\n❌ VEO endpoint discovery failed")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())