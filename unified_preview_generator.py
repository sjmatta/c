#!/usr/bin/env python3
"""
Unified Preview Generator with Babel transpilation - No more regex!
Uses proper Babel transpilation to handle TypeScript/JSX conversion.
"""

import json
import re
import os
import subprocess
import tempfile
from pathlib import Path
import sys

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def extract_component_code(component_text):
    """Extract JSX code from the component text - simplified since OpenUI now handles continuation"""
    if not component_text:
        return ""
    
    print("🔍 Extracting component code (with continuation support)")
    
    # Look for JSX code blocks (components should be complete now thanks to continuation)
    jsx_pattern = r'```(?:jsx|javascript|js|tsx|typescript)\n(.*?)\n```'
    matches = re.findall(jsx_pattern, component_text, re.DOTALL)
    
    if matches:
        # Take the longest match (usually the main component)
        longest_match = max(matches, key=len)
        print(f"✅ Found complete code block, length: {len(longest_match)}")
        return longest_match.strip()
    
    # Handle case where markdown markers might be missing
    # Look for React component patterns directly
    react_pattern = r'(import React.*?export default \w+;)'
    match = re.search(react_pattern, component_text, re.DOTALL)
    
    if match:
        print(f"✅ Found React component pattern, length: {len(match.group(1))}")
        return match.group(1).strip()
    
    # Fallback: look for component definition without imports
    component_pattern = r'((?:const|function)\s+[A-Z]\w*.*?export default [A-Z]\w*;)'
    match = re.search(component_pattern, component_text, re.DOTALL)
    
    if match:
        # Add basic React import
        component_code = f"import React from 'react';\n\n{match.group(1).strip()}"
        print(f"✅ Found component definition, added React import, length: {len(component_code)}")
        return component_code
    
    # If no patterns match, return the text as-is (might be a complete component without markdown)
    print(f"⚠️  No patterns matched, returning raw text, length: {len(component_text)}")
    return component_text.strip()


# Note: fix_truncated_component function removed since we now handle 
# truncation at the API level with continuation


def extract_component_name(code):
    """Extract the component name from React code"""
    if not code:
        return 'Component'
    
    # Look for export default ComponentName;
    match = re.search(r'export\s+default\s+(\w+)\s*;', code)
    if match:
        return match.group(1)
    
    # Look for const ComponentName = 
    match = re.search(r'const\s+([A-Z][A-Za-z0-9_]*)\s*[:=]', code)
    if match:
        return match.group(1)
    
    # Look for function ComponentName
    match = re.search(r'function\s+([A-Z][A-Za-z0-9_]*)\s*\(', code)
    if match:
        return match.group(1)
    
    return 'Component'


def transpile_component_with_babel(component_code, component_name):
    """Use Babel CLI to transpile TypeScript/JSX to browser-compatible JavaScript"""
    
    # Prepare the component code for transpilation
    # Remove imports/exports and make it a standalone component
    prepared_code = component_code
    
    # Remove all import statements (including CSS imports with comments)
    prepared_code = re.sub(r'^import\s+.*?;?\s*(?://.*)?$', '', prepared_code, flags=re.MULTILINE)
    
    # Remove export statements and assign to window for global access
    prepared_code = re.sub(r'export\s+default\s+(\w+)\s*;', f'window.{component_name} = \\1;', prepared_code)
    
    # Add React destructuring at the top
    prepared_code = '''
const { useState, useEffect, useCallback, useMemo } = React;
const { orderBy } = _;

''' + prepared_code
    
    try:
        # Check if babel is available
        babel_check = subprocess.run(['npx', 'babel', '--version'], 
                                   capture_output=True, text=True, timeout=10)
        
        if babel_check.returncode != 0:
            print("⚠️  Babel CLI not available, falling back to basic cleaning")
            return clean_component_basic(prepared_code)
        
        # Create temporary files for Babel transpilation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsx', delete=False) as input_file:
            input_file.write(prepared_code)
            input_path = input_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as output_file:
            output_path = output_file.name
        
        # Use Babel to transpile TypeScript/JSX to ES5
        babel_cmd = [
            'npx', 'babel', 
            input_path,
            '--out-file', output_path,
            '--presets', '@babel/preset-typescript,@babel/preset-react'
        ]
        
        result = subprocess.run(babel_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Read the transpiled output
            with open(output_path, 'r') as f:
                transpiled_code = f.read()
            
            # Clean up temp files
            os.unlink(input_path)
            os.unlink(output_path)
            
            print("✅ Babel transpilation successful")
            return transpiled_code
        else:
            print(f"❌ Babel transpilation failed: {result.stderr}")
            print("Falling back to basic cleaning")
            
            # Clean up temp files
            os.unlink(input_path)
            os.unlink(output_path)
            
            return clean_component_basic(prepared_code)
            
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"❌ Babel execution failed: {e}")
        print("Falling back to basic cleaning")
        return clean_component_basic(prepared_code)


