#!/usr/bin/env python3
"""
CrewAI agents for component creation, testing, and refinement
"""

from crewai import Agent, Task, Crew, Process
from openui_client import OpenUIClient
from gemini_client import GeminiClient
from pure_analyst import PureFrameworkAnalyst
import json
import re
import os


class ComponentCreationCrew:
    def __init__(self, use_pure_framework=None):
        self.openui_client = OpenUIClient()
        self.gemini_client = GeminiClient()
        
        # Determine which analyst to use
        if use_pure_framework is None:
            use_pure_framework = os.getenv('USE_PURE_FRAMEWORK', 'false').lower() in ['true', '1', 'yes']
        
        self.use_pure_framework = use_pure_framework
        if use_pure_framework:
            # Pass API key to PURE analyst to ensure it works
            api_key = os.getenv('GEMINI_API_KEY')
            self.pure_analyst = PureFrameworkAnalyst(api_key=api_key)
            print("🎯 Using PURE Framework Analyst (Purposeful, Usable, Readable, Extensible)")
        else:
            self.pure_analyst = None
            print("🔍 Using Standard Quality Analyst")
        
        # Define agents
        self.component_designer = Agent(
            role='Aria - Senior Frontend Component Designer',
            goal='Create exceptional React components that meet user requirements',
            backstory="""You are Aria, a senior frontend developer with 10+ years of experience 
            creating beautiful, functional, and accessible React components. You understand 
            modern design patterns, accessibility standards, and performance best practices. 
            You have an artistic eye and believe that code should be both functional and elegant.""",
            verbose=True,
            allow_delegation=False
        )
        
        if use_pure_framework:
            self.quality_analyst = Agent(
                role='Phoenix - PURE Framework Quality Analyst',
                goal='Analyze components using PURE framework: Purposeful, Usable, Readable, Extensible',
                backstory="""You are Phoenix, a PURE framework specialist who evaluates components across 
                four key dimensions: Purposeful (solves the right problem), Usable (intuitive and 
                accessible), Readable (clear and maintainable code), and Extensible (flexible and 
                future-proof). You provide structured analysis with actionable improvements. Your analytical 
                mind sees patterns others miss, like a phoenix rising with clarity from complexity.""",
                verbose=True,
                allow_delegation=False
            )
        else:
            self.quality_analyst = Agent(
                role='Quinn - Code Quality and UX Analyst',
                goal='Analyze components for quality, usability, and adherence to best practices',
                backstory="""You are Quinn, a meticulous quality analyst who reviews code for 
                functionality, performance, accessibility, and user experience. You catch 
                issues others miss and provide actionable improvement suggestions. Your keen eye 
                for detail and passion for user experience makes you the team's quality guardian.""",
                verbose=True,
                allow_delegation=False
            )
        
        self.test_engineer = Agent(
            role='Sage - Test Automation Engineer',
            goal='Create comprehensive test suites for React components',
            backstory="""You are Sage, a test automation expert who creates thorough test 
            coverage including unit tests, integration tests, accessibility tests, 
            and edge case scenarios. You believe that every great component needs great tests,
            and your wisdom comes from preventing bugs before they happen.""",
            verbose=True,
            allow_delegation=False
        )
        
        self.refiner = Agent(
            role='Nova - Component Refinement Specialist',
            goal='Iteratively improve components based on feedback and testing',
            backstory="""You are Nova, a perfectionist who takes feedback and transforms 
            it into concrete improvements. You excel at refining components to meet 
            the highest standards of quality and user experience. Like a supernova, 
            you transform ordinary code into stellar components through iterative excellence.""",
            verbose=True,
            allow_delegation=False
        )
    
    def create_component(self, requirements, max_iterations=3):
        """
        Main workflow to create and refine a component
        """
        print(f"🚀 Starting component creation with requirements: {requirements}")
        
        # Initial component creation
        component_code = self._generate_initial_component(requirements)
        if not component_code:
            return None
        
        iteration = 1
        
        while iteration <= max_iterations:
            print(f"\n🔄 Iteration {iteration}/{max_iterations}")
            
            # Analyze current component
            analysis = self._analyze_component(component_code, requirements)
            if not analysis:
                break
            
            # Extract score from analysis
            score = self._extract_score(analysis)
            print(f"📊 Current component score: {score}/10")
            
            # If score is good enough, we're done
            if score >= 8.5:
                print("✅ Component meets quality standards!")
                break
            
            # Generate improvements
            improvements = self._suggest_improvements(component_code, analysis)
            if not improvements:
                break
            
            # Generate tests
            tests = self._generate_tests(component_code, requirements)
            
            # Refine component
            refined_component = self._refine_component(
                component_code, requirements, improvements, analysis
            )
            
            if refined_component:
                component_code = refined_component
            
            iteration += 1
        
        # Final result
        final_analysis = self._analyze_component(component_code, requirements)
        final_score = self._extract_score(final_analysis)
        
        result = {
            "component_code": component_code,
            "final_analysis": final_analysis,
            "final_score": final_score,
            "iterations": iteration - 1,
            "tests": self._generate_tests(component_code, requirements)
        }
        
        return result
    
    def _generate_initial_component(self, requirements):
        """Generate initial component using OpenUI"""
        print("🎨 Generating initial component with OpenUI...")
        
        enhanced_prompt = f"""
        Create a React component: {requirements}
        
        CRITICAL: Use complete Tailwind class names - NEVER use "..." or placeholders.
        
        Requirements:
        - React functional component with TypeScript
        - Use ONLY Tailwind CSS classes (no custom CSS)
        - Include hover/focus states
        - Make it responsive
        
        Examples of complete Tailwind classes:
        - Button: "bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg"
        - Card: "bg-white rounded-lg shadow-lg p-6"
        - Text: "text-gray-900 font-semibold text-lg"
        
        Format as:
        ```jsx
        import React from 'react';
        
        interface Props {{
          // props here
        }}
        
        const Component: React.FC<Props> = (props) => {{
          return (
            // JSX with complete Tailwind classes
          );
        }};
        
        export default Component;
        ```
        """
        
        return self.openui_client.create_component(enhanced_prompt)
    
    def _analyze_component(self, component_code, requirements):
        """Analyze component using either PURE framework or standard analysis"""
        if self.use_pure_framework:
            print("🎯 Analyzing component using PURE framework...")
            return self.pure_analyst.analyze_component(component_code, requirements)
        else:
            print("🔍 Analyzing component quality...")
            return self.gemini_client.analyze_component(component_code, requirements)
    
    def _suggest_improvements(self, component_code, analysis):
        """Get improvement suggestions using appropriate analyst"""
        print("💡 Generating improvement suggestions...")
        if self.use_pure_framework:
            return self.pure_analyst.suggest_improvements(component_code, analysis)
        else:
            return self.gemini_client.suggest_improvements(component_code, analysis)
    
    def _generate_tests(self, component_code, requirements):
        """Generate test cases using appropriate analyst"""
        print("🧪 Generating test cases...")
        if self.use_pure_framework:
            return self.pure_analyst.generate_pure_tests(component_code, requirements)
        else:
            return self.gemini_client.create_test_cases(component_code, requirements)
    
    def _refine_component(self, component_code, requirements, improvements, analysis):
        """Refine component based on improvements"""
        print("✨ Refining component...")
        
        refinement_prompt = f"""
        Improve this React component based on the analysis and suggestions:
        
        CURRENT COMPONENT:
        ```jsx
        {component_code}
        ```
        
        REQUIREMENTS:
        {requirements}
        
        ANALYSIS:
        {analysis}
        
        IMPROVEMENTS TO IMPLEMENT:
        {improvements}
        
        Please provide the improved component code that addresses the identified issues.
        Focus on the highest priority improvements first.
        """
        
        return self.openui_client.create_component(refinement_prompt)
    
    def _extract_score(self, analysis):
        """Extract overall score from analysis (supports both standard and PURE framework)"""
        if not analysis:
            return 0
        
        if self.use_pure_framework:
            return self.pure_analyst.extract_pure_score(analysis)
        
        # Standard analysis score extraction
        # Look for JSON in the analysis
        json_match = re.search(r'\{[^}]*"overall_score":\s*(\d+)[^}]*\}', analysis)
        if json_match:
            try:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                return data.get("overall_score", 0)
            except json.JSONDecodeError:
                pass
        
        # Fallback: look for score patterns
        score_patterns = [
            r'overall[_\s]*score[:\s]*(\d+)',
            r'score[:\s]*(\d+)[/\s]*10',
            r'rating[:\s]*(\d+)'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, analysis, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return 5  # Default neutral score


def test_crew():
    """Test the component creation crew"""
    crew = ComponentCreationCrew()
    
    requirements = """
    Create a modern card component for displaying user profiles. The card should include:
    - User avatar/photo
    - Name and title
    - Brief bio or description
    - Social media links
    - Follow/Connect button
    - Responsive design
    - Accessible
    - Hover effects
    """
    
    print("🎯 Testing component creation crew...")
    result = crew.create_component(requirements, max_iterations=2)
    
    if result:
        print(f"\n✅ Component creation completed!")
        print(f"Final score: {result['final_score']}/10")
        print(f"Iterations: {result['iterations']}")
        print(f"Component code length: {len(result['component_code'])} characters")
        return True
    else:
        print("\n❌ Component creation failed")
        return False


if __name__ == "__main__":
    test_crew()