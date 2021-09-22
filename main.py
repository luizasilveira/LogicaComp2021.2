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
# lg.add('POT', r'\^')
lg.add('OPEN_PARENS', r'\(')
lg.add('CLOSE_PARENS', r'\)')
lg.ignore('\s+')
#lg.ignore("/.*?/")
lg.ignore("/\*.*?\*/")
lexer = lg.build()

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
            return (self.children[0].eval() / self.children[1].eval())

# class UnOp(BinaryOp):
#     def __init__(self, op, value):
#         self.op = op
#         self.value = value

#     def eval(self):
#         if self.op == "SUM":
#             return self.value.eval()
#         elif self.op == "SUB":
#             return -self.value.eval()

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

class NoOp(Node):
    def __init__(self, value):
        self.value = value
        #self.value = children

    def eval(self):
        return self.value.eval()

class Number(BaseBox):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value



# class Add(BinaryOp):
#     def eval(self):
#         return self.left.eval() + self.right.eval()

# class Sub(BinaryOp):
#     def eval(self):
#         return self.left.eval() - self.right.eval()

# class Mul(BinaryOp):
#     def eval(self):
#         return self.left.eval() * self.right.eval()

# class Div(BinaryOp):
#     def eval(self):
#         return self.left.eval() / self.right.eval()

# class Pot(BinaryOp):
#     def eval(self):
#         return self.left.eval() ** self.right.eval()



pg = ParserGenerator(
    # A list of all token names, accepted by the parser.
    # ['NUMBER', 'OPEN_PARENS', 'CLOSE_PARENS',
    #  'PLUS', 'MINUS', 'MUL', 'DIV', 'POT'
    # ],
    ['NUMBER', 'OPEN_PARENS', 'CLOSE_PARENS',
     'PLUS', 'MINUS',"MUL","DIV"
    ],
    # A list of precedence rules with ascending precedence, to
    # disambiguate ambiguous production rules.
    precedence=[
        ('left', ['PLUS', 'MINUS']),
        ('left', ['MUL', 'DIV'])
        # ('left', ['POT'])
    ]
)

@pg.production('expression : PLUS expression')
@pg.production('expression : MINUS expression')
def expression_unary(p):
    # right = p[2]
    left = p[0]
    if left.gettokentype() == 'PLUS':
        return UnOp("PLUS", p[1])
    elif left.gettokentype() == 'MINUS':
        return UnOp("MINUS", p[1])

@pg.production('expression : NUMBER')
def expression_number(p):
    # p is a list of the pieces matched by the right hand side of the
    # rule
    return IntVal(p[0].getstr())
    #return Number(float(p[0].getstr()))

@pg.production('expression : OPEN_PARENS expression CLOSE_PARENS')
def expression_parens(p):
    return p[1]

@pg.production('expression : expression PLUS expression')
@pg.production('expression : expression MINUS expression')
@pg.production('expression : expression MUL expression')
@pg.production('expression : expression DIV expression')
# @pg.production('expression : expression POT expression')
def expression_binop(p):
    left = p[0]
    right = p[2]
    if p[1].gettokentype() == 'PLUS':
        return BinOp("PLUS",left, right)
    elif p[1].gettokentype() == 'MINUS':
        return BinOp('MINUS',left, right)
    elif p[1].gettokentype() == 'MUL':
        return BinOp('MUL',left, right)
    elif p[1].gettokentype() == 'DIV':
        return BinOp('DIV',left, right)
    # elif p[1].gettokentype() == 'POT':
    #     return Pot(left, right)
    else:
        raise AssertionError('Oops, this should not be possible!')

parser = pg.build()

def main(entrada):
    result = parser.parse(lexer.lex(entrada)).eval()
    print(int(result))


if __name__ == "__main__":
    main(sys.argv[1])
    #main(input())