def clean_component_basic(code):
    """Basic fallback cleaning for when Babel is not available"""
    if not code:
        return ""
    
    print("🧹 Applying basic cleaning (removing imports and TypeScript syntax)")
    
    # Remove all import statements (including CSS imports with comments)
    code = re.sub(r'^import\s+.*?;?\s*(?://.*)?$', '', code, flags=re.MULTILINE)
    
    # Remove interface definitions
    code = re.sub(r'interface\s+\w+\s*\{[^}]*\}', '', code, flags=re.DOTALL)
    
    # Remove type annotations from function parameters and variables
    code = re.sub(r':\s*React\.FC\b[^=]*', '', code)
    code = re.sub(r':\s*(string|number|boolean|any)\b', '', code)
    code = re.sub(r':\s*keyof\s+\w+', '', code)
    code = re.sub(r':\s*[A-Z]\w*\[\]', '', code)
    code = re.sub(r':\s*\'[^\']*\'[\s]*\|[\s]*\'[^\']*\'', '', code)  # Remove union types like 'asc' | 'desc'
    
    # Remove generic type parameters
    code = re.sub(r'<[^>]*>', '', code)
    
    # Fix common sorting issues - add guard for empty sortedColumn
    code = re.sub(
        r'return \[\.\.\.\s*data\]\s*\.sort\(\s*\(a,\s*b\)\s*=>\s*\{',
        'return sortedColumn ? [...data].sort((a, b) => {',
        code
    )
    
    # Also need to close the conditional
    if 'return sortedColumn ?' in code:
        code = re.sub(
            r'(\}\s*\)\s*;\s*\}\s*,\s*\[.*?\]\s*\)\s*;)',
            r'\1 : data;',
            code
        )
    
    # Clean up multiple empty lines
    code = re.sub(r'\n\s*\n\s*\n', '\n\n', code)
    
    return code.strip()


def include_component_library():
    """Include our custom component library in the preview"""
    
    # Transpiled Pagination component (simplified for preview)
    pagination_component = """
// Custom Pagination Component (transpiled)
const Pagination = ({ currentPage, totalPages, onPageChange, className = "" }) => {
  const cn = (...classes) => classes.filter(Boolean).join(' ');
  
  const baseButtonClasses = "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2";
  const regularButtonClasses = baseButtonClasses + " h-10 px-4 py-2 border border-gray-300 bg-white hover:bg-gray-100";
  const numberButtonClasses = baseButtonClasses + " h-10 w-10 border border-gray-300 bg-white hover:bg-gray-100";
  const activeButtonClasses = "bg-blue-600 text-white hover:bg-blue-600/90";
  const disabledButtonClasses = "opacity-50 cursor-not-allowed";

  return React.createElement("div", 
    { className: cn("flex items-center justify-center gap-2 py-4", className) },
    
    // Previous Button
    React.createElement("button", {
      className: cn(regularButtonClasses, currentPage === 1 && disabledButtonClasses),
      disabled: currentPage === 1,
      onClick: () => onPageChange(currentPage - 1),
      "aria-label": "Go to previous page"
    }, "Previous"),
    
    // Page Numbers
    ...Array.from({ length: totalPages }, (_, index) => {
      const pageNumber = index + 1;
      const isActive = currentPage === pageNumber;
      
      return React.createElement("button", {
        key: pageNumber,
        className: cn(
          numberButtonClasses,
          isActive && activeButtonClasses,
          !isActive && "hover:bg-gray-100"
        ),
        onClick: () => onPageChange(pageNumber),
        "aria-current": isActive ? "page" : undefined,
        "aria-label": `Go to page ${pageNumber}`
      }, pageNumber);
    }),
    
    // Next Button
    React.createElement("button", {
      className: cn(regularButtonClasses, currentPage === totalPages && disabledButtonClasses),
      disabled: currentPage === totalPages,
      onClick: () => onPageChange(currentPage + 1),
      "aria-label": "Go to next page"
    }, "Next")
  );
};

// Make Pagination available globally
window.Pagination = Pagination;
"""
    
    return pagination_component

