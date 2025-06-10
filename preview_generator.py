#!/usr/bin/env python3
"""
Generate interactive HTML preview of created components
"""

import json
import re
import os
from pathlib import Path


def extract_component_code(component_text):
    """Extract JSX code from the component text"""
    # Look for JSX code blocks
    jsx_pattern = r'```(?:jsx|javascript|js|tsx|typescript)\n(.*?)\n```'
    matches = re.findall(jsx_pattern, component_text, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    
    # Fallback: try to find React component pattern
    react_pattern = r'(import React.*?export default \w+;)'
    match = re.search(react_pattern, component_text, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    return component_text.strip()


def extract_css(component_text):
    """Extract CSS from the component text"""
    css_pattern = r'```css\n(.*?)\n```'
    matches = re.findall(css_pattern, component_text, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    
    return ""


def jsx_to_vanilla_js(jsx_code):
    """Convert JSX to vanilla JavaScript for browser preview"""
    # Simple JSX to vanilla JS conversion for preview
    # This is a basic conversion - for complex components, use a proper transpiler
    
    # Extract component name
    component_name_match = re.search(r'const\s+(\w+)\s*=', jsx_code)
    if not component_name_match:
        component_name_match = re.search(r'function\s+(\w+)\s*\(', jsx_code)
    
    component_name = component_name_match.group(1) if component_name_match else 'Component'
    
    # Create a simple vanilla JS version for demo
    vanilla_js = f"""
function {component_name}(props) {{
    const element = document.createElement('button');
    element.textContent = props.children || props.label || 'Click me!';
    element.className = 'button ' + (props.variant || 'primary');
    
    if (props.loading) {{
        element.textContent = 'Loading...';
        element.disabled = true;
    }}
    
    if (props.onClick) {{
        element.addEventListener('click', props.onClick);
    }}
    
    return element;
}}

// Create and mount the component
function renderComponent() {{
    const container = document.getElementById('component-container');
    container.innerHTML = '';
    
    // Example usage
    const component1 = {component_name}({{
        children: 'Primary Button',
        variant: 'primary',
        onClick: () => alert('Primary clicked!')
    }});
    
    const component2 = {component_name}({{
        children: 'Secondary Button', 
        variant: 'secondary',
        onClick: () => alert('Secondary clicked!')
    }});
    
    const component3 = {component_name}({{
        children: 'Loading Button',
        loading: true
    }});
    
    container.appendChild(component1);
    container.appendChild(document.createTextNode(' '));
    container.appendChild(component2);
    container.appendChild(document.createTextNode(' '));
    container.appendChild(component3);
}}
"""
    return vanilla_js


def create_html_preview(component_code, css_code="", component_name="Component"):
    """Create an interactive HTML preview"""
    
    vanilla_js = jsx_to_vanilla_js(component_code)
    
    # Default CSS if none provided
    if not css_code:
        css_code = """
.button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    margin: 8px;
    transition: all 0.3s ease;
}

.button:hover {
    background-color: #0056b3;
    transform: translateY(-2px);
}

.button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
    transform: none;
}

.button.primary {
    background-color: #007bff;
}

.button.secondary {
    background-color: #6c757d;
}

.button.danger {
    background-color: #dc3545;
}

.spinner {
    border: 2px solid #f3f3f3;
    border-top: 2px solid #3498db;
    border-radius: 50%;
    width: 16px;
    height: 16px;
    animation: spin 1s linear infinite;
    display: inline-block;
    margin-right: 8px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
"""
    
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{component_name} Preview</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
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
        
        .code-section {{
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
        
        .tabs {{
            display: flex;
            border-bottom: 1px solid #dee2e6;
            margin-bottom: 16px;
        }}
        
        .tab {{
            padding: 8px 16px;
            background: none;
            border: none;
            cursor: pointer;
            border-bottom: 2px solid transparent;
        }}
        
        .tab.active {{
            border-bottom-color: #007bff;
            color: #007bff;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        {css_code}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 {component_name} Preview</h1>
        <p>Generated by OpenUI + CrewAI + Gemini Integration</p>
    </div>
    
    <div class="preview-section">
        <h2>📱 Interactive Preview</h2>
        <div id="component-container" style="text-align: center; padding: 20px;">
            <!-- Components will be rendered here -->
        </div>
    </div>
    
    <div class="code-section">
        <h2>📋 Generated Code</h2>
        <div class="tabs">
            <button class="tab active" onclick="showTab('jsx')">JSX</button>
            <button class="tab" onclick="showTab('css')">CSS</button>
            <button class="tab" onclick="showTab('usage')">Usage</button>
        </div>
        
        <div id="jsx-content" class="tab-content active">
            <pre><code>{component_code.replace('<', '&lt;').replace('>', '&gt;')}</code></pre>
        </div>
        
        <div id="css-content" class="tab-content">
            <pre><code>{css_code}</code></pre>
        </div>
        
        <div id="usage-content" class="tab-content">
            <pre><code>// Basic usage
import {component_name} from './{component_name}';

function App() {{
  return (
    &lt;div&gt;
      &lt;{component_name} 
        label="Click me!"
        onClick={{() =&gt; alert('Clicked!')}}
      /&gt;
      
      &lt;{component_name}
        label="Loading"
        loading={{true}}
      /&gt;
    &lt;/div&gt;
  );
}}</code></pre>
        </div>
    </div>
    
    <script>
        {vanilla_js}
        
        // Tab functionality
        function showTab(tabName) {{
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Show selected tab content
            document.getElementById(tabName + '-content').classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }}
        
        // Render component on page load
        document.addEventListener('DOMContentLoaded', renderComponent);
    </script>
</body>
</html>
"""
    
    return html_template


def generate_preview_from_result(result_file="component_result.json", output_file="preview.html"):
    """Generate preview from result JSON file"""
    
    try:
        with open(result_file, 'r') as f:
            result = json.load(f)
        
        component_code = result.get('component_code', '')
        if not component_code:
            print(f"❌ No component code found in {result_file}")
            return False
        
        # Extract component name from code
        component_name_match = re.search(r'const\s+(\w+)\s*=', component_code)
        if not component_name_match:
            component_name_match = re.search(r'function\s+(\w+)\s*\(', component_code)
        
        component_name = component_name_match.group(1) if component_name_match else 'Component'
        
        # Extract CSS if present
        css_code = extract_css(component_code)
        
        # Generate HTML preview
        html_content = create_html_preview(component_code, css_code, component_name)
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"✅ Preview generated: {output_file}")
        print(f"📊 Component score: {result.get('final_score', 'N/A')}/10")
        print(f"🔄 Iterations: {result.get('iterations', 'N/A')}")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Result file not found: {result_file}")
        return False
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in result file: {result_file}")
        return False
    except Exception as e:
        print(f"❌ Error generating preview: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    result_file = sys.argv[1] if len(sys.argv) > 1 else "component_result.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "preview.html"
    
    if generate_preview_from_result(result_file, output_file):
        print(f"\n🌐 Open {output_file} in your browser to interact with the component!")
    else:
        print("\n💥 Preview generation failed!")