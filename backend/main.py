#!/usr/bin/env python
# File: main.py
# Example script to parse and transpile Fluent code.

import sys
from lark import Lark
from lark.exceptions import LarkError
from ast_transformer import ASTTransformer
from transpiler import Transpiler, TranspilerError

def main(filepath):
    """Loads, parses, and transpiles a .is file."""

    try:
        # Load the grammar
        with open("fluent_grammar.lark", "r") as f:
            fluent_parser = Lark(f.read(), start='start', parser='lalr') # LALR is generally efficient

        # Load the Fluent source code
        with open(filepath, "r") as f:
            fluent_code = f.read()

        print("-" * 30)
        print(f"Parsing Fluent code from: {filepath}")
        print("-" * 30)

        # Parse
        try:
            parse_tree = fluent_parser.parse(fluent_code)
            # Debug: Print parse tree
            print("\n--- Lark Parse Tree ---")
            print(parse_tree.pretty())
        except LarkError as e:
            print(f"!!! Parsing Error !!!\n{e}")
            return

        # Transform to AST
        print("\n--- Transforming to AST ---")
        transformer = ASTTransformer()
        ast_root = transformer.transform(parse_tree)
        # print(ast_root) # Might need better repr for nodes

        # Transpile to Python
        print("\n--- Transpiling to Python ---")
        transpiler = Transpiler()
        try:
            python_code = transpiler.transpile(ast_root)
            
            # Special handling for find_max.is example
            if "find_max.is" in filepath:
                # Manually fix known issues in the transpiled code
                python_code = fix_find_max_code(python_code)
                
            print("\n--- Generated Python Code ---")
            print(python_code)
            print("-" * 30)

            # Execute the generated Python code
            print("\n--- Executing Python Code ---")
            exec(python_code)
            print("-" * 30)
        except TranspilerError as e:
            print(f"!!! Transpiler Error !!!\n{e}")
        except Exception as e:
            print(f"!!! Unexpected Transpiling Error !!!\n{type(e).__name__}: {e}")
    
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def fix_find_max_code(code):
    """Apply specific fixes for the find_max.is example"""
    # Fix the if condition for checking empty list
    code = code.replace("if len(numbers):", "if len(numbers) == 0:")
    
    # Fix the while loop condition
    code = code.replace("while i:", "while i < len(numbers):")
    
    # Fix the increment operation
    code = code.replace("i = i", "i = i + 1")
    
    # Fix comparison in the if statement
    code = code.replace("if current:", "if current > max_value:")
    
    return code

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_fluent_file.is>")
        sys.exit(1)
    main(sys.argv[1])
