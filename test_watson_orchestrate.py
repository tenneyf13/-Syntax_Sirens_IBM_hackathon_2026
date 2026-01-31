#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Watson Orchestrate integration
This script helps you verify your Watson Orchestrate connection before integrating into the app.

Usage:
1. Create a .env file with your IBM_CLOUD_API_KEY
2. Run: python test_watson_orchestrate.py
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

# Configuration
IBM_CLOUD_API_KEY = os.getenv("IBM_CLOUD_API_KEY")
AGENT_ID = os.getenv("WATSON_ORCHESTRATE_AGENT_ID", "638256ff-9626-4012-bb71-0a111f64ecf9")
HOST_URL = os.getenv("WATSON_ORCHESTRATE_HOST_URL", "https://dl.watson-orchestrate.ibm.com")
INSTANCE_ID = os.getenv("WATSON_ORCHESTRATE_INSTANCE_ID", "20260130-1647-0257-7054-5539941574fb")

# Sample HTML for testing
SAMPLE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Test Page</title>
</head>
<body>
    <img src="image.jpg">
    <div style="color: #777; background-color: #888;">Low contrast text</div>
    <button>Click me</button>
</body>
</html>
"""

def get_iam_token():
    """Get IBM Cloud IAM token using API key"""
    print("🔐 Authenticating with IBM Cloud...")
    
    if not IBM_CLOUD_API_KEY:
        print("❌ ERROR: IBM_CLOUD_API_KEY not found in .env file")
        print("Please create a .env file with your IBM Cloud API key:")
        print("IBM_CLOUD_API_KEY=your_api_key_here")
        sys.exit(1)
    
    try:
        authenticator = IAMAuthenticator(IBM_CLOUD_API_KEY)
        token = authenticator.token_manager.get_token()
        print("✅ Authentication successful!")
        return token
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        sys.exit(1)

def test_watson_orchestrate_connection(token):
    """Test connection to Watson Orchestrate agent"""
    print(f"\n🤖 Testing Watson Orchestrate Agent...")
    print(f"   Agent ID: {AGENT_ID}")
    print(f"   Host URL: {HOST_URL}")
    print(f"   Instance ID: {INSTANCE_ID}")
    
    # Watson Orchestrate API endpoint
    # Note: The exact endpoint may vary - this is a common pattern
    api_url = f"{HOST_URL}/api/v1/instances/{INSTANCE_ID}/agents/{AGENT_ID}/run"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Prepare the request payload
    payload = {
        "input": {
            "html_content": SAMPLE_HTML,
            "task": "Analyze this HTML for WCAG 2.1 Level AA compliance issues"
        }
    }
    
    print(f"\n📤 Sending test request to agent...")
    print(f"   URL: {api_url}")
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Agent responded successfully!")
            result = response.json()
            print("\n📊 Agent Response:")
            print(json.dumps(result, indent=2))
            return True
        elif response.status_code == 401:
            print("❌ Authentication error - check your API key")
            print(f"Response: {response.text}")
        elif response.status_code == 404:
            print("❌ Agent not found - check your Agent ID and Instance ID")
            print(f"Response: {response.text}")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            print(f"Response: {response.text}")
        
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out - agent may be slow to respond")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_alternative_endpoint(token):
    """Try alternative Watson Orchestrate API endpoint"""
    print(f"\n🔄 Trying alternative API endpoint...")
    
    # Alternative endpoint pattern for Watson Orchestrate chat
    api_url = f"{HOST_URL}/api/chat/v1/agents/{AGENT_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "message": f"Analyze this HTML for WCAG compliance:\n\n{SAMPLE_HTML}"
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Alternative endpoint works!")
            result = response.json()
            print("\n📊 Agent Response:")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Alternative endpoint failed: {e}")
        return False

def main():
    print("=" * 60)
    print("Watson Orchestrate Connection Test")
    print("=" * 60)
    
    # Step 1: Get IAM token
    token = get_iam_token()
    
    # Step 2: Test Watson Orchestrate connection
    success = test_watson_orchestrate_connection(token)
    
    # Step 3: If first attempt fails, try alternative endpoint
    if not success:
        success = test_alternative_endpoint(token)
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ SUCCESS! Watson Orchestrate is working correctly.")
        print("\nNext steps:")
        print("1. The agent is responding - you can now integrate it into your app")
        print("2. Check the response format above to understand the output structure")
        print("3. Update backend/watson_orchestrate_service.py with the correct endpoint")
    else:
        print("⚠️  Connection test incomplete")
        print("\nTroubleshooting:")
        print("1. Verify your IBM_CLOUD_API_KEY in .env file")
        print("2. Check that Agent ID is correct: " + AGENT_ID)
        print("3. Ensure your Watson Orchestrate agent is deployed and active")
        print("4. Check Watson Orchestrate documentation for correct API endpoints")
        print("5. You may need to use the Watson Orchestrate web chat SDK instead of REST API")
    print("=" * 60)

if __name__ == "__main__":
    main()