# $ git tag -a v0.1.1 -m "Mensagem sobre o release"
# $ git push origin v0.1.1
#!/usr/bin/env python
# -- coding: utf-8 --
import sys
import re
from rply import LexerGenerator
from rply.token import BaseBox
from rply import ParserGenerator

lg = LexerGenerator()

# comentarios
lg.ignore(r"//.*?//")
# Print
lg.add('PRINT', r'println')
# Parenthesis and Braces
lg.add('OPEN_PAREN', r'\(')
lg.add('CLOSE_PAREN', r'\)')
lg.add('OPEN_BRACES', r'\{')
lg.add('CLOSE_BRACES', r'\}')
# Semi Colon
lg.add('SEMI_COLON', r'\;')
lg.add('COMMA', r'\,')
# function
lg.add('FUNCTION', r'def')
lg.add('RETURN', r'return')
# type
lg.add('TYPE', 'int')
lg.add('TYPE', 'bool')
# Operators
# lg.add('PLUS_ONE', r'\++')`
lg.add('EQUAL_EQUAL', r'\=\=')
lg.add('PLUS_EQUAL', r'\+\=')
lg.add('MINUS_EQUAL', r'\-\=')
# If-else
lg.add("ELSE", r'else')
lg.add("IF", r'if')

lg.add('AND', r'\&\&')
lg.add('OR', r'\|\|')
lg.add('EQUAL', r'\=')
lg.add('SUM', r'\+')
lg.add('NOT', r'not')
lg.add('SUB', r'\-')

lg.add('MUL', r'\*')
lg.add('DIV', r'/')
lg.add('REST', r'\%')
# Logical Operators
lg.add("GREATER", r'\>')
lg.add("LESS", r'\<')
# Types
lg.add('INT', r'int')
lg.add('DOUBLE', r'doble')
# Statement
lg.add("WHILE", r'while')
lg.add("FOR", r'for')

# Identifier
# IDENTIFIER = LETTER, { LETTER | DIGIT | "_" } ;
lg.add("IDENTIFIER", r'[a-zA-Z]*([a-zA-Z]|/d+|_)')
# Number
lg.add('NUMBER', r'\d+')

lg.ignore('\s+')
lg.ignore("/\*.*?\*/")
lexer = lg.build()
class SymbolTable:

    st_function = {}

    def __init__(self):
        self.a = {}

    def getter(self, value):
        return self.a[value]

    def setter_valor(self, value, number):
        self.a[value][0] = number

    def setter(self, value, v_type):
        if value in self.a:
            raise ValueError
        self.a[value] = [None, v_type]

    def setter_func(self, nome, func_name, func_type, params_name):
        if nome in self.st_function:
            raise ValueError("Already in the dictionary")

        self.st_function[nome] = [func_name, func_type, params_name]

    # pegar a função
    def getter_func(self, nome):

        return self.st_function[nome]

    def set_return(self, return_f, valor):
        self.st_function[return_f] = valor



st = SymbolTable()


class Number():
    def __init__(self, value):
        self.value = value

    def eval(self, st):
        return [int(self.value), "int"]


class BinaryOp():
    def __init__(self, left, right):
        self.left = left
        self.right = right


class Block():
    def __init__(self, children):
        self.children = children

    def eval(self, st):
        for node in self.children:
            if "return" in st.st_function:
                break
            node.eval(st)


class Setter(BinaryOp):
    def __init__(self, left, right, v_type):
        self.left = left
        self.right = right
        self.v_type = v_type

    def eval(self, st):

        if self.v_type in ["int", "bool"]:
            return st.setter(self.left, self.v_type)

        elif self.v_type == "vuelve":
            return st.set_return(self.left, self.right.eval(st))
        else:

            s = st.getter(self.left)
            if s[1] == "bool":
                return st.setter_valor(
                    self.left, int(bool(self.right.eval(st)[0]))
                )
            else:
                st.setter_valor(self.left, self.right.eval(st)[0])


class Getter(BinaryOp):
    def __init__(self, value):
        self.value = value

    def eval(self, st):
        return st.getter(self.value)


class PlusOne(BinaryOp):
    def eval(self, st):
        return int(self.left.eval(st) + 1)


class PlusEqual(BinaryOp):
    def eval(self, st):
        c = self.left.eval(st)
        c += self.right.eval(st)
        return c


class MinusEqual(BinaryOp):
    def eval(self, st):
        c = self.left.eval(st)
        c -= self.right.eval(st)
        return c


