from globalTypes import RESERVED_WORDS, S_LIST, TokenType, config

import logging
import sys
import re


class LexerData:
    '''
     Used to store the lexer state.
    '''
    def __init__(self):
        self.pos = 0
        self.ln = 0
        self.col = 0

        self.token = ''
        self.line_string = ''
        self.token_last = ''

        self.token_list = []

    def addToken(self, tokenType, tokenValue):
        self.token_list.append((tokenType, tokenValue))
        _printToken(tokenType, tokenValue)


# ANSI escape sequences for colors
RESET = "\033[0m"
COLOR_MAP = {
    logging.DEBUG: "\033[90m",  # Gray
    logging.INFO: "\033[94m",   # Blue
    logging.ERROR: "\033[91m",  # Red
}

# Pretty printing
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        # Remove any prefix formatting by using only the message
        msg = record.getMessage()
        # Retrieve color for current log level if specified
        color = COLOR_MAP.get(record.levelno, "")
        return f"{color}{msg}{RESET}"


# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler with the custom formatter
console_handler = logging.StreamHandler(sys.stdout)
# Set handler level to DEBUG to catch all messages
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(ColoredFormatter())
logger.addHandler(console_handler)

# actual code

def getToken(imprime=True):
    '''
    getToken The default function, actually works kinda different for how it's described

    Args:
        imprime (bool, optional): Should it print the statements?. Defaults to True.
    '''
    if config is None:
        print('Config not set. Please set the config.')
        return

    # make a proper function.

    return _parseToken(imprime, config.programa)


def _printToken(tokenType, tokenString):
    '''
    _printToken Helper function for printing the token

    Args:
        tokenType (str): The type of token 
        tokenString (str): The value
    '''
    logger.debug(f'{tokenType} = {tokenString}')


def getProgramEnumerator(program, data: LexerData):
    '''
    getProgramEnumerator A generator function that helps with pacing and whatnot

    Args:
        program (str): The program string
        data (LexerData): The state of the lexer

    Yields:
        str: The current state
    '''
    for t in program:
        data.pos += 1
        data.col += 1

        yield t


def processSafe(tokens, token, data: LexerData):
    '''
    processSafe Run after making any advancements. Make sure that the file ends if required. 

    Args:
        tokens (generator): The generator
        token (str): The last used token
        data (LexerData): The lexer data

    Returns:
        bool: if safe to return
    '''
    match token:
        case TokenType.EOL.value:
            data.col = 0
            data.ln += 1
            data.line_string = ''
            data.token = ''
            return False
        case TokenType.ENDFILE.value:
            return True

        case _t if token == TokenType.S_END.value:
            data.addToken(TokenType.S_END.name, TokenType.S_END.value)

        case _:
            return False


def _getTokenData(tokens, token, data: LexerData, includeUnsafe=False):
    '''
    _getTokenData iterate untill there is a symbol

    Args:
        tokens (generator): The generator
        token (str): The last used token
        data (LexerData): The lexer data
        includeUnsafe (bool): Should it include unsafe symbols?

    Returns:
        bool: if safe to return
    '''
    data.token = token
    data.line_string = token

    for i in tokens:
        data.token += i
        data.line_string += i

        match i:
            case t if i in TokenType.SAFE_SYMBOLS.value:
                data.token_last = data.token[:-1]
                data.token = ''

                return i
            case t if includeUnsafe and i in TokenType.SYMBOLS.value:
                data.token_last = data.token[:-1]
                data.token = t

                return i
            case _:
                pass


def _getInverseToken(tokens, token, data: LexerData):
    '''
    _getInverseToken _summary_

    Args:
        tokens (_type_): _description_
        token (_type_): _description_
        data (LexerData): _description_

    Returns:
        _type_: _description_
    '''
    data.token = token
    data.line_string = token

    for i in tokens:
        data.token += i
        data.line_string += i

        match i:
            case t if i in TokenType.SAFE_SYMBOLS.value:
                data.token_last = data.token[:-1]
                data.token = ''

                return i
            case t if re.match(TokenType.R_ID.value, i):
                data.token_last = data.token[:-1]
                data.token = t

                return i
            case t if re.match(TokenType.R_NUM.value, i):
                data.token_last = data.token[:-1]
                data.token = t

                return i
            case _:
                pass


def continueUntilSafe(tokens, token, data: LexerData):
    '''
    continueUntilSafe Panic mode!!!!

    Args:
        tokens (generator): The generator
        token (str): The last used token
        data (LexerData): The lexer data

    Returns:
        bool: if safe to return
    '''
    token = _getTokenData(tokens, token, data)

    logger.error(data.line_string)
    logger.error(''.join([' ' for i in range(
        data.col - len(data.token_last) - 1)]) + '^' + ''.join(['~' for i in range(len(data.token_last) - 1)]))

    data.addToken('ERR', data.token_last)

    return processSafe(tokens, token, data)


