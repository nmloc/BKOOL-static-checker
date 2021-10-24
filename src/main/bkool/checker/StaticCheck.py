
"""
 * @author nhphung
 * Student's name: Nguyen Minh Loc
 * Student's ID: 1852554
"""
# from AST import * 
# from Visitor import *
# from Utils import Utils
from StaticError import *

from main.bkool.utils.AST import * 
from main.bkool.utils.Visitor import *
from main.bkool.utils.Utils import Utils

class MType: #type of method declaration
    def __init__(self,partype,rettype):
        self.partype = partype #param type
        self.rettype = rettype #return type

class Symbol:
    def __init__(self,name,mtype,value = None):
        self.name = name
        self.mtype = mtype
        self.value = value

class StaticChecker(BaseVisitor,Utils):

    global_envi = [
        Symbol("getInt", MType([], IntType())),
        Symbol("putInt", MType([IntType()], VoidType())),
        Symbol("putIntLn", MType([IntType()], VoidType())),
        Symbol("getFloat", MType([], FloatType())),
        Symbol("putFloat", MType([FloatType()], VoidType())),
        Symbol("putFloatLn", MType([FloatType()], VoidType())),
        Symbol("getBool", MType([], BoolType())),
        Symbol("putBool", MType([BoolType()], VoidType())),
        Symbol("putBoolLn", MType([BoolType()], VoidType())),
        Symbol("getStr", MType([], StringType())),
        Symbol("putStr", MType([StringType()], VoidType())),
        Symbol("putStrLn", MType([StringType()], VoidType())),
    ]
            
    
    def __init__(self,ast):
        self.ast = ast
    
    def check(self):
        return self.ast.accept(self,StaticChecker.global_envi)
    
    def visitProgram(self, ast: Program, param):
        globalEnv = [param]
        list(map(lambda x: x.accept(self,globalEnv),ast.decl))
    
    def visitVarDecl(self, ast: VarDecl, param):
        print(ast)
    
    def visitConstDecl(self, ast, param):
        print(ast)
    
    def visitClassDecl(self, ast, param):
        print(ast)
    
    def visitStatic(self, ast, param):
        print(ast)
    
    def visitInstance(self, ast, param):
        print(ast)
    
    def visitMethodDecl(self, ast, param):
        print(ast)
        return list(map(lambda x: self.visit(x,(param,True)),ast.body.stmt))
    
    def visitAttributeDecl(self, ast, param):
        print(ast)
    
    def visitIntType(self, ast, param):
        print(ast)
    
    def visitFloatType(self, ast, param):
        print(ast)
    
    def visitBoolType(self, ast, param):
        print(ast)
    
    def visitStringType(self, ast, param):
        print(ast)
    
    def visitVoidType(self, ast, param):
        print(ast)
    
    def visitArrayType(self, ast, param):
        print(ast)
    
    def visitClassType(self, ast, param):
        print(ast)
    
    def visitBinaryOp(self, ast, param):
        print(ast)
    
    def visitUnaryOp(self, ast, param):
        print(ast)
    
    def visitCallExpr(self, ast, param): 
        at = [self.visit(x,(param[0],False)) for x in ast.param]
        
        res = self.lookup(ast.method.name,param[0],lambda x: x.name)
        print(ast)
        if res is None or not type(res.mtype) is MType:
            raise Undeclared(Function(),ast.method.name)
        elif len(res.mtype.partype) != len(at):
            if param[1]:
                raise TypeMismatchInStatement(ast)
            else:
                raise TypeMismatchInExpression(ast)
        else:
            return res.mtype.rettype
    
    def visitNewExpr(self, ast, param):
        print(ast)
    
    def visitId(self, ast, param):
        print(ast)
    
    def visitArrayCell(self, ast, param):
        print(ast)
    
    def visitFieldAccess(self, ast, param):
        print(ast)
    
    def visitBlock(self, ast, param):
        print(ast)
    
    def visitIf(self, ast, param):
        print(ast)
    
    def visitFor(self, ast: For, param):
        print(ast)
    
    def visitContinue(self, ast, param):
        print(ast)
        return (ast, Continue())
    
    def visitBreak(self, ast, param):
        print(ast)
        return (ast, Break())
    
    def visitReturn(self, ast, param):
        print(ast)
    
    def visitAssign(self, ast, param):
        print(ast)
    
    def visitCallStmt(self, ast, param):
        print(ast)
    
    def visitIntLiteral(self, ast, param):
        return IntType()
    
    def visitFloatLiteral(self, ast, param):
        return FloatType()
    
    def visitBooleanLiteral(self, ast, param):
        return BoolType()
    
    def visitStringLiteral(self, ast, param):
        return StringType()
    
    def visitNullLiteral(self, ast, param):
        return None
    
    def visitSelfLiteral(self, ast, param):
        return None

    def visitArrayLiteral(self, ast, param):
        return ArrayType() 