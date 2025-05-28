import re

# Global dictionary to store variables and their values
variables = {}

# --- Value Parsing Functions ---

# Parses a string value into an appropriate type (int, float, or string)
def parse_value(val):
    val = val.strip()
    try:
        # Float detection
        if re.match(r'^-?\d+\.\d+$', val):
            return float(val)
        # Integer detection
        if re.match(r'^-?\d+$', val):
            return int(val)
        # Strip quotes if string literal
        return val.strip('"') if val.startswith('"') and val.endswith('"') else val
    except ValueError:
        return val

# --- Expression Evaluation Functions ---

# Evaluates a mathematical or logical expression after replacing operators and variables
def evaluate_expression(expr):
    try:
        # Replace | with % (mod) and ^ with ** (power) to ensure correct operation
        # Note: ^ is strictly treated as power, not factorial
        expr = expr.strip().replace('|', '%').replace('^', '**')

        # Replace variables with their values
        for var in sorted(variables.keys(), key=len, reverse=True):
            # Ensure whole word replacement (avoid partial variable matches)
            expr = re.sub(rf'\b{var}\b', str(variables[var]), expr)

        # Define safe eval environment to prevent unsafe code execution
        safe_dict = {
            "__builtins__": None,
            "and": lambda x, y: x and y,
            "or": lambda x, y: x or y,
            "True": True,
            "False": False,
        }

        return eval(expr, safe_dict, {})
    except Exception as e:
        return f"Evaluation error: {str(e)}"

# --- String Formatting Functions ---

# Interprets f-strings by evaluating expressions within curly braces
def interpret_fstring(content):
    result = ""
    i = 0
    while i < len(content):
        if content[i] == '{':
            i += 1
            expr = ""
            while i < len(content) and content[i] != '}':
                expr += content[i]
                i += 1
            if i >= len(content):
                return "Formatting error: Unclosed '{'"
            i += 1
            evaluated = evaluate_expression(expr)
            if isinstance(evaluated, str) and evaluated.startswith("Evaluation error"):
                return f"Formatting error: {evaluated}"
            result += str(evaluated)
        else:
            result += content[i]
            i += 1
    return result

# Removes quotes from a string if it is enclosed in quotes
def strip_quotes(s):
    if isinstance(s, str) and len(s) >= 2:
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return s[1:-1]
    return s

# --- Line Interpretation Functions ---

