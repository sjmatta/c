#!/usr/bin/env python3
"""
Test script to verify we can access OpenUI's /v1/chat/completions endpoint
"""

import requests
import json

def test_openui_api():
    """Test OpenUI API access with the retrieved cookie"""
    
    # Load cookies
    try:
        with open('openui_cookies.json', 'r') as f:
            cookies = json.load(f)
        print(f"Loaded cookies: {cookies}")
    except FileNotFoundError:
        print("No cookies file found. Run get_openui_cookie.py first.")
        return False
    
    # Test API endpoint
    url = "http://localhost:7878/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "OpenUI-Integration/1.0"
    }
    
    # Simple test payload
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Create a simple button component in React"}
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    try:
        print(f"Testing POST to {url}")
        response = requests.post(
            url, 
            json=payload, 
            headers=headers,
            cookies=cookies,
            timeout=30,
            stream=True  # Handle streaming response
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ API call successful!")
            print("Streaming response data:")
            
            # Read streaming response
            full_response = ""
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    print(f"  {line}")
                    full_response += line + "\n"
                    # Stop after getting some data to avoid infinite stream
                    if len(full_response) > 1000:
                        break
            
            return True
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_openui_api()
    if success:
        print("\n🎉 OpenUI API is accessible!")
    else:
        print("\n💥 OpenUI API test failed!")