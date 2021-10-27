
"""
 * @author nhphung
 * Student's name: Nguyen Minh Loc
 * Student's ID: 1852554
"""
from AST import * 
from Visitor import *

from main.bkool.utils.AST import * 
from main.bkool.utils.Visitor import *

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

class Stack:
    def __init__(self):
        self.stack = []

    def isEmpty(self):
        return True if len(self.stack) == 0 else False

    def length(self):
        return len(self.stack)

    def top(self):
        return self.stack[-1]

    def push(self, x):
        self.x = x
        self.stack.append(x)

    def pop(self):
        try:
            self.stack.pop()
            return True
        except IndexError:
            return False

class StaticChecker(BaseVisitor, Stack):

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
        programEnvi = [{"global": c}]
        list(map(lambda x: x.accept(self, programEnvi), ast.decl))

    def lookupVar(self, variable, envi):
        for index, item in enumerate(envi):
            if item:
                if index > 0:
                    if item["name"] == variable:
                        return True, item["type"], index
                else:
                    for x in item["global"]:
                        if type(x) is not Symbol and x["name"] == variable:
                            return True, x["type"], index
        return False, None, None
    
    def lookupObj(self, objName, envi):
        for index, item in enumerate(envi):
            if item:
                if index > 0:
                    if item["name"] == objName:
                        return True, item["type"], index
                else:
                    for x in item["global"]:
                        if type(x) is not Symbol and x["name"] == objName:
                            return True, x["type"], index
        return False, None, None

    def checkType(self, varType, varInit):
        if varInit == varType:
            return True, 'Literal'
        else:
            if varInit not in [IntType(), FloatType(), StringType(), BoolType()]:
                return False, 'Id_Or_Op'
        return False, 'Literal'

    def checkVarDecl(self, ast: VarDecl, c):
        variable = ast.variable.accept(self, c)
        varType = ast.varType.accept(self, c)
        varInit = ast.varInit.accept(self, c) if ast.varInit else [None, True]
        check = self.checkType(varType, varInit[0])
        # if not check[0]:
        #     if check[1] == "Literal":
        #         print("deo cung type cua literal")
        #     else:
        #         print("hinh nhu dung cung may type khac luon")
        return {
            "type": varType,
            "name": variable,
            "value_type": varInit[0] if varInit != None else varType,
            "isConst": False,
        }

    def checkConstDecl(self, ast: ConstDecl, c):
        constant = ast.constant.accept(self, c)
        constType = ast.constType.accept(self, c)
        value = ast.value.accept(self, c) if ast.value else [None, True]

        if ast.value.__class__.__name__ == "Id":
            lookup = self.lookupVar(ast.value.accept(self, c), c)
            if lookup[0]:
                if not c[lookup[0]["isConst"]]:
                    raise IllegalConstantExpression(ast.value)
            else:
                raise IllegalConstantExpression(ast.value)
        check = self.checkType(constType, value[0])
        if not value[1]:
            raise IllegalConstantExpression(ast.value)
        if not check[0]:
            if check[1] == "Literal":
                raise TypeMismatchInConstant(ast)
            else:
                raise IllegalConstantExpression(ast.value)
        return {"type": constType, "name": constant, "value_type": value[0], "isConst": True}
    
    def visitVarDecl(self, ast: VarDecl, c):
        variable = ast.variable.accept(self, c)

        if not self.lookupVar(variable, c)[0]:
            return self.checkVarDecl(ast, c)
        else:
            raise Redeclared(Variable(), variable)
    
    def visitConstDecl(self, ast: ConstDecl, c):
        constant = ast.constant.accept(self, c)

        if not self.lookupVar(constant, c)[0]:
            return self.checkConstDecl(ast, c)
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
        foundChild = self.lookupClass(classname, envi)
        foundParent = self.lookupClass(parentname, envi)
        if foundChild[0]:
            raise Redeclared(Class(), classname)
        if parentname != None:
            if not foundParent[0]:
                raise Undeclared(Class(), parentname)
            else:
                return envi[foundParent[1]]["local"]
        return []
    
    def visitClassDecl(self, ast: ClassDecl, c):
        localVar = [c[0]]
        classname = ast.classname.accept(self, c)
        parentname = ast.parentname.accept(self, c) if ast.parentname else None
        localVar += self.referenceClass(classname, parentname, c)
        memDecl = []
        for mem in ast.memlist:
            if mem.__class__.__name__ == "AttributeDecl":
                name = mem.decl.variable.name if (self.getClass(mem.decl) == "VarDecl") else mem.decl.constant.name
                if name not in memDecl:
                    if mem.kind.accept(self, c) == "Instance":
                        member = mem.accept(self, localVar)
                        if member != None:
                            member.update({"class": classname})
                            localVar.append(member)
                    else:
                        member = mem.accept(self, localVar)
                        # member.update({"class": nameclass})
                        localVar[0]["global"].append(member)
                        c[0]["global"] = localVar[0]["global"]
                    memDecl.append(name)
                else:
                    raise Redeclared(Attribute(), name)
        for mem in ast.memlist:
            if mem.__class__.__name__ == "MethodDecl":
                mem.accept(self, localVar)

        c[0].update({"class": classname})
        c.append({"class": classname, "local": localVar[1:]})
    
    def visitStatic(self, ast: Static, c):
        return "static"
    
    def visitInstance(self, ast: Instance, c):
        return "instance"
    
    def visitMethodDecl(self, ast: MethodDecl, c):
        kind = ast.kind.accept(self, c)
        name = ast.name.accept(self, c)
        param = ast.param
        returnType = ast.returnType.accept(self, c)
        body = ast.body.accept(self, c)

        return list(map(lambda x: x.accept(self, c), ast.body.stmt))
        #raise Redeclared(Method(), str(name))
    
    def visitAttributeDecl(self, ast: AttributeDecl, c):
        kind = ast.kind.accept(self, c)
        decl = ast.decl.accept(self, c)
        attributeName = (ast.decl.variable.name if (ast.decl.__class__.__name__ == "VarDecl") else ast.decl.constant.name)

        lookup = self.lookupVar(attributeName, c)
        if lookup[0]:
            if lookup[2] > 0:
                if ast.decl.__class__.__name__ == "VarDecl":
                    check = self.checkVarDecl(ast.decl, c)
                else:
                    check = self.checkConstDecl(ast.decl, c)
                c[lookup[2]] = check
            else:
                raise Redeclared(Attribute(), attributeName)
        else:
            return decl
    
    def visitIntType(self, ast: IntType, c):
        return IntType()
    
    def visitFloatType(self, ast: FloatType, c):
        return FloatType()
    
    def visitBoolType(self, ast: BoolType, c):
        return BoolType()
    
    def visitStringType(self, ast: StringType, c):
        return StringType()
    
    def visitVoidType(self, ast: VoidType, c):
        return VoidType()
    
    def visitArrayType(self, ast: ArrayType, c):
        return ArrayType()
    
    def visitClassType(self, ast: ClassType, c):
        return ClassType()
    
    def visitBinaryOp(self, ast: BinaryOp, c):
        pass
    
    def visitUnaryOp(self, ast: UnaryOp, c):
        pass
    
    def visitCallExpr(self, ast: CallExpr, c): 
        at = [self.visit(x,(c[0],False)) for x in ast.c]
        res = self.lookup(ast.method.name,c[0],lambda x: x.name)
        if res is None or not type(res.mtype) is MType:
            raise Undeclared(CallExpr(),ast.method.name)
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
        lookup = self.lookupClass(ast.obj.accept(self, c), c)
        if lookup[0]:
            lookupVar = self.lookupVar(
                ast.fieldname.accept(self, c), c[lookup[1]]
            )
            if lookupVar[0]:
                return lookupVar[1], False
        else:
            lookupobj = self.lookupVar(
                ast.fieldname.accept(self, c), c[lookup[1]]
            )
    
    def visitBlock(self, ast: Block, c):
        tempStack = Stack()
        for decl in ast.decl:
            decl.accept(self, c)
        for stmt in ast.stmt:
            if stmt.__class__.__name__ == "For":
                tempStack.push(stmt)
            if stmt.__class__.__name__ in ["Continue", "Break"]:
                res = tempStack.pop()
                if not res:
                    raise MustInLoop(stmt)
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