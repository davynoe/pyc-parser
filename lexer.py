import ply.lex as lex

# List of token names
tokens = (
    'IDENT',
    'INT',
    'FLOAT',
    'STRING',
    # Operators
    'PLUS','MINUS','TIMES','DIVIDE','MOD',
    'EQ','NEQ','LT','GT','LE','GE',
    'ASSIGN',
    'LPAREN','RPAREN',
    'LBRACE','RBRACE','LBRACKET','RBRACKET',
    'COMMA','SEMICOLON',
    'COLON',
)

# Reserved keywords
reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'in': 'IN',
    'def': 'DEF',
    'return': 'RETURN',
    'pass': 'PASS',
    'True': 'TRUE',
    'False': 'FALSE',
    'None': 'NONE',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'print': 'PRINT',
}

tokens = tokens + tuple(reserved.values())

# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_MOD     = r'%'
t_EQ      = r'=='
t_NEQ     = r'!='
t_LE      = r'<='
t_GE      = r'>='
t_LT      = r'<'
t_GT      = r'>'
t_ASSIGN  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACE  = r'\{'
t_RBRACE  = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA   = r','
t_SEMICOLON = r';'
t_COLON = r':'

t_ignore = ' \t'

# Comments
def t_COMMENT(t):
    r'\#.*'
    pass

def t_FLOAT(t):
    r'([0-9]*\.[0-9]+)|([0-9]+\.[0-9]*)'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"|\'([^\\\n]|(\\.))*?\''
    # strip quotes
    s = t.value[1:-1]
    t.value = s
    return t

def t_IDENT(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, 'IDENT')  # Check for reserved words
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

def build_lexer(**kwargs):
    return lex.lex(**kwargs)

if __name__ == '__main__':
    data = '''
    # quick test
    def add(a, b) {
        return a + b;
    }
    x = add(1, 2);
    print(x);
    '''
    lexer = build_lexer()
    lexer.input(data)
    for tok in lexer:
        print(tok)
