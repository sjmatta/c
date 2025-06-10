# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **intelligent React component creation system** that integrates OpenUI, CrewAI, and Google Gemini to automatically generate, analyze, and refine React components through iterative improvement workflows. The system now includes enhanced design capabilities with **icon library integration** and **AI-generated placeholder images** for richer component development.

## Core Architecture

### Multi-Service Integration
- **OpenUI** (localhost:7878): Component generation via `/v1/chat/completions` with SSE streaming
- **CrewAI**: Multi-agent orchestration system with 3 specialized agents
- **Google Gemini**: Deep component analysis using either Standard or PURE framework

### Agent System Design
The system uses CrewAI to orchestrate specialized agents in `crew_agents.py`:
- **Aria** (Component Designer): Interfaces with OpenUI for initial component generation with enhanced design capabilities
- **Phoenix/Quinn** (Quality Analyst): Performs quality assessment (configurable framework)
- **Nova** (Refiner): Iteratively improves components based on analysis feedback (currently disabled to prevent token overflow)

**Note**: Test generation has been removed for simplified workflow.

### Enhanced Design Capabilities
- **Icon Library Manager** (`icon_library.py`): Provides context-aware icon suggestions for Heroicons, Lucide React, and Tabler Icons
- **AI-Generated Images**: Uses contextual placeholder images via placehold.co with component-specific colors and text
- **Component Type Detection**: Automatically identifies component types (button, table, card, form, navigation) for targeted enhancement
- **Rich Metadata Output**: Enhanced result structure includes icon suggestions, image URLs, and enhancement recommendations

### Analysis Frameworks
Two analysis approaches are available:
- **Standard Framework** (default): 6-dimension evaluation (functionality, code quality, accessibility, performance, UX, missing features)
- **PURE Framework** (optional): Structured evaluation of Purposeful, Usable, Readable, Extensible dimensions

## Essential Commands

### Setup and Prerequisites
```bash
# Complete setup (install deps + get OpenUI cookies)
make setup

# Get authentication cookies from OpenUI frontend
make get-cookies

# Verify system health (OpenUI connection, dependencies, cookies)
make health-check
```

### Component Creation
```bash
# Quick test (1 iteration, ~90 seconds)
make simple

# Full demo (2 iterations, ~3 minutes)  
make demo

# PURE framework analysis
make pure-demo

# Custom component creation
make create REQUIREMENTS='Your custom requirements' ITERATIONS=3

# Predefined components with optimized prompts
make button    # Modern button with variants, loading states, accessibility
make card      # User profile card with hover effects
make toggle    # Toggle switch with animations and keyboard support
make table     # Data table with sorting, filtering, pagination
```

### Testing and Development
```bash
# Test API connectivity
make test-apis        # Both OpenUI and Gemini
make test-openui      # OpenUI connection only
make test-gemini      # Gemini API only

# Generate interactive HTML preview from existing results
make preview

# Performance benchmarking
make benchmark
```

## Authentication and Environment

### Required Environment Variables
- `GEMINI_API_KEY`: Google Gemini API key (never commit to repo)
- `USE_PURE_FRAMEWORK`: Optional framework selection (true/false)

### Authentication Flow
1. **OpenUI Cookies**: `get_openui_cookie.py` uses Selenium to extract session cookies from localhost:7878
2. **Cookie Storage**: Saved to `openui_cookies.json` (gitignored)
3. **API Key Loading**: Environment-based loading with fallbacks in clients

## Key Implementation Details

### OpenUI Integration with Automatic Continuation (`openui_client.py`)
OpenUI generates Tailwind-based React components with intelligent continuation support:
- **Automatic Truncation Handling**: Uses AST validation and conversation continuation to generate complete components
- **No Token Limit Restrictions**: Can generate arbitrarily complex components through iterative refinement
- **Self-Healing**: Automatically detects and fixes syntax errors through LLM collaboration
- OpenUI responds via SSE streaming with finish_reason detection:
```python
# New continuation-aware approach
def create_component_with_continuation(self, prompt, max_retries=3):
    conversation = [{"role": "user", "content": prompt}]
    accumulated_response = ""
    
    for attempt in range(max_retries + 1):
        response_data = self._make_api_call(conversation, model, max_tokens)
        accumulated_response += response_data["content"]
        
        validation = self.validator.validate_component(accumulated_response)
        if validation["status"] == "COMPLETE":
            return accumulated_response
        elif validation["status"] == "TRUNCATED":
            conversation.extend([
                {"role": "assistant", "content": response_data["content"]},
                {"role": "user", "content": "Please continue from exactly where you left off."}
            ])
```

