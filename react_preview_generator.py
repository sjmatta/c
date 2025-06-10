#!/usr/bin/env python3
"""
Generate React-based preview pages that can actually render the components
"""

import json
import re
import os
from pathlib import Path


def extract_component_code(component_text):
    """Extract JSX code from the component text"""
    jsx_pattern = r'```(?:jsx|javascript|js|tsx|typescript)\n(.*?)\n```'
    matches = re.findall(jsx_pattern, component_text, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    
    return component_text.strip()


def extract_component_name(jsx_code):
    """Extract the component name from JSX code"""
    # Look for React component patterns
    patterns = [
        r'const\s+(\w+)\s*:\s*React\.FC',
        r'const\s+(\w+)\s*=.*?=>', 
        r'function\s+(\w+)\s*\(',
        r'export\s+default\s+(\w+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, jsx_code)
        if match:
            return match.group(1)
    
    return 'Component'


def create_react_preview_page(component_code, component_name="Component", score=None, iterations=None, analysis_text=None):
    """Create a full React application page that can render the component"""
    
    # Extract imports and clean component code
    imports = []
    clean_code = component_code
    
    # Extract import statements
    import_matches = re.findall(r'import.*?;', component_code, re.MULTILINE)
    for imp in import_matches:
        if 'React' in imp:
            imports.append(imp)
        elif '@heroicons' in imp:
            imports.append(imp.replace('@heroicons/react/24/outline', 'https://cdn.skypack.dev/@heroicons/react/outline'))
    
    # Generate sample data based on component type
    sample_data = generate_sample_data(component_name, component_code)
    
    # Create the preview page
    preview_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{component_name} Preview</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        
        .preview-header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .component-demo {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .code-viewer {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        
        pre {{
            background: #2d3748;
            color: #e2e8f0;
            padding: 16px;
            border-radius: 4px;
            overflow-x: auto;
            font-family: 'Fira Code', 'SF Mono', Consolas, monospace;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="preview-header">
        <h1>🎨 {component_name} Preview</h1>
        <p>Live React Component Demo</p>
        {generate_score_display(score, iterations)}
    </div>
    
    <div class="component-demo">
        <div id="component-root"></div>
    </div>
    
    <div class="code-viewer">
        <h3>📋 Component Code</h3>
        <pre><code>{component_code.replace('<', '&lt;').replace('>', '&gt;')}</code></pre>
        {f'<h3>📊 Analysis</h3><pre style="white-space: pre-wrap; background: #f8f9fa; color: #333; padding: 20px;"><code>{analysis_text.replace("<", "&lt;").replace(">", "&gt;") if analysis_text else ""}</code></pre>' if analysis_text else ''}
    </div>

    <script type="text/babel" data-type="module">
        const {{ useState, useEffect }} = React;
        
        // Mock any missing dependencies
        const lodash = {{ orderBy: (arr, key, direction) => [...arr].sort((a, b) => {{
            if (direction === 'desc') return b[key] > a[key] ? 1 : -1;
            return a[key] > b[key] ? 1 : -1;
        }}) }};
        
        // Sample data
        {sample_data}
        
        // Component code (cleaned up)
        {clean_component_code(component_code)}
        
        // Demo App
        function DemoApp() {{
            return (
                <div className="w-full">
                    {generate_demo_usage(component_name, component_code)}
                </div>
            );
        }}
        
        // Render the demo
        ReactDOM.render(<DemoApp />, document.getElementById('component-root'));
    </script>
</body>
</html>"""
    
    return preview_html


def generate_sample_data(component_name, component_code):
    """Generate appropriate sample data for the component"""
    component_lower = component_name.lower()
    
    if 'table' in component_lower or 'data' in component_lower:
        return """
        const sampleData = [
            { id: 1, name: 'John Doe', age: 32, position: 'Software Engineer', email: 'john@example.com' },
            { id: 2, name: 'Jane Smith', age: 28, position: 'UX Designer', email: 'jane@example.com' },
            { id: 3, name: 'Bob Wilson', age: 35, position: 'Product Manager', email: 'bob@example.com' },
            { id: 4, name: 'Alice Brown', age: 29, position: 'Data Scientist', email: 'alice@example.com' }
        ];
        
        const sampleColumns = [
            { header: 'Name', accessor: 'name' },
            { header: 'Age', accessor: 'age' },
            { header: 'Position', accessor: 'position' },
            { header: 'Email', accessor: 'email' }
        ];
        """
    elif 'card' in component_lower or 'profile' in component_lower:
        return """
        const sampleProfile = {
            name: 'John Doe',
            avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
            profession: 'Software Engineer',
            occupation: 'Software Engineer',
            bio: 'Passionate developer who loves creating amazing user experiences.',
            onFollow: () => alert('Following!'),
            onMessage: () => alert('Message sent!')
        };
        """
    else:
        return """
        const sampleProps = {
            onClick: () => alert('Button clicked!'),
            children: 'Click Me',
            label: 'Sample Button'
        };
        """


def clean_component_code(component_code):
    """Clean up component code for browser execution"""
    # Extract only the JSX code from the component_code
    jsx_code = extract_component_code(component_code)
    
    # Remove import statements (we'll handle dependencies differently)
    cleaned = re.sub(r'import.*?;', '', jsx_code, flags=re.MULTILINE)
    
    # Remove TypeScript interfaces completely
    cleaned = re.sub(r'interface\s+\w+\s*\{[^}]*\}', '', cleaned, flags=re.DOTALL)
    
    # Remove TypeScript type annotations from function parameters and variables
    cleaned = re.sub(r':\s*React\.FC<[^>]*>', '', cleaned)
    cleaned = re.sub(r':\s*\w+(\[\])?(?=[,\)\s=])', '', cleaned)
    
    # Replace lodash import with our mock
    cleaned = re.sub(r'orderBy', 'lodash.orderBy', cleaned)
    
    # Remove export statement
    cleaned = re.sub(r'export default.*?;', '', cleaned)
    
    # Clean up extra whitespace
    cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
    
    return cleaned.strip()


def generate_demo_usage(component_name, component_code):
    """Generate appropriate demo usage based on component type"""
    component_lower = component_name.lower()
    
    if 'table' in component_lower or 'data' in component_lower:
        return f"<{component_name} data={{sampleData}} columns={{sampleColumns}} />"
    elif 'card' in component_lower or 'profile' in component_lower:
        return f"<{component_name} {{...sampleProfile}} />"
    else:
        return f"<{component_name} {{...sampleProps}} />"


def generate_score_display(score, iterations):
    """Generate score display HTML"""
    if score is None:
        return ""
    
    score_color = "#28a745" if score >= 8 else "#fd7e14" if score >= 6 else "#dc3545"
    
    return f"""
    <div style="margin-top: 15px;">
        <div style="display: inline-block; background: {score_color}; color: white; padding: 12px 20px; border-radius: 8px; margin-right: 15px;">
            <div style="font-size: 20px; font-weight: bold;">{score:.1f}/10</div>
            <div style="font-size: 12px; opacity: 0.9;">Quality Score</div>
        </div>
        {f'<div style="display: inline-block; background: #007bff; color: white; padding: 12px 20px; border-radius: 8px;"><div style="font-size: 20px; font-weight: bold;">{iterations}</div><div style="font-size: 12px; opacity: 0.9;">Iterations</div></div>' if iterations is not None else ''}
    </div>
    """


def generate_react_preview_from_result(result_file, output_file):
    """Generate React preview from result JSON file"""
    try:
        with open(result_file, 'r') as f:
            result = json.load(f)
        
        component_code = result.get('component_code', '')
        if not component_code:
            print(f"❌ No component code found in {result_file}")
            return False
        
        # Extract actual JSX code
        jsx_code = extract_component_code(component_code)
        component_name = extract_component_name(jsx_code)
        
        # Get metadata
        score = result.get('final_score')
        iterations = result.get('iterations')
        analysis_text = result.get('final_analysis')
        
        # Generate React preview
        html_content = create_react_preview_page(
            jsx_code, 
            component_name, 
            score=score, 
            iterations=iterations, 
            analysis_text=analysis_text
        )
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"✅ React preview generated: {output_file}")
        print(f"📊 Component: {component_name}")
        print(f"📊 Score: {score}/10" if score else "📊 Score: N/A")
        print(f"🔄 Iterations: {iterations}" if iterations else "🔄 Iterations: N/A")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Result file not found: {result_file}")
        return False
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in result file: {result_file}")
        return False
    except Exception as e:
        print(f"❌ Error generating React preview: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    result_file = sys.argv[1] if len(sys.argv) > 1 else "table_result.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "react_preview.html"
    
    if generate_react_preview_from_result(result_file, output_file):
        print(f"\\n🌐 Open {output_file} in your browser to see the live React component!")
    else:
        print("\\n💥 React preview generation failed!")