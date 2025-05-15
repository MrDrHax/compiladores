from lexer import logger
from parser import Node
from globalTypes import TokenType

# pre-load built ins
symbolics = {
    'input': {
        'type': 'INT',
        'status': 'call',
    },
    'output': {
        'type': 'VOID',
        'status': 'call',
    },
}

latestType = None

pending: list[Node] = []

def _iterate(tree: Node):
    global latestType

    results = [_iterate(child) for child in tree._children]

    if tree._final:
        if tree._token[0] == 'R_ID':
            if not tree._token[1] in symbolics.keys():
                if tree._parent._action.name in ['var-declaration', 'fun-declaration']:
                    symbolics[tree._token[1]] = {
                        'type': latestType,
                        'status': tree._parent._action.name,
                    }
                else:
                    pending.append(tree)
            
        elif tree._token[0] == 'VOID':
            latestType = 'VOID'
        elif tree._token[0] == 'INT':
            latestType = 'INT'
        # elif 

def _test_types(tree: Node):
    error = False

    results_pre = [_test_types(child) for child in tree._children]

    results = [r for r in results_pre if r is not None]

    operands = ['relop', 'addop', 'mulop']

    if tree._final:
        if tree._token[0] == 'R_ID':
            return symbolics[tree._token[1]]['type']
        return None
    else:
        if tree._action.name in operands:
            return 'check'
        else:
            if 'check' in results:
                if len([r for r in results if r != 'check']) == 0:
                    return results[0]
                letype = results[0]
                for r in results[1:]:
                    if r != 'check':
                        if letype != r:
                            print('error')
                return letype
            else:
                return None



def tabla(tree: Node):
    logger.info('Creating table')
    _iterate(tree)

    error = False

    for i in pending:
        if not i._token[1] in symbolics.keys():
            error = True
            logger.error(
                f"Error, '{i._token[1]}' not defined at ln {i._token[2][1] + 1}, col {i._token[2][2]}.")

    if error:
        return True

    _test_types(tree)

    logger.debug('id\t| value')
    logger.debug('----\t| ----')
    for k, v in symbolics.items():
        logger.debug(f'{k}\t| {v}')

    logger.info('Table created')

    logger.info('Verifying semantics')


