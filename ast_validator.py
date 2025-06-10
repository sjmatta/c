#!/usr/bin/env python3
"""
AST Validator for React/TypeScript component validation
Uses Babel to parse and validate component syntax
"""

import subprocess
import tempfile
import os
import json
from typing import Dict, Any, Optional


class ASTValidator:
    """Validates React/TypeScript component syntax using Babel AST parsing"""
    
    def __init__(self):
        self.babel_available = self._check_babel_availability()
    
    def _check_babel_availability(self) -> bool:
        """Check if Babel CLI is available"""
        try:
            result = subprocess.run(['npx', 'babel', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def validate_component(self, code: str) -> Dict[str, Any]:
        """
        Validate React component syntax and completeness
        
        Returns:
            {
                "status": "COMPLETE" | "TRUNCATED" | "SYNTAX_ERROR",
                "details": "Error message or completion info",
                "error_location": {"line": int, "column": int} or None
            }
        """
        if not code or not code.strip():
            return {
                "status": "SYNTAX_ERROR",
                "details": "Empty or whitespace-only code",
                "error_location": None
            }
        
        # Extract just the code part for analysis (ignore explanatory text)
        clean_code = self._clean_code_for_parsing(code)
        
        # Quick heuristic checks for obvious truncation on the clean code
        truncation_indicators = [
            clean_code.count('{') != clean_code.count('}'),
            clean_code.count('(') != clean_code.count(')'),
            clean_code.count('[') != clean_code.count(']'),
        ]
        
        # Check for unbalanced quotes (more sophisticated)
        in_string = False
        quote_char = None
        escaped = False
        for char in clean_code:
            if escaped:
                escaped = False
                continue
            if char == '\\':
                escaped = True
                continue
            if not in_string and char in ['"', "'"]:
                in_string = True
                quote_char = char
            elif in_string and char == quote_char:
                in_string = False
                quote_char = None
        
        # Add quote imbalance to indicators
        if in_string:
            truncation_indicators.append(True)
        
        if any(truncation_indicators):
            return {
                "status": "TRUNCATED",
                "details": "Code appears incomplete based on bracket/quote balance",
                "error_location": None
            }
        
        # Use Babel for comprehensive syntax validation
        if self.babel_available:
            return self._validate_with_babel(code)
        else:
            # Fallback to basic validation
            return self._validate_basic(code)
    
    def _validate_with_babel(self, code: str) -> Dict[str, Any]:
        """Validate using Babel AST parser"""
        try:
            # Create temporary file for Babel
            with tempfile.NamedTemporaryFile(mode='w', suffix='.tsx', delete=False) as input_file:
                # Prepare code for parsing (remove markdown artifacts)
                clean_code = self._clean_code_for_parsing(code)
                input_file.write(clean_code)
                input_path = input_file.name
            
            # Use Babel to parse (not transpile, just parse for validation)
            babel_cmd = [
                'npx', 'babel', input_path,
                '--presets', '@babel/preset-typescript,@babel/preset-react',
                '--no-babelrc',
                '--filename', 'component.tsx'
            ]
            
            result = subprocess.run(babel_cmd, capture_output=True, text=True, timeout=10)
            
            # Clean up temp file
            os.unlink(input_path)
            
            if result.returncode == 0:
                # Check if the output is reasonable (not empty)
                if len(result.stdout.strip()) > 10:
                    return {
                        "status": "COMPLETE",
                        "details": "Code parsed successfully",
                        "error_location": None
                    }
                else:
                    return {
                        "status": "SYNTAX_ERROR", 
                        "details": "Babel produced empty output",
                        "error_location": None
                    }
            else:
                # Parse Babel error message for location info
                error_location = self._parse_babel_error(result.stderr)
                
                # Check if it's a truncation vs syntax error
                error_indicators = [
                    "Unexpected token" in result.stderr,
                    "Unterminated" in result.stderr,
                    "Unexpected end of input" in result.stderr
                ]
                
                if any(error_indicators):
                    return {
                        "status": "TRUNCATED",
                        "details": f"Babel parsing error: {result.stderr}",
                        "error_location": error_location
                    }
                else:
                    return {
                        "status": "SYNTAX_ERROR",
                        "details": f"Babel syntax error: {result.stderr}",
                        "error_location": error_location
                    }
                    
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
            return {
                "status": "SYNTAX_ERROR",
                "details": f"Babel validation failed: {e}",
                "error_location": None
            }
    
    def _parse_babel_error(self, error_text: str) -> Optional[Dict[str, int]]:
        """Extract line/column info from Babel error message"""
        import re
        
        # Look for patterns like "(130:12)" or "line 130, column 12"
        patterns = [
            r'\((\d+):(\d+)\)',
            r'line (\d+),?\s*column (\d+)',
            r':(\d+):(\d+):'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_text)
            if match:
                return {
                    "line": int(match.group(1)),
                    "column": int(match.group(2))
                }
        
        return None
    
    def _clean_code_for_parsing(self, code: str) -> str:
        """Clean code for Babel parsing by removing markdown artifacts"""
        import re
        
        # Extract just the code block content, ignore text before/after
        jsx_pattern = r'```(?:jsx|typescript|tsx|javascript|js)?\s*\n(.*?)```'
        match = re.search(jsx_pattern, code, re.DOTALL)
        
        if match:
            code = match.group(1)
        else:
            # Remove markdown code block markers if present
            code = re.sub(r'^```(?:jsx|typescript|tsx|javascript|js)?\s*$', '', code, flags=re.MULTILINE)
            code = re.sub(r'^```\s*$', '', code, flags=re.MULTILINE)
        
        # Add React import if missing (required for JSX)
        if 'import React' not in code and ('JSX' in code or '<' in code):
            code = "import React from 'react';\n\n" + code
        
        return code.strip()
    
    def _validate_basic(self, code: str) -> Dict[str, Any]:
        """Basic validation when Babel is not available"""
        # Check for required React patterns
        required_patterns = [
            r'(?:import\s+React|const\s+\w+|function\s+\w+)',  # Component definition
            r'(?:export\s+default|export\s+\{)',               # Export statement
        ]
        
        missing_patterns = []
        for pattern in required_patterns:
            if not re.search(pattern, code):
                missing_patterns.append(pattern)
        
        if missing_patterns:
            return {
                "status": "TRUNCATED",
                "details": f"Missing required patterns: {missing_patterns}",
                "error_location": None
            }
        
        return {
            "status": "COMPLETE",
            "details": "Basic validation passed",
            "error_location": None
        }


def test_validator():
    """Test the AST validator with sample code"""
    validator = ASTValidator()
    
    # Test cases
    test_cases = [
        {
            "name": "Complete component",
            "code": """
import React from 'react';

const Button = ({ children }) => {
    return <button>{children}</button>;
};

export default Button;
            """,
            "expected": "COMPLETE"
        },
        {
            "name": "Truncated component",
            "code": """
import React from 'react';

const Button = ({ children }) => {
    return <button>{children}</button>
            """,
            "expected": "TRUNCATED"
        },
        {
            "name": "Syntax error",
            "code": """
import React from 'react';

const Button = ({ children }) => {
    return <button>{children}</button>;;
};

export default Button;
            """,
            "expected": "SYNTAX_ERROR"
        }
    ]
    
    print("🧪 Testing AST Validator")
    print("=" * 50)
    
    for test in test_cases:
        result = validator.validate_component(test["code"])
        status = "✅" if result["status"] == test["expected"] else "❌"
        
        print(f"{status} {test['name']}")
        print(f"   Expected: {test['expected']}")
        print(f"   Got: {result['status']}")
        print(f"   Details: {result['details']}")
        print()


if __name__ == "__main__":
    test_validator()