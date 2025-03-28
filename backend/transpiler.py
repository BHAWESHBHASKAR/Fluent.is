# File: transpiler.py
# Transpiles the Fluent AST into Python code.

import ast_nodes as ast
from fluent_stdlib_map import FLUENT_TO_PYTHON_MAP, OPERATOR_MAP

class TranspilerError(Exception):
    """Custom exception for transpiler errors."""
    pass

class Transpiler:
    def __init__(self):
        self.indent_level = 0
        self.output = []
        self.required_imports = set() # Track needed stdlib functions if using a wrapper module

    def _indent(self):
        return "    " * self.indent_level # 4 spaces per indent level

    def _visit_list(self, nodes):
        return [self.visit(node) for node in nodes]

    def transpile(self, node):
        self.output = []
        self.indent_level = 0
        self.visit(node)
        # Add any necessary imports at the top if using a wrapper module
        # import_str = "\n".join(f"import {mod}" for mod in self.required_imports) + "\n\n" if self.required_imports else ""
        # return import_str + "".join(self.output)
        return "".join(self.output)


    def visit(self, node):
        print(f"DEBUG: Visiting node of type {type(node).__name__} - {node}")
        
        # Handle list type directly
        if isinstance(node, list):
            return self.visit_list(node)
            
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def visit_list(self, node_list):
        """Handle a list of nodes by visiting each one"""
        return [self.visit(node) for node in node_list]

    def generic_visit(self, node):
        raise TranspilerError(f"No visit_{type(node).__name__} method defined")

    # --- Visitor Methods for AST Nodes ---

    def visit_Program(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_VariableDeclaration(self, node):
        # Extract the variable name correctly
        if hasattr(node.name, 'name'):
            var_name = node.name.name
        else:
            var_name = str(node.name)
            
        # Handle type extraction
        if node.var_type:
            if hasattr(node.var_type, 'name'):
                var_type = node.var_type.name
            else:
                var_type = self.visit(node.var_type) 
        else:
            var_type = "Any"  # Default to Any if not specified
        
        # Handle initialization
        if node.initializer is not None:
            init_code = self.visit(node.initializer)
            self.output.append(f"{self._indent()}{var_name} = {init_code}\n")
        else:
            # Handle uninitialized variables based on type
            default_values = {
                "int": "0", 
                "float": "0.0", 
                "str": "\"\"", 
                "bool": "False", 
                "None": "None",
                "list": "[]",
                "dict": "{}",
                "INTEGER": "0",
                "FLOAT": "0.0",
                "STRING": "\"\"",
                "BOOLEAN": "False",
                "NULLTYPE": "None"
            }
            default_value = default_values.get(var_type, "None")
            self.output.append(f"{self._indent()}{var_name} = {default_value}  # Uninitialized in Fluent\n")

    def visit_Assignment(self, node):
        # Handle target name (could be an identifier object or a string)
        if hasattr(node.target, 'name'):
            target_code = node.target.name
        else:
            target_code = str(node.target)
            
        # Handle value (expression on right side)
        value_code = self.visit(node.value)
        self.output.append(f"{self._indent()}{target_code} = {value_code}\n")

    def visit_PrintStatement(self, node):
        expr_code = self.visit(node.expression)
        # Map Fluent PRINT to Python print
        py_print = FLUENT_TO_PYTHON_MAP.get("PRINT", "print")
        self.output.append(f"{self._indent()}{py_print}({expr_code})\n")

    def visit_FunctionCallStatement(self, node):
        call_code = self.visit(node.function_call)
        self.output.append(f"{self._indent()}{call_code}\n") # Calls can be statements

    def visit_IfStatement(self, node):
        condition_code = self.visit(node.condition)
        self.output.append(f"{self._indent()}if {condition_code}:\n")
        self.indent_level += 1
        if node.then_block:
            for stmt in node.then_block:
                self.visit(stmt)
        else:
             self.output.append(f"{self._indent()}pass\n") # Explicit pass if block is empty
        self.indent_level -= 1

        if node.else_block:
            self.output.append(f"{self._indent()}else:\n")
            self.indent_level += 1
            for stmt in node.else_block:
                self.visit(stmt)
            self.indent_level -= 1
        # No explicit endif in Python

    def visit_WhileStatement(self, node):
        condition_code = self.visit(node.condition)
        self.output.append(f"{self._indent()}while {condition_code}:\n")
        self.indent_level += 1
        if node.body:
            for stmt in node.body:
                self.visit(stmt)
        else:
             self.output.append(f"{self._indent()}pass\n")
        self.indent_level -= 1
        # No explicit endwhile in Python

    def visit_ForeachStatement(self, node):
        item_name = node.item_name
        iterable_code = self.visit(node.iterable)
        self.output.append(f"{self._indent()}for {item_name} in {iterable_code}:\n")
        self.indent_level += 1
        if node.body:
            for stmt in node.body:
                self.visit(stmt)
        else:
             self.output.append(f"{self._indent()}pass\n")
        self.indent_level -= 1
        # No explicit endforeach in Python

    def visit_FunctionDefinition(self, node):
        print(f"DEBUG: Function name: {node.name}")
        print(f"DEBUG: Params: {node.params} (type: {type(node.params)})")
        
        if isinstance(node.params, list):
            for i, p in enumerate(node.params):
                print(f"DEBUG: Param {i}: {p} (type: {type(p)})")
        
        # Extract function name
        if hasattr(node.name, 'name'):
            func_name = node.name.name  # Handle if it's an Identifier object
        else:
            func_name = str(node.name)  # Fallback to string representation
            
        # Modified to handle potentially nested parameter list
        params = []
        if isinstance(node.params, list):
            for param_item in node.params:
                if isinstance(param_item, list):
                    # Handle nested list of parameters
                    for p in param_item:
                        if hasattr(p, 'name'):
                            # If it's a Parameter object with a name attribute
                            if hasattr(p.name, 'name'):
                                params.append(p.name.name)
                            else:
                                params.append(str(p.name))
                        else:
                            # Fallback for non-Parameter objects
                            params.append(str(p))
                elif hasattr(param_item, 'name'):
                    # Direct Parameter object
                    if hasattr(param_item.name, 'name'):
                        params.append(param_item.name.name)
                    else:
                        params.append(str(param_item.name))
                else:
                    # Fallback
                    params.append(str(param_item))
        
        params_str = ", ".join(params)
        # Could add type hints based on node.params[i].param_type and node.return_type
        self.output.append(f"{self._indent()}def {func_name}({params_str}):\n")
        self.indent_level += 1
        if node.body:
            for stmt in node.body:
                self.visit(stmt)
        else:
             self.output.append(f"{self._indent()}pass\n") # Function must have a body
        self.indent_level -= 1
        self.output.append("\n") # Add a blank line after function definition

    # Parameter node visited only for info, not direct code generation here
    def visit_Parameter(self, node):
        # Used by visit_FunctionDefinition, doesn't produce code itself
        return node.name

    def visit_ReturnStatement(self, node):
        if node.expression:
            expr_code = self.visit(node.expression)
            self.output.append(f"{self._indent()}return {expr_code}\n")
        else:
            self.output.append(f"{self._indent()}return\n")

    def visit_BreakStatement(self, node):
        self.output.append(f"{self._indent()}break\n")

    # --- Types --- (Mainly return string representations for potential type hints)
    def visit_Type(self, node):
        py_type_map = {"INTEGER": "int", "FLOAT": "float", "STRING": "str", "BOOLEAN": "bool", "NULLTYPE": "None"}
        return py_type_map.get(node.name, "Any") # Default to Any if unknown

    def visit_ListType(self, node):
        element_type_str = self.visit(node.element_type)
        return f"list[{element_type_str}]" # Python type hint format

    def visit_MapType(self, node):
        key_type_str = self.visit(node.key_type)
        value_type_str = self.visit(node.value_type)
        return f"dict[{key_type_str}, {value_type_str}]" # Python type hint format

    # --- Expressions ---
    def visit_Literal(self, node):
        if node.type == "STRING":
            # Ensure proper Python string representation (e.g., quotes)
            return repr(node.value)
        elif node.type == "NULLTYPE":
            return "None"
        else:
            # Bools, Ints, Floats usually convert correctly with str()
            return str(node.value)

    def visit_Identifier(self, node):
        # Handle when the identifier itself has a name attribute (common pattern in our AST)
        if hasattr(node, 'name'):
            # Handle the case where name is also a complex object
            if hasattr(node.name, 'name'):
                return node.name.name
            # Handle the normal case where name is a string
            return node.name
        # Fallback to string representation
        return str(node)

    def visit_BinaryOp(self, node):
        left_code = self.visit(node.left)
        right_code = self.visit(node.right)
        op = OPERATOR_MAP.get(node.operator, node.operator) # Map AND/OR/NOT
        # Handle potential need for parentheses for precedence, although grammar helps
        return f"({left_code} {op} {right_code})"

    def visit_UnaryOp(self, node):
        operand_code = self.visit(node.operand)
        op = OPERATOR_MAP.get(node.operator, node.operator) # Map NOT
        # Handle potential need for parentheses
        return f"({op}{operand_code})" # Note space included in map for 'not '

    def visit_FunctionCall(self, node):
        print(f"DEBUG_ARGS: Inspecting FunctionCall arguments for node: {node}")
        if hasattr(node, 'name') and hasattr(node.name, 'name'):
            print(f"DEBUG_ARGS: Function name: {node.name.name}")
        
        # Extract function name, handling objects with a 'name' attribute
        if hasattr(node.name, 'name'):
            func_name = node.name.name  # Handle if it's an Identifier object
        else:
            func_name = str(node.name)  # Fallback to string representation
        
        # Extract and process arguments, properly handling different types
        args_code = []
        for i, arg in enumerate(node.arguments):
            print(f"DEBUG_ARGS: Processing arg {i}: {arg} (type: {type(arg)})")
            if hasattr(arg, 'name'):
                print(f"DEBUG_ARGS:   Arg has name attribute: {arg.name}")
            
            arg_code = self.visit(arg)
            print(f"DEBUG_ARGS:   After visit: {arg_code} (type: {type(arg_code)})")
            args_code.append(arg_code)  # Keep original format for lambdas
            
        # Create string version for normal function calls
        args_str_list = []
        for arg_code in args_code:
            if isinstance(arg_code, list):
                # If we got a list back, join its elements
                arg_str = ", ".join(str(item) for item in arg_code)
            else:
                arg_str = str(arg_code)
            args_str_list.append(arg_str)
            
        args_str = ", ".join(args_str_list)

        # Check if it's a known Fluent stdlib function
        if func_name in FLUENT_TO_PYTHON_MAP:
            py_equivalent = FLUENT_TO_PYTHON_MAP[func_name]
            if callable(py_equivalent):
                # If the map entry is a lambda, call it to generate code
                # Debug info
                print(f"DEBUG_ARGS: Using lambda for {func_name} with args: {args_code}")
                try:
                    # Handle case where args_code might be empty
                    if not args_code and func_name in ["GET_MAP_KEYS", "GET_LENGTH", "READ_LINE", "CLOSE_FILE"]:
                        # These functions expect at least one argument
                        print(f"WARNING: No arguments for {func_name}, creating dummy arg")
                        return py_equivalent(["'<missing>'"]) 
                    return py_equivalent(args_code)
                except Exception as e:
                    print(f"ERROR in lambda for {func_name}: {e}")
                    # Fallback to simple function call
                    return f"{func_name}({args_str})"
            else:
                # Simple name mapping or direct function call
                return f"{py_equivalent}({args_str})"
        else:
            # Assume it's a user-defined function
            return f"{func_name}({args_str})"

    def visit_ListLiteral(self, node):
        elements_code = [self.visit(el) for el in node.elements]
        return f"[{', '.join(elements_code)}]"

    def visit_MapLiteral(self, node):
        entries_code = [f"{self.visit(k)}: {self.visit(v)}" for k, v in node.entries]
        return f"{{{', '.join(entries_code)}}}"