def generate_sample_props(component_code, component_name):
    """Generate appropriate sample props based on component analysis"""
    
    props = {}
    component_lower = component_name.lower()
    
    if 'table' in component_lower or 'datatable' in component_lower:
        props = {
            "data": [
                {"id": "1", "name": "John Doe", "age": 32, "email": "john@example.com"},
                {"id": "2", "name": "Jane Smith", "age": 28, "email": "jane@example.com"},
                {"id": "3", "name": "Bob Wilson", "age": 35, "email": "bob@example.com"},
                {"id": "4", "name": "Alice Brown", "age": 29, "email": "alice@example.com"}
            ],
            "columns": [
                {"label": "ID", "key": "id"},
                {"label": "Name", "key": "name"},
                {"label": "Age", "key": "age"},
                {"label": "Email", "key": "email"}
            ]
        }
    elif 'button' in component_lower:
        props = {
            "text": "Click me!",
            "label": "Click me!",
            "children": "Click me!",
            "variant": "primary",
            "size": "medium",
            "disabled": False,
            "ariaLabel": "Click me button"
        }
    elif 'card' in component_lower:
        props = {
            "title": "Sample Card",
            "description": "This is a sample card component with some descriptive text.",
            "imageUrl": "https://via.placeholder.com/300x200",
            "author": "John Doe",
            "date": "2024-01-15"
        }
    
    return props


