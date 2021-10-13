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
lg.add("IDENTIFIER", r'[a-zA-Z]*([a-zA-Z]|/d+|_)')
lg.add('EQUAL', r'\=')
lg.add('SEMICOLON', r'\;')
lg.add('LISTA', r'\[[0-9]+\,.*\]|\[\]|\[[0-9]\]')


lg.ignore('\s+')
lg.ignore("/\*.*?\*/")
lexer = lg.build()

# for token in lexer.lex('x = 3;'):
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

    def setter(self, value):
        if value in self.variables:
            raise ValueError
        self.variables[value] = [None]

    def set_value(self, value, number):
        self.variables[value] = number


class Setter(Node):
    def __init__(self, left, right):
        self.children = [left,right]

    def eval(self):
        SymbolTable.set_value(SymbolTable(),self.children[0], self.children[1].eval())

class Getter(Node):
    def __init__(self, value):
        self.value = value

    def eval(self, st):
        return SymbolTable.getter(SymbolTable(),self.value)

class Block(Node):
    def __init__(self, children):
        self.children = children

    def eval(self):
        for node in self.children:
            node.eval()

# class Identifier():
#     def __init__(self, value):
#         self.value = value

#     def eval(self, st):
#         return SymbolTable.getter(self.value)
# class NoOp(Node):
#     def __init__(self, value):
#         self.value = value

#     def eval(self):
#         return self.value.eval()
class Number(BaseBox):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value

class Print(Node):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value.eval()

class Program():
    def __init__(self, value):
        self.value = value

    def eval(self):
        lista = []
        for e in self.value:
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

# #################### STATEMENT ####################
@pg.production('statement : SEMICOLON')
@pg.production('statement : assignment SEMICOLON')
@pg.production('statement : definition SEMICOLON')
@pg.production('statement : println')
def statement(p):
    return p[0]

# #################### ASSIGNMENT and DEFINITION ####################
@pg.production('assignment : IDENTIFIER EQUAL parseEXPR')
def assignment(p):
    if len(p) == 3:
        if p[1].gettokentype() == "EQUAL":
            # self.variables[value] = number
            return Setter(p[0].getstr(), p[2])

# @pg.production('params_assignment : parseEXPR')
# # @pg.production('params_assignment :  params_assignment COMMA parseOREXPR')
# def params_assignment(p):
#     if len(p) == 1:
#         return [p[0]]

@pg.production('definition : IDENTIFIER')
def definition(p):
    # self.variables[value] = number
    
    return Setter(p[0].getstr(), None)

# ######### PRINT #########
@pg.production('println : PRINT OPEN_PARENS parseEXPR CLOSE_PARENS SEMICOLON')
def println(p):
    value = Print(p[2])
    return value



######### parseEXPR #########
@pg.production('parseEXPR : expression')
def parseEXPR(p):
    return p[0]

######### EXPRESSION #########
@pg.production('expression : OPEN_PARENS expression CLOSE_PARENS')
def expression_parens(p):
    return p[1]

@pg.production('expression : term')
@pg.production('expression : term PLUS expression')
@pg.production('expression : term MINUS expression')
def expression(p):
    if len(p) == 1:
        return p[0]
    else:
        left = p[0]
        right = p[2]
        return BinOp(p[1].gettokentype(),left,right)

######### TERM #########
@pg.production('term : factor MUL term')
@pg.production('term : factor DIV term')
@pg.production('term : factor POT term')
def term_binop(p):
    left = p[0]
    right = p[2]
    return BinOp(p[1].gettokentype(),left,right)

@pg.production('term : factor')
def term_binop(p):
    left = p[0]
    return left

######### FACTOR #########
@pg.production('factor : NUMBER')
@pg.production('factor : IDENTIFIER')
def factor_unary(p):
    left = p[0]
    if left.gettokentype() == "NUMBER":
        return IntVal(p[0].getstr())  
    elif left.gettokentype() == "IDENTIFIER":
        return Getter(p[0].getstr())  

@pg.production('factor : PLUS factor')
@pg.production('factor : MINUS factor')
def factor_unary_unary(p):
    left = p[0]
    right = p[1]
    return UnOp(left.gettokentype(),right)

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