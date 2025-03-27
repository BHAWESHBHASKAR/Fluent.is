# Fluent Language Proof of Concept

## Introduction

Fluent is a programming language concept designed to be more natural and LLM-friendly than traditional programming languages. This proof of concept (PoC) implements a transpiler that converts Fluent code into executable Python.

The key goals of this PoC are:
- Demonstrate a simplified subset of the Fluent language
- Provide a working transpiler that converts Fluent to Python
- Allow users to run Fluent scripts and see the outputs
- Explore the feasibility of an LLM-optimized programming language

## Supported Fluent Subset

This PoC implements the following Fluent language features:

### Function Definition
```
define function_name
    inputs:
        - param_name (type optional default_value) # Optional comment
    
    # Function body
    return value
```

### Parameter Types
- `number`
- `string`
- `list`
- Other Python-compatible types can be used but aren't validated

### Variable Operations
- `initialize variable = value` - Creates and assigns a value to a variable
- `add value to variable` - Adds a value to a variable (`variable += value`)
- `reduce variable by value` - Reduces a variable by a value (`variable -= value`)
- `increase variable by value` - Increases a variable by a value (`variable += value`)

### Control Flow
- `if condition:` - Standard if condition
- `elif condition:` - Used for else-if branches
- `else:` - Used for else branch
- `for each item in items:` - Iterates over a list or sequence

### Input/Output
- `print expression` - Outputs a value to the console

### Other
- `return value` - Returns a value from a function
- `# Comment` - Single-line comments are supported

### Limitations
- Standard Python operators (+, -, *, /, etc.) are passed through directly
- Expressions are not validated and use Python syntax
- Only a simple subset of programming constructs is supported
- Error handling is basic with warnings for unrecognized syntax

## Setup

### Requirements
- Python 3.6 or higher

### Installation

#### Option 1: Clone from GitHub
```bash
git clone https://github.com/BHAWESHBHASKAR/Fluent.git
cd Fluent
```

#### Option 2: Manual Download
1. Download this repository
2. Extract the files to your desired location

#### Optional Development Setup
If you plan to contribute or run tests:
```bash
pip install -r requirements.txt
```

### Project Structure
```
fluent-language/
├── transpile_fluent.py   # Core transpiler engine
├── run_fluent.py         # CLI runner with colored output
├── LICENSE               # MIT License
├── requirements.txt      # Project dependencies
├── README.md             # This documentation
├── tests/                # Unit tests
│   ├── __init__.py
│   └── test_transpiler.py
└── examples/             # Example Fluent programs
    ├── hello.is
    ├── calculate_average.is
    ├── get_grade.is
    └── conditionals.is
```

## Usage

### Running a Fluent Script
To execute a Fluent script (`.is` file):
```bash
python3 run_fluent.py examples/your_script.is
```

If no script is specified, the runner will display a list of available `.is` files in the project:
```bash
python3 run_fluent.py
```

### Example Output
When you run a script, you'll see:
1. The Fluent logo and version information
2. The original Fluent code (with colored `.is` extension)
3. The transpiled Python code
4. The execution output of your program
5. Execution time summary

### Running Tests
To verify the transpiler is working correctly:
```bash
python -m pytest tests/
```

For more detailed test coverage:
```bash
python -m pytest --cov=. tests/
```

## Examples

### hello.is
A simple example that defines a greeting function, demonstrates string concatenation, and shows how to call functions.

```bash
python3 run_fluent.py examples/hello.is
```

### calculate_average.is
Demonstrates arithmetic operations, loops, conditionals, and function parameters with a function that calculates the average of a list of numbers.

```bash
python3 run_fluent.py examples/calculate_average.is
```

### get_grade.is
Shows how to use if/elif/else conditions by implementing a function that converts a numerical score into a letter grade.

```bash
python3 run_fluent.py examples/get_grade.is
```

### conditionals.is
Examples of various conditional structures and more complex logical operations.

```bash
python3 run_fluent.py examples/conditionals.is
```

## Creating Your Own Fluent Scripts

1. Create a new text file with a `.is` extension
2. Write your Fluent code following the syntax examples
3. Run it using the command shown above

## Future Work

- Extend the language with more Fluent-specific constructs
- Improve error reporting and diagnostics
- Add support for modules and imports
- Create a more comprehensive standard library
- Design a proper type system
