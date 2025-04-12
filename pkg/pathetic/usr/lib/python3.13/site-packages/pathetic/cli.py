# pathetic/cli.py

import sys
from pathetic.runner import run_file

def main():
    if len(sys.argv) < 3 or sys.argv[1] != "run":
        print("Usage: pathetic run <file.pth>")
        sys.exit(1)

    filepath = sys.argv[2]
    run_file(filepath)
