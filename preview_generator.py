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


def extract_pure_dimensions(analysis_text):
    """Extract individual PURE dimension scores from analysis text"""
    if not analysis_text:
        return None
    
    dimensions = {}
    
    # Extract P - PURPOSEFUL score
    p_match = re.search(r'## P - PURPOSEFUL \((\d+)/10\)', analysis_text)
    if p_match:
        dimensions['P'] = {'score': int(p_match.group(1)), 'name': 'Purposeful'}
    
    # Extract U - USABLE score  
    u_match = re.search(r'## U - USABLE \((\d+)/10\)', analysis_text)
    if u_match:
        dimensions['U'] = {'score': int(u_match.group(1)), 'name': 'Usable'}
    
    # Extract R - READABLE score
    r_match = re.search(r'## R - READABLE \((\d+)/10\)', analysis_text)
    if r_match:
        dimensions['R'] = {'score': int(r_match.group(1)), 'name': 'Readable'}
    
    # Extract E - EXTENSIBLE score
    e_match = re.search(r'## E - EXTENSIBLE \((\d+)/10\)', analysis_text)
    if e_match:
        dimensions['E'] = {'score': int(e_match.group(1)), 'name': 'Extensible'}
    
    return dimensions if dimensions else None


def jsx_to_vanilla_js(jsx_code):
    """Convert JSX to vanilla JavaScript for browser preview"""
    # Simple JSX to vanilla JS conversion for preview
    # This is a basic conversion - for complex components, use a proper transpiler
    
    # Extract component name
    component_name_match = re.search(r'const\s+(\w+)\s*=', jsx_code)
    if not component_name_match:
        component_name_match = re.search(r'function\s+(\w+)\s*\(', jsx_code)
    
    component_name = component_name_match.group(1) if component_name_match else 'Component'
    
    # Determine component type based on name and JSX content
    jsx_lower = jsx_code.lower()
    
    if 'table' in component_name.lower() or '<table' in jsx_lower:
        # Table component
        vanilla_js = f"""
function {component_name}(props) {{
    const container = document.createElement('div');
    container.style.cssText = 'width: 100%; overflow-x: auto; margin: 20px 0;';
    
    const table = document.createElement('table');
    table.style.cssText = 'width: 100%; border-collapse: collapse; border: 1px solid #ddd;';
    
    // Sample data for demo
    const sampleData = [
        {{ id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin' }},
        {{ id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'User' }},
        {{ id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'Editor' }}
    ];
    
    // Create header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    ['ID', 'Name', 'Email', 'Role', 'Actions'].forEach(text => {{
        const th = document.createElement('th');
        th.textContent = text;
        th.style.cssText = 'padding: 12px; background: #f8f9fa; border: 1px solid #ddd; text-align: left; font-weight: bold;';
        headerRow.appendChild(th);
    }});
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create body
    const tbody = document.createElement('tbody');
    sampleData.forEach(row => {{
        const tr = document.createElement('tr');
        tr.style.cssText = 'transition: background-color 0.2s;';
        tr.addEventListener('mouseenter', () => tr.style.backgroundColor = '#f8f9fa');
        tr.addEventListener('mouseleave', () => tr.style.backgroundColor = '');
        
        [row.id, row.name, row.email, row.role].forEach(text => {{
            const td = document.createElement('td');
            td.textContent = text;
            td.style.cssText = 'padding: 12px; border: 1px solid #ddd;';
            tr.appendChild(td);
        }});
        
        // Actions column
        const actionTd = document.createElement('td');
        actionTd.style.cssText = 'padding: 12px; border: 1px solid #ddd;';
        const editBtn = document.createElement('button');
        editBtn.textContent = 'Edit';
        editBtn.style.cssText = 'margin-right: 5px; padding: 4px 8px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer;';
        editBtn.onclick = () => alert(`Edit ${{row.name}}`);
        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete';
        deleteBtn.style.cssText = 'padding: 4px 8px; background: #dc3545; color: white; border: none; border-radius: 3px; cursor: pointer;';
        deleteBtn.onclick = () => alert(`Delete ${{row.name}}`);
        actionTd.appendChild(editBtn);
        actionTd.appendChild(deleteBtn);
        tr.appendChild(actionTd);
        
        tbody.appendChild(tr);
    }});
    table.appendChild(tbody);
    container.appendChild(table);
    
    return container;
}}

// Create and mount the component
function renderComponent() {{
    const container = document.getElementById('component-container');
    container.innerHTML = '';
    
    const component = {component_name}({{ data: [] }});
    container.appendChild(component);
}}
"""
    elif 'card' in component_name.lower() or 'profile' in jsx_lower:
        # Card component
        vanilla_js = f"""
function {component_name}(props) {{
    const card = document.createElement('div');
    card.style.cssText = 'max-width: 300px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); background: white;';
    
    const avatar = document.createElement('div');
    avatar.style.cssText = 'width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(45deg, #007bff, #0056b3); margin: 0 auto 16px; display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; font-weight: bold;';
    avatar.textContent = 'JD';
    
    const name = document.createElement('h3');
    name.textContent = props.name || 'John Doe';
    name.style.cssText = 'margin: 0 0 8px; text-align: center; color: #333;';
    
    const title = document.createElement('p');
    title.textContent = props.title || 'Software Engineer';
    title.style.cssText = 'margin: 0 0 16px; text-align: center; color: #666; font-size: 14px;';
    
    const bio = document.createElement('p');
    bio.textContent = props.bio || 'Passionate developer with expertise in React and modern web technologies.';
    bio.style.cssText = 'margin: 0 0 20px; text-align: center; color: #555; font-size: 13px; line-height: 1.4;';
    
    const followBtn = document.createElement('button');
    followBtn.textContent = 'Follow';
    followBtn.style.cssText = 'width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; transition: background 0.2s;';
    followBtn.onmouseover = () => followBtn.style.background = '#0056b3';
    followBtn.onmouseout = () => followBtn.style.background = '#007bff';
    followBtn.onclick = () => alert('Following user!');
    
    card.appendChild(avatar);
    card.appendChild(name);
    card.appendChild(title);
    card.appendChild(bio);
    card.appendChild(followBtn);
    
    return card;
}}

// Create and mount the component
function renderComponent() {{
    const container = document.getElementById('component-container');
    container.innerHTML = '';
    
    const component = {component_name}({{ name: 'John Doe', title: 'Software Engineer' }});
    container.appendChild(component);
}}
"""
    elif 'toggle' in component_name.lower() or 'switch' in jsx_lower:
        # Toggle component
        vanilla_js = f"""
function {component_name}(props) {{
    const container = document.createElement('div');
    container.style.cssText = 'display: flex; align-items: center; gap: 10px; margin: 20px;';
    
    const label = document.createElement('label');
    label.textContent = props.label || 'Toggle Switch';
    label.style.cssText = 'font-size: 14px; color: #333;';
    
    const toggleWrapper = document.createElement('div');
    toggleWrapper.style.cssText = 'position: relative; width: 50px; height: 24px; background: #ccc; border-radius: 12px; cursor: pointer; transition: background 0.3s;';
    
    const toggleKnob = document.createElement('div');
    toggleKnob.style.cssText = 'position: absolute; top: 2px; left: 2px; width: 20px; height: 20px; background: white; border-radius: 50%; transition: transform 0.3s; box-shadow: 0 1px 3px rgba(0,0,0,0.3);';
    
    let isOn = props.checked || false;
    
    function updateToggle() {{
        if (isOn) {{
            toggleWrapper.style.background = '#007bff';
            toggleKnob.style.transform = 'translateX(26px)';
        }} else {{
            toggleWrapper.style.background = '#ccc';
            toggleKnob.style.transform = 'translateX(0)';
        }}
    }}
    
    toggleWrapper.onclick = () => {{
        isOn = !isOn;
        updateToggle();
        if (props.onChange) props.onChange(isOn);
    }};
    
    updateToggle();
    
    toggleWrapper.appendChild(toggleKnob);
    container.appendChild(label);
    container.appendChild(toggleWrapper);
    
    return container;
}}

// Create and mount the component
function renderComponent() {{
    const container = document.getElementById('component-container');
    container.innerHTML = '';
    
    const component1 = {component_name}({{ label: 'Enable notifications', checked: false }});
    const component2 = {component_name}({{ label: 'Dark mode', checked: true }});
    
    container.appendChild(component1);
    container.appendChild(component2);
}}
"""
    else:
        # Default to button component
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


