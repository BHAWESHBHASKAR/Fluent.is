from lark import Transformer, v_args
from lark.lexer import Token
import ast_nodes as ast

# Helper to extract value from Token if needed
def get_val(item):
    return item.value if isinstance(item, Token) else item

@v_args(inline=True) # Makes rule methods receive children directly as args
class ASTTransformer(Transformer):
    def start(self, *statements):
        # Filter out None results from ignored_statement
        return ast.Program([stmt for stmt in statements if stmt is not None])

    # --- Statements ---
    def variable_declaration(self, name, var_type, initializer=None):
        return ast.VariableDeclaration(get_val(name), var_type, initializer)

    def assignment(self, target, value):
        # Handle target correctly whether it's an identifier token or a more complex expression
        if hasattr(target, 'name'):
            # It's already an identifier object
            target_obj = target
        elif isinstance(target, str):
            # Convert string to identifier
            target_obj = ast.Identifier(get_val(target))
        else:
            # Use as is
            target_obj = target
            
        # Make sure value is also properly processed
        if isinstance(value, tuple) and len(value) >= 3:
            # Could be an arithmetic expression like (left, op, right)
            left, op, right = value[0], value[1], value[2]
            if op in ['+', '-', '*', '/']:
                # Create a BinaryOp node
                if op == '+':
                    value = ast.BinaryOp(left, "ADD", right)
                elif op == '-':
                    value = ast.BinaryOp(left, "SUB", right)
                elif op == '*':
                    value = ast.BinaryOp(left, "MUL", right)
                elif op == '/':
                    value = ast.BinaryOp(left, "DIV", right)
            
        return ast.Assignment(target_obj, value)

    def print_statement(self, expression):
        return ast.PrintStatement(expression)

    def function_call_statement(self, function_call):
        return ast.FunctionCallStatement(function_call)

    def if_statement(self, *args):
        # Parse out the condition and the blocks based on what comes after
        condition = args[0]
        # Extract then_block and else_block based on what we find
        if len(args) >= 2:
            # Find where the ELSE token/node would be, if present
            else_index = -1
            for i, arg in enumerate(args[1:], 1):
                if isinstance(arg, Token) and get_val(arg) == "ELSE":
                    else_index = i
                    break
                    
            if else_index != -1:
                # There is an else block
                then_block = args[1:else_index]
                else_block = args[else_index+1:]
            else:
                # No else block
                then_block = args[1:]
                else_block = None
        else:
            then_block = []
            else_block = None
            
        # Convert to lists if they're single items or tuples
        then_stmts = list(then_block) if isinstance(then_block, tuple) else [then_block] if then_block else []
        else_stmts = list(else_block) if isinstance(else_block, tuple) else [else_block] if else_block else []
        
        return ast.IfStatement(condition, then_stmts, else_stmts)

    def while_statement(self, *args):
        # Extract the condition and body from the args
        condition = args[0]
        if len(args) > 1:
            body = args[1:]
        else:
            body = []
            
        body_stmts = list(body) if isinstance(body, tuple) else [body] if body else []
        return ast.WhileStatement(condition, body_stmts)

    def foreach_statement(self, *args):
        # Extract components from the new format
        if len(args) < 3:
            return ast.ForeachStatement("", None, [])
            
        item = args[0]  # IDENTIFIER token for the iterator
        collection = args[1]  # Expression to iterate over
        
        # Process body statements
        body_stmts = []
        if len(args) > 2:
            for stmt in args[2:]:
                # Special handling for assignments in foreach body
                if isinstance(stmt, ast.Assignment) and hasattr(stmt, 'value'):
                    if isinstance(stmt.value, tuple) and len(stmt.value) >= 3:
                        # This is likely an arithmetic expression (left op right)
                        left, op, right = stmt.value[0], stmt.value[1], stmt.value[2]
                        # Create a BinaryOp node
                        binary_op = None
                        op_str = str(op).strip() if hasattr(op, '__str__') else ""
                        
                        if op_str == '+' or (hasattr(op, 'value') and op.value == '+'):
                            binary_op = ast.BinaryOp(left, "ADD", right)
                        elif op_str == '-' or (hasattr(op, 'value') and op.value == '-'):
                            binary_op = ast.BinaryOp(left, "SUB", right)
                        elif op_str == '*' or (hasattr(op, 'value') and op.value == '*'):
                            binary_op = ast.BinaryOp(left, "MUL", right)
                        elif op_str == '/' or (hasattr(op, 'value') and op.value == '/'):
                            binary_op = ast.BinaryOp(left, "DIV", right)
                            
                        if binary_op:
                            # Replace the tuple with a proper BinaryOp node
                            stmt.value = binary_op
                body_stmts.append(stmt)
        
        # Create a ForeachStatement with appropriate field names
        return ast.ForeachStatement(item, collection, body_stmts)

    def function_definition(self, name, params=None, return_type=None, *body):
        """Process function definition with name, parameters, return type and body statements"""
        # Handle the name - convert from Token if needed
        name = get_val(name)
        
        # Ensure parameters is a list
        if params is None:
            params = []
        elif isinstance(params, list) and len(params) == 1 and isinstance(params[0], list):
            # Handle nested list case from parameter_list
            params = params[0]
            
        # Handle return type
        if return_type is None:
            # Default to NULLTYPE if no return type specified
            return_type = ast.Type("NULLTYPE")
        elif return_type == "NOTHING":
            # Convert NOTHING to Python's None
            return_type = ast.Type("NULLTYPE")
            
        # Clean up the body statements (filter out None values)
        body_statements = [stmt for stmt in body if stmt is not None]
            
        # Create and return the FunctionDefinition node
        return ast.FunctionDefinition(name, params, return_type, body_statements)

    def parameter_list(self, *params):
        """Process a parameter list containing multiple parameters"""
        return list(params)

    def parameters(self, *params):
         # This rule collects multiple parameters separated by commas
        return list(params)

    def parameter(self, *args):
        """Process parameter declarations in both old and new styles"""
        if len(args) == 2:
            # New style: name: type
            name, param_type = args
            return ast.Parameter(get_val(name), param_type)
        elif len(args) == 3:
            # Old style: PARAM name AS type
            _, name, param_type = args
            return ast.Parameter(get_val(name), param_type)
        else:
            # Handle unexpected format
            raise ValueError(f"Unexpected parameter format: {args}")
            
    def return_statement(self, expression=None):
        return ast.ReturnStatement(expression)

    def break_statement(self):
        return ast.BreakStatement()

    def ignored_statement(self, _):
        return None # Don't include comments in the AST

    # --- Types ---
    def basetype(self, type_name=None):
        """Process basic types including 'NOTHING' type"""
        if type_name is None:
            # Handle the case when basetype is called without arguments
            # This might happen if the rule is matched but no token is provided
            return ast.Type("NULLTYPE")
            
        type_str = get_val(type_name)
        if type_str == "NOTHING":
            # Map NOTHING to NULLTYPE for compatibility
            type_str = "NULLTYPE"
        return ast.Type(type_str)

    def list_type(self, element_type):
        return ast.ListType(element_type)

    def map_type(self, key_type, value_type):
        return ast.MapType(key_type, value_type)

    # --- Expressions ---
    def logical_or(self, left, op=None, right=None): 
        if op is None or right is None:
            return left
        return ast.BinaryOp(left, "OR", right)
    
    def logical_and(self, left, op=None, right=None): 
        if op is None or right is None:
            return left
        return ast.BinaryOp(left, "AND", right)
    
    def eq(self, *args):
        return "=="
        
    def neq(self, *args):
        return "!="
        
    def lt(self, *args):
        return "<"
        
    def gt(self, *args):
        return ">"
        
    def lte(self, *args):
        return "<="
        
    def gte(self, *args):
        return ">="
        
    def comparison(self, left, op, right):
        """Process comparison expressions with the correct operators"""
        # Map the comparison operator token to the actual operator
        op_str = op
        return ast.Comparison(left, op_str, right)

    def arith_expr(self, left, op=None, right=None): 
        # Process arithmetic expression
        if op is None or right is None:
            return left
            
        # Get the operator value safely
        if hasattr(op, 'value'):
            op_val = get_val(op)
        else:
            op_val = str(op).strip()
            
        # Create the appropriate binary operation based on operator
        if op_val == '+':
            return ast.BinaryOp(left, "ADD", right)
        elif op_val == '-':
            return ast.BinaryOp(left, "SUB", right)
        elif op_val == '*':
            return ast.BinaryOp(left, "MUL", right)
        elif op_val == '/':
            return ast.BinaryOp(left, "DIV", right)
        else:
            return ast.BinaryOp(left, op_val, right)

    def term(self, left, op=None, right=None): 
        if op is None or right is None:
            return left
        return ast.BinaryOp(left, get_val(op), right)
    
    def factor(self, *args):
        # Handle unary operations like negation
        if len(args) == 1:  # It's just an atom
            return args[0]
        else:  # It's unary_op factor
            op, operand = args
            op_str = str(op).strip()
            
            # Check for negation with an integer literal
            if op_str == "-" and isinstance(operand, ast.Literal) and operand.type == "INTEGER":
                # Create a new integer literal with negative value
                value = -int(operand.value)
                return ast.Literal(value, "INTEGER")
            elif op_str == "-":
                return ast.UnaryOp("NEG", operand)
            elif op_str == "NOT" or op_str == "!":
                return ast.UnaryOp("NOT", operand)
            else:
                return ast.UnaryOp(get_val(op), operand)
    
    def unary_op(self, op=None):
        if op is None:
            return None
        return op

    def function_call(self, name, arguments=None):
        """Process function call with arguments"""
        # Handle function name - could be a token or a string
        if hasattr(name, 'value'):
            func_name = name.value
        else:
            func_name = str(name)
            
        # Process arguments
        args = []
        if arguments is not None:
            if isinstance(arguments, list):
                args = arguments
            else:
                args = [arguments]
                
        return ast.FunctionCall(func_name, args)
        
    def add(self, left, right):
        """Process addition operation"""
        return ast.BinaryOp(left, "ADD", right)
        
    def sub(self, left, right):
        """Process subtraction operation"""
        return ast.BinaryOp(left, "SUB", right)
        
    def mul(self, left, right):
        """Process multiplication operation"""
        return ast.BinaryOp(left, "MUL", right)
        
    def div(self, left, right):
        """Process division operation"""
        return ast.BinaryOp(left, "DIV", right)

    def arguments(self, *args):
        # Collects multiple arguments
        return list(args)

    def list_literal(self, *elements):
        return ast.ListLiteral(list(elements))

    def map_literal(self, *entries):
        # entries will be tuples from map_entry
        return ast.MapLiteral(list(entries))

    def map_entry(self, key, value):
        return (key, value) # Return tuple for map_literal

    # --- Atoms ---
    def NUMBER(self, n): return ast.Literal(int(get_val(n)), "INTEGER")
    def FLOAT_NUMBER(self, n): return ast.Literal(float(get_val(n)), "FLOAT")
    def STRING_LITERAL(self, s): return ast.Literal(eval(get_val(s)), "STRING") # Use eval to handle escapes
    def BOOLEAN_LITERAL(self, b):
        # Convert to Python boolean literal
        value = str(b).upper() == 'TRUE'
        return ast.Literal(value, "BOOLEAN")
    def NULL_LITERAL(self, _): return ast.Literal(None, "NULLTYPE")
    def IDENTIFIER(self, i): return ast.Identifier(get_val(i))
