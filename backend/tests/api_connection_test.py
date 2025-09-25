#!/usr/bin/env python3
"""
API Connection Test Script - Phase 3 実動作確認
各APIの接続・認証・基本機能をテスト
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded .env from: {env_path}")
else:
    print(f"❌ .env file not found at: {env_path}")
    sys.exit(1)

# Color output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
PURPLE = '\033[0;35m'
CYAN = '\033[0;36m'
NC = '\033[0m'

def log_test(name):
    print(f"\n{BLUE}[TEST]{NC} {name}")

def log_success(msg):
    print(f"{GREEN}✅{NC} {msg}")

def log_error(msg):
    print(f"{RED}❌{NC} {msg}")

def log_warning(msg):
    print(f"{YELLOW}⚠️{NC} {msg}")

def log_info(msg):
    print(f"{CYAN}ℹ️{NC} {msg}")

# ============================================================================
# 1. Weather API Test (OpenWeatherMap)
# ============================================================================

def test_weather_api():
    log_test("Weather API Connection Test (OpenWeatherMap)")
    
    api_key = os.getenv('WEATHER_API_KEY', '')
    if not api_key:
        log_error("WEATHER_API_KEY not found in .env")
        return False
    
    log_info(f"API Key: ****{api_key[-4:]} (last 4 chars)")
    
    # Test current weather API
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': 'Tokyo,JP',
        'appid': api_key,
        'units': 'metric'
    }
    
    try:
        log_info("Fetching current weather for Tokyo...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            log_success(f"Weather API Connected Successfully!")
            log_info(f"City: {data.get('name', 'N/A')}")
            log_info(f"Temperature: {data.get('main', {}).get('temp', 'N/A')}°C")
            log_info(f"Weather: {data.get('weather', [{}])[0].get('description', 'N/A')}")
            log_info(f"Humidity: {data.get('main', {}).get('humidity', 'N/A')}%")
            return True
        elif response.status_code == 401:
            log_error(f"Authentication Failed (401): Invalid API Key")
            log_info("Please check your WEATHER_API_KEY in .env")
            return False
        else:
            log_error(f"API Error: {response.status_code}")
            log_info(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        log_error("Request Timeout (10s)")
        return False
    except Exception as e:
        log_error(f"Connection Error: {str(e)}")
        return False

# ============================================================================
# 2. Gemini API Test (Google Gemini)
# ============================================================================

def test_gemini_api():
    log_test("Gemini API Connection Test (Google Gemini)")
    
    api_key = os.getenv('GEMINI_API_KEY', '')
    if not api_key:
        log_error("GEMINI_API_KEY not found in .env")
        return False
    
    log_info(f"API Key: ****{api_key[-4:]} (last 4 chars)")
    
    # Gemini API endpoint - Updated to use gemini-1.5-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {
        'Content-Type': 'application/json',
    }
    params = {
        'key': api_key
    }
    
    # Simple test prompt
    data = {
        'contents': [{
            'parts': [{
                'text': 'Hello, please respond with "API Test Successful" if you receive this message.'
            }]
        }]
    }
    
    try:
        log_info("Testing Gemini API with simple prompt...")
        response = requests.post(url, headers=headers, params=params, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0].get('content', {}).get('parts', [{}])[0].get('text', '')
                log_success("Gemini API Connected Successfully!")
                log_info(f"Response: {text[:100]}...")
                return True
            else:
                log_warning("Unexpected response format")
                log_info(f"Response: {json.dumps(result, indent=2)[:500]}")
                return False
        elif response.status_code == 400:
            log_error(f"Bad Request (400): Invalid API Key or Request")
            log_info("Please check your GEMINI_API_KEY in .env")
            log_info(f"Response: {response.text[:200]}")
            return False
        elif response.status_code == 403:
            log_error(f"Forbidden (403): API Key may lack permissions")
            log_info("Please enable Gemini API in Google Cloud Console")
            return False
        else:
            log_error(f"API Error: {response.status_code}")
            log_info(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        log_error("Request Timeout (15s)")
        return False
    except Exception as e:
        log_error(f"Connection Error: {str(e)}")
        return False

# ============================================================================
# 3. VEO API Test (Google Video Intelligence / VEO)
# ============================================================================

def test_veo_api():
    log_test("VEO API Connection Test (Google Video Intelligence)")
    
    api_key = os.getenv('VEO_API_KEY', '')
    if not api_key:
        log_error("VEO_API_KEY not found in .env")
        return False
    
    log_info(f"API Key: ****{api_key[-4:]} (last 4 chars)")
    
    # Video Intelligence API endpoint (VEO is part of this)
    # Note: VEO-2 for generation might have different endpoint
    url = "https://videointelligence.googleapis.com/v1/videos:annotate"
    headers = {
        'Content-Type': 'application/json',
    }
    params = {
        'key': api_key
    }
    
    # Test with minimal request
    data = {
        'inputUri': 'gs://cloud-samples-data/video/cat.mp4',
        'features': ['LABEL_DETECTION']
    }
    
    try:
        log_info("Testing Video Intelligence API (VEO base)...")
        response = requests.post(url, headers=headers, params=params, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            log_success("VEO/Video Intelligence API Connected!")
            log_warning("Note: This tests Video Intelligence API access")
            log_warning("VEO-2 generation API may require different permissions")
            log_info("To enable VEO-2 video generation:")
            log_info("1. Enable 'Video Intelligence API' in Google Cloud Console")
            log_info("2. Enable 'Vertex AI' APIs if using VEO-2")
            log_info("3. Set up proper IAM permissions for video generation")
            return True
        elif response.status_code == 403:
            log_error(f"Permission Denied (403)")
            log_warning("VEO API requires specific permissions:")
            log_info("1. Go to Google Cloud Console")
            log_info("2. Enable 'Video Intelligence API'")
            log_info("3. Enable 'Vertex AI' APIs for VEO-2")
            log_info("4. Check API key restrictions")
            return False
        elif response.status_code == 400:
            # This might actually be expected if the API is enabled but with wrong parameters
            log_warning("Bad Request (400) - API may be enabled but request format incorrect")
            log_info("This could mean the API key is valid but needs proper setup")
            log_info(f"Response: {response.text[:200]}")
            return False
        else:
            log_error(f"API Error: {response.status_code}")
            log_info(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        log_error("Request Timeout (15s)")
        return False
    except Exception as e:
        log_error(f"Connection Error: {str(e)}")
        return False

# ============================================================================
# Main Test Runner
# ============================================================================

def main():
    print(f"{PURPLE}{'='*60}{NC}")
    print(f"{PURPLE}🔑 AI動的絵画システム - API Connection Tests{NC}")
    print(f"{PURPLE}{'='*60}{NC}")
    
    results = {}
    
    # Run all tests
    print(f"\n{CYAN}Starting API connection tests...{NC}")
    
    # Test Weather API
    results['weather'] = test_weather_api()
    time.sleep(1)  # Rate limiting
    
    # Test Gemini API
    results['gemini'] = test_gemini_api()
    time.sleep(1)  # Rate limiting
    
    # Test VEO API
    results['veo'] = test_veo_api()
    
    # Summary
    print(f"\n{PURPLE}{'='*60}{NC}")
    print(f"{PURPLE}📊 Test Results Summary{NC}")
    print(f"{PURPLE}{'='*60}{NC}")
    
    for api, success in results.items():
        status = f"{GREEN}✅ PASS{NC}" if success else f"{RED}❌ FAIL{NC}"
        print(f"{api.upper():15} : {status}")
    
    # Overall result
    all_passed = all(results.values())
    print(f"\n{PURPLE}{'='*60}{NC}")
    
    if all_passed:
        print(f"{GREEN}🎉 All API connections successful!{NC}")
        print(f"{GREEN}Phase 3 can proceed with full functionality.{NC}")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"{YELLOW}⚠️ Some APIs need attention: {', '.join(failed)}{NC}")
        print(f"{YELLOW}Please check the error messages above for each failed API.{NC}")
        
        if not results['veo']:
            print(f"\n{CYAN}📝 VEO API Setup Instructions:{NC}")
            print("1. Go to: https://console.cloud.google.com/")
            print("2. Select your project or create new one")
            print("3. Enable these APIs:")
            print("   - Video Intelligence API")
            print("   - Vertex AI API (for VEO-2)")
            print("4. Create API key with proper restrictions")
            print("5. Update VEO_API_KEY in .env file")
    
    print(f"{PURPLE}{'='*60}{NC}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())