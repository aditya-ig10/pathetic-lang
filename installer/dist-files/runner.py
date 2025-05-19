# pathetic/runner.py

from pathetic.interpreter import interpret

def run_file(filepath):
    try:
        with open(filepath, 'r') as f:
            code = f.read()
            interpret(code)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
