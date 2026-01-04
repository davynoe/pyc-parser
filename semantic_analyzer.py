"""
Semantic Analyzer - Traverses AST and generates Intermediate Representation (IR)
Performs symbol table management and basic type tracking
"""

import ast as astmod
from typing import Dict, List, Any, Optional, Tuple

class IRInstruction:
    """Represents a single IR instruction"""
    def __init__(self, op: str, args: List[Any] = None):
        self.op = op
        self.args = args or []
    
    def __repr__(self):
        if self.args:
            return f"IR({self.op}, {self.args})"
        return f"IR({self.op})"

class Symbol:
    """Represents a symbol in the symbol table"""
    def __init__(self, name: str, stype: str = "any", scope: str = "local"):
        self.name = name
        self.type = stype
        self.scope = scope
        self.value = None

class SymbolTable:
    """Manages symbol scopes"""
    def __init__(self):
        self.scopes: List[Dict[str, Symbol]] = [{}]  # Stack of scopes
        self.scope_level = 0
    
    def push_scope(self):
        """Enter a new scope"""
        self.scopes.append({})
        self.scope_level += 1
    
    def pop_scope(self):
        """Exit current scope"""
        if self.scope_level > 0:
            self.scopes.pop()
            self.scope_level -= 1
    
    def define(self, name: str, stype: str = "any", scope: str = "local"):
        """Define a symbol in current scope"""
        self.scopes[-1][name] = Symbol(name, stype, scope)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up symbol in current and parent scopes"""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

class IR:
    """Intermediate Representation"""
    def __init__(self):
        self.instructions: List[IRInstruction] = []
        # functions[name] = (instrs, params)
        self.functions: Dict[str, Tuple[List[IRInstruction], List[str]]] = {}
        self.globals: List[str] = []
        self.label_counter = 0
    
    def emit(self, op: str, *args):
        """Emit an IR instruction"""
        self.instructions.append(IRInstruction(op, list(args)))
    
    def new_label(self) -> str:
        """Generate a unique label"""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def __repr__(self):
        result = "=== IR ===\n"
        result += "=== Global Instructions ===\n"
        for instr in self.instructions:
            result += str(instr) + "\n"
        
        if self.functions:
            result += "\n=== Functions ===\n"
            for fname, (instrs, params) in self.functions.items():
                result += f"\nFunc {fname}:\n"
                for instr in instrs:
                    result += "  " + str(instr) + "\n"
        
        return result

class SemanticAnalyzer:
    """Analyzes AST and generates IR"""
    
    def __init__(self):
        self.ir = IR()
        self.symbol_table = SymbolTable()
        self.current_function = None
        self.loop_labels: List[Tuple[str, str]] = []  # Stack of (break_label, continue_label)
    
    def analyze(self, ast_node: astmod.Node) -> IR:
        """Main entry point - analyze AST and return IR"""
        self.visit(ast_node)
        return self.ir
    
    def visit(self, node: astmod.Node):
        """Dispatch to appropriate visitor method"""
        method_name = f"visit_{node.__class__.__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    
    def generic_visit(self, node: astmod.Node):
        """Called for unknown node types"""
        raise Exception(f"No visitor for {node.__class__.__name__}")
    
    # Top-level
    def visit_Program(self, node: astmod.Program):
        """Program : sequence of statements"""
        for stmt in node.stmts:
            self.visit(stmt)
    
    # Statements
    def visit_ExprStmt(self, node: astmod.ExprStmt):
        """Expression statement"""
        self.visit(node.expr)
        self.ir.emit("POP")  # Discard result
    
    def visit_Assign(self, node: astmod.Assign):
        """Assignment: name = expression"""
        self.visit(node.expr)
        self.symbol_table.define(node.name)
        self.ir.emit("STORE", node.name)
    
    def visit_If(self, node: astmod.If):
        """If statement"""
        else_label = self.ir.new_label()
        end_label = self.ir.new_label()
        
        self.visit(node.cond)
        self.ir.emit("JUMP_IF_FALSE", else_label)
        
        self.visit(node.then_block)
        self.ir.emit("JUMP", end_label)
        
        self.ir.emit("LABEL", else_label)
        if node.else_block:
            self.visit(node.else_block)
        
        self.ir.emit("LABEL", end_label)
    
    def visit_While(self, node: astmod.While):
        """While loop"""
        loop_label = self.ir.new_label()
        exit_label = self.ir.new_label()
        
        self.loop_labels.append((exit_label, loop_label))
        
        self.ir.emit("LABEL", loop_label)
        self.visit(node.cond)
        self.ir.emit("JUMP_IF_FALSE", exit_label)
        
        self.visit(node.body)
        self.ir.emit("JUMP", loop_label)
        
        self.ir.emit("LABEL", exit_label)
        self.loop_labels.pop()
    
    def visit_For(self, node: astmod.For):
        """For loop"""
        loop_label = self.ir.new_label()
        exit_label = self.ir.new_label()
        
        self.loop_labels.append((exit_label, loop_label))
        self.symbol_table.define(node.varname)
        
        # Evaluate iterable
        self.visit(node.iterable)
        self.ir.emit("SETUP_LOOP")
        
        self.ir.emit("LABEL", loop_label)
        self.ir.emit("FOR_ITER", exit_label, node.varname)
        
        self.visit(node.body)
        self.ir.emit("JUMP", loop_label)
        
        self.ir.emit("LABEL", exit_label)
        self.loop_labels.pop()
    
    def visit_FuncDef(self, node: astmod.FuncDef):
        """Function definition"""
        # Save current context
        prev_function = self.current_function
        self.current_function = node.name
        
        self.symbol_table.push_scope()
        
        # Define parameters
        for param in node.params:
            self.symbol_table.define(param, "any", "param")
        
        # Create new instruction list for function
        old_instructions = self.ir.instructions
        self.ir.instructions = []
        
        self.visit(node.body)
        self.ir.emit("RETURN_VALUE", None)  # Default return None
        
        # Store function IR
        self.ir.functions[node.name] = (self.ir.instructions, node.params)
        
        # Restore context
        self.ir.instructions = old_instructions
        self.ir.emit("DEF_FUNCTION", node.name, node.params)
        
        self.symbol_table.pop_scope()
        self.current_function = prev_function
    
    def visit_Return(self, node: astmod.Return):
        """Return statement"""
        if node.expr:
            self.visit(node.expr)
        else:
            self.ir.emit("LOAD_CONST", None)
        self.ir.emit("RETURN_VALUE", None)
    
    def visit_Pass(self, node: astmod.Pass):
        """Pass statement"""
        self.ir.emit("NOP")
    
    def visit_Print(self, node: astmod.Print):
        """Print statement"""
        for arg in node.args:
            self.visit(arg)
        self.ir.emit("PRINT", len(node.args))
    
    def visit_Block(self, node: astmod.Block):
        """Block of statements"""
        for stmt in node.stmts:
            self.visit(stmt)
    
    # Expressions
    def visit_Binary(self, node: astmod.Binary):
        """Binary operation"""
        self.visit(node.left)
        self.visit(node.right)
        
        op_map = {
            '+': 'ADD',
            '-': 'SUB',
            '*': 'MUL',
            '/': 'DIV',
            '%': 'MOD',
            '==': 'EQ',
            '!=': 'NEQ',
            '<': 'LT',
            '>': 'GT',
            '<=': 'LE',
            '>=': 'GE',
            'and': 'AND',
            'or': 'OR',
        }
        
        ir_op = op_map.get(node.op, node.op.upper())
        self.ir.emit(ir_op)
    
    def visit_Unary(self, node: astmod.Unary):
        """Unary operation"""
        self.visit(node.expr)
        
        op_map = {
            '-': 'NEGATE',
            '+': 'POS',
            'not': 'NOT',
        }
        
        ir_op = op_map.get(node.op, node.op.upper())
        self.ir.emit(ir_op)
    
    def visit_Literal(self, node: astmod.Literal):
        """Literal value"""
        self.ir.emit("LOAD_CONST", node.value)
    
    def visit_Var(self, node: astmod.Var):
        """Variable reference"""
        sym = self.symbol_table.lookup(node.name)
        if sym is None:
            # Undefined variable - still emit but mark as potential error
            pass
        self.ir.emit("LOAD", node.name)
    
    def visit_Call(self, node: astmod.Call):
        """Function call"""
        if isinstance(node.func, astmod.Var):
            func_name = node.func.name
            
            # Evaluate arguments
            for arg in node.args:
                self.visit(arg)
            
            self.ir.emit("CALL_FUNCTION", func_name, len(node.args))
        else:
            raise Exception("Complex function calls not supported")
    
    def visit_ListLiteral(self, node: astmod.ListLiteral):
        """List literal"""
        for item in node.items:
            self.visit(item)
        self.ir.emit("BUILD_LIST", len(node.items))
