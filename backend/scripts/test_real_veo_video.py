#!/usr/bin/env python3
"""
Real VEO Video Generation Test - Correct Endpoint
正しいVEOエンドポイントで実際の動画生成テスト
"""

import os
import sys
import json
import time
from pathlib import Path

# Add parent directory to path for module imports
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Environment variables loaded from: {env_path}")
except ImportError:
    print("ℹ️  python-dotenv not installed, skipping .env file loading")


def test_real_veo_video_generation(project_id: str, location: str) -> bool:
    """
    正しいVEOエンドポイントで実際の動画生成テスト
    """
    try:
        from google.cloud import aiplatform
        from google.cloud.aiplatform import gapic
        
        print(f"\n🎬 REAL VEO VIDEO GENERATION TEST")
        print(f"📍 Project: {project_id}")
        print(f"📍 Location: {location}")
        print(f"💰 Estimated Cost: $0.50-$2.00 per video")
        
        # Warning confirmation
        print(f"\n⚠️  WARNING: This will make REAL VEO video generation calls!")
        print(f"   Continue? (y/N): ", end="")
        
        confirmation = os.getenv('VEO_TEST_CONFIRM', 'n').lower()
        print(confirmation)
        
        if confirmation != 'y':
            print("❌ Test cancelled")
            return False
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)
        
        # VEO video endpoints to test (in priority order)
        veo_endpoints = [
            "veo-001-preview",
            "veo-001", 
            "videoGeneration@001"
        ]
        
        for endpoint_model in veo_endpoints:
            print(f"\n🎯 Testing VEO endpoint: {endpoint_model}")
            
            endpoint_name = f"projects/{project_id}/locations/{location}/publishers/google/models/{endpoint_model}"
            print(f"   Full endpoint: {endpoint_name}")
            
            # Create VEO video request
            video_instances = [
                {
                    "prompt": "A peaceful mountain landscape at golden hour with gentle clouds moving across the sky",
                    "parameters": {
                        "duration_seconds": 3,  # Minimum duration
                        "resolution": "720p",   # Lower resolution for cost
                        "fps": 24,
                        "format": "mp4"
                    }
                }
            ]
            
            try:
                # Get prediction client
                client_options = {"api_endpoint": f"{location}-aiplatform.googleapis.com"}
                client = gapic.PredictionServiceClient(client_options=client_options)
                
                print(f"   🔄 Sending VEO video generation request...")
                print(f"   📝 Prompt: {video_instances[0]['prompt']}")
                print(f"   ⏱️  Duration: 3 seconds")
                print(f"   📺 Resolution: 720p")
                
                # Make VEO video prediction
                response = client.predict(
                    endpoint=endpoint_name,
                    instances=video_instances,
                    parameters={}
                )
                
                print(f"   ✅ VEO video request successful!")
                print(f"   📊 Received {len(response.predictions)} video predictions")
                
                # Process video response
                for i, prediction in enumerate(response.predictions):
                    print(f"\n   🎥 Video Prediction {i+1}:")
                    
                    try:
                        prediction_dict = dict(prediction)
                        print(f"      Keys: {list(prediction_dict.keys())}")
                        
                        # Check MIME type
                        mime_type = prediction_dict.get('mimeType', 'unknown')
                        print(f"      MIME Type: {mime_type}")
                        
                        if mime_type.startswith('video/'):
                            print(f"      🎉 SUCCESS: Real video content detected!")
                            
                            # Save video
                            if 'bytesBase64Encoded' in prediction_dict:
                                video_data_b64 = prediction_dict['bytesBase64Encoded']
                                
                                import base64
                                video_data = base64.b64decode(video_data_b64)
                                
                                output_dir = Path(__file__).parent.parent / "generated_videos"
                                output_dir.mkdir(exist_ok=True)
                                
                                # Use correct video extension
                                video_ext = 'mp4' if 'mp4' in mime_type else 'webm'
                                output_file = output_dir / f"veo_video_{int(time.time())}_{i}.{video_ext}"
                                
                                with open(output_file, 'wb') as f:
                                    f.write(video_data)
                                
                                print(f"      ✅ Video saved: {output_file}")
                                print(f"      📊 Size: {len(video_data)} bytes")
                                print(f"      🎬 MIME: {mime_type}")
                                
                                # Verify it's actually a video
                                file_type_check = os.popen(f'file "{output_file}"').read()
                                print(f"      🔍 File verification: {file_type_check.strip()}")
                                
                        elif mime_type.startswith('image/'):
                            print(f"      ⚠️  WARNING: Still receiving images, not videos")
                            print(f"      📸 Image MIME: {mime_type}")
                            
                        else:
                            print(f"      ❓ Unknown content type: {mime_type}")
                            print(f"      📄 Raw prediction: {str(prediction)[:200]}...")
                            
                    except Exception as pred_error:
                        print(f"      ❌ Prediction processing error: {pred_error}")
                
                # If we got this far with videos, we found the right endpoint
                if any('video/' in dict(pred).get('mimeType', '') for pred in response.predictions):
                    print(f"\n🎉 SUCCESS: Found working VEO video endpoint!")
                    print(f"   🎯 Endpoint: {endpoint_model}")
                    return True
                    
            except Exception as api_error:
                error_str = str(api_error)
                print(f"   ❌ API Error: {api_error}")
                
                if "404" in error_str or "not found" in error_str.lower():
                    print(f"   ℹ️  Endpoint {endpoint_model} not available, trying next...")
                    continue
                elif "403" in error_str or "permission" in error_str.lower():
                    print(f"   ⚠️  Permission denied - VEO may not be enabled")
                elif "quota" in error_str.lower():
                    print(f"   ⚠️  Quota exceeded")
                else:
                    print(f"   ❓ Unknown error type")
        
        print(f"\n❌ No working VEO video endpoints found")
        return False
        
    except Exception as e:
        print(f"❌ VEO video test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("VEO_PROJECT_ID", "ai-dynamic-painting")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    print("=" * 60)
    print("Real VEO Video Generation Test")
    print("🎬 Testing correct VEO video endpoints")
    print("=" * 60)
    
    # Check prerequisites
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path or not Path(credentials_path).exists():
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        return 1
    
    success = test_real_veo_video_generation(project_id, location)
    
    print("\n" + "=" * 60)
    print("VEO Video Generation Test Summary")
    print("=" * 60)
    
    if success:
        print("🎉 SUCCESS: Real VEO video generation working!")
        print("\nCheck generated_videos/ for actual video files")
    else:
        print("❌ FAILED: No working VEO video endpoints")
        print("   VEO video generation may not be available in this region/project")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())