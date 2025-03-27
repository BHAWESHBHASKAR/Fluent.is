#!/usr/bin/env python3
"""
Fluent to Python Transpiler (Proof of Concept)

This script transforms code written in a subset of the Fluent language into
equivalent Python code. Handles if/elif/else. Adds basic error warnings.
"""

import re


def transpile(fluent_code: str) -> str:
    """
    Transpiles Fluent code into equivalent Python code.

    Args:
        fluent_code: A string containing Fluent code following the PoC syntax subset.

    Returns:
        A string containing the equivalent Python code.
    """
    # Initialize result storage
    python_lines = []
    lines = fluent_code.splitlines()

    # State machine states
    parsing_state = "TOP_LEVEL"

    # State variables
    current_function_name = None
    current_function_indent = 0
    required_params = []
    optional_params = []
    param_comments = {}

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped_line = line.strip()
        indentation = len(line) - len(line.lstrip())
        line_number = i + 1 # For error messages

        # Handle blank lines consistently across states
        if not stripped_line:
            if parsing_state != "TOP_LEVEL":  # Preserve blanks within functions
                python_lines.append("")
            i += 1
            continue

        # Process based on current state
        if parsing_state == "TOP_LEVEL":
            if stripped_line.startswith('#'):
                python_lines.append(line)
            elif stripped_line.startswith("define "):
                current_function_name = stripped_line[7:].strip()
                current_function_indent = indentation
                parsing_state = "AWAITING_INPUTS"
                required_params = []
                optional_params = []
                param_comments = {}
            # Support for top-level print statements
            elif stripped_line.startswith('print '):
                expression_part = stripped_line[6:].strip()
                if expression_part:
                    python_lines.append(f"print({expression_part})")
                else:
                    print(f"Warning: 'print' statement missing value on line {line_number}. Using empty print().")
                    python_lines.append("print()")
            # Support for top-level function calls
            elif re.match(r'^(\w+)(?:\s+(.*))?$', stripped_line):
                # This matches a word followed by optional space and arguments
                # Convert: function_name arg1 arg2 -> function_name(arg1, arg2)
                match = re.match(r'^(\w+)(?:\s+(.*))?$', stripped_line)
                func_name = match.group(1)
                args = match.group(2) if match.group(2) else ""
                
                # Format for Python: if there are args, put them in parentheses
                if args:
                    # If args look like a string with quotes, keep as is
                    if args.startswith('"') or args.startswith("'"):
                        python_lines.append(f"{func_name}({args})")
                    # Otherwise assume a comma-separated list
                    else:
                        python_lines.append(f"{func_name}({args})")
                else:
                    # No args, just add empty parentheses
                    python_lines.append(f"{func_name}()")
            elif stripped_line: # Warn about other unexpected top-level code
                 print(f"Warning: Skipping unrecognized top-level syntax on line {line_number}: '{stripped_line}'")
            # else: it's whitespace handled by the blank line check
            i += 1
            continue

        elif parsing_state == "AWAITING_INPUTS":
            if stripped_line == "inputs:":
                 if indentation > current_function_indent:
                     parsing_state = "IN_INPUTS"
                 else:
                     print(f"Error: 'inputs:' block not correctly indented on line {line_number}. Resetting state.")
                     parsing_state = "TOP_LEVEL" # Reset
            elif stripped_line.startswith('#'):
                pass # Allow comments between define and inputs
            elif stripped_line:
                 print(f"Error: Expected 'inputs:' or comment after 'define' on line {line_number}, got: '{stripped_line}'. Resetting state.")
                 parsing_state = "TOP_LEVEL" # Reset
            i += 1
            continue

        elif parsing_state == "IN_INPUTS":
            # Determine if the current line signals the end of the inputs block
            is_parameter_line = stripped_line.startswith('-')
            is_comment = stripped_line.startswith('#')
            is_still_indented = indentation > current_function_indent

            # Condition to EXIT inputs block:
            # - Line is NOT blank (already handled)
            # - AND it's either:
            #   - Dedented (or same level) OR
            #   - Still indented BUT is NOT a parameter line and NOT a comment
            if stripped_line and ((not is_still_indented) or 
               (is_still_indented and not is_parameter_line and not is_comment)):

                # End of inputs block detected.
                # 1. Generate the def line
                python_params = required_params + [f"{name}={default}" for name, default in optional_params]
                def_line = f"{' ' * current_function_indent}def {current_function_name}({', '.join(python_params)}):"
                python_lines.append(def_line)

                # 2. Add parameter comments
                comment_indent = ' ' * (current_function_indent + 4)
                for param_name in required_params + [name for name, default in optional_params]:
                     if param_name in param_comments:
                          python_lines.append(f"{comment_indent}{param_comments[param_name]}")

                # 3. Switch state and REPROCESS current line as body
                parsing_state = "IN_FUNCTION_BODY"
                # DO NOT INCREMENT i - reprocess this line in the new state
                continue # Go back to start of while loop with new state

            # --- Otherwise, process line WITHIN inputs block ---
            elif is_parameter_line: # Process parameter (if correctly indented)
                 if not is_still_indented:
                      print(f"Error: Parameter definition on line {line_number} has incorrect indentation. Skipping.")
                 else:
                      # Parse parameter definitions using regex
                      param_match = re.match(r'-\s*(\w+)\s*\((\w+)(?:\s*optional\s*([^)]+))?\)(.*)', stripped_line)
                      if param_match:
                          param_name = param_match.group(1)
                          default_value = param_match.group(3) # None if not optional
                          comment = param_match.group(4).strip()
                          if comment and comment.startswith('#'):
                              param_comments[param_name] = comment
                          if default_value is not None:
                              optional_params.append((param_name, default_value))
                          else:
                              required_params.append(param_name)
                      else:
                           print(f"Warning: Malformed parameter definition on line {line_number}: '{stripped_line}'")

            elif is_comment: # Allow comments within the inputs block
                  if is_still_indented:
                       pass # Just ignore the comment line for now
                  else: # Comment at base indent level also ends the block
                       # (This case is technically handled by the exit condition above, but good to be explicit)
                       parsing_state = "IN_FUNCTION_BODY" # Transition state
                       i -= 1 # Reprocess comment line as potential first line of body (or before it)
                       continue # Trigger state change logic by restarting loop

            # If it's not blank, not a comment, not a parameter, and not triggering exit?
            # This implies unexpected content within the properly indented block.
            elif is_still_indented and stripped_line:
                  print(f"Warning: Unexpected content inside 'inputs:' block on line {line_number}: '{stripped_line}'")

            # Only increment i if we didn't 'continue' to reprocess the line
            i += 1
            continue

        elif parsing_state == "IN_FUNCTION_BODY":
            # Check if we've exited the function (dedentation to function level or less)
            # Allow comments at the base function indent level to be part of the function
            if indentation < current_function_indent:
                 parsing_state = "TOP_LEVEL"
                 continue # Re-process this line at the top level

            if indentation == current_function_indent and not stripped_line.startswith('#'):
                 # If it's not a comment, code at the same level as 'define' ends the function body
                 parsing_state = "TOP_LEVEL"
                 continue # Re-process this line at the top level

            # Process function body line
            # Calculate the correct Python indentation relative to function definition
            # Indentation of the line minus the indent level *inside* the function (which is base + 4)
            # Ensures body starts at 4 spaces, nested blocks add more.
            base_body_indent = current_function_indent + 4
            rel_indent = max(0, indentation - base_body_indent)
            python_indent = ' ' * (4 + rel_indent) # Python body starts at 4 spaces

            # Translate based on line content
            if stripped_line.startswith('#'):
                # Comments - Apply calculated indent
                python_lines.append(f"{python_indent}{stripped_line}")

            elif stripped_line.startswith('initialize '):
                init_parts = stripped_line[11:].split('=', 1)
                if len(init_parts) == 2:
                    var_name = init_parts[0].strip()
                    value = init_parts[1].strip()
                    python_lines.append(f"{python_indent}{var_name} = {value}")
                else:
                     print(f"Warning: Malformed 'initialize' on line {line_number}: '{stripped_line}'")

            elif stripped_line.startswith('for each '):
                loop_content = stripped_line[9:]
                python_lines.append(f"{python_indent}for {loop_content}")

            elif stripped_line.startswith('add '):
                match = re.match(r'add\s+(.*?)\s+to\s+(.*)', stripped_line)
                if match:
                    value, variable = match.groups()
                    python_lines.append(f"{python_indent}{variable} += {value}")
                else:
                     print(f"Warning: Malformed 'add...to' on line {line_number}: '{stripped_line}'")

            elif stripped_line.startswith('reduce '):
                match = re.match(r'reduce\s+(.*?)\s+by\s+(.*)', stripped_line)
                if match:
                    variable, value = match.groups()
                    python_lines.append(f"{python_indent}{variable} -= {value}")
                else:
                     print(f"Warning: Malformed 'reduce...by' on line {line_number}: '{stripped_line}'")

            elif stripped_line.startswith('increase '):
                match = re.match(r'increase\s+(.*?)\s+by\s+(.*)', stripped_line)
                if match:
                    variable, value = match.groups()
                    python_lines.append(f"{python_indent}{variable} += {value}")
                else:
                     print(f"Warning: Malformed 'increase...by' on line {line_number}: '{stripped_line}'")

            # --- CONDITIONAL LOGIC ---
            elif stripped_line.startswith('if '):
                 # Assuming condition syntax is python-compatible for now
                python_lines.append(f"{python_indent}{stripped_line}")

            elif stripped_line.startswith('elif '): # **** NEW: Handle elif ****
                 # Assuming condition syntax is python-compatible for now
                 python_lines.append(f"{python_indent}{stripped_line}") # Translates directly

            elif stripped_line.startswith("else:"):
                 # Basic assumption: indentation calculation places it correctly
                 # relative to the corresponding 'if' via python_indent
                 # Extract only the 'else:' part regardless of trailing comments
                 else_line = "else:"
                 # Check if there's a comment after the else
                 if '#' in stripped_line:
                     comment_part = stripped_line[stripped_line.index('#'):]
                     else_line = f"else: {comment_part}"
                 python_lines.append(f"{python_indent}{else_line}")
            # --- END CONDITIONAL LOGIC ---

            # --- PRINT SUPPORT ---
            elif stripped_line.startswith('print '):
                # Extract the expression to print (everything after 'print ')
                expression_part = stripped_line[6:].strip()
                if expression_part:
                    python_lines.append(f"{python_indent}print({expression_part})")
                else:
                    print(f"Warning: 'print' statement missing value on line {line_number}. Using empty print().")
                    python_lines.append(f"{python_indent}print()")
            # --- END PRINT SUPPORT ---

            elif stripped_line.startswith('return '):
                python_lines.append(f"{python_indent}{stripped_line}")

            else:
                # **** Basic Error Detection ****
                print(f"Warning: Unrecognized Fluent syntax in function body on line {line_number}: '{stripped_line}' - Skipping.")
                # Could also choose to raise an error here:
                # raise SyntaxError(f"Invalid Fluent syntax on line {line_number}: {stripped_line}")

        # Move to the next line AFTER processing the current one
        i += 1

    # Combine all lines into a single string with proper line breaks
    python_code = '\n'.join(python_lines)
    return python_code


