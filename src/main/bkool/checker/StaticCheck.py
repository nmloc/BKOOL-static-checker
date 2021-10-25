
"""
 * @author nhphung
 * Student's name: Nguyen Minh Loc
 * Student's ID: 1852554
"""
from AST import * 
from Visitor import *
# from main.bkool.utils.AST import * 
# from main.bkool.utils.Visitor import *
from StaticError import *

class MType: #type of method declaration
    def __init__(self,partype,rettype):
        self.partype = partype #param type
        self.rettype = rettype #return type

class Symbol:
    def __init__(self,name,mtype,value = None):
        self.name = name
        self.mtype = mtype
        self.value = value

class StaticChecker(BaseVisitor):

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
        programEnvi = [c]
        list(map(lambda x: x.accept(self, programEnvi), ast.decl))

    def lookupVar(self, variable, envi):
        for index, element in enumerate(envi):
            if element:
                if index > 0:
                    if (element["name"] == variable):
                        return True, element["type"]
                else:
                    for x in element:
                        if isinstance(x, dict) and x == variable:
                            return True, x["type"]
        return False, None

    def checkType(self, varType, varInit):
        if varInit == varType:
            return True, 'Literal'
        else:
            if varInit not in ['int', 'float', 'string', 'boolean']:
                return False, 'Id_Or_Op'
        return False, 'Literal'
    
    def visitVarDecl(self, ast: VarDecl, c):
        variable = ast.variable.accept(self, c)
        varType = ast.varType.accept(self, c)
        varInit = ast.varInit.accept(self, c) if ast.varInit else None

        if (not self.lookupVar(variable, c)[0]):
            return {'type': varType, 'name': variable}
        else:
            raise Redeclared(Variable(), variable)
    
    def visitConstDecl(self, ast: ConstDecl, c):
        constant = ast.constant.accept(self, c)
        constType = ast.constType.accept(self, c)
        value = ast.value.accept(self, c)

        if not self.checkType(constType, value)[0]: 
            if self.checkType(constType, value)[1] == 'Literal':
                raise TypeMismatchInConstant(ast)
            else:
                raise IllegalConstantExpression(ast.value)
        if (not self.lookupVar(constant, c)[0]):
            return {'type': constType, 'name': constant}
        else:
            raise Redeclared(Constant(), constant)

    def lookupClass(self, classname, envi):
        if len(envi) > 1:
            for index, element in enumerate(envi):
                if index > 0 and element:
                    if element["class"] == classname:
                        return True, index
        return False, None
    
    def referenceClass(self, classname, parentname, envi):
        child = self.lookupClass(classname, envi)
        parent = self.lookupClass(parentname, envi)
        if child[0]:
            raise Redeclared(Class(), classname)
        if parentname != None:
            if not parent[0]:
                raise Undeclared(Class(), parentname)
            else:
                return envi[parent[1]]["local"]
        return []
    
    def visitClassDecl(self, ast: ClassDecl, c):
        classname = ast.classname.accept(self, c)
        parentname = ast.parentname.accept(self, c) if ast.parentname else None
        localVar = [c[0]]

        localVar += self.referenceClass(classname, parentname, c)
        for mem in ast.memlist:
            if mem.__class__.__name__ == "AttributeDecl":
                localVar.append(mem.accept(self, localVar))
        for mem in ast.memlist:
            if mem.__class__.__name__ == "MethodDecl":
                mem.accept(self, localVar)
        c.append({"class": classname, "local": localVar[1:]}) #append bi cc gi roi
    
    def visitStatic(self, ast: Static, c):
        return "static"
    
    def visitInstance(self, ast: Instance, c):
        return "instance"
    
    def visitMethodDecl(self, ast: MethodDecl, c):
        kind = ast.kind.accept(self, c)
        name = ast.name.accept(self, c)
        param = ast.param.accept(self, c)
        returnType = ast.returnType.accept(self, c)
        body = ast.body.accept(self, c)

        return list(map(lambda x: x.accept(self, c), ast.body.stmt))
        #raise Redeclared(Method(), str(name))
    
    def visitAttributeDecl(self, ast: AttributeDecl, c):
        kind = ast.kind.accept(self, c)
        decl = ast.decl.accept(self, c)
        attributeName = ast.decl.variable.name if (ast.decl.__class__.__name__ == "VarDecl") else ast.decl.constant.name

        #raise Undeclared(Attribute(), str())
        if self.lookupVar(attributeName, c)[0]:
            raise Redeclared(Attribute(), attributeName)
        else:
            decl = ast.decl.accept(self, c)
            return decl
    
    def visitIntType(self, ast: IntType, c):
        return "int"
    
    def visitFloatType(self, ast: FloatType, c):
        return "float"
    
    def visitBoolType(self, ast: BoolType, c):
        return "bool"
    
    def visitStringType(self, ast: StringType, c):
        return "string"
    
    def visitVoidType(self, ast: VoidType, c):
        return "void"
    
    def visitArrayType(self, ast: ArrayType, c):
        return "array"
    
    def visitClassType(self, ast: ClassType, c):
        return "class"
    
    def visitBinaryOp(self, ast: BinaryOp, c):
        pass
    
    def visitUnaryOp(self, ast: UnaryOp, c):
        pass
    
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
        pass
    
    def visitId(self, ast: Id, c):
        return ast.name
    
    def visitArrayCell(self, ast: ArrayCell, c):
        pass
    
    def visitFieldAccess(self, ast: FieldAccess, c):
        pass
    
    def visitBlock(self, ast: Block, c):
        for decl in ast.decl:
            decl.accept(self, c)
        for stmt in ast.stmt:
            stmt.accept(self, c)
    
    def visitIf(self, ast: If, c):
        pass
    
    def visitFor(self, ast: For, c):
        pass
    
    def visitContinue(self, ast: Continue, c):
        return (ast, Continue())
        # raise MustInLoop(Continue())
    
    def visitBreak(self, ast: Break, c):
        return (ast, Break())
        # raise MustInLoop(Break())
    
    def visitReturn(self, ast: Return, c):
        pass
    
    def visitAssign(self, ast: Assign, c):
        pass
    
    def visitCallStmt(self, ast: CallStmt, c):
        pass
    
    def visitIntLiteral(self, ast: IntLiteral, c):
        return IntType()
    
    def visitFloatLiteral(self, ast: FloatLiteral, c):
        return FloatType()
    
    def visitBooleanLiteral(self, ast: BooleanLiteral, c):
        return BoolType()
    
    def visitStringLiteral(self, ast: StringLiteral, c):
        return StringType()
    
    def visitNullLiteral(self, ast: NullLiteral, c):
        return NullLiteral()
    
    def visitSelfLiteral(self, ast: SelfLiteral, c):
        return SelfLiteral()

    def checkTypeArrayLiteral(self, arr, envi):
        list = [x.accept(self, envi) for x in arr]
        res = all(map(lambda x: x == list[0], list))
        return res, list[0]

    def visitArrayLiteral(self, ast: ArrayLiteral, c):
        res = self.checkTypeArrayLiteral(ast.value, c)
        if (not res[0]):
            raise IllegalArrayLiteral(ast)
        return res[1]