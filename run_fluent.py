#!/usr/bin/env python3
"""
Fluent Language Runner

This script transpiles and executes Fluent (.is) code files.
Usage: python3 run_fluent.py <filename.is>
"""

import sys
import os
from transpile_fluent import transpile

# ANSI color codes
YELLOW = '\033[93m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'
BACK_YELLOW = '\033[43m'
BLACK = '\033[30m'

# Function to colorize .is extension in filenames
def colorize_is_extension(filename):
    if filename.endswith('.is'):
        base_name = filename[:-3]  # everything except the extension
        return f"{base_name}{YELLOW}.is{RESET}"
    return filename

# Version info
VERSION = "0.1.0"

def display_logo():
    # Using lines individually to avoid escape sequence issues
    print(f"{YELLOW}    ______ __                  __ {RESET}")
    print(f"{YELLOW}   / ____// /__ _____ ____   / /_{RESET}")
    print(f"{YELLOW}  / /_   / // // ___// __ \\/ __/{RESET}")
    print(f"{YELLOW} / __/  / // // /__ / / / // /_  {RESET}")
    print(f"{YELLOW}/_/    /_//_/ \\___//_/ /_/ \\__/  {RESET}")
    print(f"{YELLOW}                     Language PoC v{VERSION}{RESET}")
    print(f"{BOLD}A natural programming language concept{RESET}")
    print(f"{BLUE}-----------------------------------{RESET}\n")

def list_is_files():
    """List all .is files in the current directory and subdirectories with yellow highlighting"""
    print(f"\n{BOLD}Available Fluent {YELLOW}.is{RESET}{BOLD} files:{RESET}")
    print(f"{BLUE}--------------------------------{RESET}")
    
    # Find all .is files in the current directory and subdirectories
    is_files = []
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith('.is'):
                is_files.append(os.path.relpath(os.path.join(root, file)))
    
    # Display files with yellow extension
    for i, file_path in enumerate(sorted(is_files), 1):
        dirname, filename = os.path.split(file_path)
        name, ext = os.path.splitext(filename)
        if dirname:
            location = f"{dirname}/"
        else:
            location = ""
        
        # Make .is extension yellow
        colored_filename = f"{location}{name}{YELLOW}.is{RESET}"
        print(f"  {i}. {colored_filename}")
    
    print(f"\n{BOLD}Run a specific file using:{RESET} python3 run_fluent.py <filename.is>")

def main():
    # Display the Fluent logo
    display_logo()
    
    # Track execution time
    import time
    start_time = time.time()
    
    # Check if correct number of arguments are provided
    if len(sys.argv) != 2:
        list_is_files()
        sys.exit(0)
    
    # Get the filename from command line argument
    filename = sys.argv[1]
    
    # Optional: Warn if the file doesn't have .is extension
    if not filename.endswith('.is'):
        print(f"Warning: File '{filename}' does not have a .is extension. Proceeding anyway...")
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    
    # Read the file content
    try:
        colored_filename = colorize_is_extension(filename)
        print(f"\n{BOLD}--- Reading Fluent code from '{colored_filename}' ---{RESET}")
        with open(filename, 'r') as file:
            fluent_code_string = file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Transpile the Fluent code to Python
    try:
        print(f"\n{BOLD}--- Transpiling Fluent code to Python ---{RESET}")
        python_code_string = transpile(fluent_code_string)
        print(f"{BOLD}--- Generated Python Code ---{RESET}")
        print(python_code_string)
        print(f"{BOLD}-----------------------------{RESET}")
    except Exception as e:
        print(f"Error during transpilation: {e}")
        sys.exit(1)
    
    # Execute the generated Python code
    try:
        print(f"\n{BOLD}--- Executing Python Code ---{RESET}")
        exec_globals = {}
        exec(python_code_string, exec_globals)
        print(f"\n{GREEN}{BOLD}--- Execution completed successfully ---{RESET}")
    except Exception as e:
        print(f"{RED}Error during execution: {e}{RESET}")
        sys.exit(1)
    finally:
        # Calculate and display execution time
        execution_time = time.time() - start_time
        print(f"\n{BOLD}Execution finished in {execution_time:.2f} seconds.{RESET}")

if __name__ == "__main__":
    main()