# Main block for testing
if __name__ == "__main__":
    # Example Fluent code using if/elif/else
    fluent_code_if_elif_else = """
define categorize_value
    inputs:
        - value (number)
        - low_threshold (number optional 10)
        - high_threshold (number optional 20)

    # Categorize based on thresholds
    if value < low_threshold:
        initialize category = "Low"
    elif value < high_threshold: # Check if between low and high
        initialize category = "Medium"
    else: # If >= high_threshold
        initialize category = "High"
        # Some comment

    return category

# Another function to ensure state resets
define simple_add
    inputs:
        - a (number)
        - b (number)

    initialize result = a + b # Relying on operator passthrough
    return result
"""

    print("--- Testing Transpiler with if/elif/else ---")
    python_code = transpile(fluent_code_if_elif_else)
    print("\n--- Generated Python Code ---")
    print(python_code)

    print("\n--- Testing Execution ---")
    try:
        exec_globals = {}
        exec(python_code, exec_globals)

        if 'categorize_value' in exec_globals:
            cat_func = exec_globals['categorize_value']
            print(f"categorize_value(5): {cat_func(5)}")      # Expected: Low
            print(f"categorize_value(10): {cat_func(10)}")    # Expected: Medium (since < 20)
            print(f"categorize_value(15): {cat_func(15)}")    # Expected: Medium
            print(f"categorize_value(20): {cat_func(20)}")    # Expected: High (since >= 20)
            print(f"categorize_value(25): {cat_func(25)}")    # Expected: High
            # Test with custom thresholds
            print(f"categorize_value(50, low_threshold=40, high_threshold=60): {cat_func(50, low_threshold=40, high_threshold=60)}") # Expected: Medium
        else:
            print("categorize_value function not found.")

        if 'simple_add' in exec_globals:
             print(f"simple_add(10, 22): {exec_globals['simple_add'](10, 22)}") # Expected: 32
        else:
             print("simple_add function not found.")

    except Exception as e:
        print(f"Error executing generated code: {e}")