def create_html_preview(component_code, css_code="", component_name="Component", score=None, iterations=None, analysis_framework=None, analysis_text=None):
    """Create an interactive HTML preview"""
    
    vanilla_js = jsx_to_vanilla_js(component_code)
    
    # Only use CSS if it was actually provided by the component generation
    if not css_code:
        css_code = "/* No CSS provided by component generation */"
    
    # Generate score section if score data is available
    score_section = ""
    if score is not None:
        framework_text = f" ({analysis_framework} Framework)" if analysis_framework else ""
        score_color = "#28a745" if score >= 8 else "#fd7e14" if score >= 6 else "#dc3545"
        
        # Check if we have PURE dimension breakdown
        pure_dimensions = None
        if analysis_framework == "PURE" and analysis_text:
            pure_dimensions = extract_pure_dimensions(analysis_text)
        
        if pure_dimensions:
            # Show detailed PURE breakdown
            dimension_cards = ""
            for letter, data in pure_dimensions.items():
                dim_score = data['score']
                dim_name = data['name']
                dim_color = "#28a745" if dim_score >= 8 else "#fd7e14" if dim_score >= 6 else "#dc3545"
                dimension_cards += f"""
                <div style="background: {dim_color}; color: white; padding: 12px 16px; border-radius: 8px; text-align: center; min-width: 100px;">
                    <div style="font-size: 20px; font-weight: bold;">{letter}</div>
                    <div style="font-size: 18px; font-weight: bold;">{dim_score}/10</div>
                    <div style="font-size: 11px; opacity: 0.9;">{dim_name}</div>
                </div>"""
            
            score_section = f"""
            <div style="margin-top: 20px;">
                <div style="text-align: center; margin-bottom: 15px;">
                    <div style="display: inline-block; background: {score_color}; color: white; padding: 16px 24px; border-radius: 8px;">
                        <div style="font-size: 28px; font-weight: bold;">{score:.1f}/10</div>
                        <div style="font-size: 14px; opacity: 0.9;">Overall PURE Score</div>
                    </div>
                    {f'<div style="display: inline-block; margin-left: 15px; background: #007bff; color: white; padding: 16px 24px; border-radius: 8px;"><div style="font-size: 28px; font-weight: bold;">{iterations}</div><div style="font-size: 14px; opacity: 0.9;">Iterations</div></div>' if iterations is not None else ''}
                </div>
                <div style="display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;">
                    {dimension_cards}
                </div>
            </div>"""
        else:
            # Standard single score display
            score_section = f"""
            <div style="display: flex; justify-content: center; gap: 20px; margin-top: 20px; flex-wrap: wrap;">
                <div style="background: {score_color}; color: white; padding: 12px 20px; border-radius: 8px; text-align: center; min-width: 120px;">
                    <div style="font-size: 24px; font-weight: bold;">{score:.1f}/10</div>
                    <div style="font-size: 12px; opacity: 0.9;">Quality Score{framework_text}</div>
                </div>
                {f'<div style="background: #007bff; color: white; padding: 12px 20px; border-radius: 8px; text-align: center; min-width: 120px;"><div style="font-size: 24px; font-weight: bold;">{iterations}</div><div style="font-size: 12px; opacity: 0.9;">Iterations</div></div>' if iterations is not None else ''}
            </div>"""
    
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
        {score_section}
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
            {f'<button class="tab" onclick="showTab(\'analysis\')">Analysis</button>' if analysis_text else ''}
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
        
        {f'<div id="analysis-content" class="tab-content"><pre style="white-space: pre-wrap; background: #f8f9fa; color: #333; padding: 20px; border-radius: 4px; line-height: 1.6;"><code>{analysis_text.replace("<", "&lt;").replace(">", "&gt;") if analysis_text else ""}</code></pre></div>' if analysis_text else ''}
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
        
        # Extract score and metadata
        score = result.get('final_score')
        iterations = result.get('iterations')
        analysis_text = result.get('final_analysis')
        
        # Determine analysis framework based on file name or result data
        analysis_framework = None
        if 'pure' in result_file.lower():
            analysis_framework = "PURE"
        elif score is not None:
            analysis_framework = "Standard"
        
        # Generate HTML preview
        html_content = create_html_preview(
            component_code, 
            css_code, 
            component_name, 
            score=score, 
            iterations=iterations, 
            analysis_framework=analysis_framework,
            analysis_text=analysis_text
        )
        
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