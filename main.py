# $ git tag -a v0.1.1 -m "Mensagem sobre o release"
# $ git push origin v0.1.1
#!/usr/bin/env python
# -- coding: utf-8 --
import sys
import re
from rply import LexerGenerator
from rply import ParserGenerator

from rply import LexerGenerator

lg = LexerGenerator()

lg.add('NUMBER', r'\d+')
lg.add('PLUS', r'\+')
lg.add('MINUS', r'-')
lg.add('MUL', r'\*')
lg.add('DIV', r'/')
lg.add('OPEN_PARENS', r'\(')
lg.add('CLOSE_PARENS', r'\)')

lg.add('INT', r'int')
lg.add('STRING', r'string')
lg.add('ID', r'[a-zA-z][a-zA-z0-9]*')
lg.add('EQUALS', r'=')
lg.add('SEMICOL', r';')

lg.ignore('\s+')

lexer = lg.build()

from rply.token import BaseBox

class Prog(BaseBox):
    def __init__(self, decls,atrib):
        self.decls = decls
        self.atrib = atrib

    def accept(self, visitor):
        visitor.visit_prog(self)

class VarDecls(BaseBox):
    def __init__(self, decl,decls):
        self.decl = decl
        self.decls = decls

    def accept(self, visitor):
        visitor.visit_vardecls(self)

class VarDecl(BaseBox):
    def __init__(self, id,tp):
        self.id = id
        self.tp = tp
        

    def accept(self, visitor):
        visitor.visit_vardecl(self)

class Atrib(BaseBox):
    def __init__(self, id,expr):
        self.id = id
        self.expr = expr

    def accept(self, visitor):
        visitor.visit_atrib(self)

class Expr(BaseBox):
    def accept(self, visitor):
        method_name = 'visit_{}'.format(self.__class__.__name__.lower())
        visit = getattr(visitor, method_name)
        visit(self)

class Id(Expr):
    def __init__(self, value):
        self.value = value

class Number(Expr):
    def __init__(self, value):
        self.value = value


