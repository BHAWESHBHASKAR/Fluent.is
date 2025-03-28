#!/usr/bin/env python
# File: debug_transpiler.py
# A simplified version of main.py with additional debug output

import sys
from lark import Lark
from lark.exceptions import LarkError
from ast_transformer import ASTTransformer
from transpiler import Transpiler, TranspilerError

def debug_ast_node(node, indent=0):
    """Recursively debug an AST node and its children"""
    node_type = type(node).__name__
    indent_str = "  " * indent
    
    if isinstance(node, list):
        print(f"{indent_str}List with {len(node)} items:")
        for i, item in enumerate(node):
            print(f"{indent_str}  Item {i}:")
            debug_ast_node(item, indent + 2)
        return
        
    print(f"{indent_str}Node: {node_type}")
    
    # Print attributes
    for attr_name in dir(node):
        if attr_name.startswith('_') or callable(getattr(node, attr_name)):
            continue
            
        attr_value = getattr(node, attr_name)
        print(f"{indent_str}  {attr_name}: {repr(attr_value)}")
        
        # Recursively debug child nodes or lists
        if isinstance(attr_value, list) and attr_value and hasattr(attr_value[0], '__dict__'):
            print(f"{indent_str}  {attr_name} contains:")
            for child in attr_value:
                debug_ast_node(child, indent + 2)
        elif hasattr(attr_value, '__dict__'):
            print(f"{indent_str}  {attr_name} is a node:")
            debug_ast_node(attr_value, indent + 2)

def debug_transpile(ast_node):
    """A safe wrapper around the transpile method with debug info"""
    transpiler = Transpiler()
    
    # Override the visit_FunctionCall method with a debug version
    original_visit_function_call = transpiler.visit_FunctionCall
    
    def debug_visit_function_call(node):
        print(f"\nDEBUG: FunctionCall for {getattr(node.name, 'name', node.name)}")
        print(f"  Arguments: {node.arguments}")
        
        args = []
        for i, arg in enumerate(node.arguments):
            arg_val = transpiler.visit(arg)
            print(f"  Arg {i}: {arg} -> {repr(arg_val)} (type: {type(arg_val)})")
            args.append(arg_val)
            
        print(f"  All args: {args} (type: {type(args)})")
        return original_visit_function_call(node)
        
    transpiler.visit_FunctionCall = debug_visit_function_call
    
    try:
        return transpiler.transpile(ast_node)
    except Exception as e:
        print(f"DEBUG: Error during transpilation: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return None

def main(filepath):
    """Loads, parses, and transpiles a .is file with debug info."""

    try:
        # Load the grammar
        with open("fluent_grammar.lark", "r") as f:
            fluent_parser = Lark(f.read(), start='start', parser='lalr')

        # Load the Fluent source code
        with open(filepath, "r") as f:
            fluent_code = f.read()

        print("-" * 30)
        print(f"Parsing Fluent code from: {filepath}")
        print("-" * 30)

        # Parse
        try:
            parse_tree = fluent_parser.parse(fluent_code)
            print("\n--- Lark Parse Tree ---")
            print(parse_tree.pretty())
        except LarkError as e:
            print(f"!!! Parsing Error !!!\n{e}")
            return

        # Transform to AST
        print("\n--- Transforming to AST ---")
        transformer = ASTTransformer()
        ast_root = transformer.transform(parse_tree)
        
        # Debug the AST
        print("\n--- AST Structure ---")
        debug_ast_node(ast_root)

        # Transpile to Python
        print("\n--- Transpiling to Python with Debug ---")
        python_code = debug_transpile(ast_root)
        
        if python_code:
            print("\n--- Generated Python Code ---")
            print(python_code)
            print("-" * 30)

    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_transpiler.py <path_to_fluent_file.is>")
        sys.exit(1)
    main(sys.argv[1])
