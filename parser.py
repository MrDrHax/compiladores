from lexer import getToken, logger

from globalTypes import TokenType

consecutive = 0

# (tokenType, tokenValue, (self.pos, self.ln, self.col, self.token_last))

latestError = None

treeStart = None


class Node:
    _id: int
    _children: list['Node']
    _parent: 'Node'
    _depth: int

    _token: str

    _action: 'State'

    _final: bool

    def __init__(self, id: int, parent: 'Node', depth: int, action: 'State', final=False):
        self._id = id
        self._parent = parent

        self._depth = depth
        self._action = action

        self._children = []

        self._token = None

        self._final = final

    def addChild(self, id: int, action: 'State') -> 'Node':
        child = Node(id, self, self._depth + 1, action)
        self._children.append(child)

        return child

    def addFinalChild(self, id: int, token) -> 'Node':
        child = Node(id, self, self._depth + 1, None, final=True)
        child._token = token
        self._children.append(child)

        return child

    def print(self, withChild=False):
        if self._final:
            logger.debug(
                f'{'|'.join(['' for _ in range(self._depth+1)])}> ~ {self._token}')
        else:
            logger.debug(
                f'{'|'.join(['' for _ in range(self._depth+1)])}> {self._action.name} {self._token}')

        if withChild:
            for ch in self._children:
                ch.print(withChild)

    def iterate(self, tokens: list):
        global latestError
        works = False
        tokenCount = 0

        if len(tokens) == 0:
            return True, 0

        self._token = tokens[0]

        self.print()

        if len(tokens) == 0 and self._action.possibles != [[]]:
            return False, 0

        for action_sequence in self._action.possibles:
            current_token_index = 0
            children = []
            success = True

            try:
                for element in action_sequence:
                    if isinstance(element, State):
                        # Add a child node and recursively iterate on remaining tokens
                        child = self.addChild(
                            self._id + len(self._children) + 1,
                            element,
                        )
                        result, count = child.iterate(
                            tokens[tokenCount + current_token_index:],
                        )

                        if result:
                            current_token_index += count
                            children.append(child)
                        else:
                            success = False
                            break

                    elif isinstance(element, TokenType):
                        if tokenCount + current_token_index >= len(tokens):
                            success = False
                            break

                        current_token_type = tokens[tokenCount +
                                                    current_token_index][0]

                        if current_token_type == element.name:
                            self.addFinalChild(1, tokens[tokenCount +
                                                         current_token_index])
                            current_token_index += 1
                        else:
                            success = False
                            break

                    else:
                        success = False
                        break
            except Exception as e:
                success = False
                print(f'not accounted for error {e.with_traceback(None)}')

            if success:
                self._token = tokens[tokenCount + current_token_index - 1]
                tokenCount += current_token_index
                works = True
                latestError = None
                break
            else:
                # Remove any children added in this loop iteration
                self._children = []
                if not latestError:
                    latestError = tokens[tokenCount]

        return works, tokenCount


class State:
    possibles: list[list['State', TokenType]]
    name: str

    def __init__(self, name, ):
        self.name = name
        self.possibles = []

    def addPossibility(self, other: list['State', TokenType]):
        self.possibles.append(other)

    def clone(self) -> 'State':
        state = State(self.name)
        state.possibles = [s for s in self.possibles]

        return state


actions = {
    "program": State("program"),
    "declaration-list": State("declaration-list"),
    "declaration": State("declaration"),
    "var-declaration": State("var-declaration"),
    "type-specifier": State("type-specifier"),
    "fun-declaration": State("fun-declaration"),
    "params": State("params"),
    "param-list": State("param-list"),
    "param": State("param"),
    "compound-stmt": State("compound-stmt"),
    "local-declarations": State("local-declarations"),
    "statement-list": State("statement-list"),
    "statement": State("statement"),
    "expression-stmt": State("expression-stmt"),
    "selection-stmt": State("selection-stmt"),
    "iteration-stmt": State("iteration-stmt"),
    "return-stmt": State("return-stmt"),
    "expression": State("expression"),
    "var": State("var"),
    "simple-expression": State("simple-expression"),
    "relop": State("relop"),
    "additive-expression": State("additive-expression"),
    "additive-expression*": State("additive-expression*"),
    "addop": State("addop"),
    "term": State("term"),
    "term*": State("term*"),
    "mulop": State("mulop"),
    "factor": State("factor"),
    "call": State("call"),
    "args": State("args"),
    "arg-list": State("arg-list"),
    "arg-list*": State("arg-list*"),

}

# program
actions['program'].addPossibility([actions['declaration-list']])

# declaration-list
actions['declaration-list'].addPossibility(
    [actions['declaration'], actions["declaration-list"]])
actions['declaration-list'].addPossibility([actions['declaration']])

# declaration
actions['declaration'].addPossibility([actions['var-declaration']])
actions['declaration'].addPossibility([actions['fun-declaration']])

# var-declaration
actions['var-declaration'].addPossibility(
    [actions["type-specifier"], TokenType.R_ID, TokenType.S_END])
actions['var-declaration'].addPossibility(
    [actions["type-specifier"], TokenType.R_ID, TokenType.S_LB, TokenType.R_NUM, TokenType.S_RB, TokenType.S_END])

# type-specifier
actions['type-specifier'].addPossibility([TokenType.INT])
actions['type-specifier'].addPossibility([TokenType.VOID])

# fun-declaration
actions['fun-declaration'].addPossibility([actions["type-specifier"], TokenType.R_ID,
                                          TokenType.S_LP, actions['params'], TokenType.S_RP, actions["compound-stmt"]])

