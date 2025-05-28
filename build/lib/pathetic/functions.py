# functions.py
import re
from typing import Dict, Any, Optional

def strip_quotes(s: str) -> str:
    if isinstance(s, str) and len(s) >= 2:
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return s[1:-1]
    return s

# Function to handle 'say' command (e.g., say "hello" or say f"formatted string")
def say_function(args: str, variables: Dict[str, Any], interpret_fstring: callable) -> Optional[str]:
    args = args.strip()
    if args.startswith('f"') and args.endswith('"'):
        content = args[1:-1]
        result = interpret_fstring(content)
        if not result.startswith("Formatting error"):
            print(strip_quotes(result))
        else:
            print(result)
    elif args.startswith('"') and args.endswith('"'):
        print(args[1:-1])
    else:
        print("Syntax error: Invalid string format")
    return None

# Function to handle 'get' command (e.g., get(x) or get(arr[5]))
def get_function(args: str, variables: Dict[str, Any]) -> Optional[str]:
    if "[" in args and "]" in args:
        # Array input
        try:
            name, size = args[:args.index("]")].split("[")
            name = name.strip()
            size = int(size.strip())
            val = input().split()
            variables[name] = [parse_value(v) for v in val][:size]
        except Exception as e:
            print(f"Syntax error: Invalid array input - {str(e)}")
    else:
        # Scalar input
        if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", args):
            print("Syntax error: Invalid variable name")
            return None
        val = input()
        variables[args] = parse_value(val)
    return None

# Helper to parse values (used by get_function and let)
def parse_value(val: str) -> Any:
    val = val.strip()
    try:
        if re.match(r'^-?\d+\.\d+$', val):
            return float(val)
        if re.match(r'^-?\d+$', val):
            return int(val)
        return val.strip('"') if val.startswith('"') and val.endswith('"') else val
    except ValueError:
        return val

# Dictionary mapping function names to their implementations
FUNCTIONS = {
    "say": say_function,
    "get": get_function,
}