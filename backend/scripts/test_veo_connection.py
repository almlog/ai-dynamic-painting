#!/usr/bin/env python3
"""
VEO API Connection Test Script
技術的接続確認とコスト無料の最小限テスト

This script verifies that we can successfully authenticate with Google Cloud
and access the Vertex AI platform without incurring any costs.
"""

import os
import sys
import json
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

def check_environment() -> Dict[str, Any]:
    """
    環境変数とGoogle Cloud設定を確認
    
    Returns:
        Dict containing environment check results
    """
    results = {
        "google_application_credentials": False,
        "gcloud_config": False,
        "project_id": None,
        "location": None,
        "errors": []
    }
    
    # Check for service account key
    if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
        creds_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
        if Path(creds_path).exists():
            results["google_application_credentials"] = True
            print(f"✅ Service account key found: {creds_path}")
        else:
            results["errors"].append(f"Service account key file not found: {creds_path}")
            print(f"❌ Service account key file not found: {creds_path}")
    else:
        print("ℹ️  GOOGLE_APPLICATION_CREDENTIALS not set (will try ADC)")
    
    # Check for gcloud config
    gcloud_config_path = Path.home() / ".config" / "gcloud" / "application_default_credentials.json"
    if gcloud_config_path.exists():
        results["gcloud_config"] = True
        print(f"✅ gcloud ADC found: {gcloud_config_path}")
    else:
        print("ℹ️  gcloud ADC not found (run 'gcloud auth application-default login' if needed)")
    
    # Get project and location from env or use defaults
    results["project_id"] = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("VEO_PROJECT_ID", "ai-dynamic-painting")
    results["location"] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    print(f"📍 Project ID: {results['project_id']}")
    print(f"📍 Location: {results['location']}")
    
    return results

def test_basic_import() -> bool:
    """
    Google Cloud AIライブラリのインポート確認
    
    Returns:
        True if import successful, False otherwise
    """
    try:
        import google.cloud.aiplatform as aiplatform
        print("✅ google-cloud-aiplatform successfully imported")
        print(f"   Version: {aiplatform.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import google-cloud-aiplatform: {e}")
        print("   Run: pip install google-cloud-aiplatform>=1.38.0")
        return False

