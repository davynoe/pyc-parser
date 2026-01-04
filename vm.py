"""
Virtual Machine - Executes bytecode
Stack-based execution engine
"""

from codegen import Bytecode, OPCODES, OPCODE_ARGS
from typing import Any, Dict, List, Optional

class VM:
    """Stack-based virtual machine"""
    
    def __init__(self, bytecode: Bytecode):
        self.bytecode = bytecode
        self.stack: List[Any] = []
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, 'FunctionObject'] = {}
        self.pc = 0  # Program counter
        self.code = bytecode.code
        self.halted = False
        self.return_value = None
        self.loop_stack: List[Dict] = []  # Stack of loop contexts
    
    def execute(self) -> Any:
        """Execute the bytecode"""
        self.pc = 0
        self.code = self.bytecode.code
        
        while self.pc < len(self.code) and not self.halted:
            self._execute_instruction()
        
        return self.return_value
    
    def _execute_instruction(self):
        """Execute a single bytecode instruction"""
        opcode = self.code[self.pc]
        self.pc += 1
        
        # Opcodes
        if opcode == OPCODES['LOAD_CONST']:
            const_idx = self.code[self.pc]
            self.pc += 1
            self.stack.append(self.bytecode.constants[const_idx])
        
        elif opcode == OPCODES['LOAD']:
            name_idx = self.code[self.pc]
            self.pc += 1
            var_name = self.bytecode.names[name_idx]
            if var_name in self.variables:
                self.stack.append(self.variables[var_name])
            else:
                raise Exception(f"Undefined variable: {var_name}")
        
        elif opcode == OPCODES['STORE']:
            name_idx = self.code[self.pc]
            self.pc += 1
            var_name = self.bytecode.names[name_idx]
            value = self.stack.pop()
            self.variables[var_name] = value
        
        elif opcode == OPCODES['POP']:
            self.stack.pop()
        
        elif opcode == OPCODES['ADD']:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left + right)
        
        elif opcode == OPCODES['SUB']:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left - right)
        
        elif opcode == OPCODES['MUL']:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left * right)
        
        elif opcode == OPCODES['DIV']:
            right = self.stack.pop()
            left = self.stack.pop()
            if right == 0:
                raise Exception("Division by zero")
            # Integer division
            self.stack.append(left // right if isinstance(left, int) and isinstance(right, int) else left / right)
        
        elif opcode == OPCODES['MOD']:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left % right)
        
        elif opcode == OPCODES['NEGATE']:
            value = self.stack.pop()
            self.stack.append(-value)
        
        elif opcode == OPCODES['POS']:
            value = self.stack.pop()
            self.stack.append(+value)
        
        elif opcode == OPCODES['NOT']:
            value = self.stack.pop()
            self.stack.append(not value)
        
        elif opcode == OPCODES['EQ']:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left == right)
        
        elif opcode == OPCODES['NEQ']:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left != right)
        
        elif opcode == OPCODES['LT']:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left < right)
        
        elif opcode == OPCODES['GT']:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left > right)
        
        elif opcode == OPCODES['LE']:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left <= right)
        
        elif opcode == OPCODES['GE']:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left >= right)
        
        elif opcode == OPCODES['AND']:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left and right)
        
        elif opcode == OPCODES['OR']:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left or right)
        
        elif opcode == OPCODES['JUMP']:
            target = self.code[self.pc]
            self.pc = target
        
        elif opcode == OPCODES['JUMP_IF_FALSE']:
            target = self.code[self.pc]
            self.pc += 1
            condition = self.stack.pop()
            if not condition:
                self.pc = target
        
        elif opcode == OPCODES['PRINT']:
            num_args = self.code[self.pc]
            self.pc += 1
            args = []
            for _ in range(num_args):
                args.insert(0, self.stack.pop())
            print(*args)
        
        elif opcode == OPCODES['CALL_FUNCTION']:
            func_name_idx = self.code[self.pc]
            self.pc += 1
            num_args = self.code[self.pc]
            self.pc += 1
            
            func_name = self.bytecode.names[func_name_idx]
            
            if func_name in self.functions:
                func_obj = self.functions[func_name]
                # Get arguments from stack
                args = []
                for _ in range(num_args):
                    args.insert(0, self.stack.pop())
                
                # Call function
                result = func_obj.call(self, args)
                self.stack.append(result)
            else:
                raise Exception(f"Undefined function: {func_name}")
        
        elif opcode == OPCODES['RETURN_VALUE']:
            self.return_value = self.stack.pop() if self.stack else None
            self.halted = True
        
        elif opcode == OPCODES['NOP']:
            pass
        
        elif opcode == OPCODES['BUILD_LIST']:
            num_items = self.code[self.pc]
            self.pc += 1
            items = []
            for _ in range(num_items):
                items.insert(0, self.stack.pop())
            self.stack.append(items)
        
        elif opcode == OPCODES['SETUP_LOOP']:
            pass
        
        elif opcode == OPCODES['FOR_ITER']:
            target = self.code[self.pc]
            self.pc += 1
            var_idx = self.code[self.pc]
            self.pc += 1
            
            var_name = self.bytecode.names[var_idx]
            
            # For now, just a simple implementation
            pass
        
        elif opcode == OPCODES['DEF_FUNCTION']:
            func_name_idx = self.code[self.pc]
            self.pc += 1
            func_name = self.bytecode.names[func_name_idx]
            
            if func_name in self.bytecode.functions:
                func_entry = self.bytecode.functions[func_name]
                func_code = func_entry.get("code", [])
                func_params = func_entry.get("params", [])
                self.functions[func_name] = FunctionObject(func_name, func_code, func_params, self.bytecode)
        
        else:
            raise Exception(f"Unknown opcode: {opcode}")

class FunctionObject:
    """Represents a callable function"""
    
    def __init__(self, name: str, code: List[int], params: List[str], bytecode: Bytecode):
        self.name = name
        self.code = code
        self.params = params
        self.bytecode = bytecode
    
    def call(self, vm: 'VM', args: List[Any]) -> Any:
        """Execute the function"""
        # Save VM state
        old_pc = vm.pc
        old_code = vm.code
        old_halted = vm.halted
        old_return = vm.return_value
        old_vars = vm.variables
        
        # New execution context
        vm.pc = 0
        vm.code = self.code
        vm.halted = False
        vm.return_value = None
        # Shallow copy of variables for isolation
        vm.variables = old_vars.copy()
        
        # Bind parameters to arguments
        for idx, param in enumerate(self.params):
            vm.variables[param] = args[idx] if idx < len(args) else None
        
        # Execute function code
        while vm.pc < len(vm.code) and not vm.halted:
            vm._execute_instruction()
        
        result = vm.return_value
        
        # Restore VM state
        vm.pc = old_pc
        vm.code = old_code
        vm.halted = old_halted
        vm.return_value = old_return
        vm.variables = old_vars
        
        return result if result is not None else None
