from lexer import build_lexer
from parser import build_parser

def parse_string(s):
    lexer = build_lexer()
    parser = build_parser()
    ast = parser.parse(s, lexer=lexer)
    return ast

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        with open(fname, 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()
    ast = parse_string(code)
    if ast:
        print(ast.to_sexpr())
