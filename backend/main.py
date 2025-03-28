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
            print("\n--- Generated Python Code ---")
            print(python_code)
            print("-" * 30)

            # (Optional) Execute the generated Python code
            print("\n--- Executing Python Code ---")
            try:
                exec(python_code)
            except Exception as e_exec:
                print(f"!!! Python Execution Error !!!\n{type(e_exec).__name__}: {e_exec}")
            print("-" * 30)

        except TranspilerError as e:
            print(f"!!! Transpiling Error !!!\n{e}")
        except Exception as e_transpile:
             print(f"!!! Unexpected Transpiling Error !!!\n{type(e_transpile).__name__}: {e_transpile}")


    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_fluent_file.is>")
    else:
        main(sys.argv[1])
