# File: fluent_stdlib_map.py
# Maps Fluent standard library function names to Python implementations for the LLM-friendly Major PoC.

# Python implementation functions for special handling cases
def _concatenate_strings(str1, str2):
    """Concatenates two strings safely, returning None if inputs are not strings."""
    try:
        return str(str1) + str(str2)
    except:
        return None

def _get_element(lst, index):
    """Gets element at index, returns None if index is out of bounds."""
    try:
        return lst[index]
    except (IndexError, TypeError):
        return None

def _set_element(lst, index, value):
    """Sets element at index, returns True if successful, False if index out of bounds."""
    try:
        lst[index] = value
        return True
    except (IndexError, TypeError):
        return False

def _add_element(lst, element):
    """Adds element to list, returns None (modifies list in-place)."""
    try:
        lst.append(element)
        return None
    except:
        return None

def _map_has_key(map_obj, key):
    """Checks if a map has the specified key."""
    try:
        return key in map_obj
    except:
        return False

def _get_map_value(map_obj, key):
    """Gets value for key from map, returns None if key not found."""
    try:
        return map_obj.get(key, None)  # Default to None if key not found
    except:
        return None

def _set_map_value(map_obj, key, value):
    """Sets key-value in map, returns None (modifies map in-place)."""
    try:
        map_obj[key] = value
        return None
    except:
        return None

def _get_map_keys(map_obj):
    """Returns list of keys from map."""
    try:
        return list(map_obj.keys())
    except:
        return None

def _string_to_integer(s):
    """Converts string to integer, returns None if conversion fails."""
    try:
        return int(s)
    except:
        return None

def _string_to_float(s):
    """Converts string to float, returns None if conversion fails."""
    try:
        return float(s)
    except:
        return None

def _string_to_boolean(s):
    """Convert a string to a boolean value"""
    if isinstance(s, str):
        return s.lower() in ('true', 'yes', '1', 't', 'y')
    return bool(s)

def _boolean_to_string(b):
    """Converts boolean to 'TRUE' or 'FALSE'."""
    return "TRUE" if b else "FALSE"

def _null_to_string(_):
    """Converts NULL to 'NULL'."""
    return "NULL"

def _open_file(filepath, mode):
    """Opens file with specified mode, returns file handle or None on error."""
    try:
        if mode not in ('r', 'w'):
            return None
        return open(filepath, mode)
    except:
        return None

def _read_line(filehandle):
    """Reads line from file, returns string without newline or None on EOF/error."""
    try:
        line = filehandle.readline()
        if not line:  # EOF
            return None
        return line.rstrip('\n')
    except:
        return None

def _write_line(filehandle, line):
    """Writes line to file, returns True on success, False on error."""
    try:
        print(line, file=filehandle)
        return True
    except:
        return False

def _close_file(filehandle):
    """Closes file handle, returns None."""
    try:
        filehandle.close()
        return None
    except:
        return None

def _split_string(s, delimiter):
    """Splits string by delimiter, returns list of strings."""
    try:
        return s.split(delimiter)
    except:
        return None

# List conversion functions
def list_to_string(lst):
    """Convert a list to a string representation"""
    return str(lst)

# File operations
def _read_file(filename):
    """Read the contents of a file"""
    try:
        with open(filename, 'r') as f:
            return f.read()
    except:
        return None

def _write_file(filename, content):
    """Write content to a file"""
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return True
    except:
        return False

def _append_file(filename, content):
    """Append content to a file"""
    try:
        with open(filename, 'a') as f:
            f.write(content)
        return True
    except:
        return False

def _file_exists(filename):
    """Check if a file exists"""
    import os
    return os.path.exists(filename)

# String operations
def _substring(s, start, length=None):
    """Get a substring from a string"""
    if length is None:
        return s[start:]
    return s[start:start+length]

def _string_contains(s, substring):
    """Check if a string contains a substring"""
    return substring in s

def _replace_string(s, old, new):
    """Replace occurrences of old with new in string s"""
    return s.replace(old, new)

# Math operations
def _sqrt(x):
    """Calculate the square root of a number"""
    import math
    return math.sqrt(x)

