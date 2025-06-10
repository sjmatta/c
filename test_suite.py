#!/usr/bin/env python3
"""
Comprehensive test suite for OpenUI + CrewAI + Gemini integration
"""

import unittest
import json
import os
import sys
import time
from unittest.mock import patch, MagicMock
import requests

# Import our modules
from openui_client import OpenUIClient
from gemini_client import GeminiClient
from crew_agents import ComponentCreationCrew
from preview_generator import generate_preview_from_result, extract_component_code, extract_css


class TestOpenUIClient(unittest.TestCase):
    """Test OpenUI client functionality"""
    
    def setUp(self):
        self.client = OpenUIClient()
    
    def test_cookie_loading(self):
        """Test that cookies are loaded properly"""
        self.assertIsInstance(self.client.cookies, dict)
        if os.path.exists('openui_cookies.json'):
            self.assertIn('session', self.client.cookies)
    
    def test_api_connection(self):
        """Test basic API connection"""
        try:
            response = requests.get("http://localhost:7878", timeout=5)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.RequestException:
            self.skipTest("OpenUI not running at localhost:7878")


class TestGeminiClient(unittest.TestCase):
    """Test Gemini client functionality"""
    
    def setUp(self):
        self.client = GeminiClient()
    
    def test_client_initialization(self):
        """Test that Gemini client initializes properly"""
        self.assertIsNotNone(self.client.model)
    
    @patch('google.generativeai.GenerativeModel')
    def test_analyze_component_mock(self, mock_model):
        """Test component analysis with mocked response"""
        mock_response = MagicMock()
        mock_response.text = """
        Analysis of the component:
        1. Functionality: 8/10
        2. Code quality: 7/10
        Overall score: 7.5
        {"overall_score": 8, "functionality": 8, "code_quality": 7}
        """
        mock_model.return_value.generate_content.return_value = mock_response
        
        result = self.client.analyze_component("test code", "test requirements")
        self.assertIsNotNone(result)


class TestCrewAgents(unittest.TestCase):
    """Test CrewAI agents functionality"""
    
    def setUp(self):
        self.crew = ComponentCreationCrew()
    
    def test_crew_initialization(self):
        """Test that crew initializes with all agents"""
        self.assertIsNotNone(self.crew.component_designer)
        self.assertIsNotNone(self.crew.quality_analyst)
        self.assertIsNotNone(self.crew.test_engineer)
        self.assertIsNotNone(self.crew.refiner)
    
    def test_score_extraction(self):
        """Test score extraction from analysis"""
        analysis_with_json = '{"overall_score": 8, "functionality": 9}'
        score = self.crew._extract_score(analysis_with_json)
        self.assertEqual(score, 8)
        
        analysis_with_pattern = "Overall score: 7/10"
        score = self.crew._extract_score(analysis_with_pattern)
        self.assertEqual(score, 7)
        
        analysis_without_score = "This is just text"
        score = self.crew._extract_score(analysis_without_score)
        self.assertEqual(score, 5)  # Default


class TestPreviewGenerator(unittest.TestCase):
    """Test preview generation functionality"""
    
    def test_extract_component_code(self):
        """Test JSX code extraction"""
        sample_text = """
        Here's a component:
        ```jsx
        import React from 'react';
        const Button = () => <button>Click</button>;
        export default Button;
        ```
        """
        
        extracted = extract_component_code(sample_text)
        self.assertIn("import React", extracted)
        self.assertIn("Button", extracted)
    
    def test_extract_css(self):
        """Test CSS extraction"""
        sample_text = """
        And the CSS:
        ```css
        .button { color: blue; }
        ```
        """
        
        extracted = extract_css(sample_text)
        self.assertIn(".button", extracted)
        self.assertIn("color: blue", extracted)
    
    def test_generate_preview_from_mock_result(self):
        """Test preview generation from mock result"""
        mock_result = {
            "component_code": """
            ```jsx
            import React from 'react';
            const TestButton = () => <button>Test</button>;
            export default TestButton;
            ```
            """,
            "final_score": 8,
            "iterations": 1
        }
        
        # Create temporary result file
        with open('test_result.json', 'w') as f:
            json.dump(mock_result, f)
        
        try:
            success = generate_preview_from_result('test_result.json', 'test_preview.html')
            self.assertTrue(success)
            self.assertTrue(os.path.exists('test_preview.html'))
            
            # Check preview content
            with open('test_preview.html', 'r') as f:
                content = f.read()
                self.assertIn('TestButton', content)
                self.assertIn('Interactive Preview', content)
        finally:
            # Cleanup
            for file in ['test_result.json', 'test_preview.html']:
                if os.path.exists(file):
                    os.remove(file)