def getWord(tokens, token, data: LexerData):
    '''
    getWord Get an ID function 

    Args:
        tokens (generator): The generator
        token (str): The last used token
        data (LexerData): The lexer data

    Returns:
        bool: if safe to return
    '''
    token = _getTokenData(tokens, token, data, True)

    for t in RESERVED_WORDS:
        if data.token_last == t.value:
            data.addToken(t.name, data.token_last)

            return processSafe(tokens, token, data)

    if re.fullmatch(TokenType.R_ID.value, data.token_last):
        data.addToken(TokenType.R_ID.name, data.token_last)
    else:
        logger.error(
            f'Error: Expected ID, got: {data.token_last} in line {data.ln} col {data.col} ')
        logger.error(data.line_string)
        logger.error(''.join([' ' for i in range(
            data.col - len(data.token_last) - 1)]) + '^' + ''.join(['~' for i in range(len(data.token_last) - 1)]))

        data.addToken('ERR', data.token_last)

    return processSafe(tokens, token, data)


def getInt(tokens, token, data: LexerData):
    '''
    getInt Get a number function

    Args:
        tokens (generator): The generator
        token (str): The last used token
        data (LexerData): The lexer data

    Returns:
        bool: if safe to return
    '''
    token = _getTokenData(tokens, token, data, True)

    if re.fullmatch(TokenType.R_NUM.value, data.token_last):
        data.addToken(TokenType.R_NUM.name, data.token_last)
    else:
        logger.error(
            f'Error: Expected number, got: {data.token_last} in line {data.ln} col {data.col} ')
        logger.error(data.line_string)
        logger.error(''.join([' ' for i in range(
            data.col - len(data.token_last) - 1)]) + '^' + ''.join(['~' for i in range(len(data.token_last) - 1)]))

        data.addToken('ERR', data.token_last)

    return processSafe(tokens, token, data)


def getSymbol(tokens, token, data: LexerData):
    '''
    getSymbol Get a symbol function

    Args:
        tokens (generator): The generator
        token (str): The last used token
        data (LexerData): The lexer data

    Returns:
        bool: if safe to return
    '''
    token = _getInverseToken(tokens, token, data)

    toProcess = data.token_last

    pairs = []

    while len(toProcess) > 0:
        for s in S_LIST:
            if toProcess[:len(s.value)] == s.value:
                pairs.append((s.name, s.value))
                toProcess = toProcess[len(s.value):]
                break
        else:
            pairs.append(("ERR", toProcess[0]))
            toProcess = toProcess[1:]

            logger.error(
                f'Error: Unexpected symbol, got: {toProcess[0]} in line {data.ln} col {data.col} ')
            logger.error(data.line_string)
            logger.error(''.join([' ' for i in range(
                data.col - len(data.token_last) - 1)]) + '^' + ''.join(['~' for i in range(len(data.token_last) - 1)]))

    for x, y in pairs:
        data.addToken(x, y)

    return processSafe(tokens, token, data)


def matchToken(tokens, t, data: LexerData):
    '''
    matchToken Match a token after running the parser

    Args:
        tokens (generator): The generator
        token (str): The last used token
        data (LexerData): The lexer data

    Returns:
        bool: if safe to return
    '''
    match t:
        case _t if t in TokenType.SAFE_SYMBOLS.value:
            if processSafe(tokens, t, data):
                return

        case _t if t == TokenType.S_END.value:
            data.addToken(TokenType.S_END.name, TokenType.S_END.value)

        case _t if re.match(TokenType.R_ID.value, t):
            if getWord(tokens, t, data):
                return

        case _t if re.match(TokenType.R_NUM.value, t):
            if getInt(tokens, t, data):
                return

        case _t if t in TokenType.SYMBOLS.value:
            if getSymbol(tokens, t, data):
                return

        case _:
            logger.error(
                f'Error, unknown token: {t} in line {data.ln} col {data.col}')
            continueUntilSafe(tokens, t, data)

    if len(data.token) != 0:
        # NOTA: caso raro, se que recursion mala, pero while en python es muy lento, mejor usar algunas recursiones.
        matchToken(tokens, data.token, data)


def _parseToken(print: bool, program: str):
    '''
    _parseToken The main loop function

    Args:
        print (bool): Should it print for debugging?
        program (str): The program to analyse

    Returns:
        LexerData: The parsed data
    '''
    logger.setLevel(logging.DEBUG if print else logging.INFO)

    data = LexerData()

    tokens = getProgramEnumerator(program, data)

    for t in tokens:

        matchToken(tokens, t, data)

    logger.info('Finished lexing!')
    return data
