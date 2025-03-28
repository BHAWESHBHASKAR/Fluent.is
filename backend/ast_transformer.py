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
        return ast.Assignment(get_val(target), value)

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
        # Extract components from args
        if len(args) < 2:
            return ast.ForeachStatement("", None, [])
            
        item_name = args[0]
        iterable = args[1]
        
        if len(args) > 2:
            body = args[2:]
        else:
            body = []
            
        body_stmts = list(body) if isinstance(body, tuple) else [body] if body else []
        return ast.ForeachStatement(get_val(item_name), iterable, body_stmts)

    def function_definition(self, *args):
        # Extract components from a variable number of args
        if len(args) < 1:
            return ast.FunctionDefinition("", [], None, [])
            
        name = args[0]
        
        # Find parameters and return type in the argument list
        param_index = -1
        return_type_index = -1
        
        for i, arg in enumerate(args):
            if isinstance(arg, list) and all(hasattr(p, 'name') for p in arg if p is not None):
                param_index = i
            elif hasattr(arg, 'name') and arg.name in ["INTEGER", "FLOAT", "STRING", "BOOLEAN", "NULLTYPE", "LIST", "MAP"]:
                return_type_index = i
                
        # Extract parameters if found
        params = args[param_index] if param_index != -1 else None
        
        # Extract return type if found
        return_type = args[return_type_index] if return_type_index != -1 else None
        
        # Find body statements (should be everything after the header elements)
        body_start_index = max(1, param_index, return_type_index) + 1
        if body_start_index < len(args):
            body_stmts = args[body_start_index:]
        else:
            body_stmts = []
                
        # Handle case where params might be missing (None)
        param_list = list(params) if isinstance(params, tuple) else [params] if params else []
        
        # Create the function definition
        return ast.FunctionDefinition(get_val(name), param_list, return_type, list(body_stmts))

    def parameters(self, *params):
         # This rule collects multiple parameters separated by commas
        return list(params)

    def parameter(self, name, param_type):
        return ast.Parameter(get_val(name), param_type)

    def return_statement(self, expression=None):
        return ast.ReturnStatement(expression)

    def break_statement(self):
        return ast.BreakStatement()

    def ignored_statement(self, _):
        return None # Don't include comments in the AST

    # --- Types ---
    def basetype(self, token=None):
        if token is None:
            # Called without arguments from the grammar rule
            return ast.Type("UNKNOWN")
        return ast.Type(get_val(token))

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
    
    def comparison(self, left, op=None, right=None):
        if op is None or right is None:  # No comparison operator was present
            return left  # Just pass the arith_expr through
        return ast.BinaryOp(left, get_val(op), right)
    
    def comp_op(self, op=None):
        if op is None:
            return None
        return op
    
    def arith_expr(self, left, op=None, right=None): 
        if op is None or right is None:
            return left
        return ast.BinaryOp(left, get_val(op), right)
    
    def term(self, left, op=None, right=None): 
        if op is None or right is None:
            return left
        return ast.BinaryOp(left, get_val(op), right)
    
    def factor(self, *args):
        if len(args) == 1:  # It's just an atom
            return args[0]
        else:  # It's unary_op factor
            op, operand = args
            return ast.UnaryOp(get_val(op), operand)
    
    def unary_op(self, op=None):
        if op is None:
            return None
        return op

    def function_call(self, name, args=None):
        arg_list = list(args) if isinstance(args, tuple) else [args] if args else []
        return ast.FunctionCall(get_val(name), arg_list)

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
    def BOOLEAN_LITERAL(self, b): return ast.Literal(get_val(b) == "TRUE", "BOOLEAN")
    def NULL_LITERAL(self, _): return ast.Literal(None, "NULLTYPE")
    def IDENTIFIER(self, i): return ast.Identifier(get_val(i))
