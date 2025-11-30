from typing import List, Optional, Any

class Node:
    def to_sexpr(self):
        raise NotImplementedError()

    def __repr__(self):
        return self.to_sexpr()

class Program(Node):
    def __init__(self, stmts: List[Node]):
        self.stmts = stmts
    def to_sexpr(self):
        return "(program " + " ".join(s.to_sexpr() for s in self.stmts) + ")"

# Statements
class ExprStmt(Node):
    def __init__(self, expr):
        self.expr = expr
    def to_sexpr(self):
        return f"(expr {self.expr.to_sexpr()})"

class Assign(Node):
    def __init__(self, name: str, expr):
        self.name = name
        self.expr = expr
    def to_sexpr(self):
        return f"(assign {self.name} {self.expr.to_sexpr()})"

class If(Node):
    def __init__(self, cond, then_block, else_block=None):
        self.cond = cond
        self.then_block = then_block
        self.else_block = else_block
    def to_sexpr(self):
        s = f"(if {self.cond.to_sexpr()} {self.then_block.to_sexpr()}"
        if self.else_block:
            s += f" {self.else_block.to_sexpr()}"
        s += ")"
        return s

class While(Node):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body
    def to_sexpr(self):
        return f"(while {self.cond.to_sexpr()} {self.body.to_sexpr()})"

class For(Node):
    def __init__(self, varname, iterable, body):
        self.varname = varname
        self.iterable = iterable
        self.body = body
    def to_sexpr(self):
        return f"(for {self.varname} {self.iterable.to_sexpr()} {self.body.to_sexpr()})"

class FuncDef(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
    def to_sexpr(self):
        return f"(def {self.name} ({' '.join(self.params)}) {self.body.to_sexpr()})"

class Return(Node):
    def __init__(self, expr=None):
        self.expr = expr
    def to_sexpr(self):
        if self.expr:
            return f"(return {self.expr.to_sexpr()})"
        return "(return)"

class Pass(Node):
    def to_sexpr(self):
        return "(pass)"

class Print(Node):
    def __init__(self, args):
        self.args = args
    def to_sexpr(self):
        if self.args:
            return "(print " + " ".join(a.to_sexpr() for a in self.args) + ")"
        return "(print)"

class Block(Node):
    def __init__(self, stmts):
        self.stmts = stmts
    def to_sexpr(self):
        return "(block " + " ".join(s.to_sexpr() for s in self.stmts) + ")"

# Expressions
class Binary(Node):
    def __init__(self, op: str, left, right):
        self.op = op
        self.left = left
        self.right = right
    def to_sexpr(self):
        return f"({self.op} {self.left.to_sexpr()} {self.right.to_sexpr()})"

class Unary(Node):
    def __init__(self, op: str, expr):
        self.op = op
        self.expr = expr
    def to_sexpr(self):
        return f"({self.op} {self.expr.to_sexpr()})"

class Literal(Node):
    def __init__(self, value: Any):
        self.value = value
    def to_sexpr(self):
        return repr(self.value)

class Var(Node):
    def __init__(self, name: str):
        self.name = name
    def to_sexpr(self):
        return self.name

class Call(Node):
    def __init__(self, func, args):
        self.func = func
        self.args = args
    def to_sexpr(self):
        return f"(call {self.func.to_sexpr()} " + " ".join(a.to_sexpr() for a in self.args) + ")"

class ListLiteral(Node):
    def __init__(self, items):
        self.items = items
    def to_sexpr(self):
        return "(list " + " ".join(i.to_sexpr() for i in self.items) + ")"
