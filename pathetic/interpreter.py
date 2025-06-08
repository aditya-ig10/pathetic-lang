import re

# Global dictionaries to store variables and functions
variables = {}
functions = {}

# --- Value Parsing Functions ---

def process_escape_sequences(s):
    """Process escape sequences like \\n, \\t, \\r, \\\\, \\\", etc."""
    if not isinstance(s, str):
        return s
    
    escape_sequences = {
        '\\n': '\n',
        '\\t': '\t',
        '\\r': '\r',
        '\\b': '\b',
        '\\f': '\f',
        '\\v': '\v',
        '\\\\"': '"',
        "\\\\'": "'",
        '\\\\': '\\',
    }
    
    for escape, replacement in escape_sequences.items():
        s = s.replace(escape, replacement)
    
    return s

def parse_value(val):
    val = val.strip()
    try:
        if re.match(r'^-?\d+\.\d+$', val):
            return float(val)
        if re.match(r'^-?\d+$', val):
            return int(val)
        if val.startswith('"') and val.endswith('"'):
            return process_escape_sequences(val[1:-1])
        elif val.startswith("'") and val.endswith("'"):
            return process_escape_sequences(val[1:-1])
        return val
    except ValueError:
        return val

# --- Expression Evaluation Functions ---

def evaluate_expression(expr, local_vars=None):
    if local_vars is None:
        local_vars = variables
    try:
        expr = expr.strip().replace('|', '%').replace('^', '**')
        for var in sorted(local_vars.keys(), key=len, reverse=True):
            if var in local_vars:
                value = local_vars[var]
                if isinstance(value, str):
                    escaped_value = value.replace('\\', '\\\\').replace('"', '\\"')
                    value = f'"{escaped_value}"'
                expr = re.sub(rf'\b{re.escape(var)}\b', str(value), expr)
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

def interpret_fstring(content, local_vars=None):
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
            evaluated = evaluate_expression(expr, local_vars)
            if isinstance(evaluated, str) and evaluated.startswith("Evaluation error"):
                return f"Formatting error: {evaluated}"
            result += str(evaluated if evaluated is not None else "")
        else:
            result += content[i]
            i += 1
    return result

def strip_quotes(s):
    if isinstance(s, str) and len(s) >= 2:
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return process_escape_sequences(s[1:-1])
    return s

# --- Line Interpretation Functions ---

