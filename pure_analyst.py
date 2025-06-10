#!/usr/bin/env python3
"""
PURE Framework Analyst - Alternative to the standard quality analyst
PURE: Purposeful, Usable, Readable, Extensible
"""

from gemini_client import GeminiClient
import json
import re


class PureFrameworkAnalyst:
    """
    Analyst that uses the PURE framework for component evaluation
    - Purposeful: Does it solve the intended problem effectively?
    - Usable: Is it intuitive and accessible for users?
    - Readable: Is the code clear and maintainable?
    - Extensible: Can it be easily modified and extended?
    """
    
    def __init__(self, api_key=None):
        # Load from environment if available
        if api_key is None:
            import os
            api_key = os.getenv('GEMINI_API_KEY')
        
        self.gemini_client = GeminiClient(api_key=api_key)
    
    def analyze_component(self, component_code, requirements):
        """
        Analyze component using PURE framework
        """
        prompt = f"""
        Analyze this React component using the PURE framework:
        
        REQUIREMENTS:
        {requirements}
        
        COMPONENT CODE:
        ```jsx
        {component_code}
        ```
        
        Please evaluate the component across the PURE dimensions:
        
        ## P - PURPOSEFUL (0-10)
        - Does it solve the intended problem effectively?
        - Does it meet all stated requirements?
        - Is the component focused on its core purpose?
        - Are there unnecessary features or missing essential ones?
        
        ## U - USABLE (0-10)
        - Is it intuitive for end users?
        - Is it accessible (ARIA, keyboard navigation, screen readers)?
        - Does it provide clear feedback (loading states, hover effects)?
        - Is it responsive across different devices?
        - Does it handle edge cases gracefully?
        
        ## R - READABLE (0-10)
        - Is the code structure clear and logical?
        - Are naming conventions consistent and meaningful?
        - Is it properly documented/commented where needed?
        - Would a new developer understand this code quickly?
        - Does it follow React best practices?
        
        ## E - EXTENSIBLE (0-10)
        - Can it be easily modified for new requirements?
        - Is it properly componentized/modular?
        - Does it have a flexible API (props, callbacks)?
        - Is it testable and maintainable?
        - Would adding new features require major refactoring?
        
        For each dimension, provide:
        1. Score (0-10)
        2. Specific strengths
        3. Specific weaknesses
        4. Actionable improvement suggestions
        
        Calculate overall PURE score as the average of all four dimensions.
        
        IMPORTANT: End with this exact format:
        
        PURE_SCORE: X.X
        
        Where X.X is the average of all four PURE dimension scores.
        """
        
        try:
            response = self.gemini_client.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"PURE analysis failed: {e}")
            return None
    
    def extract_pure_score(self, analysis):
        """Extract PURE score from analysis - simple approach"""
        if not analysis:
            return 5.0
        
        # Look for the simple format: PURE_SCORE: X.X
        match = re.search(r'PURE_SCORE:\s*([0-9.]+)', analysis)
        if match:
            return float(match.group(1))
        
        return 5.0  # Default neutral score
    
    def extract_pure_breakdown(self, analysis):
        """Extract detailed PURE breakdown - let the LLM handle formatting"""
        # Don't overcomplicate this - the analysis text itself IS the breakdown
        return {"analysis_text": analysis if analysis else "No analysis available"}
    
    def suggest_improvements(self, component_code, analysis):
        """Generate improvement suggestions based on PURE analysis"""
        prompt = f"""
        Based on this PURE analysis, provide 3-5 specific, actionable improvements:
        
        ANALYSIS:
        {analysis}
        
        COMPONENT:
        ```jsx
        {component_code}
        ```
        
        Provide concrete suggestions to improve the lowest-scoring PURE dimensions.
        """
        
        try:
            response = self.gemini_client.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"PURE improvement suggestions failed: {e}")
            return None
    
    def generate_pure_tests(self, component_code, requirements):
        """Generate tests focused on PURE framework"""
        prompt = f"""
        Generate Jest/React Testing Library tests for this component focused on PURE framework:
        
        COMPONENT:
        ```jsx
        {component_code}
        ```
        
        Create tests for:
        - Purposeful: Does it work as intended?
        - Usable: Is it accessible and user-friendly?
        - Readable: Is the API clear?
        - Extensible: Can it be customized?
        
        Provide actual test code.
        """
        
        try:
            response = self.gemini_client.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"PURE test generation failed: {e}")
            return None


def test_pure_analyst():
    """Test the PURE framework analyst"""
    # Use environment variable for API key
    import os
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Please set GEMINI_API_KEY environment variable")
        return
    analyst = PureFrameworkAnalyst(api_key=api_key)
    
    sample_code = """
    import React from 'react';
    
    const Button = ({ children, onClick, disabled = false }) => {
      return (
        <button 
          onClick={onClick}
          disabled={disabled}
          style={{ 
            padding: '8px 16px',
            backgroundColor: disabled ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px'
          }}
        >
          {children}
        </button>
      );
    };
    
    export default Button;
    """
    
    requirements = "Create a button component that is accessible, customizable, and follows React best practices."
    
    print("🔍 Testing PURE Framework Analysis...")
    analysis = analyst.analyze_component(sample_code, requirements)
    
    if analysis:
        print("✅ PURE analysis successful!")
        print(f"Analysis preview: {analysis[:300]}...")
        
        # Test score extraction
        score = analyst.extract_pure_score(analysis)
        
        print(f"\n📊 PURE Score: {score}/10")
        print("✅ PURE framework is working!")
        
        return True
    else:
        print("❌ PURE analysis failed")
        return False


if __name__ == "__main__":
    test_pure_analyst()