class TestIntegration(unittest.TestCase):
    """Integration tests for the full system"""
    
    def test_result_file_structure(self):
        """Test that result files have the expected structure"""
        result_files = ['simple_result.json', 'component_result.json']
        
        for result_file in result_files:
            if os.path.exists(result_file):
                with open(result_file, 'r') as f:
                    result = json.load(f)
                
                # Check required fields
                self.assertIn('component_code', result)
                self.assertIn('final_score', result)
                self.assertIn('iterations', result)
                
                # Check data types
                self.assertIsInstance(result['component_code'], str)
                self.assertIsInstance(result['final_score'], (int, float))
                self.assertIsInstance(result['iterations'], int)
                
                # Check score range
                self.assertGreaterEqual(result['final_score'], 0)
                self.assertLessEqual(result['final_score'], 10)
                
                break
        else:
            self.skipTest("No result files found to test")


class TestFileGeneration(unittest.TestCase):
    """Test file generation and cleanup"""
    
    def test_makefile_commands(self):
        """Test that Makefile commands exist"""
        with open('Makefile', 'r') as f:
            makefile_content = f.read()
        
        required_commands = ['demo', 'simple', 'preview', 'setup', 'clean']
        for command in required_commands:
            self.assertIn(f'{command}:', makefile_content)
    
    def test_required_files_exist(self):
        """Test that all required files exist"""
        required_files = [
            'main.py', 'openui_client.py', 'gemini_client.py',
            'crew_agents.py', 'preview_generator.py', 'get_openui_cookie.py',
            'Makefile', 'README.md', 'pyproject.toml'
        ]
        
        for file in required_files:
            self.assertTrue(os.path.exists(file), f"Required file missing: {file}")


def run_performance_test():
    """Performance test for component generation"""
    print("\n🚀 Running performance test...")
    
    start_time = time.time()
    
    try:
        crew = ComponentCreationCrew()
        result = crew.create_component("Create a simple span element", max_iterations=1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Performance test completed in {duration:.2f} seconds")
        
        if result:
            print(f"📊 Component score: {result['final_score']}/10")
            print(f"📝 Component length: {len(result['component_code'])} characters")
            
            if duration < 120:  # 2 minutes
                print("🟢 Performance: Excellent (< 2 minutes)")
            elif duration < 300:  # 5 minutes
                print("🟡 Performance: Good (< 5 minutes)")
            else:
                print("🔴 Performance: Slow (> 5 minutes)")
        else:
            print("❌ Performance test failed - no result generated")
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")


def capture_findings():
    """Capture test findings and system status"""
    findings = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "system_status": {},
        "test_results": {},
        "recommendations": []
    }
    
    # Check system components
    print("\n🔍 Capturing system findings...")
    
    # Check OpenUI connection
    try:
        response = requests.get("http://localhost:7878", timeout=5)
        findings["system_status"]["openui"] = "✅ Connected"
    except:
        findings["system_status"]["openui"] = "❌ Not accessible"
    
    # Check generated files
    result_files = ['simple_result.json', 'component_result.json']
    preview_files = ['simple_preview.html', 'preview.html']
    
    findings["system_status"]["result_files"] = len([f for f in result_files if os.path.exists(f)])
    findings["system_status"]["preview_files"] = len([f for f in preview_files if os.path.exists(f)])
    
    # Check cookies
    findings["system_status"]["cookies"] = "✅ Present" if os.path.exists('openui_cookies.json') else "❌ Missing"
    
    # Analyze latest result if available
    for result_file in result_files:
        if os.path.exists(result_file):
            try:
                with open(result_file, 'r') as f:
                    result = json.load(f)
                
                findings["test_results"]["latest_score"] = result.get('final_score')
                findings["test_results"]["latest_iterations"] = result.get('iterations')
                findings["test_results"]["component_length"] = len(result.get('component_code', ''))
                break
            except:
                pass
    
    # Add recommendations
    if findings["system_status"]["openui"] == "❌ Not accessible":
        findings["recommendations"].append("Start OpenUI server at localhost:7878")
    
    if findings["test_results"].get("latest_score", 0) < 8:
        findings["recommendations"].append("Consider increasing iteration count for higher quality")
    
    if findings["system_status"]["result_files"] == 0:
        findings["recommendations"].append("Run 'make simple' or 'make demo' to generate components")
    
    # Save findings
    with open('test_findings.json', 'w') as f:
        json.dump(findings, f, indent=2)
    
    print("📋 Test Findings Summary:")
    print("=" * 40)
    for key, value in findings["system_status"].items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    if findings["test_results"]:
        print("\nLatest Results:")
        for key, value in findings["test_results"].items():
            print(f"{key.replace('_', ' ').title()}: {value}")
    
    if findings["recommendations"]:
        print("\nRecommendations:")
        for i, rec in enumerate(findings["recommendations"], 1):
            print(f"{i}. {rec}")
    
    print(f"\n💾 Detailed findings saved to test_findings.json")


if __name__ == "__main__":
    print("🧪 OpenUI + CrewAI + Gemini Integration Test Suite")
    print("=" * 55)
    
    # Run unit tests
    print("\n📝 Running unit tests...")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run performance test
    run_performance_test()
    
    # Capture findings
    capture_findings()
    
    # Summary
    print("\n" + "=" * 55)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
    
    print("🎯 Test suite completed. Check test_findings.json for detailed analysis.")