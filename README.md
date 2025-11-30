# Pyc Parser

## Overview

This project implements a parser for **Pyc**.<br> Python-like syntax + C-like structural elements.

In the previous homework assignment, I was working on lexing normal Python code.<br>
However, for this assignment, I've changed things up by creating a modified language that uses braces and semicolons instead of Python's indentation-based syntax.

## Language Description

Pyc is a statically-structured language that uses Python keywords but with explicit block delimiters (braces) and statement terminators (semicolons). The language is designed to be similar to Python in terms of keywords and operators, but with a syntax that's more similar to C or JavaScript.

## Differences from Python

The main differences between Pyc and standard Python are defined by the syntax rules:

**Semicolons (`;`)** after simple statements - Python: No semicolons needed, Pyc: `x = 10;` (semicolon required)

**Braces (`{}`)** for blocks - Python: Uses indentation for blocks, Pyc: `if (x > 5) { print(x); }` (braces required)

**Parentheses (`()`)** for:

- Function definitions: `def name(params)` (same as Python)
- Function calls: `name(args)` (same as Python)
- If/while conditions: `if (condition)` (Python doesn't require parentheses)
- For loop: `for (var in iterable)` (Python uses `for var in iterable`)
- Grouping expressions: `(a + b)` (same as Python)

**Commas (`,`)** for:

- Function parameters: `def f(a, b, c)` (same as Python)
- Function arguments: `f(1, 2, 3)` (same as Python)
- List elements: `[1, 2, 3]` (same as Python)

## Features

- Function definitions with parameters
- Variable assignments
- Arithmetic operations (+, -, \*, /, %)
- Comparison operators (==, !=, <, >, <=, >=)
- Logical operators (and, or, not)
- Control flow (if/else, while, for loops)
- Function calls
- List literals
- String, integer, float, boolean, and None literals
- Comments (single-line with `#`)

## Installation

### Prerequisites

- Python 3.x
- pip (Python package manager)

### Install PLY

PLY (Python Lex-Yacc) is required for the parser. Install it using pip:

```bash
pip install ply
```

Or if you're using a virtual environment:

```bash
# Create virtual environment (optional)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate

# Install PLY
pip install ply
```

## Usage

### Running the Parser

To parse a Pyc file, use the `run_parser.py` script with a file from the `tests/` directory:

```bash
python run_parser.py tests/valid1.pc
```

### Example

```bash
# Parse a valid file
python run_parser.py tests/valid1.pc

# Parse another test file
python run_parser.py tests/valid_if.pc

# Parse an invalid file (will show syntax errors)
python run_parser.py tests/invalid_missing_semicolon.pc
```

### Output

The parser outputs an Abstract Syntax Tree (AST) in S-expression format. For example:

**Input** (`tests/valid1.pc`):

```python
def add(a, b) {
  return a + b;
}
x = add(1, 2);
print(x);
```

**Output**:

```
(program (def add (a b) (block (return (+ a b)))) (assign x (call add 1 2)) (print x))
```

## Test Files

The `tests/` directory contains various test cases:

- **Valid tests**: Files starting with `valid_` contain syntactically correct Pyc code
- **Invalid tests**: Files starting with `invalid_` contain syntax errors for testing error handling

## Project Structure

```
minipython/
├── lexer.py          # Lexical analyzer (tokenizer)
├── parser.py         # Syntax analyzer (parser)
├── ast.py            # Abstract Syntax Tree node definitions
├── run_parser.py     # Main script to run the parser
├── parsetab.py       # Auto-generated parsing tables (by PLY)
├── README.md         # This file
└── tests/            # Test files directory
    ├── valid_*.pc    # Valid Pyc programs
    └── invalid_*.pc  # Invalid programs for error testing
```

## Example Pyc Code

```python
# Function definition
def add(a, b) {
    return a + b;
}

# Variables and assignment
x = 10;
y = 20;
result = add(x, y);

# Conditional statement
if (result > 15) {
    print("Big result");
} else {
    print("Small result");
}

# While loop
i = 0;
while (i < 5) {
    print(i);
    i = i + 1;
}

# For loop
for (num in [1, 2, 3, 4, 5]) {
    print(num);
}
```
