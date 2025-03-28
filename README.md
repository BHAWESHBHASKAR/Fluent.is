# Fluent Programming Language

Fluent is a modern, expressive programming language designed to be intuitive and readable. It transpiles to Python, making it powerful yet accessible for both beginners and experienced programmers.

## Overview

Fluent features:
- Clear, explicit syntax with a focus on readability
- Strong typing system with type annotations
- Function-based programming model
- Rich standard library
- Seamless integration with Python ecosystem

## Project Structure

- `backend/fluent_grammar.lark`: Formal grammar for the Lark parser
- `backend/ast_nodes.py`: Abstract Syntax Tree node classes
- `backend/ast_transformer.py`: Lark Transformer to build the custom AST
- `backend/transpiler.py`: Walks the AST and generates Python code
- `backend/fluent_stdlib_map.py`: Maps Fluent standard library functions to Python
- `backend/main.py`: Entry point to run the transpiler
- `backend/examples/`: Example Fluent (.is) files
  - `greeting.is`: A simple greeting program
  - `find_max.is`: Finds the maximum value in a list
  - `word_count.is`: Counts occurrences of words in a text
  - `bubble_sort.is`: Implementation of the bubble sort algorithm

## Requirements

- Python 3.6+
- lark-parser

## Installation

Install the required dependencies:

```bash
pip install lark-parser
```

If pip is not available, you may need to install it first:

```bash
# For Ubuntu/Debian
sudo apt install python3-pip

# For macOS (using Homebrew)
brew install python

# For Windows
# Download and run the official Python installer from python.org
```

## Usage

To transpile and run a Fluent file:

```bash
python backend/main.py path/to/your/program.is
```

This will:
1. Parse the Fluent code
2. Transform it into an Abstract Syntax Tree
3. Transpile it to equivalent Python code
4. Execute the generated Python code

## Language Structure

### Basic Syntax

```
// Variable declaration with type annotation
name: STRING = "Fluent"

// Function declaration
FUNCTION greet(person: STRING): NOTHING
  PRINT(CONCATENATE_STRINGS("Hello, ", person))
END

// Function call
greet("World")
```

### Data Types

Fluent supports the following primitive data types:
- `INTEGER`: Whole numbers
- `FLOAT`: Decimal numbers
- `STRING`: Text sequences
- `BOOLEAN`: True/False values
- `NOTHING`: Represents void/null (equivalent to None in Python)

And the following collection types:
- `LIST<T>`: Ordered collection of elements of type T
- `MAP<K, V>`: Key-value pairs with keys of type K and values of type V

### Control Flow

Fluent has the following control flow structures:

#### Conditional Statements
```
IF condition THEN
  // Code executed if condition is true
ELSE
  // Code executed if condition is false
END
```

#### While Loops
```
WHILE condition DO
  // Code executed repeatedly while condition is true
END
```

#### Foreach Loops
```
FOREACH item IN collection DO
  // Code executed for each item in the collection
END
```

### Functions

Functions in Fluent are defined with explicit parameter types and return types:

```
FUNCTION function_name(param1: TYPE1, param2: TYPE2): RETURN_TYPE
  // Function body
  RETURN value
END
```

Functions with no return value use `NOTHING` as the return type.

## Standard Library

Fluent includes a standard library with common functions:

### List Operations
- `GET_LENGTH(list)`: Returns the length of a list
- `GET_ELEMENT(list, index)`: Gets an element at a specific index
- `SET_ELEMENT(list, index, value)`: Sets an element at a specific index
- `LIST_TO_STRING(list)`: Converts a list to its string representation

### String Operations
- `GET_STRING_LENGTH(string)`: Returns the length of a string
- `SPLIT_STRING(string, delimiter)`: Splits a string by delimiter
- `CONCATENATE_STRINGS(string1, string2)`: Combines two strings

### I/O Operations
- `PRINT(value)`: Outputs value to the console

