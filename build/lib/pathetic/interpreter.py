import re

# Global dictionary to store variables and their values
variables = {}

# --- Value Parsing Functions ---

# Processes escape sequences in strings
def process_escape_sequences(s):
    """Process escape sequences like \\n, \\t, \\r, \\\\, \\\", etc."""
    if not isinstance(s, str):
        return s
    
    # Dictionary of escape sequences
    escape_sequences = {
        '\\n': '\n',    # newline
        '\\t': '\t',    # tab
        '\\r': '\r',    # carriage return
        '\\b': '\b',    # backspace
        '\\f': '\f',    # form feed
        '\\v': '\v',    # vertical tab
        '\\\\"': '"',   # double quote
        "\\\\'": "'",   # single quote
        '\\\\': '\\',   # backslash (must be last to avoid conflicts)
    }
    
    # Replace escape sequences
    for escape, replacement in escape_sequences.items():
        s = s.replace(escape, replacement)
    
    return s

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
        # Strip quotes if string literal and process escape sequences
        if val.startswith('"') and val.endswith('"'):
            return process_escape_sequences(val[1:-1])
        elif val.startswith("'") and val.endswith("'"):
            return process_escape_sequences(val[1:-1])
        return val
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
            if var in variables:
                value = variables[var]
                # If the value is a string, quote it to avoid syntax errors
                if isinstance(value, str):
                    # Escape quotes and backslashes in the string for safe eval
                    escaped_value = value.replace('\\', '\\\\').replace('"', '\\"')
                    value = f'"{escaped_value}"'
                expr = re.sub(rf'\b{re.escape(var)}\b', str(value), expr)

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
    # Process escape sequences in the f-string content first
    content = process_escape_sequences(content)
    
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
            # Check if the evaluation failed
            if isinstance(evaluated, str) and evaluated.startswith("Evaluation error"):
                return f"Formatting error: {evaluated}"
            # Convert the evaluated result to string, handling None or other types
            result += str(evaluated if evaluated is not None else "")
        else:
            result += content[i]
            i += 1
    return result

# Removes quotes from a string if it is enclosed in quotes and processes escape sequences
def strip_quotes(s):
    if isinstance(s, str) and len(s) >= 2:
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return process_escape_sequences(s[1:-1])
    return s

# --- Line Interpretation Functions ---

# Interprets a single line of code and executes the corresponding action
def interpret_line(line):
    line = line.strip()
    if not line or line.startswith("//"):
        return None

    # Handle say f"formatted string" for f-string output (no automatic newline)
    if line.startswith("say f\"") and line.endswith("\""):
        content = line[6:-1]  # Extract content between f" and "
        result = interpret_fstring(content)
        if not result.startswith("Formatting error"):
            print(result, end='')
        else:
            print(result, end='')
        return None

    # Handle say "string" for direct string output (no automatic newline)
    elif line.startswith("say "):
        content = line[4:].strip()
        if content.startswith('"') and content.endswith('"'):
            # Process escape sequences in the string
            processed_content = process_escape_sequences(content[1:-1])
            print(processed_content, end='')
        elif content.startswith("'") and content.endswith("'"):
            # Process escape sequences in the string
            processed_content = process_escape_sequences(content[1:-1])
            print(processed_content, end='')
        else:
            print("Syntax error: Invalid string format")
        return None

    # Handle for loop: for i as ( init ; condition ; update )
    elif line.startswith("for ") and " as (" in line and line.endswith(")"):
        try:
            # Extract the loop variable and components
            parts = line.split(" as (")
            if len(parts) != 2:
                print("Syntax error: Invalid for loop syntax - expected 'as ('")
                return None
            var_name = parts[0].replace("for ", "").strip()
            if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", var_name):
                print(f"Syntax error: Invalid loop variable name '{var_name}' - must start with a letter or underscore")
                return None

            loop_parts = parts[1][:-1].split(";")
            if len(loop_parts) != 3:
                print("Syntax error: For loop must have 3 components (init; condition; update)")
                return None

            init_stmt = loop_parts[0].strip()  # e.g., i = 0
            condition = loop_parts[1].strip()  # e.g., i < 5
            update_stmt = loop_parts[2].strip()  # e.g., i++

            if not init_stmt or not condition or not update_stmt:
                print("Syntax error: For loop components cannot be empty")
                return None

            return ("for", var_name, init_stmt, condition, update_stmt)
        except Exception as e:
            print(f"Syntax error: Invalid for loop - {str(e)}")
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

    # Handle do (statement) for loop constructs
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
                name = name.strip()
                if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name):
                    print(f"Syntax error: Invalid array name '{name}' - must start with a letter or underscore")
                    return None
                size = int(size.strip())
                # Value part can be comma separated or a string literal
                if value_part.startswith('"') and value_part.endswith('"'):
                    values = process_escape_sequences(value_part.strip('"'))
                else:
                    values = [parse_value(v.strip()) for v in value_part.split(',') if v.strip()]
                variables[name] = values[:size]
            except Exception as e:
                print(f"Syntax error: Invalid array declaration - {str(e)}")
        else:
            # Scalar variable
            if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name_part):
                print(f"Syntax error: Invalid variable name '{name_part}' - must start with a letter or underscore")
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
                if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name):
                    print(f"Syntax error: Invalid array name '{name}' - must start with a letter or underscore")
                    return None
                size = int(size.strip())
                val = input().split()
                variables[name] = [parse_value(v) for v in val][:size]
            except Exception as e:
                print(f"Syntax error: Invalid array input - {str(e)}")
        else:
            # Scalar input
            if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", arg):
                print(f"Syntax error: Invalid variable name '{arg}' - must start with a letter or underscore")
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
                    print(f"Syntax error: Invalid variable name '{var}' - must start with a letter or underscore")
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

