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
        
        # Image generation model (Imagen 3 via Gemini)
        try:
            self.image_model = genai.GenerativeModel('gemini-1.5-pro')
        except:
            self.image_model = None
    
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
    
    def generate_placeholder_image_description(self, component_type, context=""):
        """Generate description for AI-generated placeholder images"""
        prompt = f"""
        Generate a detailed description for a placeholder image that would be perfect for a {component_type} component.
        
        Context: {context}
        
        The description should be:
        - Professional and modern
        - Suitable for UI/UX design
        - Specific enough for AI image generation
        - Appropriate for the component type
        
        Examples:
        - For a profile card: "Professional headshot of a person in business attire, clean background, modern lighting"
        - For a product card: "Minimalist product photography of a modern gadget on clean white background"
        - For a hero section: "Abstract geometric patterns in soft blue and white, modern and professional"
        
        Provide just the image description, no extra text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini image description generation failed: {e}")
            # Fallback descriptions
            fallbacks = {
                'button': 'Modern abstract background with soft gradients in blue and white',
                'card': 'Clean minimalist design with subtle shadows and modern typography',
                'table': 'Professional data visualization with clean lines and modern design',
                'form': 'Clean interface design with modern input fields and soft colors',
                'hero': 'Abstract geometric patterns in professional blue and white colors'
            }
            return fallbacks.get(component_type.lower(), 'Modern, clean, professional design background')
    
    def suggest_component_enhancements(self, component_code, component_type):
        """Suggest AI-generated content enhancements for components"""
        prompt = f"""
        Analyze this {component_type} component and suggest specific enhancements:
        
        ```jsx
        {component_code}
        ```
        
        Provide suggestions for:
        1. **Icons**: Which Heroicons would enhance this component? Be specific with icon names.
        2. **Images**: What kind of placeholder images would improve the design?
        3. **Content**: Suggest realistic sample content (text, data, etc.)
        4. **Animations**: What Tailwind animations would enhance UX?
        5. **Variants**: What style variants would be useful?
        
        Format as actionable recommendations a developer can implement.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini enhancement suggestions failed: {e}")
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