from lexer import build_lexer
from parser import build_parser
from semantic_analyzer import SemanticAnalyzer
from codegen import CodeGenerator
from vm import VM

def compile_and_run(source_code: str, stage: str = 'execute', verbose: bool = False) -> any:
    """
    Complete compilation pipeline:
    Source Code -> Lexer -> Parser -> AST -> Semantic Analyzer -> IR -> CodeGen -> Bytecode -> VM
    
    Args:
        source_code: The source code to compile
        stage: Which stage to stop at ('tokens', 'ast', 'ir', 'code', 'execute')
        verbose: Whether to print detailed output
    """
    
    # Lexing
    lexer = build_lexer()
    if verbose: print("=== Tokens ===")
    lexer.input(source_code)
    if verbose or stage == 'tokens':
        for tok in lexer: print(tok)
    if stage == 'tokens': return 0
    
    # Parsing
    parser = build_parser()
    if verbose: print("\n=== AST ===")
    ast = parser.parse(source_code, lexer=lexer)
    if not ast:
        print("ERROR: Failed to parse")
        return 1
    if verbose or stage == 'ast':
        print(ast.to_tree())
    if stage == 'ast': return 0
    
    # Semantic Analysis
    analyzer = SemanticAnalyzer()
    if verbose: print("\n=== Semantic Analysis ===")
    ir = analyzer.analyze(ast)
    if verbose or stage == 'ir':
        print(ir)
    if stage == 'ir': return 0
    
    # Code Generation
    codegen = CodeGenerator()
    if verbose: print("\n=== Code Generation ===")
    bytecode = codegen.generate(ir)
    if verbose or stage == 'code':
        print(bytecode)
    if stage == 'code': return 0
    
    # Execution
    vm = VM(bytecode)
    if verbose: print("\n=== Execution ===")
    result = vm.execute()
    return 0

if __name__ == '__main__':
    import sys

    # Determine verbosity
    verbose = False # Default
    if '-v' in sys.argv or '--verbose' in sys.argv:
        verbose = True
        
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
    flags = {'-t', '--tokens', '-a', '--ast', '-ir', '--ir', 
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