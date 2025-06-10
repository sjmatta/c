#!/usr/bin/env python3
"""
OpenUI API client that handles Server-Sent Events streaming
"""

import requests
import json
import time
# import sseclient  # Using requests.iter_lines instead


class OpenUIClient:
    def __init__(self, base_url="http://localhost:7878", cookie_file="openui_cookies.json"):
        self.base_url = base_url
        self.cookies = self._load_cookies(cookie_file)
        
    def _load_cookies(self, cookie_file):
        """Load cookies from file"""
        try:
            with open(cookie_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Cookie file {cookie_file} not found. Run get_openui_cookie.py first.")
            return {}
    
    def create_component(self, prompt, model="gpt-3.5-turbo", max_tokens=2000):
        """
        Create a component using OpenUI's chat completions endpoint
        """
        url = f"{self.base_url}/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "User-Agent": "OpenUI-Integration/1.0"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "stream": True
        }
        
        try:
            print(f"Sending request to {url}")
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                cookies=self.cookies,
                stream=True,
                timeout=60
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
                return None
            
            # Handle SSE stream
            full_response = ""
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data == "[DONE]":
                            break
                        try:
                            json_data = json.loads(data)
                            if "choices" in json_data and len(json_data["choices"]) > 0:
                                delta = json_data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    full_response += content
                                    print(content, end="", flush=True)
                        except json.JSONDecodeError:
                            print(f"Could not parse JSON: {data}")
                            continue
            
            print("\n\nFull response received:")
            return full_response
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None


def test_openui_client():
    """Test the OpenUI client"""
    client = OpenUIClient()
    
    prompt = "Create a simple React button component with a blue background and white text that says 'Click me!'"
    
    print(f"Testing component creation with prompt: {prompt}")
    print("-" * 50)
    
    result = client.create_component(prompt)
    
    if result:
        print(f"\n✅ Success! Generated component:\n{result}")
        return True
    else:
        print("\n❌ Failed to generate component")
        return False


if __name__ == "__main__":
    success = test_openui_client()
    if not success:
        print("\nTrying simpler approach...")
        # Fallback test
        import subprocess
        try:
            result = subprocess.run([
                "curl", "-s", "--max-time", "10",
                "http://localhost:7878/v1/chat/completions",
                "-H", "Content-Type: application/json",
                "-H", "Cookie: session=eyJzZXNzaW9uX2lkIjogImM0YTk0NTZmLTBiNWEtNDZmNC05ZWYxLTUwZTc2NDE0ZDhiOCIsICJ1c2VyX2lkIjogIjIwM2ExYTNjLWE2OWYtNDc2Yi05OTdiLWNmZjhiZjcyZTM3NiJ9.aEeF1A.7__3juIeJkrrea_TQQ2gZyhvWFo",
                "-d", '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"hello"}],"max_tokens":100,"stream":true}'
            ], capture_output=True, text=True, timeout=15)
            
            print(f"Curl exit code: {result.returncode}")
            print(f"Curl stdout: {result.stdout[:500]}")
            print(f"Curl stderr: {result.stderr[:500]}")
            
        except subprocess.TimeoutExpired:
            print("Curl command timed out - this might be normal for streaming responses")