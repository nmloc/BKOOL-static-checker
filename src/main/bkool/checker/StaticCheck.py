
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
        return self.ast.accept(self, StaticChecker.global_envi)
    
    def visitProgram(self, ast: Program, c):
        globalEnv = [c]
        list(map(lambda x: x.accept(self, globalEnv), ast.decl))
    
    def visitVarDecl(self, ast: VarDecl, c):
        variable = ast.variable.accept(self, c)
        varType = ast.varType.accept(self, c)
        varInit = ast.varInit.accept(self, c) if ast.varInit else None
        
        raise Redeclared(Variable(), str(variable))
    
    def visitConstDecl(self, ast: ConstDecl, c):
        constant = ast.constant.accept(self, c)
        constType = ast.constType.accept(self, c)
        value = ast.value.accept(self, c)

        raise Redeclared(Constant(), str(constant))
        raise IllegalConstantExpression(value)
    
    def visitClassDecl(self, ast: ClassDecl, c):
        classname = ast.classname.accept(self, c)
        memlist = ast.memlist
        parentname = ast.parentname.accept(self, c) if ast.parentname else None

        raise Redeclared(Class(), str(classname))
        raise Undeclared(Class(), str(classname))
    
    def visitStatic(self, ast: Static, c):
        return None
    
    def visitInstance(self, ast: Instance, c):
        return None
    
    def visitMethodDecl(self, ast: MethodDecl, c):
        kind = ast.kind.accept(self, c)
        name = ast.name.accept(self, c)
        param = ast.param.accept(self, c)
        returnType = ast.returnType.accept(self, c)
        body = ast.body.accept(self, c)

        return list(map(lambda x: x.accept(self, c), ast.body.stmt))
        raise Redeclared(Method(), str(name))
    
    def visitAttributeDecl(self, ast: AttributeDecl, c):
        kind = ast.kind.accept(self, c)
        decl = ast.decl.accept(self, c)

        raise Redeclared(Attribute(), str())
        raise Undeclared(Attribute(), str())
    
    def visitIntType(self, ast: IntType, c):
        print(ast)
    
    def visitFloatType(self, ast: FloatType, c):
        print(ast)
    
    def visitBoolType(self, ast: BoolType, c):
        print(ast)
    
    def visitStringType(self, ast: StringType, c):
        print(ast)
    
    def visitVoidType(self, ast: VoidType, c):
        print(ast)
    
    def visitArrayType(self, ast: ArrayType, c):
        print(ast)
    
    def visitClassType(self, ast: ClassType, c):
        print(ast)
    
    def visitBinaryOp(self, ast: BinaryOp, c):
        print(ast)
    
    def visitUnaryOp(self, ast: UnaryOp, c):
        print(ast)
    
    def visitCallExpr(self, ast: CallExpr, c): 
        at = [self.visit(x,(c[0],False)) for x in ast.c]
        
        res = self.lookup(ast.method.name,c[0],lambda x: x.name)
        if res is None or not type(res.mtype) is MType:
            raise Undeclared(Function(),ast.method.name)
        elif len(res.mtype.partype) != len(at):
            if c[1]:
                raise TypeMismatchInStatement(ast)
            else:
                raise TypeMismatchInExpression(ast)
        else:
            return res.mtype.rettype
    
    def visitNewExpr(self, ast: NewExpr, c):
        print(ast)
    
    def visitId(self, ast: Id, c):
        print(ast)
    
    def visitArrayCell(self, ast: ArrayCell, c):
        print(ast)
    
    def visitFieldAccess(self, ast: FieldAccess, c):
        print(ast)
    
    def visitBlock(self, ast: Block, c):
        pass
    
    def visitIf(self, ast: If, c):
        print(ast)
    
    def visitFor(self, ast: For, c):
        print(ast)
    
    def visitContinue(self, ast: Continue, c):
        return (ast, Continue())
    
    def visitBreak(self, ast: Break, c):
        return (ast, Break())
    
    def visitReturn(self, ast: Return, c):
        print(ast)
    
    def visitAssign(self, ast: Assign, c):
        print(ast)
    
    def visitCallStmt(self, ast: CallStmt, c):
        print(ast)
    
    def visitIntLiteral(self, ast: IntLiteral, c):
        return IntType()
    
    def visitFloatLiteral(self, ast: FloatLiteral, c):
        return FloatType()
    
    def visitBooleanLiteral(self, ast: BooleanLiteral, c):
        return BoolType()
    
    def visitStringLiteral(self, ast: StringLiteral, c):
        return StringType()
    
    def visitNullLiteral(self, ast: NullLiteral, c):
        return None
    
    def visitSelfLiteral(self, ast: SelfLiteral, c):
        return None

    def visitArrayLiteral(self, ast: ArrayLiteral, c):
        return ArrayType() 