def _power(base, exponent):
    """Calculate base raised to the power of exponent"""
    return base ** exponent

def _random_integer(min_val, max_val):
    """Generate a random integer between min_val and max_val (inclusive)"""
    import random
    return random.randint(min_val, max_val)

def _random_float(min_val, max_val):
    """Generate a random float between min_val and max_val"""
    import random
    return random.uniform(min_val, max_val)

# List operations
def _remove_element(lst, index):
    """Remove an element at the specified index from a list"""
    if 0 <= index < len(lst):
        del lst[index]
        return True
    return False

def _insert_element(lst, index, value):
    """Insert a value at the specified index in a list"""
    if 0 <= index <= len(lst):
        lst.insert(index, value)
        return True
    return False

def _find_element(lst, value):
    """Find the index of a value in a list, or -1 if not found"""
    try:
        return lst.index(value)
    except ValueError:
        return -1

def _create_list():
    """Create a new empty list"""
    return []

# Map operations
def _create_map():
    """Create a new empty map (dictionary)"""
    return {}

# Direct mapping of Fluent standard library functions to their Python equivalents or helper functions
FLUENT_TO_PYTHON_MAP = {
    # I/O
    "PRINT": print,
    "INPUT": input,
    "READ_FILE": _read_file,
    "WRITE_FILE": _write_file,
    "APPEND_FILE": _append_file,
    "FILE_EXISTS": _file_exists,
    "OPEN_FILE": _open_file,
    "CLOSE_FILE": _close_file,
    "READ_LINE": _read_line,
    
    # String manipulation
    "CONCATENATE_STRINGS": _concatenate_strings,
    "GET_STRING_LENGTH": len,
    "SUBSTRING": _substring,
    "STRING_CONTAINS": _string_contains,
    "SPLIT_STRING": _split_string,
    "REPLACE_STRING": _replace_string,
    "TRIM_STRING": str.strip,
    
    # Type conversion
    "INTEGER_TO_STRING": str,
    "STRING_TO_INTEGER": _string_to_integer,
    "FLOAT_TO_STRING": str,
    "STRING_TO_FLOAT": _string_to_float,
    "BOOLEAN_TO_STRING": _boolean_to_string,
    "STRING_TO_BOOLEAN": _string_to_boolean,
    
    # Math operations
    "ABSOLUTE_VALUE": abs,
    "SQUARE_ROOT": _sqrt,
    "POWER": _power,
    "RANDOM_INTEGER": _random_integer,
    "RANDOM_FLOAT": _random_float,
    "ROUND": round,
    
    # List operations
    "CREATE_LIST": _create_list,
    "GET_LENGTH": len,
    "GET_ELEMENT": _get_element,
    "SET_ELEMENT": _set_element,
    "ADD_ELEMENT": _add_element,
    "REMOVE_ELEMENT": _remove_element,
    "INSERT_ELEMENT": _insert_element,
    "FIND_ELEMENT": _find_element,
    "LIST_TO_STRING": list_to_string,
    
    # Map operations
    "CREATE_MAP": _create_map,
    "MAP_HAS_KEY": _map_has_key,
    "GET_MAP_VALUE": _get_map_value,
    "SET_MAP_VALUE": _set_map_value,
    "GET_MAP_KEYS": _get_map_keys,
}

# Map operators to their Python equivalents
OPERATOR_MAP = {
    "+": "+", "-": "-", "*": "*", "/": "/",  # Arithmetic
    "==": "==", "!=": "!=", "<": "<", "<=": "<=", ">": ">", ">=": ">=",  # Comparison
    "AND": "and", "OR": "or", "NOT": "not "  # Logical (Note space after 'not')
}

# Exports for the standard library functions (lowercase versions for imports)
get_length = lambda x: len(x) if isinstance(x, (list, str, dict)) else 0
get_element = _get_element
get_string_length = lambda s: len(s) if isinstance(s, str) else 0
split_string = _split_string
concatenate_strings = _concatenate_strings
integer_to_string = lambda n: str(n) if isinstance(n, (int, float)) else "0"
map_has_key = _map_has_key
get_map_value = _get_map_value
set_map_value = _set_map_value
get_map_keys = _get_map_keys
list_to_string = list_to_string
