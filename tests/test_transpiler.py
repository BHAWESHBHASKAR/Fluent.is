#!/usr/bin/env python3
"""
Unit tests for the Fluent to Python transpiler.
"""

import sys
import os
import unittest

# Add parent directory to path to import transpile_fluent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transpile_fluent import transpile


class TestFluentTranspiler(unittest.TestCase):
    """Tests for the Fluent language transpiler."""

    def test_hello_world(self):
        """Test basic function definition and call."""
        fluent_code = """
define greet
    inputs:
        - name (string optional "World")
    
    initialize greeting = "Hello, " + name + "!"
    print greeting
    return greeting

greet
"""
        python_code = transpile(fluent_code)
        
        # Basic assertions to verify the transpiled code
        self.assertIn("def greet(name=\"World\"):", python_code)
        self.assertIn("greeting = \"Hello, \" + name + \"!\"", python_code)
        self.assertIn("print(greeting)", python_code)
        self.assertIn("return greeting", python_code)
        self.assertIn("greet()", python_code)

    def test_comments_preserved(self):
        """Test that comments are preserved during transpilation."""
        fluent_code = """
# Top level comment
define example
    inputs:
        - x (number) # Parameter comment
    
    # Function body comment
    return x
"""
        python_code = transpile(fluent_code)
        
        self.assertIn("# Top level comment", python_code)
        self.assertIn("# Parameter comment", python_code)
        self.assertIn("# Function body comment", python_code)

    def test_conditionals(self):
        """Test if/elif/else transpilation."""
        fluent_code = """
define check_value
    inputs:
        - value (number)
    
    if value > 10:
        initialize result = "greater"
    elif value < 10:
        initialize result = "less"
    else:
        initialize result = "equal"
    
    return result
"""
        python_code = transpile(fluent_code)
        
        self.assertIn("if value > 10:", python_code)
        self.assertIn("elif value < 10:", python_code)
        self.assertIn("else:", python_code)
        self.assertIn("result = \"greater\"", python_code)
        self.assertIn("result = \"less\"", python_code)
        self.assertIn("result = \"equal\"", python_code)

    def test_loops(self):
        """Test loop transpilation."""
        fluent_code = """
define sum_list
    inputs:
        - numbers (list)
    
    initialize total = 0
    
    for each num in numbers:
        add num to total
    
    return total
"""
        python_code = transpile(fluent_code)
        
        self.assertIn("for num in numbers:", python_code)
        self.assertIn("total += num", python_code)

    def test_string_safety(self):
        """Test that str() is used for numeric to string conversions."""
        fluent_code = """
define describe_number
    inputs:
        - num (number)
    
    print "The number is: " + str(num)
    return "Value: " + str(num)
"""
        python_code = transpile(fluent_code)
        
        self.assertIn("print(\"The number is: \" + str(num))", python_code)
        self.assertIn("return \"Value: \" + str(num)", python_code)


if __name__ == "__main__":
    unittest.main()