class Greater(BinaryOp):
    def eval(self, st):
        return int(self.left.eval(st) > self.right.eval(st))


class Equal_Equal(BinaryOp):
    def eval(self, st):
        return int(self.left.eval(st) == self.right.eval(st))


class Less(BinaryOp):
    def eval(self, st):
        return int(self.left.eval(st) < self.right.eval(st))


class Or(BinaryOp):
    def eval(self, st):
        return int(self.left.eval(st) or self.right.eval(st))


class And(BinaryOp):
    def eval(self, st):
        return int(self.left.eval(st) and self.right.eval(st))


class Sum(BinaryOp):
    def eval(self, st):
        return self.left.eval(st) + self.right.eval(st)


class Sub(BinaryOp):
    def eval(self, st):
        return self.left.eval(st) - self.right.eval(st)


class Mul(BinaryOp):
    def eval(self, st):
        return int(self.left.eval(st) * self.right.eval(st))


class Div(BinaryOp):
    def eval(self, st):
        return int(self.left.eval(st) / self.right.eval(st))


class Rest(BinaryOp):
    def eval(self, st):
        return int(self.left.eval(st) % self.right.eval(st))


class UnOp(BinaryOp):
    def __init__(self, value, children):
        self.value = value
        self.children = children

    def eval(self, st):
        if self.value == "SUM":
            return self.children.eval(st)
        elif self.value == "SUB":
            return -self.children.eval(st)
        elif self.value == "NOT":
            return int(not self.children.eval(st))


class Identifier():
    def __init__(self, value):
        self.value = value

    def eval(self, st):
        return st.getter(self.value)



class If():
    def __init__(self, children):
        self.children = children

    def eval(self, st):
        if self.children[0].eval(st):
            self.children[1].eval(st)
        else:
            if self.children[2] != None:
                self.children[2].eval(st)

class While():
    def __init__(self, children):
        self.children = children

    def eval(self, st):
        while self.children[0].eval(st):
            self.children[1].eval(st)


class Print():
    def __init__(self, value):
        self.value = value

    def eval(self, st):
        print(self.value.eval(st)[0])

class FuncCall():
    def __init__(self, func_name, name_params):
        self.func_name = func_name
        self.name_params = name_params

    def eval(self, st):
        funcSt = SymbolTable()
        args = st.getter_func(self.func_name)

        if len(self.name_params) != 0:
            for i in range(len(args[1])):
                a, b = self.name_params[i].eval(st)
                funcSt.setter(args[1][i][1], b)
                funcSt.setter_valor(args[1][i][1], a)

                if b == "string":
                    raise ValueError("Cannot operate string")

        args[2].eval(funcSt)

        if "vuelve" in funcSt.st_function:
            return_return = funcSt.getter_func("vuelve")
            if args[0].lower() == return_return[1]:
                del funcSt.st_function["vuelve"]
                return return_return
            else:
                raise ValueError

class FuncDec():
    def __init__(self, children, func_name, func_type):
        self.children = children
        self.func_name = func_name
        self.func_type = func_type

    def eval(self, st):
        return st.setter_func(
            self.func_name,
            self.func_type,
            self.children[0],
            self.children[1],
        )

    params_name = []


pg = ParserGenerator(
    # A list of all token names accepted by the parser.
    ['NUMBER', 'PRINT', 'OPEN_PAREN', 'CLOSE_PAREN',
        'SEMI_COLON', 'OPEN_BRACES', 'CLOSE_BRACES',
        'EQUAL', 'IDENTIFIER', 'LESS', 'GREATER',
        'SUM', 'SUB', 'NOT', 'MUL', 'DIV', 'EQUAL_EQUAL',
        'AND', 'OR', 'IF', 'ELSE', 'WHILE', 'TYPE']
)


@pg.production('begin : OPEN_BRACES block CLOSE_BRACES ')
def begin(p):
    return p[1]

@pg.production('block : command')
@pg.production('block : block command')
def block(p):
    if len(p) == 1:
        return Block([p[0]])

    p[0].children += [p[1]]
    return p[0]

@pg.production('command : SEMI_COLON')
@pg.production('command : assignment SEMI_COLON')
@pg.production('command : println')
@pg.production('command : cond')
@pg.production('command : while_')
@pg.production('command : definition SEMI_COLON')
def command(p):
    return p[0]