# Interprets a single line of code and executes the corresponding action
def interpret_line(line):
    line = line.strip()
    if not line or line.startswith("##"):
        return None

    # Handle say f"formatted string" for f-string output
    if line.startswith("say f\"") and line.endswith("\""):
        content = line[5:-1]
        result = interpret_fstring(content)
        if not result.startswith("Formatting error"):
            print(strip_quotes(result))
        else:
            print(result)
        return None

    # Handle say "string" for direct string output
    elif line.startswith("say "):
        content = line[4:].strip()
        if content.startswith('"') and content.endswith('"'):
            print(content[1:-1])
        else:
            print("Syntax error: Invalid string format")
        return None

    # Handle then (statement) for if-then-else blocks
    elif line.startswith("then (") and line.endswith(")"):
        return line[6:-1].strip()

    # Handle else (statement) for if-then-else blocks
    elif line.startswith("else (") and line.endswith(")"):
        return line[6:-1].strip()

    # Handle while (condition) for loop constructs
    elif line.startswith("while (") and line.endswith(")"):
        return line[7:-1].strip()

    # Handle do (body) for loop constructs
    elif line.startswith("do (") and line.endswith(")"):
        return line[4:-1].strip()

    # Handle let for variable or array declaration
    elif line.startswith("let "):
        parts = line[4:].split("=", 1)
        if len(parts) != 2:
            print("Syntax error: Invalid declaration")
            return None
        name_part, value_part = parts[0].strip(), parts[1].strip()

        if "[" in name_part and "]" in name_part:
            # Array declaration
            try:
                name, size = name_part[:name_part.index("]")].split("[")
                if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name.strip()):
                    print("Syntax error: Invalid array name")
                    return None
                size = int(size.strip())
                # Value part can be comma separated or a string literal
                if value_part.startswith('"') and value_part.endswith('"'):
                    values = value_part.strip('"')
                else:
                    values = [parse_value(v.strip()) for v in value_part.split(',') if v.strip()]
                variables[name.strip()] = values[:size]
            except Exception as e:
                print(f"Syntax error: Invalid array declaration - {str(e)}")
        else:
            # Scalar variable
            if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name_part):
                print("Syntax error: Invalid variable name")
                return None
            variables[name_part] = parse_value(value_part)
        return None

    # Handle get(input) for variable or array input
    elif line.startswith("get(") and line.endswith(")"):
        arg = line[4:-1].strip()
        if "[" in arg and "]" in arg:
            # Array input
            try:
                name, size = arg[:arg.index("]")].split("[")
                name = name.strip()
                size = int(size.strip())
                val = input().split()
                variables[name] = [parse_value(v) for v in val][:size]
            except Exception as e:
                print(f"Syntax error: Invalid array input - {str(e)}")
        else:
            # Scalar input
            if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", arg):
                print("Syntax error: Invalid variable name")
                return None
            val = input()
            variables[arg] = parse_value(val)
        return None

    # Handle if (condition) for conditional statements
    elif line.startswith("if (") and line.endswith(")"):
        condition = line[4:-1].strip()
        result = evaluate_expression(condition)
        if isinstance(result, str) and result.startswith("Evaluation error"):
            print(result)
            return None
        return result

    # Handle assignment or expression evaluation
    elif any(op in line for op in ["+", "-", "*", "/", "|", "^", ">", "<", "!=", "<=", ">=", "=", "and", "or"]):
        # Assignment (var = expr)
        if "=" in line and not any(sym + "=" in line for sym in ["!", "<", ">"]):
            try:
                var, expr = line.split("=", 1)
                var = var.strip()
                expr = expr.strip()
                if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", var):
                    print("Syntax error: Invalid variable name")
                    return None
                result = evaluate_expression(expr)
                if isinstance(result, str) and result.startswith("Evaluation error"):
                    print(result)
                    return None
                variables[var] = result
            except Exception as e:
                print(f"Syntax error: Invalid assignment - {str(e)}")
        else:
            # Just evaluate expression and print result
            result = evaluate_expression(line)
            if isinstance(result, str) and result.startswith("Evaluation error"):
                print(result)
            else:
                print(result)
        return None

    else:
        print(f"Syntax error: Unknown statement: {line}")
        return None

# --- Main Interpretation Function ---

# Interprets a block of code, handling control structures like if and while
def interpret(code):
    lines = code.strip().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("##"):
            i += 1
            continue

        # Handle if statement with then and optional else
        if line.startswith("if "):
            condition_result = interpret_line(line)
            i += 1

            if i >= len(lines):
                continue

            then_line = lines[i].strip()
            if not then_line.startswith("then ("):
                print("Syntax error: Expected 'then' after 'if'")
                i += 1
                continue
            then_stmt = interpret_line(then_line)
            i += 1

            else_stmt = None
            if i < len(lines) and lines[i].strip().startswith("else ("):
                else_stmt = interpret_line(lines[i].strip())
                i += 1

            if condition_result:
                if then_stmt:
                    interpret(then_stmt)
            elif else_stmt:
                interpret(else_stmt)
            continue

        # Handle while loop
        if line.startswith("while "):
            condition = interpret_line(line)
            i += 1
            if i >= len(lines):
                continue

            do_line = lines[i].strip()
            if not do_line.startswith("do ("):
                print("Syntax error: Expected 'do' after 'while'")
                i += 1
                continue

            body = interpret_line(do_line)
            i += 1

            while True:
                while_result = evaluate_expression(condition)
                if isinstance(while_result, str) and while_result.startswith("Evaluation error"):
                    print(while_result)
                    break
                if not while_result:
                    break
                interpret(body)
            continue

        # Handle normal line
        interpret_line(line)
        i += 1