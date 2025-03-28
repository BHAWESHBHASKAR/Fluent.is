# File: ast_transformer.py
# Transforms the Lark parse tree into custom AST nodes.

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

    def if_statement(self, condition, then_block, else_block=None):
        # Lark passes blocks as single items if one statement, or tuple if multiple
        then_stmts = list(then_block) if isinstance(then_block, tuple) else [then_block] if then_block else []
        else_stmts = list(else_block) if isinstance(else_block, tuple) else [else_block] if else_block else []
        return ast.IfStatement(condition, then_stmts, else_stmts)

    def while_statement(self, condition, body):
        body_stmts = list(body) if isinstance(body, tuple) else [body] if body else []
        return ast.WhileStatement(condition, body_stmts)

    def foreach_statement(self, item_name, iterable, body):
        body_stmts = list(body) if isinstance(body, tuple) else [body] if body else []
        return ast.ForeachStatement(get_val(item_name), iterable, body_stmts)

    def function_definition(self, name, params, return_type, *body_stmts):
        # Handle case where params might be missing (None)
        param_list = list(params) if isinstance(params, tuple) else [params] if params else []
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
    def basetype_integer(self):
        return ast.Type("INTEGER")
        
    def basetype_float(self):
        return ast.Type("FLOAT")
        
    def basetype_string(self):
        return ast.Type("STRING")
        
    def basetype_boolean(self):
        return ast.Type("BOOLEAN")
        
    def basetype_nulltype(self):
        return ast.Type("NULLTYPE")

    def list_type(self, element_type):
        return ast.ListType(element_type)

    def map_type(self, key_type, value_type):
        return ast.MapType(key_type, value_type)

    # --- Expressions ---
    def logical_or(self, left, op, right): 
        return ast.BinaryOp(left, "OR", right)
    
    def logical_and(self, left, op, right): 
        return ast.BinaryOp(left, "AND", right)
    
    def comparison(self, left, op, right): 
        return ast.BinaryOp(left, get_val(op), right)
    
    def arith_expr(self, left, op, right): 
        return ast.BinaryOp(left, get_val(op), right)
    
    def term(self, left, op, right): 
        return ast.BinaryOp(left, get_val(op), right)
    
    def factor(self, op, operand): 
        return ast.UnaryOp(get_val(op), operand) # Only handles unary op case

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
