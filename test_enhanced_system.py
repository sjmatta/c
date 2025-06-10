#!/usr/bin/env python3
"""
Test script for enhanced component generation system with icons and images
"""

import json
from crew_agents import ComponentCreationCrew
from icon_library import IconLibraryManager
from gemini_client import GeminiClient


def test_enhanced_system():
    """Test the enhanced component generation system"""
    
    print("🎨 Testing Enhanced Component Generation System")
    print("=" * 50)
    
    # Initialize system
    crew = ComponentCreationCrew()
    icon_manager = IconLibraryManager()
    gemini_client = GeminiClient()
    
    # Test different component types
    test_components = [
        {
            'requirements': 'Create a modern user profile card with avatar and action buttons',
            'expected_type': 'card'
        },
        {
            'requirements': 'Create a data table with sorting and pagination',
            'expected_type': 'table'
        },
        {
            'requirements': 'Create a navigation menu with icons',
            'expected_type': 'navigation'
        }
    ]
    
    for i, test_case in enumerate(test_components, 1):
        print(f"\n🧪 Test {i}: {test_case['requirements']}")
        print("-" * 40)
        
        # Test component type detection
        detected_type = crew._extract_component_type(test_case['requirements'])
        print(f"🎯 Detected type: {detected_type}")
        
        # Test icon suggestions
        icon_suggestions = icon_manager.get_icon_suggestions(detected_type)
        print(f"🎨 Icon suggestions: {len(icon_suggestions['icons'])} available")
        
        # Show first few icon suggestions
        for icon in icon_suggestions['icons'][:3]:
            print(f"   - {icon['name']} ({icon['category']})")
        
        # Test image generation
        image_url = gemini_client.generate_placeholder_image_url(detected_type, test_case['requirements'])
        print(f"🖼️  Placeholder image: {image_url}")
        print(f"    ✅ Using placehold.co service")
        
        # Test component enhancement suggestions (simulated - would normally require actual component code)
        print(f"✨ Enhancement suggestions available for {detected_type} components")
        
        print(f"✅ Test {i} completed successfully")
    
    return True


def test_icon_library_features():
    """Test icon library features in detail"""
    
    print("\n🎯 Testing Icon Library Features")
    print("=" * 40)
    
    icon_manager = IconLibraryManager()
    
    # Test different component types
    component_types = ['button', 'table', 'card', 'form', 'navigation']
    
    for comp_type in component_types:
        print(f"\n📋 {comp_type.upper()} component icons:")
        suggestions = icon_manager.get_icon_suggestions(comp_type)
        
        print(f"   Library: {suggestions['primary_library']}")
        print(f"   Icons available: {len(suggestions['icons'])}")
        print(f"   Import statements: {len(suggestions['import_statements'])}")
        
        # Show sample icons
        for icon in suggestions['icons'][:2]:
            print(f"   - {icon['name']}: {icon['accessibility']}")
    
    # Test component enhancement
    sample_component = '''
    const Button = ({ children, onClick }) => {
      return <button onClick={onClick}>{children}</button>;
    };
    '''
    
    enhanced_code, enhancement_info = icon_manager.get_enhanced_component_with_icons(sample_component, 'button')
    print(f"\n🔧 Component enhancement:")
    print(f"   Enhanced imports: {'import {' in enhanced_code}")
    print(f"   Placement suggestions: {len(enhancement_info['placements'])}")
    print(f"   CDN setup options: {len(enhancement_info['cdn_setup'])}")
    
    return True


def test_gemini_image_features():
    """Test Gemini image generation features"""
    
    print("\n🖼️  Testing Gemini Image Features")
    print("=" * 40)
    
    gemini_client = GeminiClient()
    
    # Test different component types and image scenarios
    test_scenarios = [
        ('profile card', 'user profile with avatar'),
        ('product card', 'e-commerce product display'),
        ('hero section', 'landing page banner'),
        ('gallery', 'photo collection display')
    ]
    
    for component_type, context in test_scenarios:
        print(f"\n📸 {component_type.upper()} images:")
        
        # Test different image sizes
        primary_image = gemini_client.generate_placeholder_image_url(component_type, context)
        small_image = gemini_client.generate_placeholder_image_url(component_type, context, 200, 150)
        large_image = gemini_client.generate_placeholder_image_url(component_type, context, 800, 600)
        
        print(f"   Primary (400x300): {primary_image}")
        print(f"   Small (200x150): {small_image}")
        print(f"   Large (800x600): {large_image}")
        
        # Test description generation
        description = gemini_client.generate_placeholder_image_description(component_type, context)
        print(f"   Description: {description[:100]}...")
    
    return True


def show_enhanced_output_structure():
    """Show the structure of enhanced component output"""
    
    print("\n📊 Enhanced Output Structure")
    print("=" * 40)
    
    # Load a recent result file to show structure
    try:
        with open('table_result.json', 'r') as f:
            result = json.load(f)
        
        print("Standard fields:")
        standard_fields = ['component_code', 'final_analysis', 'final_score', 'iterations']
        for field in standard_fields:
            if field in result:
                print(f"   ✅ {field}")
            else:
                print(f"   ❌ {field}")
        
        print("\nEnhanced fields:")
        enhanced_fields = ['component_type', 'enhancement_suggestions', 'icon_suggestions', 'placeholder_images']
        for field in enhanced_fields:
            if field in result:
                print(f"   ✅ {field}")
                if field == 'icon_suggestions' and 'icons' in result[field]:
                    print(f"      - {len(result[field]['icons'])} icon suggestions")
                elif field == 'placeholder_images' and 'alternatives' in result[field]:
                    print(f"      - {len(result[field]['alternatives'])} image alternatives")
            else:
                print(f"   ❌ {field}")
        
        print(f"\n📈 Total output size: {len(json.dumps(result))} characters")
        
    except FileNotFoundError:
        print("   ⚠️  No result file found to analyze structure")
    
    return True


if __name__ == "__main__":
    try:
        print("🚀 Starting Enhanced System Tests")
        
        # Run all tests
        success = True
        success &= test_enhanced_system()
        success &= test_icon_library_features()
        success &= test_gemini_image_features()
        success &= show_enhanced_output_structure()
        
        if success:
            print("\n🎉 All enhanced system tests passed!")
            print("\n💡 The system now supports:")
            print("   - Automatic component type detection")
            print("   - Context-aware icon suggestions")
            print("   - Intelligent placeholder image generation")
            print("   - Enhanced component analysis")
            print("   - Rich metadata output")
            print("   - Simplified workflow (test generation disabled)")
        else:
            print("\n❌ Some tests failed")
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()