def create_babel_preview_html(transpiled_code, component_name, sample_props, score, iterations, analysis):
    """Create the HTML preview with transpiled JavaScript (no Babel needed in browser)"""
    
    props_json = json.dumps(sample_props, indent=2)
    analysis_preview = analysis[:500] + "..." if len(analysis) > 500 else analysis
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{component_name} Preview</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- React and ReactDOM -->
    <script src="https://unpkg.com/react@18/umd/react.development.js" crossorigin></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js" crossorigin></script>
    
    <!-- PropTypes -->
    <script src="https://unpkg.com/prop-types@15/prop-types.min.js" crossorigin></script>
    
    <!-- Lodash -->
    <script src="https://unpkg.com/lodash@4/lodash.min.js" crossorigin></script>
    
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .preview-section {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        .metrics {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .metric {{
            background: #007bff;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            text-align: center;
            min-width: 120px;
        }}
        
        .metric.score {{
            background: #fd7e14;
        }}
        
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
        }}
        
        .metric-label {{
            font-size: 12px;
            opacity: 0.9;
        }}
        
        .error-display {{
            background: #fee;
            border: 1px solid #fcc;
            color: #800;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
            font-family: monospace;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 {component_name} Preview</h1>
        <p>Generated by Babel-Transpiled React Preview System</p>
        
        <div class="metrics">
            <div class="metric score">
                <div class="metric-value">{score}/10</div>
                <div class="metric-label">Quality Score</div>
            </div>
            <div class="metric">
                <div class="metric-value">{iterations}</div>
                <div class="metric-label">Iterations</div>
            </div>
        </div>
    </div>
    
    <div class="preview-section">
        <h2>📱 Live Component Preview</h2>
        <div id="component-root" style="min-height: 200px;">
            Loading component...
        </div>
    </div>
    
    <div class="preview-section">
        <h2>📊 Component Analysis</h2>
        <pre style="line-height: 1.6; color: #666; white-space: pre-wrap; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">{analysis_preview}</pre>
    </div>
    
    <!-- Error display for debugging -->
    <div id="error-display" class="error-display" style="display: none;"></div>
    
    <script>
        // Error handling
        window.addEventListener('error', (e) => {{
            const errorDiv = document.getElementById('error-display');
            errorDiv.style.display = 'block';
            errorDiv.innerHTML = `
                <strong>JavaScript Error:</strong><br>
                ${{e.message}}<br>
                <strong>File:</strong> ${{e.filename}}:${{e.lineno}}<br>
                <strong>Stack:</strong><br>
                <pre>${{e.error ? e.error.stack : 'No stack trace available'}}</pre>
            `;
        }});
        
        try {{
            // Transpiled component code (no Babel needed in browser)
            {transpiled_code}
            
            // Sample props for the component
            const sampleProps = {props_json};
            
            // Demo wrapper component
            const DemoApp = () => {{
                return React.createElement('div', {{ style: {{ padding: '20px' }} }},
                    React.createElement(window.{component_name}, sampleProps)
                );
            }};
            
            // Render the component using vanilla React (no JSX)
            const container = document.getElementById('component-root');
            const root = ReactDOM.createRoot(container);
            root.render(React.createElement(DemoApp));
            
        }} catch (error) {{
            console.error('Component rendering error:', error);
            const errorDiv = document.getElementById('error-display');
            errorDiv.style.display = 'block';
            errorDiv.innerHTML = `
                <strong>Component Error:</strong><br>
                ${{error.message}}<br>
                <strong>Stack:</strong><br>
                <pre>${{error.stack}}</pre>
            `;
            
            const container = document.getElementById('component-root');
            container.innerHTML = `
                <div style="color: red; padding: 20px; border: 2px dashed red; border-radius: 8px;">
                    <h3>⚠️ Component Failed to Render</h3>
                    <p>There was an error rendering the {component_name} component.</p>
                    <p>Check the error details above for debugging information.</p>
                </div>
            `;
        }}
    </script>
</body>
</html>'''


def validate_preview_in_browser(html_file_path, timeout_ms=10000):
    """Use Playwright to check for console errors in the generated preview"""
    
    if not PLAYWRIGHT_AVAILABLE:
        print("⚠️  Playwright not available. Skipping browser validation.")
        return True
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            errors = []
            warnings = []
            
            def handle_console(msg):
                if msg.type == 'error':
                    errors.append(f"CONSOLE ERROR: {msg.text}")
                elif msg.type == 'warning':
                    warnings.append(f"CONSOLE WARNING: {msg.text}")
            
            def handle_page_error(exc):
                errors.append(f"PAGE ERROR: {exc}")
            
            page.on("console", handle_console)
            page.on("pageerror", handle_page_error)
            
            html_path = Path(html_file_path).resolve()
            uri = html_path.as_uri()
            
            print(f"🔍 Validating preview in browser: {html_path.name}")
            
            page.goto(uri, timeout=timeout_ms)
            page.wait_for_timeout(3000)  # Wait for React to render
            
            # Check if component rendered
            component_root = page.query_selector('#component-root')
            if component_root:
                content = component_root.inner_text()
                if content.strip() and "Loading component" not in content:
                    print(f"✅ Component rendered successfully")
                else:
                    errors.append("Component appears to be stuck loading")
            else:
                errors.append("Component root element not found")
            
            browser.close()
            
            if warnings:
                print("⚠️  Browser warnings (ignorable):")
                for warning in warnings[:2]:  # Limit to 2 warnings
                    print(f"    {warning}")
            
            if errors:
                print("❌ Browser validation failed:")
                for error in errors:
                    print(f"    {error}")
                return False
            
            print("✅ Browser validation successful!")
            return True
            
    except Exception as e:
        print(f"❌ Browser validation exception: {e}")
        return False


def create_unified_preview(result_file, output_file):
    """Generate a React-based preview using Babel transpilation"""
    
    try:
        with open(result_file, 'r') as f:
            result = json.load(f)
        
        component_code = result.get('component_code', '')
        if not component_code:
            print(f"❌ No component code found in {result_file}")
            return False
        
        # Extract clean component code
        clean_code = extract_component_code(component_code)
        component_name = extract_component_name(clean_code)
        
        print(f"🔧 Transpiling {component_name} component with Babel...")
        
        # Transpile using Babel
        transpiled_code = transpile_component_with_babel(clean_code, component_name)
        
        # Generate sample props
        sample_props = generate_sample_props(clean_code, component_name)
        
        # Get metadata
        score = result.get('final_score', 'N/A')
        iterations = result.get('iterations', 'N/A')
        analysis = result.get('final_analysis', 'No analysis available')
        
        # Create the preview HTML
        preview_html = create_babel_preview_html(
            transpiled_code, 
            component_name, 
            sample_props, 
            score, 
            iterations, 
            analysis
        )
        
        # Write the preview file
        with open(output_file, 'w') as f:
            f.write(preview_html)
        
        print(f"✅ Babel-transpiled preview generated: {output_file}")
        print(f"📊 Component: {component_name}")
        print(f"📊 Score: {score}/10")
        print(f"🔄 Iterations: {iterations}")
        
        # Validate the preview in browser
        validation_success = validate_preview_in_browser(output_file)
        
        return validation_success
        
    except Exception as e:
        print(f"❌ Error generating preview: {e}")
        return False


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python unified_preview_generator_babel.py <result_file.json> <output_file.html>")
        sys.exit(1)
    
    result_file = sys.argv[1]
    output_file = sys.argv[2]
    
    success = create_unified_preview(result_file, output_file)
    sys.exit(0 if success else 1)