class BinaryOp(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Add(BinaryOp):
  pass
    

class Sub(BinaryOp):
  pass
   

class Mul(BinaryOp):
  pass
    

class Div(BinaryOp):
  pass

from rply import ParserGenerator

pg = ParserGenerator(
    # A list of all token names, accepted by the lexer.
    ['NUMBER', 'OPEN_PARENS', 'CLOSE_PARENS',
     'PLUS', 'MINUS', 'MUL', 'DIV', 'INT', 'STRING', 'ID','SEMICOL',
     'EQUALS'
    ],
    # A list of precedence rules with ascending precedence, to
    # disambiguate ambiguous production rules.
    precedence=[
        ('left', ['PLUS', 'MINUS']),
        ('left', ['MUL', 'DIV'])    
    ]
)

@pg.production('prog : vardecls atrib')
def prog(p):
    return Prog(p[0],p[1])

@pg.production('vardecls : vardecl')
def expression_vardeclsOne(p):
    return VarDecls(p[0],None) 

@pg.production('vardecls : vardecl vardecls')
def vardecls(p):
    return VarDecls(p[0],p[1])

@pg.production('vardecl : STRING ID SEMICOL')
def expression_vardeclstring(p):
    return VarDecl(p[1].getstr(), p[0].getstr())

@pg.production('vardecl : INT ID SEMICOL')
def expression_vardeclint(p):
    return VarDecl(p[1].getstr(), p[0].getstr())

@pg.production('atrib : ID EQUALS expression')
def atrib(p):
    return Atrib(p[0].getstr(),p[2])


@pg.production('expression : ID')
def expression_id(p):
    return Id(p[0].getstr())

@pg.production('expression : NUMBER')
def expression_number(p):
    return Number(int(p[0].getstr()))

@pg.production('expression : OPEN_PARENS expression CLOSE_PARENS')
def expression_parens(p):
    return p[1]

@pg.production('expression : expression PLUS expression')
@pg.production('expression : expression MINUS expression')
@pg.production('expression : expression MUL expression')
@pg.production('expression : expression DIV expression')
def expression_binop(p):
    left = p[0]
    right = p[2]
    if p[1].gettokentype() == 'PLUS':
        return Add(left, right)
    elif p[1].gettokentype() == 'MINUS':
        return Sub(left, right)
    elif p[1].gettokentype() == 'MUL':
        return Mul(left, right)
    elif p[1].gettokentype() == 'DIV':
        return Div(left, right)
    else:
        raise AssertionError('Oops, this should not be possible!')

parser = pg.build()
arvore=parser.parse(lexer.lex('int x;int y;int z;z=2+x')) 

ST={}

class Visitor(object):
  pass

class SymbolTable(Visitor):
    def visit_prog(self, prog):
        prog.decls.accept(self)
        
    def visit_vardecls(self, d):
        d.decl.accept(self)
        if d.decls!=None:
          d.decls.accept(self)

    def visit_vardecl(self, d):
        ST[d.id]=d.tp

arvore.accept(SymbolTable())
# for k, v in ST.items():
#   print(k, v)

class Decorator(Visitor):

    def visit_prog(self, i):
        i.atrib.accept(self)

    def visit_atrib(self, i):
        if i.id in ST:
          i.id_decor_type=ST[i.id]
        else:
          raise AssertionError('id not declared')
        i.expr.accept(self)
        i.expr_decor_type=i.expr.decor_type

    def visit_id(self, i):
        if i.value in ST:
          i.decor_type=ST[i.value]
        else:
          raise AssertionError('id not declared')


    def visit_number(self, i):
        i.decor_type="int"
        

    def visit_add(self, a):
        a.left.accept(self)
        a.right.accept(self)
        if a.left.decor_type=="int" and a.right.decor_type=="int":
          a.decor_type="int"
          

    def visit_sub(self, a):
        a.left.accept(self)
        a.right.accept(self)
        if a.left.decor_type=="int" and a.right.decor_type=="int":
          a.decor_type="int"

    def visit_mul(self, a):
        a.left.accept(self)
        a.right.accept(self)
        if a.left.decor_type=="int" and a.right.decor_type=="int":
          a.decor_type="int"

    def visit_div(self, a):
        a.left.accept(self)
        a.right.accept(self)
        if a.left.decor_type=="int" and a.right.decor_type=="int":
          a.decor_type="int"

arvore.accept(Decorator())

class TypeVerifier(Visitor):

    def visit_prog(self, i):
        i.atrib.accept(self)

    def visit_atrib(self, i):
        if i.id_decor_type!=i.expr_decor_type:
          raise AssertionError('type error')

    def visit_add(self, a):
        if a.left.decor_type != a.right.decor_type:
          raise AssertionError('type error')
          

    def visit_sub(self, a):
        if a.left.decor_type != a.right.decor_type:
          raise AssertionError('type error')

    def visit_mul(self, a):
        if a.left.decor_type != a.right.decor_type:
          raise AssertionError('type error')

    def visit_div(self, a):
        if a.left.decor_type != a.right.decor_type:
          raise AssertionError('type error')

arvore.accept(TypeVerifier())
class IntermediateCode(Visitor):

  def visit_prog(self, i):
    i.atrib.accept(self)
    
  def visit_atrib(self, i):
    i.expr.accept(self)
    print("sto 0 z","\n")
        

  def visit_id(self, i):
    print("lod 0",i.value,"\n")


  def visit_number(self, i):
    print("lit 0",i.value,"\n")
        

  def visit_add(self, a):
    a.left.accept(self)
    a.right.accept(self)
    print("opr 0 2\n")   

  def visit_sub(self, a):
    a.left.accept(self)
    a.right.accept(self)
    print("opr 0 3\n")

  def visit_mul(self, a):
    a.left.accept(self)
    a.right.accept(self)
    print("opr 0 4\n")

  def visit_div(self, a):
    a.left.accept(self)
    a.right.accept(self)
    print("opr 0 5\n")

arvore=parser.parse(lexer.lex('int x;int y;int z;z=2*x+60/y'))
arvore.accept(SymbolTable())
arvore.accept(Decorator())
arvore.accept(TypeVerifier())
arvore.accept(IntermediateCode())   
# class SymbolTable:

#     st_function = {}

#     def __init__(self):
#         self.a = {}

#     def getter(self, value):
#         return self.a[value]

#     def setter_valor(self, value, number):
#         self.a[value] = number
#         print("value", value)
#         print(number,"number")

#     def setter(self, value):
#         if value in self.a:
#             raise ValueError
#         self.a[value] = [None]

#     # pegar a função

#     def set_return(self, return_f, valor):
#         self.st_function[return_f] = valor



# st = SymbolTable()


# class Number():
#     def __init__(self, value):
#         self.value = value
        
#     def eval(self, st):
#         return int(self.value)


# class BinaryOp():
#     def __init__(self, left, right):
#         self.left = left
#         self.right = right


# class Block():
#     def __init__(self, children):
#         self.children = children

#     def eval(self, st):
#         for node in self.children:
#             if((node) == None):
#                 pass
#             else:
#                 node.eval(st)


# class Setter(BinaryOp):
#     def __init__(self, left, right):
#         self.left = left
#         self.right = right
#         print(right,"right")
#         print(left,"left")

#     def eval(self, st):
#         print("eval------!")
#         st.setter_valor(self.left, self.right.eval(st))


# class Getter(BinaryOp):
#     def __init__(self, value):
#         self.value = value

#     def eval(self, st):
#         return st.getter(self.value)


# class PlusOne(BinaryOp):
#     def eval(self, st):
#         return int(self.left.eval(st) + 1)


# class PlusEqual(BinaryOp):
#     def eval(self, st):
#         c = self.left.eval(st)
#         c += self.right.eval(st)
#         return c


# class MinusEqual(BinaryOp):
#     def eval(self, st):
#         c = self.left.eval(st)
#         c -= self.right.eval(st)
#         return c


# class Greater(BinaryOp):
#     def eval(self, st):
#         return int(self.left.eval(st) > self.right.eval(st))


# class Equal_Equal(BinaryOp):
#     def eval(self, st):
#         return int(self.left.eval(st) == self.right.eval(st))


# class Less(BinaryOp):
#     def eval(self, st):
#         return int(self.left.eval(st) < self.right.eval(st))


# class Or(BinaryOp):
#     def eval(self, st):
#         return int(self.left.eval(st) or self.right.eval(st))


# class And(BinaryOp):
#     def eval(self, st):
#         return int(self.left.eval(st) and self.right.eval(st))


# class Sum(BinaryOp):
#     def eval(self, st):
#         # print(self.left.eval(st) , "left")
#         # print(self.right.eval(st) , "right")
#         # print(self.left.eval(st) + self.right.eval(st), "soma")
#         return self.left.eval(st) + self.right.eval(st)


# class Sub(BinaryOp):
#     def eval(self, st):
#         return self.left.eval(st) - self.right.eval(st)


# class Mul(BinaryOp):
#     def eval(self, st):
#         return int(self.left.eval(st) * self.right.eval(st))


# class Div(BinaryOp):
#     def eval(self, st):
#         return int(self.left.eval(st) / self.right.eval(st))


# class Rest(BinaryOp):
#     def eval(self, st):
#         return int(self.left.eval(st) % self.right.eval(st))


# class UnOp(BinaryOp):
#     def __init__(self, value, children):
#         self.value = value
#         self.children = children

#     def eval(self, st):
#         if self.value == "SUM":
#             return self.children.eval(st)
#         elif self.value == "SUB":
#             return -self.children.eval(st)
#         elif self.value == "NOT":
#             return int(not self.children.eval(st))


# class Identifier():
#     def __init__(self, value):
#         self.value = value

#     def eval(self, st):
#         return st.getter(self.value)



# class If():
#     def __init__(self, children):
#         self.children = children

#     def eval(self, st):
#         if self.children[0].eval(st):
#             self.children[1].eval(st)
#         else:
#             if self.children[2] != None:
#                 self.children[2].eval(st)

# class While():
#     def __init__(self, children):
#         self.children = children

#     def eval(self, st):
#         while self.children[0].eval(st):
#             self.children[1].eval(st)


# class Print():
#     def __init__(self, value):
#         self.value = value

#     def eval(self, st):
#         print(self.value.eval(st))

# class Read():
#     def __init__(self, value):
#         self.value = value
#         print(self.value,"read_value")

#     def eval(self, st):
#         print(self.value.eval(st),"read---")
#         return self.value.eval(st)

# pg = ParserGenerator(
#     # A list of all token names accepted by the parser.
#     ['NUMBER', 'PRINT', 'OPEN_PAREN', 'CLOSE_PAREN',
#         'SEMI_COLON', 'OPEN_BRACES', 'CLOSE_BRACES',
#         'EQUAL', 'IDENTIFIER', 'LESS', 'GREATER',
#         'SUM', 'SUB', 'NOT', 'MUL', 'DIV', 'EQUAL_EQUAL',
#         'AND', 'OR', 'IF', 'ELSE', 'WHILE',"FOR","READLN"],

#         precedence=[
#                 ('left', ['PLUS', 'MINUS']),
#                 ('left', ['MUL', 'DIV']),
#                 ('left', ['NOT']),
#                 ('left', ['AND', 'OR', 'EQUAL_EQUAL', 'GREATER', 'LESS']),
#             ]
# )



# @pg.production('begin : OPEN_BRACES block CLOSE_BRACES ')
# def begin(p):
#     return p[1]

# @pg.production('block : command')
# @pg.production('block : block command')
# def block(p):
   
#     if len(p) == 1:
#         if(type([p[0]]) == int):
#             return Number(p[0])
#         else:
#             return Block([p[0]])

#     p[0].children += [p[1]]
#     return p[0]

# @pg.production('command : println')
# @pg.production('command : readln')
# @pg.production('command : cond')
# @pg.production('command : while_')
# def command(p):
#     print(p[0].eval(), "p[0]---")
#     return p[0]

# @pg.production('command : SEMI_COLON')
# @pg.production('command : assignment SEMI_COLON')
# def command(p):
#     if len(p) > 1:
#         return p[0]
#     else:
#         pass

# @pg.production('assignment : IDENTIFIER OPEN_PAREN CLOSE_PAREN')
# @pg.production('assignment : IDENTIFIER EQUAL OREXPR')
# @pg.production('assignment : IDENTIFIER EQUAL readln')
# def assignment(p):
#     print("assin")
#     print("----------")
#     if len(p) == 3:
#         if p[1].gettokentype() == "EQUAL":
#             return Setter(p[0].getstr(), p[2])


# @pg.production('println : PRINT OPEN_PAREN OREXPR CLOSE_PAREN SEMI_COLON')
# def println(p):
#     return Print(p[2])

# @pg.production('readln : READLN OPEN_PAREN CLOSE_PAREN SEMI_COLON')
# def println(p):
#     print("readln")
#     x = int(input())
#     return Read(x)
   


# @pg.production('while_ : WHILE OPEN_PAREN OREXPR CLOSE_PAREN begin')
# def while_(p):
#     condition = p[2]
#     todo = p[4]
#     return While([condition, todo])

# @pg.production('cond : IF OPEN_PAREN OREXPR CLOSE_PAREN begin')
# @pg.production('cond : IF OPEN_PAREN OREXPR CLOSE_PAREN begin ELSE begin')
# def cond(p):
#     if p[0].gettokentype() == "IF":
#         if len(p) == 5:
#             condition = p[2]
#             todo = p[4]
#             return If([condition, todo, None])
#         else:
#             return If([p[2], p[4], p[6]])


# @pg.production('OREXPR : ANDEXPR')
# @pg.production('OREXPR : ANDEXPR OR OREXPR')
# def OREXPR(p):
#     if len(p) == 1:
#         return p[0]
#     else:
#         right = p[2]
#         left = p[0]
#         operator = p[1]
#         if operator.gettokentype() == 'OR':
#             return Or(left, right)

# @pg.production('ANDEXPR : EQ')
# @pg.production('ANDEXPR : EQ AND ANDEXPR')
# def ANDEXPR(p):
#     if len(p) == 1:
#         return p[0]
#     else:
#         right = p[2]
#         left = p[0]
#         operator = p[1]
#         if operator.gettokentype() == 'AND':
#             return Equal_Equal(left, right)

# @pg.production('EQ : EXPR')
# @pg.production('EQ : EXPR EQUAL_EQUAL EQ')
# def parseEQEXPR(p):
#     if len(p) == 1:
#         return p[0]
#     else:
#         right = p[2]
#         left = p[0]
#         operator = p[1]
#         if operator.gettokentype() == 'EQUAL_EQUAL':
#             return Equal_Equal(left, right)

# @pg.production('EXPR : expression')
# @pg.production('EXPR : expression LESS EXPR')
# @pg.production('EXPR : expression GREATER EXPR')

# def EXPR(p):
#     if len(p) == 1:
#         return p[0]
#     else:
#         right = p[2]
#         left = p[0]
#         operator = p[1]
#         if operator.gettokentype() == 'LESS':
#             return Less(left, right)
#         elif operator.gettokentype() == 'GREATER':
#             return Greater(left, right)
# ######### EXPRESSION #########
# @pg.production('EXPR : OPEN_PAREN EXPR CLOSE_PAREN')
# @pg.production('EQ : OPEN_PAREN EQ CLOSE_PAREN')
# @pg.production('ANDEXPR : OPEN_PAREN ANDEXPR CLOSE_PAREN')
# @pg.production('OREXPR : OPEN_PAREN OREXPR CLOSE_PAREN')
# @pg.production('expression : OPEN_PAREN expression CLOSE_PAREN')

# #@pg.production('expression : OPEN_PAREN expression CLOSE_PAREN')
# def expression_parens(p):
#     return p[1]


# @pg.production('expression : expression SUM expression')
# @pg.production('expression : expression SUB expression')
# @pg.production('expression : expression MUL expression')
# @pg.production('expression : expression DIV expression')
# def expression(p):
#     right = p[2]
#     left = p[0]
#     operator = p[1]
#     if operator.gettokentype() == 'SUM':
#         return Sum(left, right)
#     if operator.gettokentype() == 'DIV':
#         return Div(left, right)
#     if operator.gettokentype() == 'MUL':
#         return Mul(left, right)
#     elif operator.gettokentype() == 'SUB':
#         return Sub(left, right)

# @pg.production('expression : term')
# @pg.production('expression : term SUM expression')
# @pg.production('expression : term SUB expression')
# def expression(p):
#     if len(p) == 1:
#         return p[0]
#     else:
#         right = p[2]
#         left = p[0]
#         operator = p[1]
#         if operator.gettokentype() == 'SUM':
#             return Sum(left, right)
#         elif operator.gettokentype() == 'SUB':
#             return Sub(left, right)

        

# @pg.production('term : factor')
# @pg.production('term : factor DIV term')
# @pg.production('term : factor MUL term')
# @pg.production('term : term DIV term')
# @pg.production('term : term MUL term')
# def term(p):
#     if len(p) == 1:
#         return p[0]
#     else:
#         right = p[2]
#         left = p[0]
#         operator = p[1]
#         if operator.gettokentype() == 'DIV':
#             return Div(left, right)
#         elif operator.gettokentype() == 'MUL':
#             return Mul(left, right)

# @pg.production('factor : SUM factor')
# @pg.production('factor : SUB factor')
# @pg.production('factor : NOT factor') 
# @pg.production('factor : NUMBER')
# @pg.production('factor : IDENTIFIER')

# def factor(p):
#     left = p[0]
#     if left.gettokentype() == 'SUM':
#         print("sum_unop")
#         return UnOp("SUM", p[1])
#     elif left.gettokentype() == 'SUB':
#         return UnOp("SUB", p[1])
#     elif left.gettokentype() == 'NOT':
#         return UnOp("SUB", p[1])
#     elif left.gettokentype() == "NUMBER":
#         return Number(p[0].value)
#     elif left.gettokentype() == "IDENTIFIER":
#         if len(p) == 1:
#             return Getter(p[0].getstr())

# ######### ERROR #########
# @pg.error
# def error_handle(token):
#     raise ValueError(token)
# parser = pg.build()

# def main(entrada):
#     parser.parse(lexer.lex(entrada)).eval(st)

# if __name__ == "__main__":
#     f = open(sys.argv[1])
#     data = f.read()
#     #main(data)
#     main(sys.argv[1])