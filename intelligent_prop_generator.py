#!/usr/bin/env python3
"""
Intelligent React Component Prop Generator
Automatically generates appropriate sample props for ANY React component
"""

import re
import ast
import json
from typing import Dict, Any, List, Optional
from gemini_client import GeminiClient


class IntelligentPropGenerator:
    def __init__(self):
        self.gemini_client = GeminiClient()
        
    def generate_props(self, component_code: str, component_name: str) -> Dict[str, Any]:
        """
        Generate appropriate props for ANY React component using multi-layered analysis
        """
        print(f"🧠 Analyzing {component_name} component for intelligent prop generation...")
        
        # Layer 1: TypeScript Interface Analysis
        props = self._analyze_typescript_interfaces(component_code)
        if props:
            print("✅ Generated props from TypeScript interfaces")
            return props
        
        # Layer 2: Component Signature Analysis  
        props = self._analyze_component_signature(component_code)
        if props:
            print("✅ Generated props from component signature")
            return props
            
        # Layer 3: Usage Pattern Analysis
        props = self._analyze_prop_usage_patterns(component_code)
        if props:
            print("✅ Generated props from usage patterns")
            return props
            
        # Layer 4: AI-Powered Analysis
        props = self._ai_analyze_component(component_code, component_name)
        if props:
            print("✅ Generated props using AI analysis")
            return props
            
        # Layer 5: Fallback to basic inference
        props = self._basic_prop_inference(component_code)
        print("⚠️  Using basic prop inference fallback")
        return props
    
    def _analyze_typescript_interfaces(self, code: str) -> Optional[Dict[str, Any]]:
        """Extract and generate props from TypeScript interface definitions"""
        
        # Find interface definitions
        interface_pattern = r'interface\s+(\w*Props)\s*\{([^}]+)\}'
        matches = re.findall(interface_pattern, code, re.DOTALL)
        
        if not matches:
            return None
            
        props = {}
        
        for interface_name, interface_body in matches:
            # Parse interface properties
            prop_lines = interface_body.strip().split('\n')
            
            for line in prop_lines:
                line = line.strip().rstrip(';,')
                if not line or line.startswith('//'):
                    continue
                    
                # Parse property definition: propName: type | propName?: type
                prop_match = re.match(r'(\w+)(\?)?:\s*(.+)', line)
                if prop_match:
                    prop_name, optional, prop_type = prop_match.groups()
                    is_optional = optional == '?'
                    
                    # Generate sample value based on type
                    sample_value = self._generate_value_for_type(prop_type, prop_name)
                    
                    if sample_value is not None:
                        props[prop_name] = sample_value
        
        return props if props else None
    
    def _analyze_component_signature(self, code: str) -> Optional[Dict[str, Any]]:
        """Analyze component function signature for prop destructuring"""
        
        # Look for component definition with prop destructuring
        patterns = [
            r'const\s+\w+[^=]*=\s*\(\s*\{([^}]+)\}[^)]*\)\s*=>\s*\{',
            r'function\s+\w+\s*\(\s*\{([^}]+)\}[^)]*\)\s*\{',
            r':\s*React\.FC[^=]*=\s*\(\s*\{([^}]+)\}[^)]*\)\s*=>\s*\{'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, code, re.DOTALL)
            if match:
                destructured_props = match.group(1)
                return self._parse_destructured_props(destructured_props, code)
        
        return None
    
    def _parse_destructured_props(self, destructured_props: str, full_code: str) -> Dict[str, Any]:
        """Parse destructured props and generate sample values"""
        
        props = {}
        
        # Split by comma and analyze each prop
        prop_items = [p.strip() for p in destructured_props.split(',')]
        
        for item in prop_items:
            item = item.strip()
            if not item:
                continue
                
            # Handle different prop patterns:
            # propName
            # propName = defaultValue  
            # propName: type
            
            if '=' in item:
                # Has default value
                prop_name = item.split('=')[0].strip()
                default_value = item.split('=')[1].strip()
                props[prop_name] = self._parse_default_value(default_value)
            else:
                # No default, infer from usage
                prop_name = item.strip()
                props[prop_name] = self._infer_prop_value_from_usage(prop_name, full_code)
        
        return props
    
    def _analyze_prop_usage_patterns(self, code: str) -> Optional[Dict[str, Any]]:
        """Analyze how props are used in the component to infer their types"""
        
        props = {}
        
        # Common patterns to detect:
        
        # Array usage: prop.map(), prop.length, prop.filter()
        array_pattern = r'(\w+)\.(?:map|filter|reduce|forEach|length|slice)\s*\('
        array_matches = re.findall(array_pattern, code)
        for prop_name in set(array_matches):
            if self._looks_like_prop(prop_name):
                props[prop_name] = self._generate_sample_array(prop_name, code)
        
        # String usage: prop.includes(), prop.toLowerCase(), prop.split()
        string_pattern = r'(\w+)\.(?:includes|toLowerCase|toUpperCase|split|trim|replace)\s*\('
        string_matches = re.findall(string_pattern, code)
        for prop_name in set(string_matches):
            if self._looks_like_prop(prop_name):
                props[prop_name] = self._generate_sample_string(prop_name)
        
        # Object property access: prop.property
        object_pattern = r'(\w+)\.(\w+)(?!\s*\()'
        object_matches = re.findall(object_pattern, code)
        for prop_name, property_name in object_matches:
            if self._looks_like_prop(prop_name) and prop_name not in props:
                props[prop_name] = self._generate_sample_object(prop_name, property_name)
        
        # Boolean usage: prop && something, !prop, prop ? true : false
        boolean_pattern = r'(?:!(\w+)|(\w+)\s*(?:\?|&&))'
        boolean_matches = re.findall(boolean_pattern, code)
        for match in boolean_matches:
            prop_name = match[0] or match[1]
            if self._looks_like_prop(prop_name) and prop_name not in props:
                props[prop_name] = True
        
        return props if props else None
    
    def _ai_analyze_component(self, code: str, component_name: str) -> Optional[Dict[str, Any]]:
        """Use AI to analyze component and generate appropriate props"""
        
        prompt = f"""
        Analyze this React component and generate appropriate sample props in JSON format:
        
        Component Name: {component_name}
        
        ```typescript
        {code}
        ```
        
        Requirements:
        1. Identify all props the component expects
        2. Determine the data type for each prop (string, number, array, object, boolean)
        3. For arrays, provide 3-4 realistic sample items
        4. For objects, include all necessary properties
        5. Use realistic, contextual sample data
        6. Return ONLY valid JSON - no explanation
        
        Example output:
        {{
            "title": "Sample Title",
            "items": [{{"id": 1, "name": "Item 1"}}, {{"id": 2, "name": "Item 2"}}],
            "isVisible": true,
            "variant": "primary"
        }}
        """
        
        try:
            response = self.gemini_client.model.generate_content(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
                
        except Exception as e:
            print(f"⚠️  AI analysis failed: {e}")
            
        return None
    
    def _generate_value_for_type(self, type_str: str, prop_name: str) -> Any:
        """Generate sample value based on TypeScript type"""
        
        type_str = type_str.strip()
        
        # Array types
        if '[]' in type_str or 'Array<' in type_str:
            return self._generate_sample_array(prop_name, "")
            
        # Union types ('primary' | 'secondary')
        if '|' in type_str:
            options = [opt.strip().strip("'\"") for opt in type_str.split('|')]
            return options[0] if options else "primary"
            
        # Basic types
        if type_str in ['string']:
            return self._generate_sample_string(prop_name)
        elif type_str in ['number']:
            return 42
        elif type_str in ['boolean']:
            return True
        elif type_str.startswith('(') and '=>' in type_str:
            return None  # Function props not needed for preview
            
        # Object types or custom interfaces
        return self._generate_sample_object(prop_name, "")
    
    def _generate_sample_array(self, prop_name: str, context: str) -> List[Dict[str, Any]]:
        """Generate contextual sample array data"""
        
        name_lower = prop_name.lower()
        
        if 'event' in name_lower:
            return [
                {"id": 1, "title": "Event 1", "date": "2024-01-15", "description": "Sample event"},
                {"id": 2, "title": "Event 2", "date": "2024-02-15", "description": "Another event"},
                {"id": 3, "title": "Event 3", "date": "2024-03-15", "description": "Future event"}
            ]
        elif 'user' in name_lower or 'people' in name_lower:
            return [
                {"id": 1, "name": "John Doe", "email": "john@example.com", "avatar": "https://placehold.co/40x40"},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "avatar": "https://placehold.co/40x40"}
            ]
        elif 'item' in name_lower or 'data' in name_lower:
            return [
                {"id": 1, "name": "Item 1", "value": "Value 1"},
                {"id": 2, "name": "Item 2", "value": "Value 2"},
                {"id": 3, "name": "Item 3", "value": "Value 3"}
            ]
        elif 'column' in name_lower:
            return [
                {"key": "name", "label": "Name"},
                {"key": "email", "label": "Email"},
                {"key": "status", "label": "Status"}
            ]
        else:
            # Generic array
            return [
                {"id": 1, "label": "Option 1"},
                {"id": 2, "label": "Option 2"},
                {"id": 3, "label": "Option 3"}
            ]
    
    def _generate_sample_string(self, prop_name: str) -> str:
        """Generate contextual sample string"""
        
        name_lower = prop_name.lower()
        
        if 'title' in name_lower:
            return "Sample Title"
        elif 'description' in name_lower:
            return "This is a sample description with some meaningful content."
        elif 'name' in name_lower:
            return "Sample Name"
        elif 'email' in name_lower:
            return "user@example.com"
        elif 'url' in name_lower or 'image' in name_lower:
            return "https://placehold.co/300x200"
        elif 'text' in name_lower or 'content' in name_lower:
            return "Sample content text"
        else:
            return f"Sample {prop_name}"
    
    def _generate_sample_object(self, prop_name: str, property_name: str) -> Dict[str, Any]:
        """Generate contextual sample object"""
        
        name_lower = prop_name.lower()
        
        if 'user' in name_lower:
            return {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "avatar": "https://placehold.co/40x40"
            }
        elif 'config' in name_lower or 'settings' in name_lower:
            return {
                "theme": "light",
                "enabled": True,
                "value": 42
            }
        else:
            # Generic object with the accessed property
            obj = {"id": 1, "name": "Sample"}
            if property_name:
                obj[property_name] = "sample value"
            return obj
    
    def _parse_default_value(self, default_str: str) -> Any:
        """Parse default value from code"""
        
        default_str = default_str.strip()
        
        if default_str.startswith("'") or default_str.startswith('"'):
            return default_str.strip("'\"")
        elif default_str.lower() in ['true', 'false']:
            return default_str.lower() == 'true'
        elif default_str.isdigit():
            return int(default_str)
        elif '.' in default_str and all(part.isdigit() for part in default_str.split('.')):
            return float(default_str)
        else:
            return default_str
    
    def _infer_prop_value_from_usage(self, prop_name: str, code: str) -> Any:
        """Infer prop value by analyzing how it's used in the code"""
        
        # Look for map usage (indicates array)
        if f"{prop_name}.map" in code:
            return self._generate_sample_array(prop_name, code)
            
        # Look for property access (indicates object)
        property_access = re.search(f"{prop_name}" + r"\.(\w+)", code)
        if property_access:
            return self._generate_sample_object(prop_name, property_access.group(1))
            
        # Look for string methods
        if any(f"{prop_name}.{method}" in code for method in ['includes', 'toLowerCase', 'split']):
            return self._generate_sample_string(prop_name)
            
        # Default to string
        return self._generate_sample_string(prop_name)
    
    def _looks_like_prop(self, name: str) -> bool:
        """Determine if a variable name looks like a prop (not a local variable)"""
        
        # Exclude common local variables
        excluded = {'index', 'item', 'key', 'value', 'i', 'j', 'result', 'temp', 'data', 'response', 'error'}
        
        # Exclude React hooks
        if name.startswith('use') or name in ['useState', 'useEffect', 'useCallback', 'useMemo']:
            return False
            
        # Exclude common JS variables
        if name in excluded:
            return False
            
        return True
    
    def _basic_prop_inference(self, code: str) -> Dict[str, Any]:
        """Basic fallback prop inference"""
        
        props = {}
        
        # Look for common prop patterns in JSX
        jsx_props = re.findall(r'(\w+)=\{', code)
        for prop in set(jsx_props):
            props[prop] = f"sample-{prop}"
            
        # If no props found, return empty (component might not need props)
        return props


def test_intelligent_prop_generator():
    """Test the intelligent prop generator with various component types"""
    
    generator = IntelligentPropGenerator()
    
    # Test Timeline component
    timeline_code = '''
    interface TimelineProps {
        events: Event[];
        variant?: 'compact' | 'detailed';
    }
    
    const Timeline: React.FC<TimelineProps> = ({ events, variant = 'detailed' }) => {
        return (
            <div>
                {events.map((event, index) => (
                    <div key={event.id}>{event.title}</div>
                ))}
            </div>
        );
    };
    '''
    
    props = generator.generate_props(timeline_code, "Timeline")
    print("Timeline Props:", json.dumps(props, indent=2))
    
    return props


if __name__ == "__main__":
    test_intelligent_prop_generator()