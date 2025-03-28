# Fluent Language Transpiler

A transpiler that converts Fluent language code (`.is` files) to Python.

## Project Structure

- `fluent_grammar.lark`: Formal grammar for the Lark parser
- `ast_nodes.py`: Abstract Syntax Tree node classes
- `ast_transformer.py`: Lark Transformer to build the custom AST
- `transpiler.py`: Walks the AST and generates Python code
- `fluent_stdlib_map.py`: Maps Fluent standard library functions to Python
- `main.py`: Entry point to run the transpiler
- `examples/`: Example Fluent (.is) files
  - `greeting.is`: A simple greeting program
  - `find_max.is`: Finds the maximum value in a list
  - `word_count.is`: Counts occurrences of words in a text

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

To transpile a Fluent file to Python:

```bash
python main.py examples/greeting.is
```

This will:
1. Parse the Fluent code
2. Transform it into an Abstract Syntax Tree
3. Transpile it to equivalent Python code
4. Execute the generated Python code

## Fluent Language Features

The Fluent language (`*.is` files) supports:

- Variable declarations with type annotations
- Basic data types: INTEGER, FLOAT, STRING, BOOLEAN, NULLTYPE
- Collection types: LIST and MAP
- Control structures: IF-THEN-ELSE, WHILE, FOREACH
- Function definitions with typed parameters
- Standard library functions for common operations

## Example

```
// Fluent code (greeting.is)
FUNCTION create_greeting(PARAM name AS STRING) RETURNS STRING;
  VAR prefix AS STRING = "Hello, ";
  VAR suffix AS STRING = "!";
  VAR message AS STRING = CALL CONCATENATE_STRINGS(prefix, name);
  message = CALL CONCATENATE_STRINGS(message, suffix);
  RETURN message;
ENDFUNCTION;

VAR user_name AS STRING = "Fluent Builder";
VAR greeting_message AS STRING;

greeting_message = CALL create_greeting(user_name);

PRINT greeting_message; // Output: Hello, Fluent Builder!
```

Gets transpiled to:

```python
# Generated Python code
def create_greeting(name):
    prefix = "Hello, "
    suffix = "!"
    message = (prefix + name)
    message = (message + suffix)
    return message

user_name = "Fluent Builder"
greeting_message = create_greeting(user_name)
print(greeting_message)
```
