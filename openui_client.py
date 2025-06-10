#!/usr/bin/env python3
"""
OpenUI API client that handles Server-Sent Events streaming
"""

import requests
import json
import time
from ast_validator import ASTValidator
# import sseclient  # Using requests.iter_lines instead


class OpenUIClient:
    def __init__(self, base_url="http://localhost:7878", cookie_file="openui_cookies.json"):
        self.base_url = base_url
        self.cookies = self._load_cookies(cookie_file)
        self.validator = ASTValidator()
        
    def _load_cookies(self, cookie_file):
        """Load cookies from file"""
        try:
            with open(cookie_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Cookie file {cookie_file} not found. Run get_openui_cookie.py first.")
            return {}
    
    def create_component(self, prompt, model="gpt-3.5-turbo", max_tokens=32000):
        """
        Create a component using OpenUI's chat completions endpoint with automatic continuation
        """
        return self.create_component_with_continuation(prompt, model, max_tokens)
    
    def create_component_with_continuation(self, prompt, model="gpt-3.5-turbo", max_tokens=32000, max_retries=3):
        """
        Create a component with automatic continuation for truncated responses
        """
        conversation = [{"role": "user", "content": prompt}]
        accumulated_response = ""
        
        print(f"🎯 Generating component with continuation support (max {max_retries} retries)")
        
        for attempt in range(max_retries + 1):
            print(f"\n📡 Attempt {attempt + 1}/{max_retries + 1}")
            
            # Make the API call
            response_data = self._make_api_call(conversation, model, max_tokens)
            if not response_data:
                print(f"❌ API call failed on attempt {attempt + 1}")
                continue
            
            response_content = response_data["content"]
            finish_reason = response_data.get("finish_reason", "unknown")
            
            # Accumulate the response
            accumulated_response += response_content
            
            # Validate the accumulated response
            validation = self.validator.validate_component(accumulated_response)
            
            print(f"\n🔍 Validation result: {validation['status']}")
            print(f"   Details: {validation['details']}")
            
            if validation["status"] == "COMPLETE":
                print(f"✅ Component generation completed successfully!")
                return accumulated_response
            
            elif validation["status"] == "TRUNCATED" or finish_reason == "length":
                if attempt < max_retries:
                    print(f"⚠️  Response truncated, continuing generation...")
                    
                    # Add the assistant's response and continuation prompt to conversation
                    conversation.extend([
                        {"role": "assistant", "content": response_content},
                        {"role": "user", "content": "The previous response was truncated. Please continue from exactly where you left off, without repeating any of the provided code."}
                    ])
                else:
                    print(f"❌ Max retries ({max_retries}) reached for truncated response")
                    return accumulated_response  # Return what we have
            
            elif validation["status"] == "DEPENDENCY_ERROR":
                if attempt < max_retries:
                    print(f"🚫 Dependency violation detected, requesting fix...")
                    
                    # Create a dependency fix prompt - this is critical for security
                    fix_prompt = f"""CRITICAL: The component uses disallowed dependencies.

Error: {validation['details']}

Current problematic code:
```jsx
{accumulated_response}
```

You MUST rewrite this component using ONLY these approved libraries:
- react (available globally as React)
- react-dom (available globally as ReactDOM)  
- lodash (available globally as _)
- Tailwind CSS classes only

DO NOT import react-table, moment, d3, or any other external libraries.
Implement the functionality manually using the approved dependencies above.

Please provide the complete, corrected component that uses only approved dependencies."""
                    
                    # Reset conversation with fix prompt - dependency violations require complete rewrite
                    conversation = [{"role": "user", "content": fix_prompt}]
                    accumulated_response = ""  # Reset since we're asking for a complete rewrite
                else:
                    print(f"❌ Max retries ({max_retries}) reached for dependency violations")
                    return accumulated_response  # Return what we have
            
            elif validation["status"] == "SYNTAX_ERROR":
                if attempt < max_retries:
                    print(f"🔧 Syntax error detected, attempting to fix...")
                    
                    # Create a fix prompt
                    fix_prompt = f"""The React component has a syntax error.
Error details: {validation['details']}

Here is the problematic code:
```jsx
{accumulated_response}
```

Please analyze the error, fix the code, and provide the complete, corrected component."""
                    
                    # Reset conversation with fix prompt
                    conversation = [{"role": "user", "content": fix_prompt}]
                    accumulated_response = ""  # Reset since we're asking for a complete fix
                else:
                    print(f"❌ Max retries ({max_retries}) reached for syntax errors")
                    return accumulated_response  # Return what we have
        
        print(f"❌ Component generation failed after all attempts")
        return accumulated_response
    
    def _make_api_call(self, conversation, model, max_tokens):
        """Make a single API call and return the response data"""
        url = f"{self.base_url}/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "User-Agent": "OpenUI-Integration/1.0"
        }
        
        payload = {
            "model": model,
            "messages": conversation,
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "stream": True
        }
        
        try:
            print(f"📡 Sending request to {url}")
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                cookies=self.cookies,
                stream=True,
                timeout=60
            )
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return None
            
            # Handle SSE stream
            full_response = ""
            finish_reason = None
            
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data == "[DONE]":
                            break
                        try:
                            json_data = json.loads(data)
                            if "choices" in json_data and len(json_data["choices"]) > 0:
                                choice = json_data["choices"][0]
                                delta = choice.get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    full_response += content
                                    print(content, end="", flush=True)
                                
                                # Capture finish_reason
                                if "finish_reason" in choice and choice["finish_reason"]:
                                    finish_reason = choice["finish_reason"]
                                    
                        except json.JSONDecodeError:
                            print(f"Could not parse JSON: {data}")
                            continue
            
            print(f"\n📋 Response complete (finish_reason: {finish_reason})")
            return {
                "content": full_response,
                "finish_reason": finish_reason
            }
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
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