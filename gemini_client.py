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
    
    def generate_placeholder_image_url(self, component_type, context="", width=400, height=300):
        """Generate appropriate placeholder image URL using placehold.co"""
        # Create appropriate text and colors based on component type
        text_map = {
            'button': 'Button',
            'card': 'Card',
            'table': 'Table', 
            'form': 'Form',
            'hero': 'Hero',
            'banner': 'Banner',
            'profile': 'Profile',
            'user': 'User',
            'product': 'Product',
            'navigation': 'Nav',
            'gallery': 'Gallery'
        }
        
        color_map = {
            'button': '3B82F6/FFFFFF',  # Blue
            'card': '8B5CF6/FFFFFF',    # Purple
            'table': '10B981/FFFFFF',   # Green
            'form': 'F59E0B/FFFFFF',    # Amber
            'hero': '6366F1/FFFFFF',    # Indigo
            'banner': '6366F1/FFFFFF',  # Indigo
            'profile': 'EC4899/FFFFFF', # Pink
            'user': 'EC4899/FFFFFF',    # Pink
            'product': 'EF4444/FFFFFF', # Red
            'navigation': '6B7280/FFFFFF', # Gray
            'gallery': '059669/FFFFFF'  # Emerald
        }
        
        # Get text and colors for component type
        display_text = text_map.get(component_type.lower(), component_type.title())
        colors = color_map.get(component_type.lower(), '3B82F6/FFFFFF')
        
        # Generate placehold.co URL
        return f"https://placehold.co/{width}x{height}/{colors}?text={display_text}"
    
# Unsplash keywords method removed - using only placehold.co

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
        1. **Icons**: Which Heroicons/Lucide React icons would enhance this component? Be specific with icon names and placement.
        2. **Images**: What kind of placeholder images would improve the design? Include specific URLs.
        3. **Content**: Suggest realistic sample content (text, data, etc.)
        4. **Animations**: What Tailwind animations would enhance UX?
        5. **Variants**: What style variants would be useful?
        6. **Accessibility**: Icon accessibility improvements (alt text, aria-labels)
        
        Available Icon Libraries:
        - Heroicons (outline, solid): ChevronDownIcon, UserIcon, HeartIcon, etc.
        - Lucide React: ChevronDown, User, Heart, Search, Settings, etc.
        - Tabler Icons: icon-chevron-down, icon-user, icon-heart, etc.
        
        Format as actionable recommendations with specific implementation code snippets.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini enhancement suggestions failed: {e}")
            return None
    
    def suggest_icons_for_component(self, component_code, component_type):
        """Suggest specific icons for a component with implementation details"""
        prompt = f"""
        Suggest specific icons for this {component_type} component:
        
        ```jsx
        {component_code}
        ```
        
        Provide:
        1. **Heroicons suggestions** with exact icon names and where to place them
        2. **Lucide React alternatives** 
        3. **Implementation code** showing how to integrate the icons
        4. **Accessibility considerations** for each icon
        
        Focus on:
        - User interaction cues (arrows, chevrons, plus/minus)
        - Status indicators (check, warning, info, error)
        - Navigation aids (home, back, forward, menu)
        - Content types (user, settings, search, filter)
        
        Return as structured JSON:
        {{
            "suggested_icons": [
                {{
                    "icon_name": "ChevronDownIcon",
                    "library": "heroicons",
                    "placement": "sort indicator",
                    "implementation": "<ChevronDownIcon className='w-4 h-4' />",
                    "aria_label": "Sort descending"
                }}
            ],
            "cdn_links": ["https://heroicons.com", "https://lucide.dev"],
            "import_statements": ["import {{ ChevronDownIcon }} from '@heroicons/react/24/outline'"]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini icon suggestions failed: {e}")
            return self._get_fallback_icons(component_type)
    
    def _get_fallback_icons(self, component_type):
        """Provide fallback icon suggestions when Gemini fails"""
        fallback_icons = {
            'button': {
                'suggested_icons': [
                    {'icon_name': 'ChevronRightIcon', 'library': 'heroicons', 'placement': 'action indicator'},
                    {'icon_name': 'PlusIcon', 'library': 'heroicons', 'placement': 'add action'}
                ]
            },
            'table': {
                'suggested_icons': [
                    {'icon_name': 'ChevronUpIcon', 'library': 'heroicons', 'placement': 'sort ascending'},
                    {'icon_name': 'ChevronDownIcon', 'library': 'heroicons', 'placement': 'sort descending'},
                    {'icon_name': 'FunnelIcon', 'library': 'heroicons', 'placement': 'filter'}
                ]
            },
            'card': {
                'suggested_icons': [
                    {'icon_name': 'UserIcon', 'library': 'heroicons', 'placement': 'profile indicator'},
                    {'icon_name': 'HeartIcon', 'library': 'heroicons', 'placement': 'favorite action'},
                    {'icon_name': 'ShareIcon', 'library': 'heroicons', 'placement': 'share action'}
                ]
            }
        }
        
        return str(fallback_icons.get(component_type.lower(), fallback_icons['button']))


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