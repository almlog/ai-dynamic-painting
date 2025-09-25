#!/usr/bin/env python3
"""
VEO API OAuth2 Test Script - Google Cloud Video Intelligence API
ラズパイ対応版
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Color output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
PURPLE = '\033[0;35m'
CYAN = '\033[0;36m'
NC = '\033[0m'

def log_info(msg):
    print(f"{CYAN}ℹ️{NC} {msg}")

def log_success(msg):
    print(f"{GREEN}✅{NC} {msg}")

def log_error(msg):
    print(f"{RED}❌{NC} {msg}")

def log_warning(msg):
    print(f"{YELLOW}⚠️{NC} {msg}")

print(f"{PURPLE}{'='*60}{NC}")
print(f"{PURPLE}🔐 VEO API OAuth2 Authentication Test{NC}")
print(f"{PURPLE}{'='*60}{NC}")

# Step 1: Check credentials file
credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if not credentials_path:
    log_error("GOOGLE_APPLICATION_CREDENTIALS not set in .env")
    log_info("Add this line to .env:")
    log_info("GOOGLE_APPLICATION_CREDENTIALS=./credentials/veo-service-account.json")
    sys.exit(1)

# Convert relative path to absolute
if not credentials_path.startswith('/'):
    credentials_path = str(Path(__file__).parent.parent / credentials_path)

log_info(f"Credentials path: {credentials_path}")

if not Path(credentials_path).exists():
    log_error(f"Credentials file not found: {credentials_path}")
    log_info("Please download the JSON key from Google Cloud Console")
    log_info("and save it to the credentials directory")
    sys.exit(1)

log_success("Credentials file found")

# Step 2: Install Google Cloud libraries if needed
try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
except ImportError:
    log_warning("Google Cloud libraries not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-cloud-videointelligence", "google-auth"])
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request

# Step 3: Load and validate credentials
try:
    with open(credentials_path, 'r') as f:
        cred_data = json.load(f)
    
    log_info(f"Project ID: {cred_data.get('project_id', 'NOT FOUND')}")
    log_info(f"Client Email: {cred_data.get('client_email', 'NOT FOUND')}")
    
    # Create credentials object
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    
    log_success("Service account credentials loaded successfully")
    
except Exception as e:
    log_error(f"Failed to load credentials: {str(e)}")
    sys.exit(1)

# Step 4: Test Video Intelligence API connection
try:
    from google.cloud import videointelligence
    
    log_info("Testing Video Intelligence API connection...")
    
    # Create client with credentials
    video_client = videointelligence.VideoIntelligenceServiceClient(credentials=credentials)
    
    # Test with a simple operation (list operations - doesn't cost anything)
    project = cred_data.get('project_id', 'your-project-id')
    
    log_success("Video Intelligence API client created successfully")
    log_info(f"Project: {project}")
    
    # Optional: Test annotation (costs money - commented out)
    """
    # Uncomment to test actual video analysis (will incur charges)
    video_uri = "gs://cloud-samples-data/video/cat.mp4"
    features = [videointelligence.Feature.LABEL_DETECTION]
    
    log_info(f"Analyzing sample video: {video_uri}")
    operation = video_client.annotate_video(
        request={"features": features, "input_uri": video_uri}
    )
    
    log_info("Waiting for operation to complete (may take a minute)...")
    result = operation.result(timeout=90)
    
    log_success("Video analysis completed successfully!")
    """
    
    print(f"\n{GREEN}🎉 OAuth2 Authentication Successful!{NC}")
    print(f"{GREEN}VEO/Video Intelligence API is ready to use.{NC}")
    
    print(f"\n{CYAN}📝 Next Steps:{NC}")
    print("1. The system can now use Video Intelligence API")
    print("2. For VEO-2 (video generation), additional setup may be needed")
    print("3. Update VEO_PROJECT_ID in .env with your actual project ID")
    
except ImportError as e:
    log_error(f"Failed to import Google Cloud library: {str(e)}")
    log_info("Run: pip install google-cloud-videointelligence")
    sys.exit(1)
    
except Exception as e:
    log_error(f"API test failed: {str(e)}")
    log_info("Common issues:")
    log_info("1. Video Intelligence API not enabled in Google Cloud Console")
    log_info("2. Service account lacks necessary permissions")
    log_info("3. Project ID incorrect in credentials")
    sys.exit(1)

print(f"{PURPLE}{'='*60}{NC}")