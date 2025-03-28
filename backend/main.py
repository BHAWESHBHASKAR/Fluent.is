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
    print(f"Parsing Fluent code from: {filepath}")
    print("-" * 30)
    
    try:
        # Read input file
        with open(filepath, 'r') as f:
            fluent_code = f.read()
            
        # Parse with Lark grammar
        with open("fluent_grammar.lark", 'r') as f:
            grammar = f.read()
        parser = Lark(grammar, start='start')
        parse_tree = parser.parse(fluent_code)
        
        # Display parse tree for debugging
        print("\n--- Lark Parse Tree ---")
        print(parse_tree.pretty())
        
        # Transform to AST
        print("\n--- Transforming to AST ---")
        transformer = ASTTransformer()
        ast_root = transformer.transform(parse_tree)
        
        # Transpile to Python
        print("\n--- Transpiling to Python ---")
        transpiler = Transpiler()
        python_code = transpiler.transpile(ast_root)
        
        # Write the generated code to a temp file
        import os
        output_file = os.path.join(os.path.dirname(filepath), "temp_output.py")
        with open(output_file, 'w') as f:
            f.write(python_code)
            
        print("\n--- Generated Python Code ---")
        print(python_code)
        
        # Execute the Python code
        print("\n--- Executing Python Code ---")
        
        # Setup the execution environment
        # Add the backend directory to Python's path so it can find the stdlib module
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        if backend_dir not in sys.path:
            sys.path.append(backend_dir)
        
        # Execute in a subprocess to isolate environment
        import subprocess
        try:
            # Add a 5-second timeout to prevent hanging on infinite loops
            result = subprocess.run([sys.executable, output_file], 
                                    capture_output=True, 
                                    text=True, 
                                    cwd=backend_dir,
                                    timeout=5)  # 5 second timeout
            
            # Print output or errors
            if result.returncode == 0:
                print(result.stdout)
            else:
                print("!!! Execution Error !!!")
                print(result.stderr)
        except subprocess.TimeoutExpired:
            print("!!! Execution Timeout !!!")
            print("The program took too long to execute (possible infinite loop)")
            # Optionally add code to kill the process here if needed
        
    except LarkError as e:
        print(f"\nParsing error: {e}")
    except TranspilerError as e:
        print(f"\n!!! Transpiler Error !!!\n{e}")
    except Exception as e:
        print(f"\n!!! Unexpected Transpiling Error !!!\n{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_fluent_file.is>")
        sys.exit(1)
    main(sys.argv[1])
