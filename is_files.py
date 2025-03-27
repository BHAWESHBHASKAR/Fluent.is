#!/usr/bin/env python3
"""
Lists all .is files in the project with a yellow highlight
"""
import os
import glob

# ANSI color codes
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def highlight_is_files(directory):
    print(f"{BOLD}Fluent (.is) Files:{RESET}")
    print("-----------------")
    
    # Find all .is files in the given directory and its subdirectories
    is_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.is'):
                is_files.append(os.path.join(root, file))
    
    # Display files with yellow extension
    for file_path in sorted(is_files):
        dirname, filename = os.path.split(file_path)
        name, ext = os.path.splitext(filename)
        relative_path = os.path.relpath(dirname, directory)
        if relative_path == '.':
            location = ''
        else:
            location = f"{relative_path}/"
        
        # Color the .is extension in yellow
        colored_filename = f"{name}{YELLOW}{ext}{RESET}"
        print(f"{location}{colored_filename}")

if __name__ == "__main__":
    highlight_is_files(os.path.dirname(os.path.abspath(__file__)))
