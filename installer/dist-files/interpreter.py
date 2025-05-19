import re

variables = {}

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

def evaluate_expression(expr):
    try:
        # Replace | with % (mod) and ^ with ** (power)
        expr = expr.strip().replace('|', '%').replace('^', '**')

        # Replace variables with their values
        for var in sorted(variables.keys(), key=len, reverse=True):
            # Ensure whole word replacement (avoid partial variable matches)
            expr = re.sub(rf'\b{var}\b', str(variables[var]), expr)

        # Define safe eval environment
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

def strip_quotes(s):
    if isinstance(s, str) and len(s) >= 2:
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return s[1:-1]
    return s

def interpret_line(line):
    line = line.strip()
    if not line or line.startswith("//"):
        return None

    # say f"formatted string"
    if line.startswith("say f\"") and line.endswith("\""):
        content = line[5:-1]
        result = interpret_fstring(content)
        if not result.startswith("Formatting error"):
            print(strip_quotes(result))
        else:
            print(result)
        return None

    # say "string"
    elif line.startswith("say "):
        content = line[4:].strip()
        if content.startswith('"') and content.endswith('"'):
            print(content[1:-1])
        else:
            print("Syntax error: Invalid string format")
        return None

    # then (statement)
    elif line.startswith("then (") and line.endswith(")"):
        return line[6:-1].strip()

    # else (statement)
    elif line.startswith("else (") and line.endswith(")"):
        return line[6:-1].strip()

    # while (condition)
    elif line.startswith("while (") and line.endswith(")"):
        return line[7:-1].strip()

    # do (body)
    elif line.startswith("do (") and line.endswith(")"):
        return line[4:-1].strip()

    # let variable or array declaration
    elif line.startswith("let "):
        parts = line[4:].split("=", 1)
        if len(parts) != 2:
            print("Syntax error: Invalid declaration")
            return None
        name_part, value_part = parts[0].strip(), parts[1].strip()

        if "[" in name_part and "]" in name_part:
            # array declaration
            try:
                name, size = name_part[:name_part.index("]")].split("[")
                if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name.strip()):
                    print("Syntax error: Invalid array name")
                    return None
                size = int(size.strip())
                # value part can be comma separated or a string literal
                if value_part.startswith('"') and value_part.endswith('"'):
                    values = value_part.strip('"')
                else:
                    values = [parse_value(v.strip()) for v in value_part.split(',') if v.strip()]
                variables[name.strip()] = values[:size]
            except Exception as e:
                print(f"Syntax error: Invalid array declaration - {str(e)}")
        else:
            # scalar variable
            if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name_part):
                print("Syntax error: Invalid variable name")
                return None
            variables[name_part] = parse_value(value_part)
        return None

    # get(input) for variable or array
    elif line.startswith("get(") and line.endswith(")"):
        arg = line[4:-1].strip()
        if "[" in arg and "]" in arg:
            # array input
            try:
                name, size = arg[:arg.index("]")].split("[")
                name = name.strip()
                size = int(size.strip())
                val = input().split()
                variables[name] = [parse_value(v) for v in val][:size]
            except Exception as e:
                print(f"Syntax error: Invalid array input - {str(e)}")
        else:
            # scalar input
            if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", arg):
                print("Syntax error: Invalid variable name")
                return None
            val = input()
            variables[arg] = parse_value(val)
        return None

    # if (condition)
    elif line.startswith("if (") and line.endswith(")"):
        condition = line[4:-1].strip()
        result = evaluate_expression(condition)
        if isinstance(result, str) and result.startswith("Evaluation error"):
            print(result)
            return None
        return result

    # assignment or expression evaluation
    elif any(op in line for op in ["+", "-", "*", "/", "|", "^", ">", "<", "!=", "<=", ">=", "=", "and", "or"]):
        # assignment (var = expr)
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

def interpret(code):
    lines = code.strip().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("//"):
            i += 1
            continue

        # if statement with then and optional else
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

        # while loop
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

        # normal line
        interpret_line(line)
        i += 1
