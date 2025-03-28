# File: ast_nodes.py
# Defines classes for Fluent Abstract Syntax Tree (AST) nodes.

class Node:
    """Base class for all AST nodes."""
    pass

# Statements
class Program(Node):
    def __init__(self, statements):
        self.statements = statements # List of statement nodes

class VariableDeclaration(Node):
    def __init__(self, name, var_type, initializer):
        self.name = name # IDENTIFIER token
        self.var_type = var_type # Type node
        self.initializer = initializer # Expression node

class Assignment(Node):
    def __init__(self, target, value):
        self.target = target # IDENTIFIER token
        self.value = value # Expression node

class PrintStatement(Node):
    def __init__(self, expression):
        self.expression = expression # Expression node

class FunctionCallStatement(Node):
    def __init__(self, function_call):
        self.function_call = function_call # FunctionCall node

class IfStatement(Node):
    def __init__(self, condition, then_block, else_block):
        self.condition = condition # Expression node
        self.then_block = then_block # List of statement nodes
        self.else_block = else_block # List of statement nodes or None

class WhileStatement(Node):
    def __init__(self, condition, body):
        self.condition = condition # Expression node
        self.body = body # List of statement nodes

class ForeachStatement(Node):
    def __init__(self, item_name, iterable, body):
        self.item_name = item_name # IDENTIFIER token
        self.iterable = iterable   # Expression node (e.g., a list)
        self.body = body           # List of statement nodes

class FunctionDefinition(Node):
    def __init__(self, name, params, return_type, body):
        self.name = name # IDENTIFIER token
        self.params = params # List of Parameter nodes
        self.return_type = return_type # Type node
        self.body = body # List of statement nodes

class Parameter(Node):
    def __init__(self, name, param_type):
        self.name = name # IDENTIFIER token
        self.param_type = param_type # Type node

class ReturnStatement(Node):
    def __init__(self, expression):
        self.expression = expression # Expression node or None

class BreakStatement(Node):
    pass # No data needed

# Types
class Type(Node):
    def __init__(self, name):
        self.name = name # String like "INTEGER", "STRING"

class ListType(Type):
    def __init__(self, element_type):
        super().__init__("LIST")
        self.element_type = element_type # Another Type node

class MapType(Type):
    def __init__(self, key_type, value_type):
        super().__init__("MAP")
        self.key_type = key_type # Type node
        self.value_type = value_type # Type node

# Expressions
class Literal(Node):
    def __init__(self, value, literal_type):
        self.value = value # The actual value (int, float, str, bool, None)
        self.type = literal_type # String like "INTEGER", "STRING", etc.

class Identifier(Node):
    def __init__(self, name):
        self.name = name # String (variable name)

class BinaryOp(Node):
    def __init__(self, left, operator, right):
        self.left = left # Expression node
        self.operator = operator # Operator string like "+", "==", "AND"
        self.right = right # Expression node

class UnaryOp(Node):
    def __init__(self, operator, operand):
        self.operator = operator # Operator string like "-", "NOT"
        self.operand = operand # Expression node

class FunctionCall(Node):
    def __init__(self, name, arguments):
        self.name = name # IDENTIFIER token
        self.arguments = arguments # List of expression nodes

class ListLiteral(Node):
    def __init__(self, elements):
        self.elements = elements # List of expression nodes

class MapLiteral(Node):
    def __init__(self, entries):
        self.entries = entries # List of tuples (key_expr_node, value_expr_node)