### Framework Selection (`main.py`, `crew_agents.py`)
The system supports switching between analysis frameworks:
- CLI flags: `--pure`, `--framework=pure/standard`
- Environment variable: `USE_PURE_FRAMEWORK`
- Constructor parameter in `ComponentCreationCrew(use_pure_framework=True)`

### Score Extraction (`pure_analyst.py`)
PURE framework uses simple regex extraction for robust parsing:
```python
match = re.search(r'PURE_SCORE:\s*([0-9.]+)', analysis)
```

### Preview Generation (`unified_preview_generator.py`)
The system uses **Babel-transpiled React previews** with intelligent prop generation:
- **Babel Transpilation**: Converts TypeScript/JSX to browser-compatible JavaScript
- **Intelligent Prop Generation**: Automatically analyzes ANY React component to generate appropriate sample props
- **Browser Validation**: Uses Playwright to validate component rendering and catch errors

**CRITICAL**: The system supports ANY React component automatically - no manual updates needed for new component types.

### Intelligent Prop Generation (`intelligent_prop_generator.py`)
**Revolutionary multi-layered approach** that eliminates the need for hard-coded component type handling:

#### Analysis Layers (in order of preference):
1. **TypeScript Interface Analysis**: Parses `interface ComponentProps` definitions to extract prop types and generate contextual sample data
2. **Component Signature Analysis**: Analyzes prop destructuring patterns in component function signatures  
3. **Usage Pattern Analysis**: Detects how props are used (`.map()`, `.includes()`, property access) to infer data types
4. **AI-Powered Analysis**: Uses Gemini to analyze component structure and generate appropriate props
5. **Basic Inference**: Fallback pattern matching for common prop patterns

#### Key Features:
- **Universal Support**: Works with Timeline, Modal, Form, ProductCard, Carousel - ANY React component
- **Contextual Data**: Generates realistic sample data based on prop names and component context
- **Type-Aware**: Handles arrays, objects, strings, numbers, booleans, and union types
- **Extensible**: No manual updates required for new component types
- **Robust**: Multiple fallback layers ensure preview generation never fails

#### Before vs After:
```python
# OLD: Hard-coded, brittle
if 'table' in component_lower:
    props = {"data": [...]}  # Only worked for 4 component types!
else:
    return {}  # Empty props = crash!

# NEW: Intelligent, universal  
generator = IntelligentPropGenerator()
props = generator.generate_props(component_code, component_name)
# Works for ANY component automatically!
```

## Output Structure

Generated files follow consistent patterns:
- `component_result.json`: Complete analysis with code, scores, tests, and enhanced metadata
- `preview.html`: Interactive component demonstration
- Framework-specific outputs: `pure_*.json`, `pure_*.html`

### Enhanced Output Structure
The system now generates enriched metadata:
```json
{
  "component_code": "...",
  "final_analysis": "...", 
  "final_score": 8.5,
  "iterations": 1,
  "component_type": "table|button|card|form|navigation",
  "enhancement_suggestions": "AI-generated improvement recommendations",
  "icon_suggestions": {
    "primary_library": "heroicons",
    "icons": [{"name": "ChevronDownIcon", "usage": "...", "accessibility": "..."}],
    "import_statements": ["import { ChevronDownIcon } from '@heroicons/react/24/outline'"]
  },
  "placeholder_images": {
    "primary": "https://placehold.co/400x300/8B5CF6/FFFFFF?text=Card",
    "alternatives": ["300x200 variant", "600x400 variant"]
  }
}
```

**Note**: The `"tests"` field has been removed as test generation is disabled.

## Testing Strategy

**Note**: Test generation has been disabled for simplified workflow. The system focuses on component generation and analysis without automated test creation.

## Development Notes

### Framework Switching
When modifying framework behavior, ensure changes are made in:
1. `main.py`: CLI argument parsing
2. `crew_agents.py`: Agent initialization and analysis routing  
3. Respective analyst files: `gemini_client.py` or `pure_analyst.py`

