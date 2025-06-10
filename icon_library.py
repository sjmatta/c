#!/usr/bin/env python3
"""
Icon Library Integration for React Components
Provides icon suggestions and CDN integration for component generation
"""

import json
import re
from typing import Dict, List, Tuple


class IconLibraryManager:
    """Manages icon libraries and provides suggestions for React components"""
    
    def __init__(self):
        self.libraries = {
            'heroicons': {
                'name': 'Heroicons',
                'cdn_url': 'https://unpkg.com/@heroicons/react@2.0.18/24/outline/index.js',
                'import_pattern': "import { {icon_name} } from '@heroicons/react/24/outline'",
                'usage_pattern': "<{icon_name} className='w-{size} h-{size}' aria-hidden='true' />",
                'fallback_cdn': 'https://heroicons.com/',
                'common_icons': {
                    'navigation': ['ChevronLeftIcon', 'ChevronRightIcon', 'ChevronUpIcon', 'ChevronDownIcon', 'ArrowLeftIcon', 'ArrowRightIcon'],
                    'actions': ['PlusIcon', 'MinusIcon', 'XMarkIcon', 'CheckIcon', 'PencilIcon', 'TrashIcon'],
                    'ui': ['Bars3Icon', 'MagnifyingGlassIcon', 'Cog6ToothIcon', 'UserIcon', 'HomeIcon'],
                    'social': ['HeartIcon', 'ShareIcon', 'ChatBubbleLeftIcon', 'StarIcon'],
                    'status': ['ExclamationTriangleIcon', 'CheckCircleIcon', 'XCircleIcon', 'InformationCircleIcon']
                }
            },
            'lucide': {
                'name': 'Lucide React',
                'cdn_url': 'https://unpkg.com/lucide-react@latest/dist/umd/lucide-react.js',
                'import_pattern': "import { {icon_name} } from 'lucide-react'",
                'usage_pattern': "<{icon_name} size={size} className='text-current' />",
                'fallback_cdn': 'https://lucide.dev/',
                'common_icons': {
                    'navigation': ['ChevronLeft', 'ChevronRight', 'ChevronUp', 'ChevronDown', 'ArrowLeft', 'ArrowRight'],
                    'actions': ['Plus', 'Minus', 'X', 'Check', 'Edit', 'Trash2'],
                    'ui': ['Menu', 'Search', 'Settings', 'User', 'Home'],
                    'social': ['Heart', 'Share', 'MessageCircle', 'Star'],
                    'status': ['AlertTriangle', 'CheckCircle', 'XCircle', 'Info']
                }
            },
            'tabler': {
                'name': 'Tabler Icons',
                'cdn_url': 'https://unpkg.com/@tabler/icons@latest/dist/tabler-sprite.svg',
                'import_pattern': "import { Icon{icon_name} } from '@tabler/icons-react'",
                'usage_pattern': "<Icon{icon_name} size={size} className='text-current' />",
                'fallback_cdn': 'https://tabler-icons.io/',
                'common_icons': {
                    'navigation': ['ChevronLeft', 'ChevronRight', 'ChevronUp', 'ChevronDown', 'ArrowLeft', 'ArrowRight'],
                    'actions': ['Plus', 'Minus', 'X', 'Check', 'Edit', 'Trash'],
                    'ui': ['Menu2', 'Search', 'Settings', 'User', 'Home'],
                    'social': ['Heart', 'Share', 'Message', 'Star'],
                    'status': ['AlertTriangle', 'CircleCheck', 'CircleX', 'InfoCircle']
                }
            }
        }
    
    def get_icon_suggestions(self, component_type: str, context: str = "") -> Dict:
        """Get icon suggestions based on component type and context"""
        suggestions = {
            'primary_library': 'heroicons',
            'icons': [],
            'cdn_links': [],
            'import_statements': []
        }
        
        # Determine appropriate icons based on component type
        icon_mapping = self._get_component_icon_mapping()
        component_icons = icon_mapping.get(component_type.lower(), icon_mapping.get('default', []))
        
        # Get icons from primary library (Heroicons)
        library = self.libraries['heroicons']
        
        for category, icon_list in component_icons.items():
            for icon_name in icon_list:
                icon_info = {
                    'name': icon_name,
                    'library': 'heroicons',
                    'category': category,
                    'import': library['import_pattern'].replace('{icon_name}', icon_name),
                    'usage': library['usage_pattern'].replace('{icon_name}', icon_name).replace('{size}', '5'),
                    'accessibility': f"aria-label='{self._get_icon_aria_label(icon_name)}'"
                }
                suggestions['icons'].append(icon_info)
        
        # Add CDN links and import statements
        suggestions['cdn_links'] = [lib['fallback_cdn'] for lib in self.libraries.values()]
        suggestions['import_statements'] = [icon['import'] for icon in suggestions['icons']]
        
        return suggestions
    
    def _get_component_icon_mapping(self) -> Dict:
        """Map component types to relevant icon categories"""
        return {
            'button': {
                'actions': ['PlusIcon', 'CheckIcon', 'ArrowRightIcon'],
                'navigation': ['ChevronRightIcon', 'ArrowLeftIcon']
            },
            'table': {
                'navigation': ['ChevronUpIcon', 'ChevronDownIcon', 'ChevronLeftIcon', 'ChevronRightIcon'],
                'actions': ['MagnifyingGlassIcon', 'FunnelIcon', 'PencilIcon', 'TrashIcon']
            },
            'card': {
                'social': ['HeartIcon', 'ShareIcon', 'StarIcon'],
                'ui': ['UserIcon', 'Cog6ToothIcon'],
                'actions': ['PencilIcon', 'TrashIcon']
            },
            'form': {
                'ui': ['MagnifyingGlassIcon', 'EyeIcon', 'EyeSlashIcon'],
                'status': ['ExclamationTriangleIcon', 'CheckCircleIcon', 'XCircleIcon']
            },
            'navigation': {
                'navigation': ['Bars3Icon', 'HomeIcon', 'ArrowLeftIcon', 'ArrowRightIcon'],
                'ui': ['MagnifyingGlassIcon', 'UserIcon']
            },
            'default': {
                'ui': ['UserIcon', 'Cog6ToothIcon', 'HomeIcon'],
                'actions': ['PlusIcon', 'CheckIcon']
            }
        }
    
    def _get_icon_aria_label(self, icon_name: str) -> str:
        """Generate appropriate aria-label for icons"""
        # Convert PascalCase to readable text
        # ChevronDownIcon -> "Chevron down"
        words = re.findall(r'[A-Z][a-z]*', icon_name.replace('Icon', ''))
        return ' '.join(words).lower()
    
    def generate_icon_imports_for_component(self, component_code: str, library: str = 'heroicons') -> List[str]:
        """Generate import statements for icons found in component code"""
        if library not in self.libraries:
            library = 'heroicons'
        
        lib_config = self.libraries[library]
        imports = []
        
        # Find icon usage patterns in the code
        icon_patterns = [
            r'<(\w*Icon)\s',  # Heroicons pattern
            r'<(\w+)\s.*?(?:lucide|tabler)',  # Lucide/Tabler pattern
        ]
        
        found_icons = set()
        for pattern in icon_patterns:
            matches = re.findall(pattern, component_code)
            found_icons.update(matches)
        
        # Generate import statements
        for icon in found_icons:
            import_statement = lib_config['import_pattern'].replace('{icon_name}', icon)
            imports.append(import_statement)
        
        return imports
    
    def get_enhanced_component_with_icons(self, component_code: str, component_type: str) -> Tuple[str, Dict]:
        """Enhance component code with appropriate icons and return suggestions"""
        suggestions = self.get_icon_suggestions(component_type)
        
        # Add icon imports to component
        enhanced_code = self._add_icon_imports(component_code, suggestions)
        
        # Suggest icon placements
        placement_suggestions = self._suggest_icon_placements(component_code, component_type)
        
        return enhanced_code, {
            'suggestions': suggestions,
            'placements': placement_suggestions,
            'cdn_setup': self._get_cdn_setup_instructions()
        }
    
    def _add_icon_imports(self, component_code: str, suggestions: Dict) -> str:
        """Add icon import statements to component code"""
        imports = suggestions.get('import_statements', [])
        
        if not imports:
            return component_code
        
        # Find existing imports or add after React import
        import_section = '\n'.join(imports)
        
        if "import React" in component_code:
            # Add after React import
            enhanced_code = component_code.replace(
                "import React from 'react';",
                f"import React from 'react';\n{import_section}"
            )
        else:
            # Add at the beginning
            enhanced_code = f"{import_section}\n{component_code}"
        
        return enhanced_code
    
    def _suggest_icon_placements(self, component_code: str, component_type: str) -> List[Dict]:
        """Suggest where to place icons in the component"""
        suggestions = []
        
        if 'button' in component_type.lower():
            suggestions.append({
                'location': 'button content',
                'suggestion': 'Add leading or trailing icon',
                'example': '<ChevronRightIcon className="w-4 h-4 ml-2" />'
            })
        
        if 'table' in component_type.lower():
            suggestions.append({
                'location': 'table headers',
                'suggestion': 'Add sort indicators',
                'example': '<ChevronUpIcon className="w-4 h-4 inline" />'
            })
        
        if 'card' in component_type.lower():
            suggestions.append({
                'location': 'card actions',
                'suggestion': 'Add action icons',
                'example': '<HeartIcon className="w-5 h-5 text-red-500" />'
            })
        
        return suggestions
    
    def _get_cdn_setup_instructions(self) -> Dict:
        """Get CDN setup instructions for browser-based components"""
        return {
            'heroicons': {
                'script_tag': '<script src="https://unpkg.com/@heroicons/react@2.0.18/24/outline/index.js"></script>',
                'usage_note': 'Icons available as global variables: window.HeroIcons.ChevronDownIcon',
                'browser_usage': 'React.createElement(window.HeroIcons.ChevronDownIcon, {className: "w-4 h-4"})'
            },
            'lucide': {
                'script_tag': '<script src="https://unpkg.com/lucide-react@latest/dist/umd/lucide-react.js"></script>',
                'usage_note': 'Icons available as: window.LucideReact.ChevronDown',
                'browser_usage': 'React.createElement(window.LucideReact.ChevronDown, {size: 16})'
            }
        }


def test_icon_library():
    """Test the icon library functionality"""
    icon_manager = IconLibraryManager()
    
    # Test icon suggestions
    print("🎨 Testing icon suggestions for table component...")
    suggestions = icon_manager.get_icon_suggestions('table')
    
    print(f"Found {len(suggestions['icons'])} icon suggestions")
    for icon in suggestions['icons'][:3]:  # Show first 3
        print(f"  - {icon['name']} ({icon['category']}): {icon['usage']}")
    
    # Test component enhancement
    sample_component = """
    import React from 'react';
    
    const Button = ({ children, onClick }) => {
      return (
        <button onClick={onClick} className="bg-blue-500 text-white px-4 py-2 rounded">
          {children}
        </button>
      );
    };
    """
    
    enhanced_code, enhancement_info = icon_manager.get_enhanced_component_with_icons(sample_component, 'button')
    
    print("\\n🔧 Enhanced component with icons:")
    print("Enhanced code includes imports:", 'import {' in enhanced_code)
    print(f"Placement suggestions: {len(enhancement_info['placements'])}")
    
    return True


if __name__ == "__main__":
    test_icon_library()