def interpret_line(line, local_vars=None):
    if local_vars is None:
        local_vars = variables
    
    line = line.strip()
    if not line or line.startswith("//"):
        return None, None

    # Handle function definition
    if line.startswith("func ") and "{" in line:
        try:
            header = line[5:line.index("{")].strip()
            name_part, param_part = header.split("(", 1)
            name = name_part.strip()
            if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name):
                print(f"Syntax error: Invalid function name '{name}' at line: {line}")
                return None, None
            params = [p.strip() for p in param_part[:-1].split(",") if p.strip()]
            for param in params:
                if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", param):
                    print(f"Syntax error: Invalid parameter name '{param}' at line: {line}")
                    return None, None
            return ("func", name, params), None
        except Exception as e:
            print(f"Syntax error: Invalid function definition at line: {line} - {str(e)}")
            return None, None

    # Handle function call
    if re.match(r"[a-zA-Z_][a-zA-Z0-9_]*\([^)]*\)$", line):
        try:
            name, args_part = line.split("(", 1)
            name = name.strip()
            args = [arg.strip() for arg in args_part[:-1].split(",") if arg.strip()]
            if name in functions:
                func_params, func_body = functions[name]
                if len(args) != len(func_params):
                    print(f"Syntax error: Function '{name}' expects {len(func_params)} arguments, got {len(args)} at line: {line}")
                    return None, None
                evaluated_args = [evaluate_expression(arg, local_vars) for arg in args]
                for arg in evaluated_args:
                    if isinstance(arg, str) and arg.startswith("Evaluation error"):
                        print(arg)
                        return None, None
                func_vars = dict(local_vars)
                for param, arg in zip(func_params, evaluated_args):
                    func_vars[param] = arg
                result = interpret(func_body, func_vars)
                # print(f"DEBUG: Function '{name}' returned {result}")  # Uncomment for debugging
                return None, result
            else:
                print(f"Syntax error: Undefined function '{name}' at line: {line}")
                return None, None
        except Exception as e:
            print(f"Syntax error: Invalid function call at line: {line} - {str(e)}")
            return None, None

    # Handle return statement
    if line.startswith("return "):
        value = line[7:].strip()
        if value:
            result = evaluate_expression(value, local_vars)
            if isinstance(result, str) and result.startswith("Evaluation error"):
                print(result)
                return None, None
            return "return", result
        return "return", None

    # Handle say f"string"
    if line.startswith("say f\"") and line.endswith("\""):
        content = line[6:-1]
        result = interpret_fstring(content, local_vars)
        if not result.startswith("Formatting error"):
            print(result, end='')
        else:
            print(result, end='')
        return None, None

    # Handle say "string"
    elif line.startswith("say "):
        content = line[4:].strip()
        if content.startswith('"') and content.endswith('"'):
            processed_content = process_escape_sequences(content[1:-1])
            print(processed_content, end='')
        elif content.startswith("'") and content.endswith("'"):
            processed_content = process_escape_sequences(content[1:-1])
            print(processed_content, end='')
        else:
            print(f"Syntax error: Invalid string format at line: {line}")
        return None, None

    # Handle for loop
    elif line.startswith("for ") and " as (" in line and line.endswith(")"):
        try:
            parts = line.split(" as (")
            if len(parts) != 2:
                print(f"Syntax error: Invalid for loop syntax at line: {line}")
                return None, None
            var_name = parts[0].replace("for ", "").strip()
            if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", var_name):
                print(f"Syntax error: Invalid loop variable name '{var_name}' at line: {line}")
                return None, None
            loop_parts = parts[1][:-1].split(";")
            if len(loop_parts) != 3:
                print(f"Syntax error: For loop must have 3 components at line: {line}")
                return None, None
            init_stmt = loop_parts[0].strip()
            condition = loop_parts[1].strip()
            update_stmt = loop_parts[2].strip()
            if not init_stmt or not condition or not update_stmt:
                print(f"Syntax error: For loop components cannot be empty at line: {line}")
                return None, None
            return ("for", var_name, init_stmt, condition, update_stmt), None
        except Exception as e:
            print(f"Syntax error: Invalid for loop at line: {line} - {str(e)}")
            return None, None

    # Handle then
    elif line.startswith("then (") and line.endswith(")"):
        return line[6:-1].strip(), None

    # Handle else
    elif line.startswith("else (") and line.endswith(")"):
        return line[6:-1].strip(), None

    # Handle while
    elif line.startswith("while (") and line.endswith(")"):
        return line[7:-1].strip(), None

    # Handle do
    elif line.startswith("do (") and line.endswith(")"):
        return line[4:-1].strip(), None

    # Handle let
    elif line.startswith("let "):
        parts = line[4:].split("=", 1)
        if len(parts) != 2:
            print(f"Syntax error: Invalid declaration at line: {line}")
            return None, None
        name_part, value_part = parts[0].strip(), parts[1].strip()
        if "[" in name_part and "]" in name_part:
            try:
                name, size = name_part[:name_part.index("]")].split("[")
                name = name.strip()
                if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name):
                    print(f"Syntax error: Invalid array name '{name}' at line: {line}")
                    return None, None
                size = int(size.strip())
                if value_part.startswith('"') and value_part.endswith('"'):
                    values = process_escape_sequences(value_part.strip('"'))
                else:
                    values = [parse_value(v.strip()) for v in value_part.split(',') if v.strip()]
                local_vars[name] = values[:size]
                # print(f"DEBUG: Assigned array {name} = {local_vars[name]}")  # Uncomment for debugging
            except Exception as e:
                print(f"Syntax error: Invalid array declaration at line: {line} - {str(e)}")
        else:
            if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name_part):
                print(f"Syntax error: Invalid variable name '{name_part}' at line: {line}")
                return None, None
            # Check if value_part is a function call
            if re.match(r"[a-zA-Z_][a-zA-Z0-9_]*\([^)]*\)$", value_part):
                try:
                    name, args_part = value_part.split("(", 1)
                    name = name.strip()
                    args = [arg.strip() for arg in args_part[:-1].split(",") if arg.strip()]
                    if name in functions:
                        func_params, func_body = functions[name]
                        if len(args) != len(func_params):
                            print(f"Syntax error: Function '{name}' expects {len(func_params)} arguments, got {len(args)} at line: {line}")
                            return None, None
                        evaluated_args = [evaluate_expression(arg, local_vars) for arg in args]
                        for arg in evaluated_args:
                            if isinstance(arg, str) and arg.startswith("Evaluation error"):
                                print(arg)
                                return None, None
                        func_vars = dict(local_vars)
                        for param, arg in zip(func_params, evaluated_args):
                            func_vars[param] = arg
                        result = interpret(func_body, func_vars)
                        local_vars[name_part] = result
                        # print(f"DEBUG: Assigned {name_part} = {result} from function call")  # Uncomment for debugging
                    else:
                        print(f"Syntax error: Undefined function '{name}' in assignment at line: {line}")
                        return None, None
                except Exception as e:
                    print(f"Syntax error: Invalid function call in assignment at line: {line} - {str(e)}")
            else:
                result = evaluate_expression(value_part, local_vars)
                if isinstance(result, str) and result.startswith("Evaluation error"):
                    print(result)
                    return None, None
                local_vars[name_part] = result
                # print(f"DEBUG: Assigned {name_part} = {result}")  # Uncomment for debugging
        return None, None

    # Handle get
    elif line.startswith("get(") and line.endswith(")"):
        arg = line[4:-1].strip()
        if "[" in arg and "]" in arg:
            try:
                name, size = arg[:arg.index("]")].split("[")
                name = name.strip()
                if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name):
                    print(f"Syntax error: Invalid array name '{name}' at line: {line}")
                    return None, None
                size = int(size.strip())
                val = input().split()
                local_vars[name] = [parse_value(v) for v in val[:size]]
            except Exception as e:
                print(f"Syntax error: Invalid array input at line: {line} - {str(e)}")
        else:
            if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", arg):
                print(f"Syntax error: Invalid variable name '{arg}' at line: {line}")
                return None, None
            val = input()
            local_vars[arg] = parse_value(val)
        return None, None

    # Handle if
    elif line.startswith("if (") and line.endswith(")"):
        condition = line[4:-1].strip()
        result = evaluate_expression(condition, local_vars)
        if isinstance(result, str) and result.startswith("Evaluation error"):
            print(result)
            return None, None
        return result, None

    # Handle assignment or expression
    elif any(op in line for op in ["+", "-", "*", "/", "|", "^", ">", "<", "!=", "<=", ">=", "=", "and", "or"]):
        if "=" in line and not any(sym + "=" in line for sym in ["!", "<", ">"]):
            try:
                var, expr = line.split("=", 1)
                var = var.strip()
                expr = expr.strip()
                if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", var):
                    print(f"Syntax error: Invalid variable name '{var}' at line: {line}")
                    return None, None
                result = evaluate_expression(expr, local_vars)
                if isinstance(result, str) and result.startswith("Evaluation error"):
                    print(result)
                    return None, None
                local_vars[var] = result
            except Exception as e:
                print(f"Syntax error: Invalid assignment at line: {line} - {str(e)}")
        else:
            result = evaluate_expression(line, local_vars)
            if isinstance(result, str) and result.startswith("Evaluation error"):
                print(result)
            else:
                print(result)
        return None, None

    # Handle standalone closing brace
    elif line == "}":
        return "end_block", None

    else:
        print(f"Syntax error: Unknown statement at line: {line}")
        return None, None

