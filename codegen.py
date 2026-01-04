"""
Code Generator - Converts IR to bytecode
Generates stack-based bytecode instructions
"""

from semantic_analyzer import IR, IRInstruction
from typing import List, Dict, Any, Tuple

class Bytecode:
    """Represents compiled bytecode"""
    def __init__(self):
        self.code: List[int] = []  # Bytecode
        self.constants: List[Any] = []  # Constant pool
        self.names: List[str] = []  # Name pool (variable/function names)
        # functions[name] = {"code": List[int], "params": List[str]}
        self.functions: Dict[str, Dict[str, Any]] = {}  # Compiled functions
        self.label_positions: Dict[str, int] = {}  # Label -> bytecode position
    
    def __repr__(self):
        result = f"Code length: {len(self.code)}\n"
        result += f"Constants: {self.constants}\n"
        result += f"Names: {self.names}\n"
        result += f"Functions: {list(self.functions.keys())}\n"
        result += "\nDisassembly:\n"
        result += self._disassemble()
        return result
    
    def _disassemble(self) -> str:
        """Generate disassembly output"""
        result = ""
        i = 0
        while i < len(self.code):
            opcode = self.code[i]
            opcode_name = OPCODES_REVERSE.get(opcode, f'UNKNOWN({opcode})')
            result += f"{i:4d}  {opcode_name:<20}"
            
            # Show operands if any
            if opcode in OPCODE_ARGS_BY_NUM:
                num_args = OPCODE_ARGS_BY_NUM[opcode]
                args = []
                for _ in range(num_args):
                    i += 1
                    if i < len(self.code):
                        arg_val = self.code[i]
                        args.append(arg_val)
                        
                # Format args with helpful info
                if len(args) > 0:
                    result += " "
                    if opcode == OPCODES['LOAD_CONST'] and args[0] < len(self.constants):
                        result += f"{args[0]} (= {self.constants[args[0]]!r})"
                    elif opcode in [OPCODES['LOAD'], OPCODES['STORE'], OPCODES['CALL_FUNCTION'], OPCODES['DEF_FUNCTION']]:
                        if args[0] < len(self.names):
                            result += f"{args[0]} (= {self.names[args[0]]})"
                            if len(args) > 1:
                                result += f", {args[1]}"
                        else:
                            result += f"{args}"
                    elif opcode in [OPCODES['JUMP'], OPCODES['JUMP_IF_FALSE']]:
                        result += f"-> {args[0]}"
                    elif opcode == OPCODES['FOR_ITER']:
                        var_name = self.names[args[1]] if args[1] < len(self.names) else f"#{args[1]}"
                        result += f"-> {args[0]}, var={var_name}"
                    else:
                        result += f"{args}"
            
            result += "\n"
            i += 1
        
        return result

# Bytecode opcodes
OPCODES = {
    'LOAD_CONST': 1,
    'LOAD': 2,
    'STORE': 3,
    'POP': 4,
    'ADD': 5,
    'SUB': 6,
    'MUL': 7,
    'DIV': 8,
    'MOD': 9,
    'NEGATE': 10,
    'POS': 11,
    'NOT': 12,
    'EQ': 13,
    'NEQ': 14,
    'LT': 15,
    'GT': 16,
    'LE': 17,
    'GE': 18,
    'AND': 19,
    'OR': 20,
    'JUMP': 21,
    'JUMP_IF_FALSE': 22,
    'LABEL': 23,  # Pseudo-op, not actual bytecode
    'PRINT': 24,
    'CALL_FUNCTION': 25,
    'RETURN_VALUE': 26,
    'NOP': 27,
    'BUILD_LIST': 28,
    'SETUP_LOOP': 29,
    'FOR_ITER': 30,
    'DEF_FUNCTION': 31,
}

OPCODES_REVERSE = {v: k for k, v in OPCODES.items()}

# Number of arguments for each opcode (by opcode number)
OPCODE_ARGS_BY_NUM = {
    1: 1,   # LOAD_CONST
    2: 1,   # LOAD
    3: 1,   # STORE
    21: 1,  # JUMP
    22: 1,  # JUMP_IF_FALSE
    30: 2,  # FOR_ITER
    24: 1,  # PRINT
    25: 2,  # CALL_FUNCTION
    28: 1,  # BUILD_LIST
    31: 2,  # DEF_FUNCTION
}

# Number of arguments for each opcode (by name)
OPCODE_ARGS = {
    'LOAD_CONST': 1,
    'LOAD': 1,
    'STORE': 1,
    'JUMP': 1,
    'JUMP_IF_FALSE': 1,
    'FOR_ITER': 2,
    'PRINT': 1,
    'CALL_FUNCTION': 2,
    'BUILD_LIST': 1,
    'DEF_FUNCTION': 2,
}

