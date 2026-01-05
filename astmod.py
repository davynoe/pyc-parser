from typing import List, Optional, Any

class Node:
    def to_sexpr(self):
        raise NotImplementedError()

    def to_tree(self):
        """Return an ASCII tree representation of the AST."""
        lines = []
        self._build_tree(lines, prefix="", is_last=True, is_root=True)
        return "\n".join(lines)

    def _build_tree(self, lines, prefix: str, is_last: bool, is_root: bool = False):
        connector = "" if is_root else ("`-- " if is_last else "|-- ")
        lines.append(f"{prefix}{connector}{self._label()}")
        child_prefix = prefix if is_root else prefix + ("    " if is_last else "|   ")
        children = self._children()
        for idx, child in enumerate(children):
            is_child_last = idx == len(children) - 1
            if isinstance(child, list):
                for jdx, subchild in enumerate(child):
                    is_sub_last = is_child_last and jdx == len(child) - 1
                    if isinstance(subchild, Node):
                        subchild._build_tree(lines, child_prefix, is_sub_last)
            elif isinstance(child, Node):
                child._build_tree(lines, child_prefix, is_child_last)

    def __repr__(self):
        return self.to_sexpr()

    def _label(self) -> str:
        """Label used in the tree view; subclasses override for detail."""
        return self.__class__.__name__

    def _children(self):
        """Child nodes to render in the tree; subclasses override as needed."""
        return []

class Program(Node):
    def __init__(self, stmts: List[Node]):
        self.stmts = stmts
    def to_sexpr(self):
        return "(program " + " ".join(s.to_sexpr() for s in self.stmts) + ")"
    def _label(self):
        return "Program"
    def _children(self):
        return self.stmts

# Statements
class ExprStmt(Node):
    def __init__(self, expr):
        self.expr = expr
    def to_sexpr(self):
        return f"(expr {self.expr.to_sexpr()})"
    def _label(self):
        return "ExprStmt"
    def _children(self):
        return [self.expr]

class Assign(Node):
    def __init__(self, name: str, expr):
        self.name = name
        self.expr = expr
    def to_sexpr(self):
        return f"(assign {self.name} {self.expr.to_sexpr()})"
    def _label(self):
        return f"Assign {self.name}"
    def _children(self):
        return [self.expr]

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
    def _label(self):
        return "If"
    def _children(self):
        children = [self.cond, self.then_block]
        if self.else_block:
            children.append(self.else_block)
        return children

class While(Node):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body
    def to_sexpr(self):
        return f"(while {self.cond.to_sexpr()} {self.body.to_sexpr()})"
    def _label(self):
        return "While"
    def _children(self):
        return [self.cond, self.body]

class For(Node):
    def __init__(self, varname, iterable, body):
        self.varname = varname
        self.iterable = iterable
        self.body = body
    def to_sexpr(self):
        return f"(for {self.varname} {self.iterable.to_sexpr()} {self.body.to_sexpr()})"
    def _label(self):
        return f"For {self.varname}"
    def _children(self):
        return [self.iterable, self.body]

class FuncDef(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
    def to_sexpr(self):
        return f"(def {self.name} ({' '.join(self.params)}) {self.body.to_sexpr()})"
    def _label(self):
        params = ", ".join(self.params)
        return f"FuncDef {self.name}({params})"
    def _children(self):
        return [self.body]

class Return(Node):
    def __init__(self, expr=None):
        self.expr = expr
    def to_sexpr(self):
        if self.expr:
            return f"(return {self.expr.to_sexpr()})"
        return "(return)"
    def _label(self):
        return "Return"
    def _children(self):
        return [self.expr] if self.expr else []

class Pass(Node):
    def to_sexpr(self):
        return "(pass)"
    def _label(self):
        return "Pass"

class Print(Node):
    def __init__(self, args):
        self.args = args
    def to_sexpr(self):
        if self.args:
            return "(print " + " ".join(a.to_sexpr() for a in self.args) + ")"
        return "(print)"
    def _label(self):
        return "Print"
    def _children(self):
        return self.args

class Block(Node):
    def __init__(self, stmts):
        self.stmts = stmts
    def to_sexpr(self):
        return "(block " + " ".join(s.to_sexpr() for s in self.stmts) + ")"
    def _label(self):
        return "Block"
    def _children(self):
        return self.stmts

# Expressions
class Binary(Node):
    def __init__(self, op: str, left, right):
        self.op = op
        self.left = left
        self.right = right
    def to_sexpr(self):
        return f"({self.op} {self.left.to_sexpr()} {self.right.to_sexpr()})"
    def _label(self):
        return f"Binary '{self.op}'"
    def _children(self):
        return [self.left, self.right]

class Unary(Node):
    def __init__(self, op: str, expr):
        self.op = op
        self.expr = expr
    def to_sexpr(self):
        return f"({self.op} {self.expr.to_sexpr()})"
    def _label(self):
        return f"Unary '{self.op}'"
    def _children(self):
        return [self.expr]

class Literal(Node):
    def __init__(self, value: Any):
        self.value = value
    def to_sexpr(self):
        return repr(self.value)
    def _label(self):
        return f"Literal {repr(self.value)}"

class Var(Node):
    def __init__(self, name: str):
        self.name = name
    def to_sexpr(self):
        return self.name
    def _label(self):
        return f"Var {self.name}"

class Call(Node):
    def __init__(self, func, args):
        self.func = func
        self.args = args
    def to_sexpr(self):
        return f"(call {self.func.to_sexpr()} " + " ".join(a.to_sexpr() for a in self.args) + ")"
    def _label(self):
        return "Call"
    def _children(self):
        return [self.func] + self.args

class ListLiteral(Node):
    def __init__(self, items):
        self.items = items
    def to_sexpr(self):
        return "(list " + " ".join(i.to_sexpr() for i in self.items) + ")"
    def _label(self):
        return "ListLiteral"
    def _children(self):
        return self.items
