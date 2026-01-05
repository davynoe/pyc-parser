# parser.py
import ply.yacc as yacc
from lexer import tokens, build_lexer
import astmod

# Precedence rules to handle ambiguity
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('left', 'EQ','NEQ'),
    ('left', 'LT','LE','GT','GE'),
    ('left', 'PLUS','MINUS'),
    ('left', 'TIMES','DIVIDE','MOD'),
    ('right', 'UMINUS','UPLUS'),
)

def p_program(p):
    "program : stmt_list"
    p[0] = astmod.Program(p[1])

def p_stmt_list_empty(p):
    "stmt_list : "
    p[0] = []

def p_stmt_list(p):
    "stmt_list : stmt_list statement"
    p[0] = p[1] + [p[2]]

def p_statement_simple(p):
    "statement : simple_stmt SEMICOLON"
    p[0] = p[1]

def p_statement_block(p):
    "statement : block_stmt"
    p[0] = p[1]

def p_simple_stmt_expr(p):
    "simple_stmt : expression"
    p[0] = astmod.ExprStmt(p[1])

def p_simple_stmt_assign(p):
    "simple_stmt : IDENT ASSIGN expression"
    p[0] = astmod.Assign(p[1], p[3])

def p_simple_stmt_return(p):
    "simple_stmt : RETURN expression"
    p[0] = astmod.Return(p[2])

def p_simple_stmt_return_none(p):
    "simple_stmt : RETURN"
    p[0] = astmod.Return(None)

def p_simple_stmt_pass(p):
    "simple_stmt : PASS"
    p[0] = astmod.Pass()

def p_simple_stmt_print(p):
    "simple_stmt : PRINT LPAREN arg_list_opt RPAREN"
    p[0] = astmod.Print(p[3])

def p_block_stmt_if(p):
    "block_stmt : IF LPAREN expression RPAREN block"
    p[0] = astmod.If(p[3], p[5], None)

def p_block_stmt_if_else(p):
    "block_stmt : IF LPAREN expression RPAREN block ELSE block"
    p[0] = astmod.If(p[3], p[5], p[7])

def p_block_stmt_while(p):
    "block_stmt : WHILE LPAREN expression RPAREN block"
    p[0] = astmod.While(p[3], p[5])

def p_block_stmt_for(p):
    "block_stmt : FOR LPAREN IDENT IN expression RPAREN block"
    p[0] = astmod.For(p[3], p[5], p[7])

def p_block_stmt_def(p):
    "block_stmt : DEF IDENT LPAREN param_list_opt RPAREN block"
    p[0] = astmod.FuncDef(p[2], p[4], p[6])

def p_param_list_opt_empty(p):
    "param_list_opt : "
    p[0] = []

def p_param_list_opt(p):
    "param_list_opt : param_list"
    p[0] = p[1]

def p_param_list(p):
    "param_list : IDENT"
    p[0] = [p[1]]

def p_param_list_multi(p):
    "param_list : param_list COMMA IDENT"
    p[0] = p[1] + [p[3]]

def p_block(p):
    "block : LBRACE stmt_list RBRACE"
    p[0] = astmod.Block(p[2])

# Expressions
def p_expression(p):
    "expression : or_expr"
    p[0] = p[1]

def p_or(p):
    "or_expr : or_expr OR and_expr"
    p[0] = astmod.Binary('or', p[1], p[3])

def p_or_single(p):
    "or_expr : and_expr"
    p[0] = p[1]

def p_and(p):
    "and_expr : and_expr AND not_expr"
    p[0] = astmod.Binary('and', p[1], p[3])

def p_and_single(p):
    "and_expr : not_expr"
    p[0] = p[1]

def p_not(p):
    "not_expr : NOT not_expr"
    p[0] = astmod.Unary('not', p[2])

def p_not_single(p):
    "not_expr : comparison"
    p[0] = p[1]

def p_comparison_binop(p):
    """comparison : arith_expr EQ arith_expr
                  | arith_expr NEQ arith_expr
                  | arith_expr LT arith_expr
                  | arith_expr GT arith_expr
                  | arith_expr LE arith_expr
                  | arith_expr GE arith_expr"""
    p[0] = astmod.Binary(p[2], p[1], p[3])

def p_comparison_single(p):
    "comparison : arith_expr"
    p[0] = p[1]

def p_arith_plusminus(p):
    """arith_expr : arith_expr PLUS term
                  | arith_expr MINUS term"""
    p[0] = astmod.Binary(p[2], p[1], p[3])

def p_arith_term(p):
    "arith_expr : term"
    p[0] = p[1]

def p_term_times(p):
    """term : term TIMES factor
            | term DIVIDE factor
            | term MOD factor"""
    p[0] = astmod.Binary(p[2], p[1], p[3])

def p_term_factor(p):
    "term : factor"
    p[0] = p[1]

def p_factor_unary(p):
    """factor : PLUS factor %prec UPLUS
              | MINUS factor %prec UMINUS"""
    p[0] = astmod.Unary(p[1], p[2])

def p_factor_atom(p):
    "factor : atom"
    p[0] = p[1]

def p_atom_group(p):
    "atom : LPAREN expression RPAREN"
    p[0] = p[2]

def p_atom_literal_int(p):
    "atom : INT"
    p[0] = astmod.Literal(p[1])

def p_atom_literal_float(p):
    "atom : FLOAT"
    p[0] = astmod.Literal(p[1])

def p_atom_literal_string(p):
    "atom : STRING"
    p[0] = astmod.Literal(p[1])

def p_atom_true(p):
    "atom : TRUE"
    p[0] = astmod.Literal(True)

def p_atom_false(p):
    "atom : FALSE"
    p[0] = astmod.Literal(False)

def p_atom_none(p):
    "atom : NONE"
    p[0] = astmod.Literal(None)

def p_atom_var(p):
    "atom : IDENT"
    p[0] = astmod.Var(p[1])

def p_atom_call(p):
    "atom : IDENT LPAREN arg_list_opt RPAREN"
    func = astmod.Var(p[1])
    p[0] = astmod.Call(func, p[3])

def p_arg_list_opt_empty(p):
    "arg_list_opt : "
    p[0] = []

def p_arg_list_opt(p):
    "arg_list_opt : arg_list"
    p[0] = p[1]

def p_arg_list_single(p):
    "arg_list : expression"
    p[0] = [p[1]]

def p_arg_list_multi(p):
    "arg_list : arg_list COMMA expression"
    p[0] = p[1] + [p[3]]

def p_list_literal(p):
    "atom : LBRACKET arg_list_opt RBRACKET"
    p[0] = astmod.ListLiteral(p[2] if p[2] else [])

def p_error(p):
    if p:
        print(f"Syntax error at token {p.type} ({p.value!r}) line {p.lineno}")
    else:
        print("Syntax error at EOF")

def build_parser(**kwargs):
    return yacc.yacc(**kwargs)

if __name__ == '__main__':
    lexer = build_lexer()
    parser = build_parser()
    data = '''
    def add(a, b) {
        return a + b;
    }
    x = add(10, 20);
    if (x > 20) { print(x); } else { print(0); }
    '''
    result = parser.parse(data, lexer=lexer)
    print(result.to_sexpr())