### Adding New Component Templates
New predefined components should be added to `Makefile` with:
- Descriptive target name
- Optimized requirements prompt
- Appropriate iteration count
- Output file naming convention

### Intelligent Prop Generation Development
**NO MANUAL UPDATES NEEDED** for new component types! The system automatically supports ANY React component.

#### When to Modify IntelligentPropGenerator:
- **Never for new component types** - the system handles them automatically
- **Only for new prop analysis techniques** - e.g., adding support for new TypeScript syntax
- **Only for new data generation patterns** - e.g., adding specialized sample data generators

#### Adding New Analysis Layers:
1. Add new method to `IntelligentPropGenerator` class
2. Insert in the analysis chain in `generate_props()` method
3. Ensure proper fallback to next layer on failure
4. Test with diverse component types

#### Common Sample Data Patterns:
- **Arrays**: Always include 3-4 realistic items with `id`, `name`, and contextual properties
- **Objects**: Include commonly accessed properties based on usage analysis  
- **Strings**: Generate contextual content based on prop names (`title`, `description`, `email`, etc.)
- **Images**: Use `placehold.co` with appropriate dimensions and context-aware text

### Preview Generator Critical Requirements
**ALWAYS test preview generation after making changes to prevent JavaScript errors:**

1. **JSX-to-HTML Conversion Must Be Robust**:
   - Never leave React syntax like `onClick={}` in HTML output
   - Always ensure HTML attributes are properly quoted
   - Replace React expressions `{variable}` with actual values
   - Remove React comments `{/* */}` completely

2. **Testing Protocol**:
   - After any preview_generator.py changes, IMMEDIATELY test with: `python preview_generator.py result.json test.html && open test.html`
   - **CRITICAL**: Open browser developer tools (F12) and check the Console tab for JavaScript errors
   - **CRITICAL**: Actually look at the generated page - don't assume it works if the file opens
   - Verify component renders correctly and is interactive
   - If using React previews, ensure Babel can transpile the TypeScript syntax

3. **Common JSX-to-HTML Issues**:
   - **Complex React logic**: Components with `.map()`, loops, or complex state cannot be converted to static HTML
   - **Unquoted attributes**: `class=value` should be `class="value"`
   - **React events**: `onClick={handler}` should be removed entirely
   - **Missing quotes in dynamic attributes**: `alt={name}` should become `alt="John Doe"`
   - **Broken class names with "..."**: replace with actual Tailwind classes
   - **Invalid JavaScript expressions**: `{columns.map(...)}` in HTML causes JavaScript errors

4. **Complex Component Handling**:
   - For components with `.map()` or complex React logic, use `react_preview_generator.py` instead of static conversion
   - Table components should show sample data with working interactivity
   - Always provide working HTML that renders without JavaScript errors
   - Use Babel transpilation for TypeScript instead of manual syntax stripping

### Error Handling
The system handles common failures gracefully:
- OpenUI connection issues
- Gemini API rate limits  
- SSE stream interruptions
- Score extraction failures (falls back to neutral scores)
- **Preview generation failures** (must be caught and fixed immediately)

## Security Considerations

### Walled Garden Dependency Management
The system implements a **Walled Garden security architecture** to prevent dependency violations:

**Approved Dependencies:**
- `react` (available globally as React)
- `react-dom` (available globally as ReactDOM)  
- `lodash` (available globally as _)
- Tailwind CSS classes only

**Security Enforcement:**
- `ast_validator.py`: Validates all imports against approved dependency list
- `openui_client.py`: Automatic detection and remediation of dependency violations
- `crew_agents.py`: Enhanced prompts with explicit security constraints
- `component-library.md`: Documentation of approved patterns and restrictions

**Automatic Remediation:**
When disallowed dependencies are detected (e.g., react-table, moment, d3), the system:
1. Detects violations during AST validation
2. Automatically requests component rewrite using only approved dependencies
3. Guides AI to implement functionality manually using approved libraries
4. Validates final result to ensure compliance

**Proven Success:**
- ✅ Prevents "useTable is not defined" errors
- ✅ Catches FontAwesome, react-table, d3 violations  
- ✅ Self-healing through AI collaboration
- ✅ Maintains functionality while enforcing security

**API Security:**
- API keys are loaded from environment variables only
- `.env` and API key files are gitignored
- Cookie files contain session data and should not be committed
- Test functions may contain hardcoded API keys for development - these should be removed before production use