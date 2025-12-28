# Python with C Syntax - Compiler Pipeline

A complete compiler implementation for a custom language combining Python semantics with C-style syntax.

## Architecture

The compiler follows a classic multi-stage pipeline:

```
Source Code
    ↓
[Lexer] → Tokens
    ↓
[Parser] → AST (Abstract Syntax Tree)
    ↓
[Semantic Analyzer] → IR (Intermediate Representation)
    ↓
[Code Generator] → Bytecode
    ↓
[Virtual Machine] → Execution
```

## Components

### 1. **Lexer** (`lexer.py`)
- Tokenizes source code using PLY (Python Lex-Yacc)
- Supports: identifiers, numbers, strings, operators, keywords, comments
- Handles both floats and integers

### 2. **Parser** (`parser.py`)
- Builds Abstract Syntax Tree from tokens using PLY's yacc
- Grammar rules for statements, expressions, control flow
- Operators with proper precedence and associativity
- Supports: functions, loops, conditionals, arithmetic, logic, print

### 3. **AST** (`ast.py`)
- Node classes representing language constructs
- `to_sexpr()` method for S-expression representation
- Node types: Program, statements (Assign, If, While, For, FuncDef, Return), expressions (Binary, Unary, Call, Literal, Var, ListLiteral)

### 4. **Semantic Analyzer** (`semantic_analyzer.py`)
- Traverses AST and generates IR (Intermediate Representation)
- Manages symbol tables with scoping
- Basic type tracking
- Converts high-level constructs to lower-level IR instructions
- Handles label generation for control flow

### 5. **Code Generator** (`codegen.py`)
- Converts IR to stack-based bytecode
- Maintains constant pool and name table
- Two-pass generation: resource collection, then code emission
- Opcode definitions for all operations

### 6. **Virtual Machine** (`vm.py`)
- Stack-based execution engine
- Executes bytecode instructions
- Maintains variable storage and call stack
- Supports arithmetic, logical, comparison, and control flow operations
- Print statement support

### 7. **Main Compiler** (`compiler.py`)
- Entry point orchestrating the pipeline
- `compile_and_run(source_code, verbose=False)` function
- Optional verbose output showing each stage
- Handles file input or stdin

## Usage

### Basic execution:
```bash
python compiler.py script.pc
```

### Verbose output (shows AST, IR, Bytecode, etc.):
```bash
python compiler.py script.pc -v
```

### From stdin:
```bash
echo "x = 5; print(x);" | python compiler.py
```

## Language Features

### Data Types
- Integers
- Floats  
- Strings (single or double quoted)
- Booleans (True, False)
- None
- Lists

### Operators
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `and`, `or`, `not`
- Unary: `-`, `+`, `not`

### Statements
- Variable assignment: `x = 5;`
- If/else: `if (x > 5) { ... } else { ... }`
- While loops: `while (x > 0) { ... }`
- For loops: `for (i in range) { ... }`
- Function definition: `def func(a, b) { ... }`
- Return: `return value;`
- Print: `print(x, y, z);`
- Pass: `pass;`

### C-like Syntax
- Semicolons terminate statements
- Curly braces for blocks
- Parentheses for function calls and conditions

## Example Program

```c
x = 10;
y = 3;

if (x > y) {
    print(x);
} else {
    print(y);
}

i = 0;
while (i < 5) {
    print(i);
    i = i + 1;
}
```

## IR Instructions

Core IR operations:
- `LOAD_CONST` - Push constant
- `LOAD` - Load variable
- `STORE` - Store variable
- `ADD`, `SUB`, `MUL`, `DIV`, `MOD` - Arithmetic
- `EQ`, `NEQ`, `LT`, `GT`, `LE`, `GE` - Comparison
- `AND`, `OR`, `NOT` - Logical
- `JUMP`, `JUMP_IF_FALSE` - Control flow
- `PRINT` - Output
- `CALL_FUNCTION` - Function call
- `RETURN_VALUE` - Return from function

## Bytecode

Uses numeric opcodes for compact representation:
- 1 byte opcode
- Variable arguments (stored as following bytes)
- Constants indexed by position
- Variable names indexed by position

## Testing

Run individual test files:
```bash
python compiler.py tests/valid_arithmetic.pc
python compiler.py tests/valid_if.pc
python compiler.py tests/valid_while.pc
```

## Limitations & Future Enhancements

Current limitations:
- No type checking
- Limited error recovery
- No optimization passes
- Simple list support

Possible enhancements:
- Type inference and checking
- Better error messages with line numbers
- Function parameter binding
- For loop iteration over lists
- Nested function scopes
- Bytecode optimization
- Debugging symbols
- Exception handling
