#!/usr/bin/env python3
"""
CrewAI agents for component creation, testing, and refinement
"""

from crewai import Agent, Task, Crew, Process
from openui_client import OpenUIClient
from gemini_client import GeminiClient
from pure_analyst import PureFrameworkAnalyst
from icon_library import IconLibraryManager
import json
import re
import os


class ComponentCreationCrew:
    def __init__(self, use_pure_framework=None):
        self.openui_client = OpenUIClient()
        self.gemini_client = GeminiClient()
        self.icon_manager = IconLibraryManager()
        
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
        
        print("🎨 Icon library and image generation enabled")
        
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
        
# Test automation agent removed for simplified workflow
        
        self.refiner = Agent(
            role='Nova - PURE Framework Methodology Expert',
            goal='Analyze components using PURE methodology and provide structured improvement recommendations',
            backstory="""You are Nova, a PURE Framework methodology expert specializing in React component analysis. 
            You evaluate components across four critical dimensions: Purposeful (solves the right problem effectively), 
            Usable (intuitive interface and excellent user experience), Readable (clear, maintainable, well-structured code), 
            and Extensible (flexible architecture that adapts to future needs). Your analytical expertise transforms 
            components into stellar implementations through systematic PURE evaluation and targeted improvement strategies.""",
            verbose=True,
            allow_delegation=False
        )
    
    def create_component(self, requirements, max_iterations=1):
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
            
            # Skip refinement to avoid token limit issues
            print("⏭️  Skipping refinement to prevent token overflow")
            break
            
            iteration += 1
        
        # Final result with enhanced metadata
        final_analysis = self._analyze_component(component_code, requirements)
        final_score = self._extract_score(final_analysis)
        
        # Extract component type for metadata
        component_type = self._extract_component_type(requirements)
        
        # Get enhancement suggestions
        enhancement_suggestions = self.gemini_client.suggest_component_enhancements(component_code, component_type)
        icon_suggestions = self.icon_manager.get_icon_suggestions(component_type)
        
        # Get Nova's PURE framework analysis and improvements
        pure_analysis = self._get_nova_pure_analysis(component_code, requirements, final_analysis)
        pure_improvements = self._get_nova_pure_improvements(component_code, requirements, pure_analysis)
        
        result = {
            "component_code": component_code,
            "final_analysis": final_analysis,
            "final_score": final_score,
            "iterations": iteration - 1,
            "component_type": component_type,
            "enhancement_suggestions": enhancement_suggestions,
            "icon_suggestions": icon_suggestions,
            "placeholder_images": {
                "primary": self.gemini_client.generate_placeholder_image_url(component_type, requirements),
                "alternatives": [
                    self.gemini_client.generate_placeholder_image_url(component_type, requirements, 300, 200),
                    self.gemini_client.generate_placeholder_image_url(component_type, requirements, 600, 400)
                ]
            },
            "nova_pure_analysis": pure_analysis,
            "nova_pure_improvements": pure_improvements
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
        """Generate initial component using OpenUI with enhanced design capabilities"""
        print("🎨 Generating initial component with OpenUI...")
        
        # Determine component type for context-aware generation
        component_type = self._extract_component_type(requirements)
        
        # Get icon suggestions
        icon_suggestions = self.icon_manager.get_icon_suggestions(component_type)
        
        # Get placeholder image URL if needed
        placeholder_image = self.gemini_client.generate_placeholder_image_url(component_type, requirements)
        
        # Generate enhanced prompt with new libraries
        enhanced_prompt = f"""Create a React component: {requirements}

🎨 MODERN BEAUTIFUL DESIGN with animations and professional icons:

**AVAILABLE LIBRARIES:**
- Heroicons: import {{ UserIcon, ChevronDownIcon, HeartIcon }} from '@heroicons/react/24/outline'
- Framer Motion: import {{ motion }} from 'framer-motion'
- React + Tailwind CSS

**ESSENTIAL STYLING:**
- Modern Cards: "bg-white rounded-xl border border-slate-200 shadow-lg hover:shadow-xl transition-all duration-300"
- Beautiful Buttons: "bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold py-3 px-6 rounded-lg shadow-lg transition-all duration-200"
- Professional Tables: "overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xl"
- Headers: "bg-gradient-to-r from-slate-50 to-slate-100 px-6 py-4 font-semibold text-slate-900"
- Hover Effects: "hover:bg-blue-50 hover:scale-[1.02] transition-all duration-200"

**HERO ICONS (use instead of emojis):**
- User/Profile: <UserIcon className="w-5 h-5" />
- Navigation: <ChevronDownIcon className="w-4 h-4" />
- Actions: <HeartIcon className="w-5 h-5" />
- Settings: <CogIcon className="w-5 h-5" />
- Search: <MagnifyingGlassIcon className="w-5 h-5" />

**FRAMER MOTION ANIMATIONS:**
- Hover buttons: <motion.button whileHover={{{{ scale: 1.05 }}}} whileTap={{{{ scale: 0.95 }}}}>
- Fade in cards: <motion.div initial={{{{ opacity: 0, y: 20 }}}} animate={{{{ opacity: 1, y: 0 }}}}>
- Loading spinner: <motion.div animate={{{{ rotate: 360 }}}} transition={{{{ repeat: Infinity, duration: 1 }}}}>
- Stagger animations: <motion.div variants={{{{ container: {{ staggerChildren: 0.1 }} }}}}>

**PLACEHOLDER IMAGES:**
- Use: {placeholder_image}
- Style: "rounded-lg object-cover shadow-md"

**REQUIREMENTS:**
- Use Heroicons for ALL icons (no emojis!)
- Add motion.div/button for smooth animations
- Rich colors: blue-600, indigo-600, purple-600, emerald-600
- ALL interactive elements get hover animations
- CRITICAL: All .map() functions MUST have unique key props

Return TypeScript functional component with Heroicons + Framer Motion:
```jsx
import React from 'react';
import {{ UserIcon, ChevronDownIcon }} from '@heroicons/react/24/outline';
import {{ motion }} from 'framer-motion';

// Component with professional icons and smooth animations
```"""
        
        print(f"🎯 Component type detected: {component_type}")
        print(f"🖼️  Placeholder image: {placeholder_image}")
        print(f"🎨 Available icons: {len(icon_suggestions['icons'])} suggestions")
        
        return self.openui_client.create_component(enhanced_prompt)
    
    def _extract_component_type(self, requirements):
        """Extract component type from requirements for context-aware generation"""
        requirements_lower = requirements.lower()
        
        type_keywords = {
            'button': ['button', 'btn'],
            'table': ['table', 'datatable', 'grid', 'list'],
            'card': ['card', 'profile', 'user'],
            'form': ['form', 'input', 'field'],
            'navigation': ['nav', 'menu', 'header', 'sidebar'],
            'modal': ['modal', 'dialog', 'popup'],
            'hero': ['hero', 'banner', 'header'],
            'gallery': ['gallery', 'image', 'photo']
        }
        
        for component_type, keywords in type_keywords.items():
            if any(keyword in requirements_lower for keyword in keywords):
                return component_type
        
        return 'default'
    
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
        """Test generation disabled - return placeholder"""
        print("⏭️  Test generation disabled")
        return "Test generation has been disabled for simplified workflow."
    
    def _refine_component(self, component_code, requirements, improvements, analysis):
        """Refine component based on improvements"""
        print("✨ Refining component...")
        
        refinement_prompt = f"""Improve this React component with STUNNING visual polish:

CURRENT COMPONENT:
```jsx
{component_code}
```

REQUIREMENTS: {requirements}

ANALYSIS: {analysis}

IMPROVEMENTS: {improvements}

🎨 VISUAL UPGRADE PRIORITIES:
1. **Replace ALL emojis with Heroicons**: import {{ UserIcon, HeartIcon }} from '@heroicons/react/24/outline'
2. **Add Framer Motion animations**: import {{ motion }} from 'framer-motion'
3. **Modern shadows & gradients**: "shadow-xl", "bg-gradient-to-r from-blue-600 to-blue-700"
4. **Smooth hover effects**: whileHover={{{{ scale: 1.05, y: -2 }}}}
5. **Perfect spacing**: Use consistent px-6 py-4, gap-4, space-y-4

**ANIMATION EXAMPLES:**
- Buttons: <motion.button whileHover={{{{ scale: 1.05 }}}} whileTap={{{{ scale: 0.95 }}}}>
- Cards: <motion.div whileHover={{{{ y: -4 }}}} transition={{{{ duration: 0.2 }}}}>
- Icons: <motion.div whileHover={{{{ rotate: 10 }}}}>

**STYLING EXAMPLES:**
- Premium buttons: "bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
- Modern cards: "bg-white rounded-2xl border border-slate-200 shadow-lg hover:shadow-xl transition-all duration-300 p-6"

Return the improved component that looks absolutely stunning with Heroicons + Framer Motion."""
        
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
    
    def _get_nova_pure_analysis(self, component_code, requirements, existing_analysis):
        """Get Nova's PURE framework analysis of the component"""
        print("🔍 Nova performing PURE framework analysis...")
        
        pure_prompt = f"""
        As Nova, a PURE Framework methodology expert, analyze this React component using the PURE methodology:

        REQUIREMENTS:
        {requirements}

        COMPONENT CODE:
        ```jsx
        {component_code}
        ```

        EXISTING ANALYSIS (for context):
        {existing_analysis}

        ## PURE Framework Analysis Instructions:

        Evaluate the component across these four dimensions with scores 1-10 and detailed explanations:

        ### 1. PURPOSEFUL (Does it solve the right problem effectively?)
        - Problem alignment: Does the component address the stated requirements?
        - Feature completeness: Are all requested features implemented?
        - User value: Does it provide clear value to end users?
        - Scope appropriateness: Is the component focused or trying to do too much?

        ### 2. USABLE (Is the interface intuitive and user experience excellent?)
        - Intuitive design: Can users understand how to interact without instruction?
        - Accessibility: Screen readers, keyboard navigation, color contrast
        - Error handling: Graceful failure modes and user feedback
        - Performance perception: Loading states, smooth interactions

        ### 3. READABLE (Is the code clear, maintainable, and well-structured?)
        - Code clarity: Self-documenting variable names, clear logic flow
        - Structure: Well-organized components, separation of concerns
        - TypeScript usage: Proper types, interfaces, error prevention
        - Documentation: Comments where needed, not over-commented

        ### 4. EXTENSIBLE (Is the architecture flexible for future needs?)
        - Modularity: Can parts be reused or replaced independently?
        - Configuration: Props allow customization without code changes?
        - Scalability: Will it perform well with more data or features?
        - Future-proofing: Built with modern patterns that will age well?

        ## Output Format:
        Provide a structured analysis with:
        - Dimension scores (1-10)
        - Specific strengths and weaknesses for each dimension
        - Overall PURE score (average of four dimensions)
        - Critical issues that impact multiple dimensions

        Be thorough but concise. Focus on actionable insights that lead to concrete improvements.
        """
        
        try:
            response = self.gemini_client.model.generate_content(pure_prompt)
            return response.text
        except Exception as e:
            print(f"❌ Nova PURE analysis failed: {e}")
            return "PURE analysis unavailable due to technical error."
    
    def _get_nova_pure_improvements(self, component_code, requirements, pure_analysis):
        """Get Nova's PURE-based improvement recommendations"""
        print("💡 Nova generating PURE-based improvements...")
        
        improvements_prompt = f"""
        As Nova, a PURE Framework methodology expert, provide specific, actionable improvement recommendations:

        ORIGINAL REQUIREMENTS:
        {requirements}

        COMPONENT CODE:
        ```jsx
        {component_code}
        ```

        YOUR PURE ANALYSIS:
        {pure_analysis}

        ## Improvement Instructions:

        Based on your PURE analysis, provide specific improvements organized by dimension:

        ### PURPOSEFUL Improvements:
        - Features to add/modify to better meet requirements
        - Scope refinements to improve focus
        - User value enhancements

        ### USABLE Improvements:
        - Specific accessibility fixes (ARIA labels, keyboard navigation, color contrast)
        - UX enhancements (loading states, error messages, visual feedback)
        - Interaction improvements

        ### READABLE Improvements:
        - Code structure optimizations
        - TypeScript enhancements
        - Documentation additions
        - Naming improvements

        ### EXTENSIBLE Improvements:
        - Prop interface enhancements for flexibility
        - Modular architecture suggestions
        - Performance optimizations
        - Future-proofing recommendations

        ## Implementation Priority:
        Rank improvements by:
        1. Critical (must fix) - Major accessibility, functionality, or architectural issues
        2. High (should fix) - Significant UX or maintainability improvements  
        3. Medium (nice to have) - Polish and optimization opportunities

        Provide specific code examples where helpful. Focus on improvements that enhance multiple PURE dimensions simultaneously.
        """
        
        try:
            response = self.gemini_client.model.generate_content(improvements_prompt)
            return response.text
        except Exception as e:
            print(f"❌ Nova PURE improvements failed: {e}")
            return "PURE improvements unavailable due to technical error."


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
    result = crew.create_component(requirements, max_iterations=1)
    
    if result:
        print(f"\n✅ Component creation completed!")
        print(f"Final score: {result['final_score']}/10")
        print(f"Iterations: {result['iterations']}")
        print(f"Component type: {result['component_type']}")
        print(f"Component code length: {len(result['component_code'])} characters")
        print(f"Icon suggestions: {len(result['icon_suggestions']['icons'])}")
        return True
    else:
        print("\n❌ Component creation failed")
        return False


if __name__ == "__main__":
    test_crew()