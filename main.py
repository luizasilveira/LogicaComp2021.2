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
#lg.add('NUMBER', r'[+-]?\d+')
lg.add('NUMBER', r'\d+')
lg.add('PLUS', r'\+')
lg.add('MINUS', r'-')
lg.add('MUL', r'\*')
lg.add('DIV', r'/')
lg.add('POT', r'\^')
lg.add('OPEN_PARENS', r'\(')
lg.add('CLOSE_PARENS', r'\)')
lg.add('PRINT', r'println')
lg.add("IDENTIFIER", r'[a-zA-Z_]([a-zA-Z_0-9]*|_[a-zA-Z_0-9]*)')
lg.add('EQUAL', r'\=')
lg.add('SEMICOLON', r'\;')
lg.add('LISTA', r'\[[0-9]+\,.*\]|\[\]|\[[0-9]\]')

lg.ignore('\s+')
lg.ignore("/\*.*?\*/")
lexer = lg.build()

# for token in lexer.lex('x1 = 3;'):
#   print(token)

class Node(BaseBox):
    def __init__(self,value):
        self.value = value
        self.children = []

    def eval(self):
        return self.value

class BinOp(Node):
    def __init__(self, op, left, right):
        self.value = op
        self.children = [left,right]

    def eval(self):
        if self.value == "PLUS":
            return (self.children[0].eval() + self.children[1].eval())

        if self.value == "MINUS":
            return (self.children[0].eval() - self.children[1].eval())

        if self.value == "MUL":
            return (self.children[0].eval() * self.children[1].eval())

        if self.value == "DIV":
            return int((self.children[0].eval() / self.children[1].eval()))

        if self.value == "POT":
            return (self.children[0].eval() ** self.children[1].eval())

class UnOp(Node):
    def __init__(self, op, children):
        self.value = op
        self.children = [children]

    def eval(self):
        if self.value == "PLUS":
            return self.children[0].eval()
        elif self.value == "MINUS":
            return -self.children[0].eval()

class IntVal(Node):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return int(self.value)

class SymbolTable:
    def __init__(self):
        self.variables = {}

    def getter(self, value):
        return self.variables[value]

    def setter(self, value, number):
        self.variables[value] = number

st = SymbolTable()
class Setter(Node):
    def __init__(self,left,right):
        self.children = [left, right]
    def eval(self):
        return st.setter(self.children[0], self.children[1].eval())

class Getter(Node):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return st.getter(self.value)

class Print(Node):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value.eval()

class Program():
    def __init__(self, value):
        self.value = value

    def eval(self):
        for e in self.value:
            if(e.eval() is not None):
                print(e.eval())
           
pg = ParserGenerator(
    # A list of all token names, accepted by the parser.
    ['NUMBER', 'OPEN_PARENS', 'CLOSE_PARENS',
     'PLUS', 'MINUS',"MUL","DIV", "POT","IDENTIFIER","EQUAL","SEMICOLON","PRINT"
    ],
    # A list of precedence rules with ascending precedence, to
    # disambiguate ambiguous production rules.
    precedence=[
        ('left', ['PLUS', 'MINUS']),
        ('left', ['MUL', 'DIV']),
        ('left', ['POT'])
    ]
)

#################### PROGRAM ####################
@pg.production('program : statement')
@pg.production('program : program statement')
def program(p):
    if len(p) == 1:
        return(Program([p[0]]))

    p[0].value += [p[1]]
    return p[0]

##################### STATEMENT ####################
@pg.production('statement : SEMICOLON')
@pg.production('statement : assignment SEMICOLON')
@pg.production('statement : println')
def statement(p):
    return p[0]

@pg.production('println : PRINT OPEN_PARENS expression CLOSE_PARENS SEMICOLON')
@pg.production('println : PRINT OPEN_PARENS variable CLOSE_PARENS SEMICOLON')
# @self.pg.production('println : PRINT OPEN_PAREN variable expression CLOSE_PAREN SEMI_COLON')
def println(p):
    return Print(p[2])

# #################### ASSIGNMENT and DEFINITION ####################
@pg.production('assignment : IDENTIFIER EQUAL expression ')
def assignment(p):
    return Setter(p[0].getstr(), p[2])

@pg.production('variable : IDENTIFIER')
def variable(p):
    return Getter(p[0].getstr())

# variable and number
@pg.production('expression : variable MINUS expression')
@pg.production('expression : variable PLUS expression')
@pg.production('expression : variable MUL expression')
@pg.production('expression : variable DIV expression')
@pg.production('expression : variable POT expression')

@pg.production('expression : variable PLUS variable')
@pg.production('expression : variable MINUS variable')
@pg.production('expression : variable MUL variable')
@pg.production('expression : variable DIV variable')
@pg.production('expression : variable POT variable')


@pg.production('expression : expression PLUS expression')
@pg.production('expression : expression MINUS expression')
@pg.production('expression : expression MUL expression')
@pg.production('expression : expression DIV expression')
@pg.production('expression : expression POT expression')

def expression(p):
    if len(p) > 2:
        right = p[2]

    left = p[0]
    return BinOp(p[1].gettokentype(),left,right)

@pg.production('expression : PLUS expression')
@pg.production('expression : MINUS expression')
def factor_unary_unary(p):
    left = p[0]
    right = p[1]
    return UnOp(left.gettokentype(),right)

@pg.production('expression : NUMBER')
def factor_unary(p):
    return IntVal(p[0].getstr())  

######### EXPRESSION #########
@pg.production('expression : OPEN_PARENS expression CLOSE_PARENS')
def expression_parens(p):
    return p[1]

######### ERROR #########
@pg.error
def error_handle(token):
    raise ValueError(token)

parser = pg.build()

def main(entrada):
    parser.parse(lexer.lex(entrada)).eval()
    # print(int(result))

if __name__ == "__main__":
    # f = open(sys.argv[1])
    # data = f.read()
    # main(data)
    main(sys.argv[1])