import sys
from .runner import run_file

VERSION = "0.1.0"

HELP_TEXT = """
Usage:
  pathetic [file.pth]
  pathetic run [file.pth]

Options:
  -v, --version     Show version information
  -h, --help        Show this help message with syntax guide

Syntax Guide:
  say "hello"         → Output: hello
"""

def main():
    args = sys.argv[1:]

    if not args:
        print("Usage: pathetic [file.pth] or pathetic -h")
        return

    if args[0] in ("-v", "--version"):
        print(f"pathetic {VERSION}")
        return

    if args[0] in ("-h", "--help"):
        print(HELP_TEXT)
        return

    if args[0] == "run":
        if len(args) < 2:
            print("Error: Missing file to run.")
            return
        run_file(args[1])
        return

    # Default: assume first argument is a file
    run_file(args[0])
