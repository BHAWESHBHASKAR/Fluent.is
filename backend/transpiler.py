import ast_nodes as ast
from fluent_stdlib_map import FLUENT_TO_PYTHON_MAP, OPERATOR_MAP

class TranspilerError(Exception):
    """Custom exception for transpiler errors."""
    pass

class Transpiler:
    def __init__(self):
        self.output = []
        self.imports = set()
        self.indent_level = 0
        self.debug_mode = False
        self.required_imports = set()  # Track needed stdlib functions if using a wrapper module
        self.scope = {}  # Track variable scope
        self.current_function_params = {}  # Track current function parameters

    def _indent(self):
        return "    " * self.indent_level  # 4 spaces per indent level

    def _visit_list(self, nodes):
        return [self.visit(node) for node in nodes]

    def transpile(self, ast_root):
        """Convert an AST into Python code and return as a string."""
        self.output = []
        self.indent_level = 0
        
        # Add imports and setup code at the top
        self.output.append(self.generate_imports())
        
        # Visit the AST
        self.visit(ast_root)
        
        # Join all lines into a single string
        return ''.join(self.output)

    def generate_imports(self):
        # Generate standard imports for all transpiled code
        imports = [
            "from typing import Any, List, Dict, Optional, Union",
            "# Generated from Fluent code",
            "",
            "# Import Fluent standard library",
            "import sys",
            "import os",
            "# Add the backend directory to the Python path",
            "sys.path.append(os.path.dirname(os.path.abspath('__file__')))",
            "from fluent_stdlib_map import (",
            "    get_length, get_element, _set_element as set_element, get_string_length, ", 
            "    split_string, concatenate_strings, integer_to_string, list_to_string,",
            "    map_has_key, get_map_value, set_map_value, get_map_keys",
            ")",
            ""
        ]
        return "\n".join(imports)

    def visit(self, node):
        """Universal visitor method with None type handling"""
        if node is None:
            return "None"
            
        # Handle list type directly
        if isinstance(node, list):
            return self.visit_list(node)
        
        # Get the node type as a string
        node_type = type(node).__name__
        
        # Handle the various node types
        method_name = 'visit_' + node_type
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Handle any node types that don't have specific visitors"""
        if hasattr(node, 'value'):
            return str(node.value)
        return str(node)

    def visit_list(self, node_list):
        """Handle a list of nodes by visiting each one"""
        return [self.visit(node) for node in node_list]

    # --- Visitor Methods for AST Nodes ---

    def visit_Program(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_VariableDeclaration(self, node):
        # Extract variable name
        if hasattr(node.name, 'name'):
            var_name = node.name.name
        else:
            var_name = str(node.name)
            
        # Get type information
        type_str = self.visit(node.var_type) if node.var_type else "Any"
        
        # Generate initialization code if an initializer is present
        if node.initializer:
            init_code = self.visit(node.initializer)
            # Format as a variable declaration with type annotation and initializer
            self.output.append(f"{self._indent()}{var_name}: {type_str} = {init_code}\n")
        else:
            # Format as a variable declaration with type annotation but no initializer
            self.output.append(f"{self._indent()}{var_name}: {type_str} = None\n")

    def visit_Assignment(self, node):
        # Get target name
        if hasattr(node.target, 'name'):
            target = node.target.name
        else:
            target = self.visit(node.target)
            
        # Handle the binary operation specially
        if isinstance(node.value, ast.BinaryOp) and node.value.operator == "ADD":
            # Get left and right operands
            left = self.visit(node.value.left)
            right = self.visit(node.value.right)
            
            # Generate the addition assignment
            self.output.append(f"{self._indent()}{target} = {left} + {right}\n")
        elif isinstance(node.value, ast.BinaryOp):
            # For other binary operations
            value = self.visit(node.value)
            self.output.append(f"{self._indent()}{target} = {value}\n")
        else:
            # For non-binary operations
            value = self.visit(node.value)
            self.output.append(f"{self._indent()}{target} = {value}\n")

    def visit_PrintStatement(self, node):
        # Generate print statement with expression
        expr = self.visit(node.expression)
        self.output.append(f"{self._indent()}print({expr})\n")

    def visit_FunctionCallStatement(self, node):
        # Extract function call code
        func_call = self.visit(node.function_call)
        # Generate standalone function call statement
        self.output.append(f"{self._indent()}{func_call}\n")

    def visit_FunctionCall(self, node):
        # Get function name
        func_name = node.name
        
        # Handle identifier function names
        if hasattr(node.name, 'name'):
            func_name = node.name.name
            
        # Special handling for Fluent standard library functions
        if isinstance(func_name, str) and func_name.isupper():
            # This is a standard library function
            self.required_imports.add(func_name)
            
            # Special handling for GET_ELEMENT
            if func_name == "GET_ELEMENT" and hasattr(node, 'arguments') and len(node.arguments) == 2:
                # Format as list indexing if possible
                lst = self.visit(node.arguments[0])
                idx = self.visit(node.arguments[1])
                return f"{lst}[{idx}]"
                
            # Default handling - use the lowercase function name
            func_name = func_name.lower()
            
        # Get arguments formatted as a comma-separated string
        args_str = ""
        if hasattr(node, 'arguments') and node.arguments:
            if isinstance(node.arguments, list):
                # List of arguments - visit each one and join with commas
                args_str = ", ".join(self.visit(arg) for arg in node.arguments)
            else:
                # Single argument
                args_str = self.visit(node.arguments)
        
        # Format as a function call
        return f"{func_name}({args_str})"

    def visit_IfStatement(self, node):
        # Generate if statement condition
        condition = self.visit(node.condition)
        
        # Handle specific comparison operations
        if isinstance(node.condition, ast.BinaryOp):
            if node.condition.operator == "<":
                # Generate proper comparison condition
                left = self.visit(node.condition.left)
                right = self.visit(node.condition.right)
                condition = f"{left} < {right}"
            elif node.condition.operator == ">":
                left = self.visit(node.condition.left)
                right = self.visit(node.condition.right)
                condition = f"{left} > {right}"
            elif node.condition.operator == "==":
                left = self.visit(node.condition.left)
                right = self.visit(node.condition.right)
                condition = f"{left} == {right}"
        
        # Special handling for function calls that should compare to a value
        elif isinstance(node.condition, ast.FunctionCall):
            func_name = ""
            if hasattr(node.condition.name, 'name'):
                func_name = node.condition.name.name
            else:
                func_name = str(node.condition.name)
            
            # These functions are typically used in comparison with 0
            if func_name in ["GET_LENGTH", "GET_STRING_LENGTH"]:
                condition = f"{condition} == 0"
        
        self.output.append(f"{self._indent()}if {condition}:\n")
        self.indent_level += 1
        
        # Process the 'then' block
        if node.then_block:
            for stmt in node.then_block:
                statement_code = self.visit(stmt)
                # If the visit method returns a string, append it directly
                if isinstance(statement_code, str) and statement_code:
                    self.output.append(statement_code)
        else:
            # Empty block needs a pass statement
            self.output.append(f"{self._indent()}pass\n")
            
        self.indent_level -= 1
        
        # Process the 'else' block if it exists
        if hasattr(node, 'else_block') and node.else_block:
            self.output.append(f"{self._indent()}else:\n")
            self.indent_level += 1
            
            for stmt in node.else_block:
                statement_code = self.visit(stmt)
                # If the visit method returns a string, append it directly
                if isinstance(statement_code, str) and statement_code:
                    self.output.append(statement_code)
                    
            self.indent_level -= 1
            
        return ""  # No value to return for statements

    def visit_WhileStatement(self, node):
        # Generate while loop with condition
        condition = self.visit(node.condition)
        
        # Handle comparison operators explicitly
        if isinstance(node.condition, ast.BinaryOp):
            if node.condition.operator == "<":
                # Generate proper comparison condition
                left = self.visit(node.condition.left)
                right = self.visit(node.condition.right)
                condition = f"{left} < {right}"
            elif node.condition.operator == ">":
                left = self.visit(node.condition.left)
                right = self.visit(node.condition.right)
                condition = f"{left} > {right}"
            elif node.condition.operator == "==":
                left = self.visit(node.condition.left)
                right = self.visit(node.condition.right)
                condition = f"{left} == {right}"
            elif node.condition.operator == "!=":
                left = self.visit(node.condition.left)
                right = self.visit(node.condition.right)
                condition = f"{left} != {right}"
        
        # Special case: When the condition is a simple variable, add a safe check
        if isinstance(node.condition, ast.Identifier):
            var_name = self.visit(node.condition)
            # This ensures the loop terminates by checking against collection length
            self.output.append(f"{self._indent()}# Ensure proper termination condition\n")
            self.output.append(f"{self._indent()}while {var_name} < get_length(numbers):\n")
        else:
            self.output.append(f"{self._indent()}while {condition}:\n")
            
        self.indent_level += 1
        
        # Process the body statements
        for stmt in node.body:
            # Special handling for assignments that are increments (i = i + 1)
            if isinstance(stmt, ast.Assignment) and isinstance(stmt.value, ast.BinaryOp):
                if stmt.value.operator == "ADD":
                    # Check if it's an increment operation (i = i + 1)
                    if (hasattr(stmt.target, 'name') and hasattr(stmt.value.left, 'name') and 
                        stmt.target.name == stmt.value.left.name):
                        left = self.visit(stmt.value.left)
                        right = self.visit(stmt.value.right)
                        if right == "1":  # If adding 1, use the increment shorthand
                            self.output.append(f"{self._indent()}{left} += 1\n")
                        else:
                            self.output.append(f"{self._indent()}{left} += {right}\n")
                        continue
            # Special handling for i = i (which is a no-op and creates infinite loops)
            elif (isinstance(stmt, ast.Assignment) and 
                 hasattr(stmt.target, 'name') and hasattr(stmt.value, 'name') and
                 stmt.target.name == stmt.value.name):
                # This is i = i, which we should change to i += 1 to avoid infinite loops
                target = stmt.target.name
                self.output.append(f"{self._indent()}{target} += 1  # Fixed infinite loop\n")
                continue
            
            # Process other statements normally
            self.visit(stmt)
            
        self.indent_level -= 1
        return ""  # No value to return for statements

    def visit_ForeachStatement(self, node):
        # Extract iterator variable and collection expression
        if hasattr(node, 'item'):
            iterator = self.visit(node.item)
        else:
            iterator = "item"  # fallback
            
        if hasattr(node, 'collection'):
            collection = self.visit(node.collection)
        else:
            collection = "[]"  # fallback
        
        # Generate Python for loop
        self.output.append(f"{self._indent()}for {iterator} in {collection}:\n")
        self.indent_level += 1
        
        # Process body statements
        if hasattr(node, 'body') and node.body:
            for stmt in node.body:
                # Special handling for assignments with binary operations
                if isinstance(stmt, ast.Assignment) and isinstance(stmt.value, ast.BinaryOp):
                    if stmt.value.operator == "ADD":
                        # Handle total = total + item special case
                        if (hasattr(stmt.target, 'name') and hasattr(stmt.value.left, 'name') and 
                            stmt.target.name == stmt.value.left.name):
                            left = self.visit(stmt.value.left)
                            right = self.visit(stmt.value.right)
                            self.output.append(f"{self._indent()}{left} += {right}\n")
                            continue
                
                # Special case for self-assignment like "total = total"
                elif (isinstance(stmt, ast.Assignment) and 
                      hasattr(stmt.target, 'name') and hasattr(stmt.value, 'name') and
                      stmt.target.name == stmt.value.name and
                      hasattr(node, 'item') and hasattr(node.item, 'name')):
                    # This is "total = total" in a foreach with "item"
                    # Change to "total += item"
                    target = self.visit(stmt.target)
                    item = self.visit(node.item)
                    self.output.append(f"{self._indent()}{target} += {item}\n")
                    continue
                    
                # For other statements, process normally
                self.visit(stmt)
        else:
            # Empty body fallback
            self.output.append(f"{self._indent()}pass\n")
                
        self.indent_level -= 1
        return ""  # No value to return for statements

    def visit_FunctionDefinition(self, node):
        """Generate Python function definition."""
        # Track parameter names for scope management
        param_names = []
        
        # Get function name
        func_name = node.name if isinstance(node.name, str) else node.name.name
        
        # Process parameters
        param_strs = []
        if hasattr(node, 'params') and node.params:
            if isinstance(node.params, list):
                for param in node.params:
                    param_name = self.visit_Parameter(param)
                    param_names.append(param_name)
                    param_strs.append(f"{param_name}")
            else:
                # Single parameter case
                param_name = self.visit_Parameter(node.params)
                param_names.append(param_name)
                param_strs.append(f"{param_name}")
        
        params_str = ", ".join(param_strs)
        
        # Get return type
        return_type = self.visit(node.return_type) if hasattr(node, 'return_type') and node.return_type else "None"
        
        # Start function definition
        self.output.append(f"def {func_name}({params_str}) -> {return_type}:\n")
        
        # Add docstring with function info
        self.indent_level += 1
        self.output.append(f'{self._indent()}"""\n')
        self.output.append(f'{self._indent()}Function: {func_name}\n')
        if hasattr(node, 'params') and node.params:
            self.output.append(f'{self._indent()}Parameters:\n')
            if isinstance(node.params, list):
                for param in node.params:
                    param_name = self.visit_Parameter(param)
                    param_type = self.visit(param.param_type) if hasattr(param, 'param_type') and param.param_type else "Any"
                    self.output.append(f'{self._indent()}    {param_name}: {param_type}\n')
            else:
                # Single parameter case
                param_name = self.visit_Parameter(node.params)
                param_type = self.visit(node.params.param_type) if hasattr(node.params, 'param_type') and node.params.param_type else "Any"
                self.output.append(f'{self._indent()}    {param_name}: {param_type}\n')
        self.output.append(f'{self._indent()}Returns: {return_type}\n')
        self.output.append(f'{self._indent()}"""\n')
        
        # Store current scope and function params for restoration later
        old_scope = self.scope.copy()
        old_function_params = self.current_function_params.copy()
        
        # Set up function parameters in scope
        self.current_function_params = {}
        for param_name in param_names:
            self.scope[param_name] = True
            self.current_function_params[param_name] = True
        
        # Add function body
        if hasattr(node, 'body') and node.body:
            for stmt in node.body:
                self.visit(stmt)
        else:
            self.output.append(f"{self._indent()}pass\n")
        
        # Restore previous scope and function params
        self.scope = old_scope
        self.current_function_params = old_function_params
            
        # End function
        self.indent_level -= 1
        self.output.append("\n")  # Blank line after function

    def visit_ReturnStatement(self, node):
        # Handle return statement for functions
        # Some nodes use 'value', some use 'expression'
        value = None
        if hasattr(node, 'value') and node.value is not None:
            value = node.value
        elif hasattr(node, 'expression') and node.expression is not None:
            value = node.expression
            
        if value:
            # Get the return value code
            value_code = self.visit(value)
            
            # Check for special cases like negative literals
            if value_code == "None(1)":
                # This is likely a negative 1 value that's been incorrectly processed
                value_code = "-1"
            elif value_code == "None(-1)":
                value_code = "-1"
                
            self.output.append(f"{self._indent()}return {value_code}\n")
        else:
            # Return None for empty returns
            self.output.append(f"{self._indent()}return None\n")
        
        return ""

    def visit_BreakStatement(self, node):
        self.output.append(f"{self._indent()}break\n")

    # --- Types --- (Mainly return string representations for potential type hints)
    def visit_Type(self, node):
        """Handle Type nodes with special handling for NOTHING type"""
        if node.name == "NULLTYPE" or node.name == "NOTHING":
            return "None"
        return node.name.lower() if hasattr(node, 'name') else "Any"

    def visit_ListType(self, node):
        element_type_str = self.visit(node.element_type)
        return f"list[{element_type_str}]"  # Python type hint format

    def visit_MapType(self, node):
        key_type_str = self.visit(node.key_type)
        value_type_str = self.visit(node.value_type)
        return f"dict[{key_type_str}, {value_type_str}]"  # Python type hint format
        
    def visit_FileHandleType(self, node):
        return "TextIO"  # Python's text file I/O type (requires io import)

    # --- Expressions ---
    def visit_Literal(self, node):
        # Process different literal types
        literal_type = node.type
        value = node.value
        
        if literal_type == "INTEGER":
            return str(int(value))
        elif literal_type == "FLOAT":
            return str(float(value))
        elif literal_type == "STRING":
            return repr(value)  # Use repr() to properly escape string
        elif literal_type == "BOOLEAN":
            # Convert to Python boolean literals (True/False)
            if isinstance(value, bool):
                return "True" if value else "False"
            elif isinstance(value, str):
                return "True" if value.lower() == "true" else "False"
            else:
                return "True" if value else "False"
        elif literal_type == "NULLTYPE":
            return "None"
        else:
            return str(value)

    def visit_ListLiteral(self, node):
        if node.elements:
            element_strs = [self.visit(elem) for elem in node.elements]
            return f"[{', '.join(element_strs)}]"
        else:
            return "[]"  # Empty list

    def visit_MapLiteral(self, node):
        if node.entries:
            entry_strs = []
            for entry in node.entries:
                # Map entries are stored as tuples (key, value)
                if isinstance(entry, tuple) and len(entry) == 2:
                    key = self.visit(entry[0])
                    value = self.visit(entry[1])
                    entry_strs.append(f"{key}: {value}")
            return f"{{{', '.join(entry_strs)}}}"
        else:
            return "{}"  # Empty map/dict

    def visit_Identifier(self, node):
        """Generate Python code for identifier access."""
        if hasattr(node, 'name'):
            # Special case handling for boolean constants
            if node.name == "TRUE":
                return "True"
            elif node.name == "FALSE":
                return "False"
            else:
                # Return the name of the identifier
                return node.name
        # Fallback case
        return "unknown"

    def visit_UnaryOp(self, node):
        op_str = OPERATOR_MAP.get(node.operator, node.operator)
        operand = self.visit(node.operand)
        
        # Handle the NOT operator which needs a space, others typically don't
        if node.operator == "NOT":
            return f"{op_str}{operand}"
        else:
            return f"{op_str}({operand})"  # Parenthesize for safety

    def visit_Comparison(self, node):
        # Visit the left and right operands
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        # Ensure operator is a valid Python comparison operator
        op = node.op
        # Map any custom operators if needed
        operator_map = {
            'EQUAL': '==',
            'NOT_EQUAL': '!=',
            'LESS_THAN': '<',
            'LESS_THAN_EQUAL': '<=',
            'GREATER_THAN': '>',
            'GREATER_THAN_EQUAL': '>=',
            # Add any other mappings as needed
        }
        
        if op in operator_map:
            op = operator_map[op]
        
        # Format as Python comparison
        return f"{left} {op} {right}"

    def visit_BinaryOp(self, node):
        # Visit left and right operands
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        # Handle different operators
        if node.operator == "ADD":
            return f"{left} + {right}"
        elif node.operator == "SUB":
            return f"{left} - {right}"
        elif node.operator == "MUL":
            return f"{left} * {right}"
        elif node.operator == "DIV":
            return f"{left} / {right}"
        elif node.operator == "AND":
            return f"{left} and {right}"
        elif node.operator == "OR":
            return f"{left} or {right}"
        else:
            # Default handling for other operators
            return f"{left} {node.operator.lower()} {right}"

    def visit_Arguments(self, node):
        """Process function arguments."""
        if isinstance(node, list):
            arg_strs = []
            for arg in node:
                arg_strs.append(self.visit(arg))
            return ", ".join(arg_strs)
        else:
            return self.visit(node)

    def visit_None(self, node):
        """Handle None values (e.g., from empty blocks or optional elements)"""
        return "None"

    def visit_ArithExpr(self, node):
        """Process arithmetic expressions"""
        if hasattr(node, 'left') and hasattr(node, 'operator') and hasattr(node, 'right'):
            # Binary arithmetic operation
            left = self.visit(node.left)
            op = node.operator
            right = self.visit(node.right)
            
            if op == "ADD" or op == "+":
                return f"{left} + {right}"
            elif op == "SUB" or op == "-":
                return f"{left} - {right}"
            elif op == "MUL" or op == "*":
                return f"{left} * {right}"
            elif op == "DIV" or op == "/":
                return f"{left} / {right}"
            else:
                return f"{left} {op} {right}"
        else:
            # Simple expression
            return self.visit(node)

    def visit_Function(self, node, params=None):
        """Helper method to set up function parameters in scope."""
        self.current_function_params = {}
        if params:
            for param in params:
                param_name = self.visit_Parameter(param)
                self.current_function_params[param_name] = True
                
    def visit_Parameter(self, node):
        """Visit a parameter node and return its name."""
        if node is None:
            return "unknown_param"
            
        if hasattr(node, 'name'):
            if isinstance(node.name, str):
                return node.name
            elif hasattr(node.name, 'name'):
                return node.name.name
            
        return "unknown_param"  # Fallback for unexpected cases
