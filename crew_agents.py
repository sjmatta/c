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
    
    def _get_component_library_info(self):
        """Load component library documentation for AI context"""
        try:
            with open('component-library.md', 'r') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback to basic component patterns if file doesn't exist
            return """
## Available Components

### Pagination Component
```jsx
import { Pagination } from './components/Pagination';

<Pagination 
  currentPage={currentPage}
  totalPages={totalPages}
  onPageChange={handlePageChange}
/>
```

### Design Patterns
- Tables: min-w-full bg-white border border-gray-200
- Headers: bg-gray-100 px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase
- Buttons: bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg
"""
    
    def _generate_initial_component(self, requirements):
        """Generate initial component using OpenUI"""
        print("🎨 Generating initial component with OpenUI...")
        
        enhanced_prompt = f"""
        Create a React component: {requirements}
        
        🎨 MODERN DESIGN REQUIREMENTS - CREATE BEAUTIFUL, VISUALLY APPEALING COMPONENTS:
        
        **COLOR PALETTE & VISUAL HIERARCHY:**
        - Use rich, modern color schemes with proper contrast
        - Primary colors: blue-600, indigo-600, purple-600, emerald-600
        - Accent colors: amber-500, rose-500, cyan-500, violet-500  
        - Neutral grays: slate-50, slate-100, slate-200, slate-600, slate-700, slate-800
        - Background gradients: "bg-gradient-to-r from-blue-600 to-purple-600"
        
        **TABLE STYLING (if applicable):**
        - Container: "overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xl"
        - Headers: "bg-gradient-to-r from-slate-50 to-slate-100 px-6 py-4 text-left text-sm font-semibold text-slate-900 uppercase tracking-wider border-b border-slate-200"
        - ZEBRA STRIPING: "odd:bg-white even:bg-slate-50/50"
        - Row hover: "hover:bg-blue-50/50 transition-colors duration-200"
        - Cells: "px-6 py-4 text-sm text-slate-700 border-b border-slate-100"
        - Action buttons in rows: Use colored badges with "bg-emerald-100 text-emerald-800 px-2 py-1 rounded-full text-xs font-medium"
        
        **BUTTON DESIGNS:**
        - Primary: "bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold py-3 px-6 rounded-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200"
        - Secondary: "bg-white border-2 border-slate-200 hover:border-blue-300 text-slate-700 hover:text-blue-600 font-semibold py-3 px-6 rounded-lg shadow-md hover:shadow-lg transition-all duration-200"
        - Destructive: "bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white font-semibold py-3 px-6 rounded-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200"
        
        **PAGINATION STYLING:**
        - Container: "flex items-center justify-center gap-3 py-6 bg-slate-50/50 rounded-lg"
        - Page numbers: "h-10 w-10 rounded-lg border border-slate-200 bg-white hover:bg-blue-50 hover:border-blue-300 hover:text-blue-600 text-slate-600 font-medium flex items-center justify-center transition-all duration-200"
        - Active page: "h-10 w-10 rounded-lg bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold flex items-center justify-center shadow-lg"
        - Prev/Next: "px-4 py-2 rounded-lg border border-slate-200 bg-white hover:bg-blue-50 hover:border-blue-300 hover:text-blue-600 text-slate-600 font-medium transition-all duration-200"
        - Disabled: "opacity-40 cursor-not-allowed hover:bg-white hover:border-slate-200 hover:text-slate-600"
        
        **CARD COMPONENTS:**
        - Container: "bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden hover:shadow-2xl transition-shadow duration-300"
        - Header: "bg-gradient-to-r from-slate-50 to-slate-100 px-6 py-4 border-b border-slate-200"
        - Body: "p-6 space-y-4"
        - Footer: "px-6 py-4 bg-slate-50/50 border-t border-slate-200"
        
        **FORM ELEMENTS:**
        - Inputs: "border-2 border-slate-200 rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-200"
        - Labels: "text-sm font-semibold text-slate-700 mb-2 block"
        - Error states: "border-red-300 focus:border-red-500 focus:ring-red-100"
        
        **HOVER & INTERACTIVE STATES:**
        - All interactive elements MUST have smooth transitions: "transition-all duration-200"
        - Use subtle transforms: "hover:-translate-y-0.5" for buttons
        - Color transitions: "hover:bg-blue-50" with proper color progression
        - Shadow enhancements: "hover:shadow-xl" for elevated elements
        
        **VISUAL ENHANCEMENTS:**
        - Use icons (Unicode symbols): ▲ ▼ for sorting, ← → for navigation
        - Add loading states with opacity changes: "opacity-75"
        - Use badge components: "bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium"
        - Add status indicators with colored dots: "h-2 w-2 rounded-full bg-green-500"
        
        CRITICAL INSTRUCTIONS:
        - Use complete Tailwind class names - NEVER use "..." or placeholders
        - Implement all functionality from scratch using only approved dependencies
        - EVERY element must be beautifully styled - NO unstyled or boring elements
        - Create visual hierarchy with typography, spacing, and color
        
        🚨 SECURITY CONSTRAINT - APPROVED DEPENDENCIES ONLY:
        You MUST only use these libraries:
        - react (available globally as React)
        - react-dom (available globally as ReactDOM)  
        - lodash (available globally as _)
        - Tailwind CSS classes only
        
        DO NOT import react-table, moment, d3, or ANY other external libraries.
        If you need table functionality, implement it manually using React state and lodash.
        If you need pagination, create beautiful pagination with the styles above.
        If you need date functionality, use native Date objects or lodash.
        If you need data visualization, use CSS and manual calculations.
        
        Requirements:
        - React functional component with TypeScript
        - Use ONLY Tailwind CSS classes (no custom CSS)
        - Include beautiful hover/focus states with transitions
        - Make it responsive with proper breakpoints
        - Create visually stunning, modern components that users will love
        
        Format as:
        ```jsx
        import React from 'react';
        
        interface Props {{
          // props here
        }}
        
        const Component: React.FC<Props> = (props) => {{
          return (
            // JSX with beautiful, complete Tailwind classes - MAKE IT STUNNING
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
        
        🎨 ENHANCED DESIGN REQUIREMENTS - MAKE THIS COMPONENT STUNNING:
        Apply the same modern design principles for visual enhancement:
        
        **TABLE STYLING UPGRADE:**
        - Replace basic tables with: "overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xl"
        - Headers: "bg-gradient-to-r from-slate-50 to-slate-100 px-6 py-4 text-left text-sm font-semibold text-slate-900 uppercase tracking-wider border-b border-slate-200"
        - IMPLEMENT ZEBRA STRIPING: "odd:bg-white even:bg-slate-50/50"
        - Row hover: "hover:bg-blue-50/50 transition-colors duration-200"
        - Cells: "px-6 py-4 text-sm text-slate-700 border-b border-slate-100"
        
        **BUTTON ENHANCEMENT:**
        - Upgrade plain buttons to: "bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold py-3 px-6 rounded-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200"
        - Secondary buttons: "bg-white border-2 border-slate-200 hover:border-blue-300 text-slate-700 hover:text-blue-600 font-semibold py-3 px-6 rounded-lg shadow-md hover:shadow-lg transition-all duration-200"
        
        **PAGINATION BEAUTY:**
        - Container: "flex items-center justify-center gap-3 py-6 bg-slate-50/50 rounded-lg"
        - Page numbers: "h-10 w-10 rounded-lg border border-slate-200 bg-white hover:bg-blue-50 hover:border-blue-300 hover:text-blue-600 text-slate-600 font-medium flex items-center justify-center transition-all duration-200"
        - Active page: "h-10 w-10 rounded-lg bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold flex items-center justify-center shadow-lg"
        
        **COLOR & VISUAL HIERARCHY:**
        - Rich color palette: blue-600, indigo-600, purple-600, emerald-600
        - Neutral grays: slate-50, slate-100, slate-200, slate-600, slate-700, slate-800
        - Add gradients: "bg-gradient-to-r from-blue-600 to-purple-600"
        - Badge components: "bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium"
        
        CRITICAL INSTRUCTIONS:
        - Use complete Tailwind class names - NEVER use "..." or placeholders  
        - ALL interactive elements (buttons, inputs, etc.) MUST be beautifully styled
        - Implement all functionality from scratch using only approved dependencies
        - TRANSFORM this into a visually stunning, modern component
        - Add smooth transitions to ALL interactive elements: "transition-all duration-200"
        
        🚨 SECURITY CONSTRAINT - APPROVED DEPENDENCIES ONLY:
        You MUST only use these libraries:
        - react (available globally as React)
        - react-dom (available globally as ReactDOM)  
        - lodash (available globally as _)
        - Tailwind CSS classes only
        
        DO NOT import react-table, moment, d3, or ANY other external libraries.
        DO NOT import from './components/...' - implement everything inline.
        If you need table functionality, implement it manually using React state and lodash.
        If you need pagination, create beautiful pagination with the styles above.
        If you need date functionality, use native Date objects or lodash.
        
        Please provide the improved component code that addresses the identified issues.
        Focus on visual improvements and modern design while maintaining functionality.
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