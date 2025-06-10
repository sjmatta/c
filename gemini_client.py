#!/usr/bin/env python3
"""
Gemini API client for ultra-thinking and component analysis
"""

import google.generativeai as genai
import os


class GeminiClient:
    def __init__(self, api_key=None):
        """Initialize Gemini client with API key"""
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY', 'your-api-key-here')
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def analyze_component(self, component_code, requirements):
        """
        Analyze a component against requirements using Gemini's reasoning
        """
        prompt = f"""
        Analyze this React component against the given requirements:
        
        REQUIREMENTS:
        {requirements}
        
        COMPONENT CODE:
        ```jsx
        {component_code}
        ```
        
        Please provide a detailed analysis covering:
        1. Functionality: Does it meet the basic requirements?
        2. Code quality: Is it well-structured and following best practices?
        3. Accessibility: Are there any a11y considerations?
        4. Performance: Any potential performance issues?
        5. User experience: How intuitive and usable is it?
        6. Missing features: What's missing from the requirements?
        7. Improvements: Specific suggestions for enhancement
        
        Rate each aspect from 1-10 and provide an overall score.
        End with a JSON summary like:
        {{
            "overall_score": 8,
            "functionality": 9,
            "code_quality": 7,
            "accessibility": 6,
            "performance": 8,
            "user_experience": 8,
            "missing_features": ["feature1", "feature2"],
            "improvements": ["improvement1", "improvement2"]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini analysis failed: {e}")
            return None
    
    def suggest_improvements(self, component_code, analysis):
        """
        Generate specific improvement suggestions based on analysis
        """
        prompt = f"""
        Based on this component analysis, provide specific, actionable improvements:
        
        CURRENT COMPONENT:
        ```jsx
        {component_code}
        ```
        
        ANALYSIS:
        {analysis}
        
        Provide:
        1. Priority improvements (most important fixes)
        2. Code refactoring suggestions
        3. Feature enhancements
        4. Accessibility improvements
        5. Performance optimizations
        
        Format as a clear, prioritized list that a developer can follow.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini improvement suggestions failed: {e}")
            return None
    
    def create_test_cases(self, component_code, requirements):
        """
        Generate comprehensive test cases for the component
        """
        prompt = f"""
        Create comprehensive test cases for this React component:
        
        REQUIREMENTS:
        {requirements}
        
        COMPONENT:
        ```jsx
        {component_code}
        ```
        
        Generate:
        1. Unit tests (Jest/React Testing Library)
        2. Integration tests
        3. Accessibility tests
        4. Visual regression test scenarios
        5. Edge cases and error handling tests
        
        Provide actual test code that can be run.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini test generation failed: {e}")
            return None


def test_gemini_client():
    """Test the Gemini client"""
    client = GeminiClient()
    
    sample_code = """
    import React from 'react';
    
    const Button = () => {
      return (
        <button style={{ backgroundColor: 'blue', color: 'white'}}>
          Click me!
        </button>
      );
    };
    
    export default Button;
    """
    
    requirements = "Create a button component that is accessible, has hover effects, and follows modern React best practices."
    
    print("Testing Gemini component analysis...")
    analysis = client.analyze_component(sample_code, requirements)
    
    if analysis:
        print("✅ Gemini analysis successful!")
        print(f"Analysis preview: {analysis[:200]}...")
        return True
    else:
        print("❌ Gemini analysis failed")
        return False


if __name__ == "__main__":
    test_gemini_client()