### Math Operations
- Standard arithmetic operators: +, -, *, /
- Comparison operators: ==, !=, <, >, <=, >=

### Map Operations
- `MAP_HAS_KEY(map, key)`: Checks if a map contains a key
- `GET_MAP_VALUE(map, key)`: Gets a value for a key
- `SET_MAP_VALUE(map, key, value)`: Sets a value for a key
- `GET_MAP_KEYS(map)`: Gets all keys in a map

## Example Programs

### Hello World
```
PRINT("Hello, World!")
```

### Factorial Calculation
```
FUNCTION factorial(n: INTEGER): INTEGER
  IF n <= 1 THEN
    RETURN 1
  END
  
  RETURN n * factorial(n - 1)
END

PRINT(CONCATENATE_STRINGS("Factorial of 5 is: ", INTEGER_TO_STRING(factorial(5))))
```

### Bubble Sort
```
FUNCTION swap(numbers: LIST<INTEGER>, i: INTEGER, j: INTEGER): NOTHING
  temp: INTEGER = GET_ELEMENT(numbers, i)
  SET_ELEMENT(numbers, i, GET_ELEMENT(numbers, j))
  SET_ELEMENT(numbers, j, temp)
END

FUNCTION bubble_sort(numbers: LIST<INTEGER>): NOTHING
  IF GET_LENGTH(numbers) == 0 THEN
    RETURN
  END
  
  n: INTEGER = GET_LENGTH(numbers)
  i: INTEGER = 0
  
  WHILE i < n DO
    j: INTEGER = 0
    
    WHILE j < (n - i - 1) DO
      IF GET_ELEMENT(numbers, j) > GET_ELEMENT(numbers, j + 1) THEN
        swap(numbers, j, j + 1)
      END
      
      j = j + 1
    END
    
    i = i + 1
  END
END

unsorted_list: LIST<INTEGER> = [64, 34, 25, 12, 22, 11, 90]
PRINT(CONCATENATE_STRINGS("Unsorted list: ", LIST_TO_STRING(unsorted_list)))
bubble_sort(unsorted_list)
PRINT(CONCATENATE_STRINGS("Sorted list: ", LIST_TO_STRING(unsorted_list)))
```

## Implementation Details

The Fluent language implementation includes:

1. **Grammar Definition** (`fluent_grammar.lark`): Defines the language syntax using Lark grammar
2. **AST Nodes** (`ast_nodes.py`): Classes for the Abstract Syntax Tree representation
3. **AST Transformer** (`ast_transformer.py`): Transforms parse trees into AST
4. **Transpiler** (`transpiler.py`): Converts AST to executable Python code
5. **Standard Library** (`fluent_stdlib_map.py`): Maps Fluent standard library functions to Python

## Development

### Project Structure
```
Fluent/
├── backend/
│   ├── ast_nodes.py          # AST node definitions
│   ├── ast_transformer.py    # Transform parse tree to AST
│   ├── fluent_grammar.lark   # Lark grammar definition
│   ├── fluent_stdlib_map.py  # Standard library implementation
│   ├── main.py               # Main entry point
│   ├── transpiler.py         # AST to Python transpiler
│   └── examples/             # Example Fluent programs
│       ├── bubble_sort.is    # Bubble sort implementation
│       ├── greeting.is       # Simple greeting program
│       └── ... other examples
```

### Adding Features

To add new features to Fluent:
1. Update the grammar in `fluent_grammar.lark`
2. Add corresponding AST nodes in `ast_nodes.py`
3. Implement transformation in `ast_transformer.py`
4. Add transpilation support in `transpiler.py`
5. If needed, add standard library functions in `fluent_stdlib_map.py`

## Future Directions

Potential future enhancements for Fluent:
- First-class functions and closures
- Class and module system
- Custom types and interfaces
- Error handling with try/catch
- Concurrency support
- Package management
- Interactive REPL
- Debugging tools
- Optimization of the transpiled code
