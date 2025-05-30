<p align="center">
  <img src="https://github.com/user-attachments/assets/1aa15e7e-d76e-4b1f-a850-8cf7ea8d37cc" alt="pth" />
</p>

# Pathetic Programming Language Documentation

Pathetic is a simple, pseudo-code-based programming language designed for ease of use with a focus on basic control structures, variable manipulation, and string formatting. This documentation outlines the syntax, operators, and features supported by the language, as implemented in the provided interpreter.

## Table of Contents
1. [Basic Syntax](#basic-syntax)
2. [Data Types](#data-types)
3. [Variables and Arrays](#variables-and-arrays)
4. [Input and Output](#input-and-output)
5. [Operators](#operators)
6. [Control Structures](#control-structures)
7. [String Formatting (f-strings)](#string-formatting-f-strings)
8. [Comments](#comments)
9. [Examples](#examples)

## Basic Syntax
- **Statements**: Each statement is written on a new line. Statements are executed sequentially unless controlled by loops or conditionals.
- **Case Sensitivity**: Variable names and keywords are case-sensitive.
- **Whitespace**: Whitespace is ignored except within string literals.
- **Line Termination**: No explicit line terminators (e.g., semicolons) are required.
- **Valid Identifiers**: Variable and array names must start with a letter or underscore and can contain letters, digits, or underscores (regex: `[a-zA-Z_][a-zA-Z0-9_]*`).

## Data Types
Pathetic supports the following data types:
- **Integer**: Whole numbers (e.g., `5`, `-10`).
- **Float**: Decimal numbers (e.g., `3.14`, `-0.5`).
- **String**: Text enclosed in single (`'`) or double (`"`) quotes, supporting escape sequences.
- **Array**: A list of values (integers, floats, or strings) of fixed size, indexed starting at 0.
- **Boolean**: `True` and `False` (used in conditions).

Values are automatically parsed based on their format:
- Numbers matching `^-?\d+$` are integers.
- Numbers matching `^-?\d+\.\d+$` are floats.
- Text enclosed in quotes is treated as a string with escape sequence processing.
- Unquoted text is treated as a variable name or raw string (if not a variable).

## Variables and Arrays
### Variable Declaration
Use `let` to declare and initialize a variable with a value.
- **Syntax**: `let variable_name = value`
- **Example**: 
  ```
  let x = 5
  let name = "Alice"
  ```
- Variables can store integers, floats, or strings.
- Invalid variable names (e.g., starting with a number) result in a `Syntax error`.

### Array Declaration
Use `let` with square brackets to declare an array of a fixed size.
- **Syntax**: `let array_name[size] = value1, value2, ...`
- **Example**:
  ```
  let numbers[3] = 1, 2, 3
  let words[2] = "hello", "world"
  ```
- Alternatively, arrays can be initialized with a single string literal:
  ```
  let text[5] = "hello"
  ```
- The size must be an integer, and the number of values cannot exceed the specified size.
- Invalid array names or sizes result in a `Syntax error`.

### Variable Assignment
Assign a new value to an existing variable using `=`.
- **Syntax**: `variable_name = expression`
- **Example**:
  ```
  let x = 10
  x = x + 5
  ```
- The expression is evaluated and assigned to the variable.

## Input and Output
### Input
Use `get` to read input from the user.
- **Scalar Input**:
  - **Syntax**: `get(variable_name)`
  - Reads a single value and assigns it to the variable, automatically parsed as an integer, float, or string.
  - **Example**:
    ```
    get(x)
    ```
- **Array Input**:
  - **Syntax**: `get(array_name[size])`
  - Reads space-separated values and assigns them to the array, up to the specified size.
  - **Example**:
    ```
    get(numbers[3])
    ```
    (If the input is `1 2 3`, `numbers` becomes `[1, 2, 3]`.)

### Output
Use `say` to print output without a newline.
- **Direct String Output**:
  - **Syntax**: `say "string"` or `say 'string'`
  - Prints the string with escape sequences processed.
  - **Example**:
    ```
    say "Hello\nWorld"
    ```
    Output: 
    ```
    Hello
    World
    ```
- **Formatted String (f-string) Output**:
  - **Syntax**: `say f"string with {expression}"`
  - Evaluates expressions within curly braces and prints the resulting string.
  - **Example**:
    ```
    let x = 5
    say f"The value is {x}"
    ```
    Output: `The value is 5`

## Operators
Pathetic supports the following operators for use in expressions:

### Arithmetic Operators
- `+`: Addition (e.g., `3 + 2` evaluates to `5`)
- `-`: Subtraction (e.g., `5 - 2` evaluates to `3`)
- `*`: Multiplication (e.g., `4 * 3` evaluates to `12`)
- `/`: Division (e.g., `10 / 2` evaluates to `5.0`)
- `|`: Modulo (remainder) (e.g., `10 | 3` evaluates to `1`)
- `^`: Exponentiation (e.g., `2 ^ 3` evaluates to `8`)

### Comparison Operators
- `>`: Greater than (e.g., `5 > 3` evaluates to `True`)
- `<`: Less than (e.g., `3 < 5` evaluates to `True`)
- `>=`: Greater than or equal to (e.g., `5 >= 5` evaluates to `True`)
- `<=`: Less than or equal to (e.g., `3 <= 5` evaluates to `True`)
- `==`: Equal to (e.g., `5 == 5` evaluates to `True`)
- `!=`: Not equal to (e.g., `5 != 3` evaluates to `True`)

### Logical Operators
- `and`: Logical AND (e.g., `True and False` evaluates to `False`)
- `or`: Logical OR (e.g., `True or False` evaluates to `True`)

### Increment/Decrement (in for loops)
- `++`: Increment by 1 (e.g., `i++` is equivalent to `i = i + 1`)
- `--`: Decrement by 1 (e.g., `i--` is equivalent to `i = i - 1`)

### Notes
- Expressions can include variables, which are replaced with their values during evaluation.
- The `^` operator is strictly for exponentiation, not factorial.
- String literals in expressions must be quoted to avoid syntax errors.

## Control Structures
### If-Then-Else
Conditional execution with an optional else clause.
- **Syntax**:
  ```
  if (condition)
  then (statement)
  [else (statement)]
  ```
- **Example**:
  ```
  let x = 10
  if (x > 5)
  then (say "x is large")
  else (say "x is small")
  ```
  Output: `x is large`

- The `condition` is evaluated as a boolean.
- The `then` and `else` statements are single statements (not blocks). Use nested statements for complex logic.
- If the condition evaluates to `True`, the `then` statement is executed; otherwise, the `else` statement (if present) is executed.

### While Loop
Execute a block or single statement while a condition is true.
- **Syntax for Block**:
  ```
  while (condition)
  do {
    statements
  }
  ```
- **Syntax for Single Statement**:
  ```
  while (condition)
  do (statement)
  ```
- **Example**:
  ```
  let i = 0
  while (i < 3)
  do {
    say f"Count: {i}
"
    i = i + 1
  }
  ```
  Output:
  ```
  Count: 0
  Count: 1
  Count: 2
  ```

- The `condition` is evaluated before each iteration.
- The block or statement is executed as long as the condition is `True`.

### For Loop
A for loop with initialization, condition, and update statements.
- **Syntax**:
  ```
  for variable as (init; condition; update)
  do {
    statements
  }
  ```
- **Example**:
  ```
  for i as (let i = 0; i < 3; i++)
  do {
    say f"Number: {i}
"
  }
  ```
  Output:
  ```
  Number: 0
  Number: 1
  Number: 2
  ```

- **Components**:
  - `init`: Initialization statement (e.g., `let i = 0`).
  - `condition`: Boolean expression evaluated before each iteration.
  - `update`: Statement executed after each iteration (e.g., `i++` or `i = i + 1`).
- The loop variable is local to the loop and can be used within the block.
- Only block-style `do {}` is supported (not single statements).

## String Formatting (f-strings)
Pathetic supports f-strings for dynamic string output.
- **Syntax**: `say f"string with {expression}"`
- Expressions within `{}` are evaluated and replaced with their values.
- **Supported Escape Sequences**:
  - `\n`: Newline
  - `\t`: Tab
  - `\r`: Carriage return
  - `\b`: Backspace
  - `\f`: Form feed
  - `\v`: Vertical tab
  - `\"`: Double quote
  - `\'`: Single quote
  - `\\`: Backslash
- **Example**:
  ```
  let name = "Alice"
  let age = 25
  say f"Hello, {name}! You are {age} years old.\n"
  ```
  Output:
  ```
  Hello, Alice! You are 25 years old.
  ```

## Comments
- **Single-line Comments**: Start with `//` and are ignored by the interpreter.
- **Example**:
  ```
  // This is a comment
  let x = 5  // Declare x
  ```

## Examples
### Example 1: Simple Arithmetic and Output
```
let x = 10
let y = 3
say f"Sum: {x + y}\n"
say f"Product: {x * y}\n"
```
Output:
```
Sum: 13
Product: 30
```

### Example 2: Array Input and Loop
```
get(numbers[3])
for i as (let i = 0; i < 3; i++)
do {
  say f"Number {i}: {numbers[i]}\n"
}
```
Input: `1 2 3`
Output:
```
Number 0: 1
Number 1: 2
Number 2: 3
```

### Example 3: Conditional and While Loop
```
let x = 5
while (x > 0)
do {
  if (x > 3)
  then (say "Large\n")
  else (say "Small\n")
  x = x - 1
}
```
Output:
```
Large
Large
Small
Small
Small
```

## Limitations and Notes
- **No Nested Blocks**: If-then-else statements only support single statements in `then` and `else` clauses. Use multiple statements within loops for complex logic.
- **No Array Indexing in Expressions**: Array elements can be accessed in f-strings (e.g., `{numbers[i]}`), but general array indexing in expressions is not explicitly supported.
- **Error Handling**: Syntax errors or evaluation errors are printed to the console, and execution continues with the next statement.
- **No Function Definitions**: The language does not support user-defined functions.
- **Safe Evaluation**: Expressions are evaluated in a restricted environment to prevent unsafe code execution.

This documentation provides a complete overview of the Pathetic language as implemented in the interpreter. For further assistance, refer to the interpreter code or test with example programs.