@pg.production('assignment : IDENTIFIER OPEN_PAREN CLOSE_PAREN')
@pg.production('assignment : IDENTIFIER EQUAL OREXPR')
def assignment(p):
    if len(p) == 3:
        if p[1].gettokentype() == "EQUAL":
            return Setter(p[0].getstr(), p[2], None)
        else:
            node = FuncCall(p[0].getstr(), [])
            return node

@pg.production('definition : TYPE IDENTIFIER')
def definition(p):
    return Setter(p[1].getstr(), None, p[0].getstr())


@pg.production('println : PRINT OPEN_PAREN OREXPR CLOSE_PAREN SEMI_COLON')
def println(p):
    return Print(p[2])

@pg.production('while_ : WHILE OPEN_PAREN OREXPR CLOSE_PAREN begin')
def while_(p):
    condition = p[2]
    todo = p[4]
    return While([condition, todo])

@pg.production('cond : IF OPEN_PAREN OREXPR CLOSE_PAREN begin')
@pg.production('cond : IF OPEN_PAREN OREXPR CLOSE_PAREN begin ELSE begin')
def cond(p):
    if p[0].gettokentype() == "IF":
        if len(p) == 5:
            condition = p[2]
            todo = p[4]
            return If([condition, todo, None])
        else:
            return If([p[2], p[4], p[6]])


@pg.production('OREXPR : ANDEXPR')
@pg.production('OREXPR : ANDEXPR OR OREXPR')
def OREXPR(p):
    if len(p) == 1:
        return p[0]
    else:
        right = p[2]
        left = p[0]
        operator = p[1]
        if operator.gettokentype() == 'OR':
            return Or(left, right)

@pg.production('ANDEXPR : EQ')
@pg.production('ANDEXPR : EQ AND ANDEXPR')
def ANDEXPR(p):
    if len(p) == 1:
        return p[0]
    else:
        right = p[2]
        left = p[0]
        operator = p[1]
        if operator.gettokentype() == 'AND':
            return Equal_Equal(left, right)

@pg.production('EQ : EXPR')
@pg.production('EQ : EXPR EQUAL_EQUAL EQ')
def parseEQEXPR(p):
    if len(p) == 1:
        return p[0]
    else:
        right = p[2]
        left = p[0]
        operator = p[1]
        if operator.gettokentype() == 'EQUAL_EQUAL':
            return Equal_Equal(left, right)

@pg.production('EXPR : expression')
@pg.production('EXPR : expression LESS EXPR')
@pg.production('EXPR : expression GREATER EXPR')
def EXPR(p):
    if len(p) == 1:
        return p[0]
    else:
        right = p[2]
        left = p[0]
        operator = p[1]
        if operator.gettokentype() == 'LESS':
            return Less(left, right)
        elif operator.gettokentype() == 'GREATER':
            return Greater(left, right)

@pg.production('expression : term')
@pg.production('expression : term SUM expression')
@pg.production('expression : term SUB expression')
def expression(p):
    if len(p) == 1:
        return p[0]
    else:
        right = p[2]
        left = p[0]
        operator = p[1]
        if operator.gettokentype() == 'SUM':
            return Sum(left, right)
        elif operator.gettokentype() == 'SUB':
            return Sub(left, right)

@pg.production('term : factor')
@pg.production('term : factor DIV term')
@pg.production('term : factor MUL term')
def term(p):
    if len(p) == 1:
        return p[0]
    else:
        right = p[2]
        left = p[0]
        operator = p[1]
        if operator.gettokentype() == 'DIV':
            return Div(left, right)
        elif operator.gettokentype() == 'MUL':
            return Mul(left, right)
@pg.production('factor : SUM factor')
@pg.production('factor : SUB factor')
@pg.production('factor : NOT factor') 
@pg.production('factor : NUMBER')
@pg.production('factor : IDENTIFIER')

def factor(p):
    left = p[0]
    if left.gettokentype() == 'SUM':
        return UnOp("SUM", p[1])
    elif left.gettokentype() == 'SUB':
        return UnOp("SUB", p[1])
    elif left.gettokentype() == 'NOT':
        return UnOp("SUB", p[1])
    elif left.gettokentype() == "NUMBER":
        return Number(p[0].value)
    elif left.gettokentype() == "IDENTIFIER":
        if len(p) == 1:
            return Getter(p[0].getstr())
######### ERROR #########
@pg.error
def error_handle(token):
    raise ValueError(token)

parser = pg.build()
def main(entrada):
    parser.parse(lexer.lex(entrada)).eval(st)

if __name__ == "__main__":
    f = open(sys.argv[1])
    data = f.read()
    #main(data)
    main(sys.argv[1])