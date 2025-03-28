# Contributing to Fluent

This document provides technical details for developers interested in contributing to the Fluent language implementation.

## Technical Architecture

Fluent uses a multi-stage pipeline to process code:

1. **Parsing**: Using the Lark parser to convert Fluent source code to a parse tree
2. **AST Transformation**: Converting the parse tree to a custom Abstract Syntax Tree
3. **Transpilation**: Converting the AST to executable Python code
4. **Execution**: Running the generated Python code

### Parser (Lark Grammar)

The parser uses Lark, a parsing toolkit for Python. The grammar is defined in `fluent_grammar.lark` using Lark's EBNF-like syntax. Key components include:

- **Lexical definitions**: Tokens for identifiers, literals, and keywords
- **Grammar rules**: Syntax structure for statements, expressions, etc.
- **Precedence rules**: Operator precedence and associativity

Example of the grammar structure:
```lark
?start: statement*

statement: variable_declaration
         | assignment
         | if_statement
         | while_statement
         | foreach_statement
         | function_definition
         | function_call_statement
         | return_statement
         | break_statement
         | ignored_statement
```

### AST (Abstract Syntax Tree)

The AST consists of node classes defined in `ast_nodes.py`. These represent the hierarchical structure of Fluent code:

- **Program**: Root node containing all statements
- **Statements**: VariableDeclaration, Assignment, IfStatement, etc.
- **Expressions**: Literal, Identifier, BinaryOp, FunctionCall, etc.
- **Types**: Type, ListType, MapType

The transformation from parse tree to AST happens in `ast_transformer.py` using Lark's Transformer class. Each grammar rule corresponds to a method in the ASTTransformer class.

### Transpiler

The transpiler (`transpiler.py`) converts the AST to executable Python code through:

1. **Tree Walking**: Visiting each node in the AST
2. **Code Generation**: Generating Python code for each node type
3. **Scope Management**: Tracking variables and function parameters
4. **Type Handling**: Converting Fluent types to Python types

Key transpiler components:
- **NodeVisitors**: Methods for each AST node type (visit_*)
- **Indentation Management**: Tracking code block indentation
- **Standard Library Integration**: Mapping Fluent library functions to Python

### Standard Library

The standard library mapping (`fluent_stdlib_map.py`) provides Python implementations for Fluent's built-in functions:

- Direct mappings for simple functions
- Custom implementations for complex operations
- Type conversion between Fluent and Python

## Development Workflow

### Adding a New Language Feature

To add a new language feature (e.g., a new control structure):

1. **Update the grammar**:
   ```lark
   // Example: Adding a 'switch' statement
   switch_statement: "SWITCH" expression "DO" case+ default_case? "END"
   case: "CASE" expression "THEN" statement*
   default_case: "DEFAULT" "THEN" statement*
   ```

2. **Add AST nodes**:
   ```python
   class SwitchStatement(Node):
       def __init__(self, expression, cases, default_case):
           self.expression = expression
           self.cases = cases
           self.default_case = default_case
   
   class Case(Node):
       def __init__(self, expression, statements):
           self.expression = expression
           self.statements = statements
   ```

3. **Implement AST transformer**:
   ```python
   def switch_statement(self, expr, *args):
       # Process cases and default case
       cases = []
       default_case = None
       for arg in args:
           if isinstance(arg, ast.Case):
               cases.append(arg)
           elif isinstance(arg, list):
               default_case = arg
       return ast.SwitchStatement(expr, cases, default_case)
   ```

4. **Implement transpiler visitor**:
   ```python
   def visit_SwitchStatement(self, node):
       expr = self.visit(node.expression)
       self.output.append(f"{self._indent()}# Switch statement for {expr}\n")
       for i, case in enumerate(node.cases):
           case_expr = self.visit(case.expression)
           if i == 0:
               self.output.append(f"{self._indent()}if {expr} == {case_expr}:\n")
           else:
               self.output.append(f"{self._indent()}elif {expr} == {case_expr}:\n")
           # Process case statements
           # ...
   ```

### Testing

The recommended testing approach is:

1. Write example Fluent programs that use the feature
2. Run them through the entire pipeline
3. Verify the correctness of the generated Python code
4. Check the execution results

### Debugging Tips

When debugging the transpiler:

1. **Add debug output** in the main.py file to see intermediate results:
   ```python
   print("--- Lark Parse Tree ---")
   print(parse_tree.pretty())
   
   print("\n--- AST Structure ---")
   print_ast(ast_tree)
   
   print("\n--- Generated Python Code ---")
   print(python_code)
   ```

2. **Isolate components**: Test the parser, transformer, and transpiler separately
3. **Use simple test cases**: Start with minimal examples and progressively add complexity

## Code Style and Conventions

### Naming Conventions

- **AST Nodes**: PascalCase class names (e.g., `VariableDeclaration`)
- **Grammar Rules**: snake_case rule names (e.g., `variable_declaration`)
- **Visitor Methods**: Follows AST node names with `visit_` prefix (e.g., `visit_VariableDeclaration`)

### Documentation

- Document each class and method with docstrings
- Explain complex algorithms and non-obvious code
- Keep the README and CONTRIBUTING guides up to date

## Performance Considerations

- **Grammar Optimization**: Avoid excessive backtracking with well-structured rules
- **AST Transformation**: Minimize unnecessary object creation
- **Transpilation**: Generate efficient Python code
- **Memory Usage**: Be mindful of memory usage for large programs
