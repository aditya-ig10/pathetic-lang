# pathetic/interpreter.py

def interpret(code):
    lines = code.strip().splitlines()
    for line in lines:
        line = line.strip()

        # New syntax: say "text"
        if line.startswith("say "):
            content = line[4:].strip()  # Skip 'say ' part
            if content.startswith('"') and content.endswith('"'):
                print(content[1:-1])  # Remove quotes and print
            else:
                print("Syntax error: Invalid string format")
        
        # Old syntax still works for backward compatibility (optional)
        elif line.startswith("print "):
            content = line[6:].strip()  # Skip 'print ' part
            if content.startswith('"') and content.endswith('"'):
                print(content[1:-1])  # Remove quotes and print
            else:
                print("Syntax error: Invalid string format")
        
        else:
            print(f"Syntax error: Unknown statement '{line}'")