class CodeGenerator:
    """Generates bytecode from IR"""
    
    def __init__(self):
        self.bytecode = Bytecode()
        self.current_code = self.bytecode.code
    
    def generate(self, ir: IR) -> Bytecode:
        """Generate bytecode from IR"""
        # First pass: collect all constants and names
        self._collect_resources(ir)
        
        # Second pass: generate bytecode
        self._generate_code(ir.instructions)
        
        # Generate functions
        for func_name, (instrs, params) in ir.functions.items():
            old_code = self.current_code
            self.bytecode.functions[func_name] = {"code": [], "params": params}
            self.current_code = self.bytecode.functions[func_name]["code"]
            self._generate_code(instrs)
            self.current_code = old_code
        
        return self.bytecode
    
    def _collect_resources(self, ir: IR):
        """Collect constants and names from IR"""
        self._collect_from_instrs(ir.instructions)
        for instrs, _params in ir.functions.values():
            self._collect_from_instrs(instrs)
    
    def _collect_from_instrs(self, instrs: List[IRInstruction]):
        """Helper to collect from instruction list"""
        for instr in instrs:
            if instr.op == 'LOAD_CONST' and len(instr.args) > 0:
                val = instr.args[0]
                if val not in self.bytecode.constants:
                    self.bytecode.constants.append(val)
            elif instr.op in ['LOAD', 'STORE', 'CALL_FUNCTION', 'DEF_FUNCTION']:
                if len(instr.args) > 0:
                    name = instr.args[0]
                    if isinstance(name, str) and name not in self.bytecode.names:
                        self.bytecode.names.append(name)
    
    def _generate_code(self, instructions: List[IRInstruction]):
        """Generate bytecode from IR instructions"""
        # First pass: identify label positions (labels are pseudo-ops)
        label_positions = {}
        code_pos = 0
        
        for instr in instructions:
            if instr.op == 'LABEL':
                label_positions[instr.args[0]] = code_pos
            elif instr.op not in ['LABEL']:
                # Estimate bytecode size
                if instr.op in OPCODE_ARGS:
                    code_pos += 1 + OPCODE_ARGS[instr.op]
                else:
                    code_pos += 1
        
        # Update label map
        self.bytecode.label_positions.update(label_positions)
        
        # Second pass: generate actual bytecode
        for instr in instructions:
            self._emit_instruction(instr, label_positions)
    
    def _emit_instruction(self, instr: IRInstruction, label_positions: Dict[str, int]):
        """Emit a single IR instruction as bytecode"""
        op = instr.op
        
        if op == 'LABEL':
            # Skip labels (they're pseudo-ops)
            return
        
        if op == 'LOAD_CONST':
            val = instr.args[0]
            const_idx = self.bytecode.constants.index(val)
            self.current_code.append(OPCODES['LOAD_CONST'])
            self.current_code.append(const_idx)
        
        elif op == 'LOAD':
            name = instr.args[0]
            name_idx = self.bytecode.names.index(name) if name in self.bytecode.names else 0
            self.current_code.append(OPCODES['LOAD'])
            self.current_code.append(name_idx)
        
        elif op == 'STORE':
            name = instr.args[0]
            name_idx = self.bytecode.names.index(name) if name in self.bytecode.names else 0
            self.current_code.append(OPCODES['STORE'])
            self.current_code.append(name_idx)
        
        elif op == 'JUMP':
            label = instr.args[0]
            target = label_positions.get(label, 0)
            self.current_code.append(OPCODES['JUMP'])
            self.current_code.append(target)
        
        elif op == 'JUMP_IF_FALSE':
            label = instr.args[0]
            target = label_positions.get(label, 0)
            self.current_code.append(OPCODES['JUMP_IF_FALSE'])
            self.current_code.append(target)
        
        elif op == 'FOR_ITER':
            label = instr.args[0]
            varname = instr.args[1]
            target = label_positions.get(label, 0)
            name_idx = self.bytecode.names.index(varname) if varname in self.bytecode.names else 0
            self.current_code.append(OPCODES['FOR_ITER'])
            self.current_code.append(target)
            self.current_code.append(name_idx)
        
        elif op == 'CALL_FUNCTION':
            func_name = instr.args[0]
            num_args = instr.args[1]
            name_idx = self.bytecode.names.index(func_name) if func_name in self.bytecode.names else 0
            self.current_code.append(OPCODES['CALL_FUNCTION'])
            self.current_code.append(name_idx)
            self.current_code.append(num_args)
        
        elif op == 'PRINT':
            num_args = instr.args[0] if instr.args else 1
            self.current_code.append(OPCODES['PRINT'])
            self.current_code.append(num_args)
        
        elif op == 'BUILD_LIST':
            num_items = instr.args[0] if instr.args else 0
            self.current_code.append(OPCODES['BUILD_LIST'])
            self.current_code.append(num_items)
        
        elif op == 'DEF_FUNCTION':
            func_name = instr.args[0]
            # params = instr.args[1] if len(instr.args) > 1 else []
            name_idx = self.bytecode.names.index(func_name) if func_name in self.bytecode.names else 0
            self.current_code.append(OPCODES['DEF_FUNCTION'])
            self.current_code.append(name_idx)
        
        elif op == 'RETURN_VALUE':
            self.current_code.append(OPCODES['RETURN_VALUE'])
        
        elif op == 'POP':
            self.current_code.append(OPCODES['POP'])
        
        elif op == 'NOP':
            self.current_code.append(OPCODES['NOP'])
        
        elif op in OPCODES:
            self.current_code.append(OPCODES[op])
        
        else:
            raise Exception(f"Unknown IR operation: {op}")