# --- Block Parsing Functions ---

def find_matching_brace(lines, start_index):
    """Find the matching closing brace for an opening brace"""
    brace_count = 0
    for i in range(start_index, len(lines)):
        line = lines[i].strip()
        if line.endswith("{"):
            brace_count += 1
        elif line == "}":
            brace_count -= 1
            if brace_count == 0:
                return i
    return -1

def extract_block(lines, start_index, end_index):
    """Extract lines between start and end index as a block"""
    block_lines = []
    for i in range(start_index, end_index):
        line = lines[i].strip()
        if line and not line.startswith("//"):
            block_lines.append(line)
    return "\n".join(block_lines)

# --- Main Interpretation Function ---

# Interprets a block of code, handling control structures like if, while, and for
def interpret(code):
    lines = code.strip().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("//"):
            i += 1
            continue

        # Handle for loop
        if line.startswith("for "):
            loop_info = interpret_line(line)
            i += 1
            if i >= len(lines):
                continue

            if loop_info is None or loop_info[0] != "for":
                print("Syntax error: Invalid for loop")
                continue

            _, var_name, init_stmt, condition, update_stmt = loop_info

            do_line = lines[i].strip()
            if not do_line.startswith("do {"):
                print("Syntax error: Expected 'do {' after 'for'")
                i += 1
                continue

            # Find the matching closing brace
            closing_brace_index = find_matching_brace(lines, i)
            if closing_brace_index == -1:
                print("Syntax error: No matching '}' found for 'do {'")
                i += 1
                continue

            # Extract the loop body
            body = extract_block(lines, i + 1, closing_brace_index)
            i = closing_brace_index + 1

            # Execute the initialization statement
            interpret_line(init_stmt)

            # Handle the update statement (e.g., i++)
            if "++" in update_stmt:
                var = update_stmt.replace("++", "").strip()
                update_code = f"{var} = {var} + 1"
            elif "--" in update_stmt:
                var = update_stmt.replace("--", "").strip()
                update_code = f"{var} = {var} - 1"
            else:
                update_code = update_stmt

            # Execute the loop
            while True:
                for_result = evaluate_expression(condition)
                if isinstance(for_result, str) and for_result.startswith("Evaluation error"):
                    print(for_result)
                    break
                if not for_result:
                    break
                interpret(body)
                interpret_line(update_code)
            continue

        # Handle while loop
        if line.startswith("while "):
            condition = interpret_line(line)
            i += 1
            if i >= len(lines):
                continue

            do_line = lines[i].strip()
            if do_line.startswith("do {"):
                # Block-style while loop
                closing_brace_index = find_matching_brace(lines, i)
                if closing_brace_index == -1:
                    print("Syntax error: No matching '}' found for 'do {'")
                    i += 1
                    continue

                body = extract_block(lines, i + 1, closing_brace_index)
                i = closing_brace_index + 1
            elif do_line.startswith("do ("):
                # Single statement while loop
                body = interpret_line(do_line)
                i += 1
            else:
                print("Syntax error: Expected 'do' after 'while'")
                i += 1
                continue

            # Execute the loop
            while True:
                while_result = evaluate_expression(condition)
                if isinstance(while_result, str) and while_result.startswith("Evaluation error"):
                    print(while_result)
                    break
                if not while_result:
                    break
                interpret(body)
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

        # Handle normal line
        interpret_line(line)
        i += 1