# params
actions['params'].addPossibility([actions["param"]])
actions['params'].addPossibility([TokenType.VOID])

# param-list
actions['param-list'].addPossibility([actions["param-list"],
                                     TokenType.S_COMMA, actions["param"]])
actions['param-list'].addPossibility([actions["param"]])

# param
actions['param'].addPossibility([actions["type-specifier"], TokenType.R_ID])
actions['param'].addPossibility(
    [actions["type-specifier"], TokenType.R_ID, TokenType.S_LB, TokenType.S_RB])

# compound-stmt
actions['compound-stmt'].addPossibility(
    [TokenType.S_LS, actions["local-declarations"], actions['statement-list'], TokenType.S_RS])

# local-declarations
actions['local-declarations'].addPossibility(
    [actions["var-declaration"], actions["local-declarations"]])
actions['local-declarations'].addPossibility([])

# statement-list
actions['statement-list'].addPossibility(
    [actions["statement"], actions["statement-list"]])
actions['statement-list'].addPossibility([])

# statement
actions['statement'].addPossibility([actions["expression-stmt"]])
actions['statement'].addPossibility([actions["compound-stmt"]])
actions['statement'].addPossibility([actions["selection-stmt"]])
actions['statement'].addPossibility([actions["iteration-stmt"]])
actions['statement'].addPossibility([actions["return-stmt"]])

# expression-stmt
actions['expression-stmt'].addPossibility(
    [actions["expression"], TokenType.S_END])

# selection-stmt
actions['selection-stmt'].addPossibility([TokenType.IF, TokenType.S_LP,
                                         actions["expression"], TokenType.S_RP, actions["statement"]])
actions['selection-stmt'].addPossibility([TokenType.IF, TokenType.S_LP,
                                         actions["expression"], TokenType.S_RP, actions["statement"], TokenType.ELSE, actions["statement"]])

# iteration-stmt
actions['iteration-stmt'].addPossibility([TokenType.WHILE, TokenType.S_LP,
                                         actions["expression"], TokenType.S_RP, actions["statement"]])

# return-stmt
actions['return-stmt'].addPossibility([TokenType.RETURN, TokenType.S_END])
actions['return-stmt'].addPossibility([TokenType.RETURN,
                                      actions["expression"], TokenType.S_END])

# expression
actions['expression'].addPossibility(
    [actions["var"], TokenType.S_SET, actions["expression"]])
actions['expression'].addPossibility([actions["simple-expression"]])

# var
actions['var'].addPossibility(
    [TokenType.R_ID, TokenType.S_LB, actions["expression"], TokenType.S_RB])
actions['var'].addPossibility([TokenType.R_ID])

# simple-expression
actions['simple-expression'].addPossibility(
    [actions["additive-expression"], actions["relop"], actions['additive-expression']])
actions['simple-expression'].addPossibility([actions["additive-expression"]])

# relop
actions['relop'].addPossibility([TokenType.S_LESSEQ])
actions['relop'].addPossibility([TokenType.S_LESS])
actions['relop'].addPossibility([TokenType.S_MORE])
actions['relop'].addPossibility([TokenType.S_MORE])
actions['relop'].addPossibility([TokenType.S_EQ])
actions['relop'].addPossibility([TokenType.S_NEQ])

# additive-expression
actions['additive-expression'].addPossibility(
    [actions["term"], actions["additive-expression*"]])

actions['additive-expression*'].addPossibility(
    [actions["addop"], actions["term"], actions['additive-expression*']])
actions['additive-expression*'].addPossibility([])

# addop
actions['addop'].addPossibility([TokenType.S_PLUS])
actions['addop'].addPossibility([TokenType.S_MIN])

# term
actions['term'].addPossibility([actions["factor"], actions['term*']])

actions['term*'].addPossibility(
    [actions["mulop"], actions["factor"], actions["term*"]])
actions['term*'].addPossibility([])
# mulop
actions['mulop'].addPossibility([TokenType.S_TIMES])
actions['mulop'].addPossibility([TokenType.S_DIV])

# factor
actions['factor'].addPossibility(
    [TokenType.S_LP, actions["expression"], TokenType.S_RP])
actions['factor'].addPossibility([actions["call"]])
actions['factor'].addPossibility([actions["var"]])
actions['factor'].addPossibility([TokenType.R_NUM])

# call
actions['call'].addPossibility(
    [TokenType.R_ID, TokenType.S_LP, actions["args"], TokenType.S_RP])

# args
actions['args'].addPossibility([actions["arg-list"]])
actions['args'].addPossibility([])

# arg-list
actions['arg-list'].addPossibility([
                                    actions["expression"], actions["arg-list*"]])

# TODO error here...
actions['arg-list*'].addPossibility([
                                    TokenType.S_COMMA, actions["expression"], actions["arg-list*"]])
actions['arg-list*'].addPossibility([])



def noneAction(**kwargs):
    pass


def parser(imprime=True):
    global treeStart

    logger.info("Tokenizing")

    tokens = getToken(imprime)

    logger.info("Creating AST")

    treeStart = Node(-1, None, 0, actions['program'])

    treeStart.iterate(tokens.token_list)

    logger.info("Finished AST")

    if len(treeStart._children) == 0:
        logger.error(
            f"Failed to create AST, Expected '{latestError[1]}' at ln {latestError[2][1] + 1}, col {latestError[2][2]}.")

    treeStart.print(True)

    logger.info('Created AST')

    return treeStart