# --- Block Parsing Functions ---

def find_matching_brace(lines, start_index):
    """Find the matching closing brace for an opening brace"""
    brace_count = 0
    for i in range(start_index, len(lines)):
        line = lines[i].strip()
        if not line or line.startswith("//"):
            continue
        if "{" in line:
            brace_count += line.count("{")
        if "}" in line:
            brace_count -= line.count("}")
            if brace_count <= 0:
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

def interpret(code, local_vars=None):
    if local_vars is None:
        local_vars = variables
    
    lines = code.strip().splitlines()
    i = 0
    return_value = None
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("//"):
            i += 1
            continue

        # Handle function definition
        if line.startswith("func "):
            func_info, _ = interpret_line(line, local_vars)
            if func_info is None or func_info[0] != "func":
                print(f"Syntax error: Invalid function definition at line {i + 1}: {line}")
                i += 1
                continue
            _, func_name, params = func_info
            closing_brace_index = find_matching_brace(lines, i)
            if closing_brace_index == -1:
                print(f"Syntax error: No matching '}}' found for function body at line {i + 1}: {line}")
                i += 1
                continue
            body = extract_block(lines, i + 1, closing_brace_index)
            functions[func_name] = (params, body)
            i = closing_brace_index + 1
            continue

        # Handle for loop
        if line.startswith("for "):
            loop_info, _ = interpret_line(line, local_vars)
            i += 1
            if i >= len(lines):
                continue
            if loop_info is None or loop_info[0] != "for":
                print(f"Syntax error: Invalid for loop at line {i}: {line}")
                continue
            _, var_name, init_stmt, condition, update_stmt = loop_info
            do_line = lines[i].strip() if i < len(lines) else ""
            if not do_line.startswith("do {"):
                print(f"Syntax error: Expected 'do {{' after 'for' at line {i + 1}: {do_line}")
                i += 1
                continue
            closing_brace_index = find_matching_brace(lines, i)
            if closing_brace_index == -1:
                print(f"Syntax error: No matching '}}' found for 'do {{' at line {i + 1}: {do_line}")
                i += 1
                continue
            body = extract_block(lines, i + 1, closing_brace_index)
            i = closing_brace_index + 1
            interpret_line(init_stmt, local_vars)
            if "++" in update_stmt:
                var = update_stmt.replace("++", "").strip()
                update_code = f"{var} = {var} + 1"
            elif "--" in update_stmt:
                var = update_stmt.replace("--", "").strip()
                update_code = f"{var} = {var} - 1"
            else:
                update_code = update_stmt
            while True:
                for_result = evaluate_expression(condition, local_vars)
                if isinstance(for_result, str) and for_result.startswith("Evaluation error"):
                    print(for_result)
                    break
                if not for_result:
                    break
                loop_return = interpret(body, local_vars)
                if loop_return is not None:
                    return_value = loop_return
                    break
                interpret_line(update_code, local_vars)
            if return_value is not None:
                break
            continue

        # Handle while loop
        if line.startswith("while "):
            condition, _ = interpret_line(line, local_vars)
            i += 1
            if i >= len(lines):
                continue
            do_line = lines[i].strip()
            if do_line.startswith("do {"):
                closing_brace_index = find_matching_brace(lines, i)
                if closing_brace_index == -1:
                    print(f"Syntax error: No matching '}}' found for 'do {{' at line {i + 1}: {do_line}")
                    i += 1
                    continue
                body = extract_block(lines, i + 1, closing_brace_index)
                i = closing_brace_index + 1
            elif do_line.startswith("do ("):
                body = interpret_line(do_line, local_vars)[0]
                i += 1
            else:
                print(f"Syntax error: Expected 'do' after 'while' at line {i + 1}: {do_line}")
                i += 1
                continue
            while True:
                while_result = evaluate_expression(condition, local_vars)
                if isinstance(while_result, str) and while_result.startswith("Evaluation error"):
                    print(while_result)
                    break
                if not while_result:
                    break
                loop_return = interpret(body, local_vars)
                if loop_return is not None:
                    return_value = loop_return
                    break
            if return_value is not None:
                break
            continue

        # Handle if statement
        if line.startswith("if "):
            condition_result, _ = interpret_line(line, local_vars)
            i += 1
            if i >= len(lines):
                continue
            then_line = lines[i].strip()
            if not then_line.startswith("then ("):
                print(f"Syntax error: Expected 'then' after 'if' at line {i + 1}: {then_line}")
                i += 1
                continue
            then_stmt = interpret_line(then_line, local_vars)[0]
            i += 1
            else_stmt = None
            if i < len(lines) and lines[i].strip().startswith("else ("):
                else_stmt = interpret_line(lines[i].strip(), local_vars)[0]
                i += 1
            if condition_result:
                if then_stmt:
                    then_return = interpret(then_stmt, local_vars)
                    if then_return is not None:
                        return_value = then_return
            elif else_stmt:
                else_return = interpret(else_stmt, local_vars)
                if else_return is not None:
                    return_value = else_return
            if return_value is not None:
                break
            continue

        # Handle normal line
        result, return_val = interpret_line(line, local_vars)
        if result == "return":
            return return_val
        elif result == "end_block":
            print(f"Syntax error: Unexpected '}}' at line {i + 1}: {line}")
            i += 1
            continue
        i += 1

    return return_value