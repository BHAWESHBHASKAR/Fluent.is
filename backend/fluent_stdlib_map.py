# File: fluent_stdlib_map.py
# Maps Fluent standard library function names to Python equivalents.

# This is a simple dictionary lookup. More complex scenarios might need
# functions here that generate the Python code dynamically.

# Helper function for safely extracting string arguments from potentially complex data structures
def extract_str_arg(args, index):
    """Safely extract a string argument from a potentially complex nested structure."""
    if not args or index >= len(args):
        return "\"<missing>\""  # Return a placeholder for missing args
        
    arg = args[index]
    
    # Handle nested lists
    if isinstance(arg, list):
        if len(arg) > 0:
            # In the case of function call arguments, we want the direct variable name
            # without quotes (since they're variable references, not literal strings)
            return arg[0]
        return "\"<empty>\""
        
    # Handle direct values
    return str(arg)

FLUENT_TO_PYTHON_MAP = {
    # IO
    "PRINT": "print", # Direct map

    # String Operations
    "CONCATENATE_STRINGS": lambda args: f"({args[0][0]} + {args[0][1] if len(args[0]) > 1 else 'None'})", # Handle nested list structure
    "GET_STRING_LENGTH": "len",
    "CONVERT_INTEGER_TO_STRING": "str",
    "CONVERT_FLOAT_TO_STRING": "str",
    "SPLIT_STRING": lambda args: f"{args[0]}.split({args[1]})", # Assume simple split

    # List Operations
    "CREATE_LIST": "list", # Map to list constructor (might need refinement based on usage)
    "GET_LENGTH": "len",
    "ADD_ELEMENT": lambda args: f"{args[0]}.append({args[1]})",
    "GET_ELEMENT": lambda args: f"{args[0]}[{args[1]}]", # Direct index access
    "SET_ELEMENT": lambda args: f"{args[0]}[{args[1]}] = {args[2]}",

    # Map Operations
    "CREATE_MAP": "dict", # Map to dict constructor
    "MAP_HAS_KEY": lambda args: f"{args[1]} in {args[0]}", # Use Python's 'in'
    "GET_MAP_VALUE": lambda args: f"{args[0]}[{args[1]}]",
    "SET_MAP_VALUE": lambda args: f"{args[0]}[{args[1]}] = {args[2]}",
    "GET_MAP_KEYS": lambda args: f"list({args[0]}.keys())", # Convert keys view to list

    # Type Conversion (potentially more needed)
    "CONVERT_TO_INTEGER": "int",
    "CONVERT_TO_FLOAT": "float",

    # File IO (Needs more robust implementation - placeholders)
    "OPEN_FILE": "open", # Basic mapping
    "READ_LINE": lambda args: f"{args[0]}.readline().rstrip('\\n')", # Basic readline, strip newline
    "CLOSE_FILE": lambda args: f"{args[0]}.close()",

    # Others
    # "GET_ERROR_MESSAGE": lambda args: f"str({args[0]})" # Example for error handling
}

# Map operators too, for clarity if needed elsewhere, although handled in transpiler visitor
OPERATOR_MAP = {
    "+": "+", "-": "-", "*": "*", "/": "/", # Arithmetic
    "==": "==", "!=": "!=", "<": "<", "<=": "<=", ">": ">", ">=": ">=", # Comparison
    "AND": "and", "OR": "or", "NOT": "not " # Logical (Note space after 'not ')
}
