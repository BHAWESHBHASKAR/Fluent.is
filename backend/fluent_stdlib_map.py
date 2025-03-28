# File: fluent_stdlib_map.py
# Maps Fluent standard library function names to Python equivalents.

# Direct mapping of Fluent standard library functions to their Python equivalents
FLUENT_TO_PYTHON_MAP = {
    # IO
    "PRINT": "print",  # Direct map

    # String Operations
    "CONCATENATE_STRINGS": None,  # Special handling in transpiler
    "GET_STRING_LENGTH": "len",  # Direct map to Python's len()
    "SPLIT_STRING": None,  # Special handling in transpiler

    # List Operations
    "GET_LENGTH": "len",  # Also works for lists
    "ADD_ELEMENT": None,  # Special handling in transpiler
    "GET_ELEMENT": None,  # Special handling in transpiler
    "SET_ELEMENT": None,  # Special handling in transpiler

    # Map Operations
    "MAP_HAS_KEY": None,  # Special handling in transpiler
    "GET_MAP_VALUE": None,  # Special handling in transpiler
    "SET_MAP_VALUE": None,  # Special handling in transpiler
    "GET_MAP_KEYS": None,  # Special handling in transpiler

    # Type Conversion
    "INTEGER_TO_STRING": "str",
    "FLOAT_TO_STRING": "str",
    "BOOLEAN_TO_STRING": "str",
    "NULL_TO_STRING": None,  # Special handling in transpiler
    "STRING_TO_INTEGER": "int",
    "STRING_TO_FLOAT": "float",
    "STRING_TO_BOOLEAN": None,  # Special handling in transpiler

    # File Operations
    "OPEN_FILE": None,  # Special handling in transpiler
    "READ_LINE": None,  # Special handling in transpiler
    "WRITE_LINE": None,  # Special handling in transpiler
    "CLOSE_FILE": None,  # Special handling in transpiler
}

# Map operators to their Python equivalents
OPERATOR_MAP = {
    "+": "+", "-": "-", "*": "*", "/": "/",  # Arithmetic
    "==": "==", "!=": "!=", "<": "<", "<=": "<=", ">": ">", ">=": ">=",  # Comparison
    "AND": "and", "OR": "or", "NOT": "not "  # Logical (Note space after 'not')
}