def verify_veo_connection(project_id: str, location: str) -> bool:
    """
    VEO API接続の最小限確認（コスト無料）
    
    Args:
        project_id: Google Cloud プロジェクトID
        location: リージョン (us-central1推奨)
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        from google.cloud import aiplatform
        from google.api_core import exceptions
        
        print("\n🔄 Initializing Vertex AI client...")
        
        # Initialize with explicit project and location
        aiplatform.init(
            project=project_id,
            location=location,
            credentials=None  # Use default credentials discovery
        )
        
        print("✅ Vertex AI client initialized successfully")
        
        # Try to list models (read-only, no cost)
        print("\n🔄 Attempting to list available models...")
        
        try:
            # Simple model listing test (no complex filters)
            models = aiplatform.Model.list()
            
            print(f"✅ Successfully connected! Found {len(models)} total models in project")
            
            # Look for VEO/Imagen models specifically
            veo_models = []
            for model in models[:10]:  # Check first 10 models
                if any(keyword in model.display_name.lower() for keyword in ['imagen', 'veo', 'video', 'image']):
                    veo_models.append(model)
            
            if veo_models:
                print(f"✅ Found {len(veo_models)} image/video generation models:")
                for model in veo_models:
                    print(f"   - {model.display_name} (ID: {model.name})")
            else:
                print("ℹ️  No VEO/Imagen models found (this is normal for new projects)")
                
        except exceptions.PermissionDenied as e:
            print(f"⚠️  Permission denied when listing models: {e}")
            print("   This is expected if VEO/Imagen APIs are not yet enabled")
            
        except exceptions.NotFound as e:
            print(f"ℹ️  Resource not found: {e}")
            print("   This is normal for projects without deployed models")
            
        # Test endpoint listing (another read-only operation)
        print("\n🔄 Checking for available endpoints...")
        
        try:
            endpoints = aiplatform.Endpoint.list(limit=5)
            if endpoints:
                print(f"✅ Found {len(endpoints)} endpoints")
            else:
                print("ℹ️  No endpoints found (this is normal)")
                
        except Exception as e:
            print(f"ℹ️  Could not list endpoints: {e}")
        
        print("\n✅ Connection to Vertex AI successful!")
        print("   Authentication is working correctly")
        return True
        
    except Exception as e:
        if "DefaultCredentialsError" in str(type(e)):
            print(f"\n❌ Authentication error: {e}")
            print("\n📝 To fix this, choose one of:")
            print("   1. Set up service account:")
            print("      export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json")
            print("   2. Use gcloud auth:")
            print("      gcloud auth application-default login")
            return False
        else:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return False

def check_veo_api_availability(project_id: str) -> Dict[str, bool]:
    """
    VEO API関連のAPIが有効化されているか確認
    
    Args:
        project_id: Google Cloud プロジェクトID
        
    Returns:
        Dict with API availability status
    """
    required_apis = {
        "aiplatform.googleapis.com": "Vertex AI API",
        "compute.googleapis.com": "Compute Engine API (for Vertex AI)",
        "storage.googleapis.com": "Cloud Storage API (for model artifacts)",
    }
    
    print("\n📋 Checking required APIs...")
    
    try:
        from google.cloud import service_usage_v1
        
        client = service_usage_v1.ServiceUsageClient()
        parent = f"projects/{project_id}"
        
        api_status = {}
        
        for api_name, description in required_apis.items():
            service_name = f"{parent}/services/{api_name}"
            try:
                service = client.get_service(name=service_name)
                is_enabled = service.state == service_usage_v1.State.ENABLED
                api_status[api_name] = is_enabled
                
                if is_enabled:
                    print(f"✅ {description} is enabled")
                else:
                    print(f"❌ {description} is NOT enabled")
                    print(f"   Enable with: gcloud services enable {api_name}")
                    
            except Exception as e:
                print(f"⚠️  Could not check {description}: {e}")
                api_status[api_name] = None
                
        return api_status
        
    except ImportError:
        print("ℹ️  google-cloud-service-usage not installed")
        print("   Cannot check API status (this is optional)")
        return {}
    except Exception as e:
        print(f"⚠️  Could not check API status: {e}")
        return {}

def main():
    """
    メイン実行関数
    """
    print("=" * 60)
    print("VEO API Connection Test Script")
    print("=" * 60)
    
    # Step 1: Check environment
    print("\n📦 Step 1: Checking environment...")
    env_results = check_environment()
    
    # Step 2: Test imports
    print("\n📦 Step 2: Testing library imports...")
    import_ok = test_basic_import()
    
    if not import_ok:
        print("\n❌ Cannot proceed without google-cloud-aiplatform library")
        print("   Please install it first: pip install google-cloud-aiplatform>=1.38.0")
        return 1
    
    # Step 3: Check authentication
    if not env_results["google_application_credentials"] and not env_results["gcloud_config"]:
        print("\n⚠️  No authentication method configured")
        print("\n📝 Please set up authentication using one of these methods:")
        print("\n   Option 1: Service Account (Recommended for production)")
        print("   1. Create a service account in Google Cloud Console")
        print("   2. Download the JSON key file")
        print("   3. Set environment variable:")
        print("      export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json")
        print("\n   Option 2: Application Default Credentials (For development)")
        print("   1. Install gcloud CLI")
        print("   2. Run: gcloud auth application-default login")
        print("   3. Follow the browser authentication flow")
        return 1
    
    # Step 4: Test connection
    print("\n📦 Step 3: Testing Vertex AI connection...")
    connection_ok = verify_veo_connection(
        env_results["project_id"],
        env_results["location"]
    )
    
    # Step 5: Check API availability (optional)
    if connection_ok:
        check_veo_api_availability(env_results["project_id"])
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    if connection_ok:
        print("✅ SUCCESS: VEO API connection test passed!")
        print("\nNext steps:")
        print("1. Enable required APIs if not already enabled:")
        print("   gcloud services enable aiplatform.googleapis.com")
        print("2. Create a VEO/Imagen model or use pre-trained models")
        print("3. Implement the VEO client wrapper in the application")
        return 0
    else:
        print("❌ FAILED: Could not establish connection to Vertex AI")
        print("\nPlease resolve the authentication issues and try again")
        return 1

if __name__ == "__main__":
    sys.exit(main())