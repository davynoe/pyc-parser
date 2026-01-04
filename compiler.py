from lexer import build_lexer
from parser import build_parser
from semantic_analyzer import SemanticAnalyzer
from codegen import CodeGenerator
from vm import VM

def compile_and_run(source_code: str, stage: str = 'execute', verbose: bool = False):
    """
    Complete compilation pipeline:
    Source Code -> Lexer -> Parser -> AST -> Semantic Analyzer -> IR -> CodeGen -> Bytecode -> VM
    
    Args:
        source_code: The source code to compile
        stage: Which stage to stop at ('tokens', 'ast', 'ir', 'code', 'execute')
        verbose: Whether to print detailed output
    """
    
    # Stage 1a: Tokenization
    if stage == 'tokens':
        lexer = build_lexer()
        lexer.input(source_code)
        print("=== Tokens ===")
        for tok in lexer:
            print(tok)
        return None
    
    # Stage 1b: Lex and Parse
    if verbose:
        print("=== Stage 1: Lexing and Parsing ===")
    lexer = build_lexer()
    parser = build_parser()
    ast = parser.parse(source_code, lexer=lexer)
    
    if not ast:
        print("ERROR: Failed to parse")
        return None
    
    if verbose or stage == 'ast':
        if stage == 'ast':
            print("=== AST ===")
        print(ast.to_tree())
    
    if stage == 'ast':
        return ast
    
    # Stage 2: Semantic Analysis (generate IR)
    if verbose:
        print("\n=== Stage 2: Semantic Analysis ===")
    analyzer = SemanticAnalyzer()
    ir = analyzer.analyze(ast)
    
    if verbose or stage == 'ir':
        if stage == 'ir' and not verbose:
            print("=== IR ===")
        print(ir)
    
    if stage == 'ir':
        return ir
    
    # Stage 3: Code Generation (IR -> Bytecode)
    if verbose:
        print("\n=== Stage 3: Code Generation ===")
    codegen = CodeGenerator()
    bytecode = codegen.generate(ir)
    
    if verbose or stage == 'code':
        print(bytecode)
    
    if stage == 'code':
        return bytecode
    
    # Stage 4: Virtual Machine Execution
    if verbose:
        print("\n=== Stage 4: Execution ===")
    vm = VM(bytecode)
    result = vm.execute()
    
    if verbose:
        print(f"\nResult: {result}")
    
    return result

if __name__ == '__main__':
    import sys
    
    # Parse command-line arguments
    verbose = '-v' in sys.argv or '--verbose' in sys.argv
    
    # Determine stage
    stage = 'execute'  # Default
    if '-t' in sys.argv or '--tokens' in sys.argv:
        stage = 'tokens'
    elif '-a' in sys.argv or '--ast' in sys.argv:
        stage = 'ast'
    elif '-ir' in sys.argv or '--ir' in sys.argv:
        stage = 'ir'
    elif '-c' in sys.argv or '--code' in sys.argv:
        stage = 'code'
    elif '-e' in sys.argv or '--execute' in sys.argv:
        stage = 'execute'
    
    # Get input file or stdin
    flags = {'-v', '--verbose', '-t', '--tokens', '-a', '--ast', '-ir', '--ir', 
             '-c', '--code', '-e', '--execute'}
    input_file = None
    
    for arg in sys.argv[1:]:
        if arg not in flags:
            input_file = arg
            break
    
    if input_file:
        with open(input_file, 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()
    
    compile_and_run(code, stage=stage, verbose=verbose)
