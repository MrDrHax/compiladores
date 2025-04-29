from enum import Enum


class TokenType(Enum):
    ENDFILE = '$'
    EOL = '\n'

    SYMBOLS = '+-*/<>!;,()[]{}='
    SAFE_SYMBOLS = '\n;, $'

    S_PLUS = '+'
    S_MIN = '-'
    S_TIMES = '*'
    S_DIV = '/'
    S_LESS = '<'
    S_LESSEQ = '<='
    S_MORE = '>'
    S_MOREEQ = '>='
    S_EQ = '=='
    S_NEQ = '!='
    S_SET = '='
    S_END = ';'
    S_COMMA = ','
    S_LP = '('
    S_RP = ')'
    S_LB = '['
    S_RB = ']'
    S_LS = '{'
    S_RS = '}'
    S_LComment = '/*'
    S_RComment = '*/'

    

    SPACE = ' '

    R_ID = r'[a-zA-Z]+'
    R_NUM = r'[0-9]+'

    ELSE = 'else'
    IF = 'if'
    INT = 'int'
    RETURN = 'return'
    VOID = 'void'
    WHILE = 'while'

RESERVED_WORDS = [
    TokenType.ELSE,
    TokenType.IF,
    TokenType.INT,
    TokenType.RETURN,
    TokenType.VOID,
    TokenType.WHILE,
]

S_LIST = [
    # long
    TokenType.S_EQ,
    TokenType.S_NEQ,
    TokenType.S_LESSEQ,
    TokenType.S_MOREEQ,

    TokenType.S_LComment,
    TokenType.S_RComment,

    # math
    TokenType.S_PLUS,
    TokenType.S_MIN,
    TokenType.S_TIMES,
    TokenType.S_DIV,

    # comp
    TokenType.S_LESS,
    TokenType.S_MORE,

    # lang
    TokenType.S_SET,
    TokenType.S_END,
    TokenType.S_COMMA,

    # separation
    TokenType.S_LP,
    TokenType.S_RP,
    TokenType.S_LB,
    TokenType.S_RB,
    TokenType.S_LS,
    TokenType.S_RS,
]

RESERVED_WORDS.sort(key= lambda s: len(s.value), reverse=True)

class Config:
    def __init__(self, prog=None, pos=None, long=None):
        self.programa = prog
        self.posicion = pos
        self.progLong = long


config = Config()


def globales(prog, pos, long):
    config.programa = prog
    config.posicion = pos
    config.progLong = long
