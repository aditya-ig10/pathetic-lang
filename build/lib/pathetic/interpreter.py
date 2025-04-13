import re

variables = {}

def parse_value(val):
    try:
        if '.' in val:
            return float(val)
        return int(val)
    except ValueError:
        return val.strip('"') if val.startswith('"') else val

def evaluate_expression(expr):
    try:
        for var in variables:
            expr = expr.replace(var, str(variables[var]))
        return eval(expr)
    except:
        return "Evaluation error"

def interpret_line(line):
    if line.startswith("say f\"") and line.endswith("\""):
        content = line[6:-1]
        try:
            # Replace {x+y} using eval
            interpolated = re.sub(r'\{([^}]+)\}', lambda m: str(eval(m.group(1), {}, variables)), content)
            print(interpolated)
        except Exception:
            print("Formatting error")

    elif line.startswith("say "):
        content = line[4:].strip()
        if content.startswith('"') and content.endswith('"'):
            print(content[1:-1])
        else:
            print("Syntax error: Invalid string format")

    elif line.startswith("then (") and line.endswith(")"):
        interpret_line(line[6:-1].strip())

    elif line.startswith("else (") and line.endswith(")"):
        interpret_line(line[6:-1].strip())

    elif line.startswith("let "):
        parts = line[4:].split("=")
        if len(parts) != 2:
            print("Syntax error: Invalid declaration")
            return
        name_part = parts[0].strip()
        value_part = parts[1].strip()
        if "[" in name_part and "]" in name_part:
            name, size = name_part[:-1].split("[")
            name = name.strip()
            size = int(size.strip())
            if value_part.startswith('"'):
                variables[name] = value_part.strip('"')[:size]
            else:
                variables[name] = list(map(parse_value, value_part.split(',')))[:size]
        else:
            variables[name_part] = parse_value(value_part)

    elif line.startswith("get("):
        arg = line[4:-1].strip()
        if "[" in arg and "]" in arg:
            name, size = arg[:-1].split("[")
            size = size.strip()
            if size:
                size = int(size)
                val = input(f"Enter {size} values for {name.strip()}: ").split()
                variables[name.strip()] = list(map(parse_value, val))[:size]
            else:
                val = input(f"Enter array values for {name.strip()}: ").split()
                variables[name.strip()] = list(map(parse_value, val))
        else:
            val = input(f"Enter value for {arg}: ")
            variables[arg] = parse_value(val)

    elif line.startswith("if "):
        condition = line[3:].strip()[1:-1].strip()
        result = evaluate_expression(condition)
        return result

    elif any(op in line for op in ["+", "-", "*", "/", "|", "^", ">", "<", "!=", "<=", ">=", "="]):
        if "=" in line and not any(c in line for c in ["!", "<", ">", "+", "-", "*", "/", "|", "^"]):
            var, expr = line.split("=")
            variables[var.strip()] = evaluate_expression(expr.strip())
        else:
            print(evaluate_expression(line))

    else:
        print(f"Syntax error or unknown statement: {line}")

def interpret(code):
    lines = code.strip().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        if line.startswith("if "):
            condition_result = interpret_line(line)
            i += 1
            if i < len(lines):
                next_line = lines[i].strip()
                if condition_result:
                    if next_line.startswith("then ("):
                        interpret_line(next_line)
                    else:
                        print("Syntax error: expected 'then'")
                else:
                    i += 1
                    if i < len(lines):
                        else_line = lines[i].strip()
                        if else_line.startswith("else ("):
                            interpret_line(else_line)
            i += 1
            continue

        interpret_line(line)
        i += 1
