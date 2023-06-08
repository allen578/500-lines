import types
import inspect
import dis
import sys
import collections

Block = collections.namedtuple("Block", "type, handler, stack_height")

class VirtualMachineError(Exception):
    pass


class VirtualMachine(object):
    def __init__(self):
        self.frames = []  # The call stack of frames
        self.frame = None
        self.return_value = None
        self.last_exception = None
    
    def run_code(self, code, global_names=None, local_names=None):
        """An entry point to execute code using the virtual machine."""
        frame = self.make_frame(code, global_names=global_names, 
                                local_names=local_names)
        self.run_frame(frame)
        
    # Frame manipulation
    def make_frame(self, code, callargs={}, global_names=None, local_names=None):
        if global_names is not None and local_names is not None:
            # 如果提供了全局空间和局部空间
            local_names = global_names # 使用全局命名空间作为局部命名空间
        elif self.frames:
            # 如果已经存在帧对象（非全局作用域）
            global_names = self.frame.global_names  # 使用当前帧的全局命令空间
            local_names = {}         # 创建一个空的局部命名空间
        else:
            # 如果是全局作用域
            global_names = local_names = {
                '__builtin__' : __builtins__,   # 内置模块的命令空间
                '__name__' : '__main__',        # 模块的名称
                '__doc__' : None,               # 模块的文档字符串
                '__package__' : None,           # 模块的包名
            }
        local_names.update(callargs)            # 更新局部命名空间，将调用参数添加进去
        frame = Frame(code, global_names, local_names, self.frame) # 创建帧对象
        return frame  # 返回帧对象
    
    # 推入帧
    def push_frame(self, frame):
        self.frames.append(frame)
        self.frame = frame
    
    # 弹出帧
    def pop_frame(self):
        self.frame.pop()
        if self.frames:
            self.frame = self.frames[-1]
        else:
            self.frame = None
    
    def run_frame(self, frame):
        """
        Run a frame until it returns (somehow).
        Exceptions are raised, the return value is returned.
        """
        self.push_frame(frame)
        while True:
            byte_name, arguments = self.parse_byte_and_args()
            
            why = self.dispath(byte_name, arguments)
            
            # Deal with any block management we need to do
            while why and frame.block_stack:
                why = self.manage_block_stack(why)
            
            if why:
                break
        self.pop_frame()
        
        if why == 'exception':
            exc, val, tb = self.last_exception
            e = exc(val)
            e.__traceback__ = tb
            raise e
        
        return self.return_value
        
        
    # Data stack manipulation  数据栈的操作
    def top(self):
        return self.frame.stack[-1]
    
    def pop(self):
        return self.frame.stack.pop()

    def push(self, *vals):
        self.frame.stack.extend(vals)
    
    def popn(self, n):
        """
        一次弹出n个数值
        Pop a number of values from the stack.
        A list of `n` values is returned, the deepest value first.
        """
        if n:
            ret = self.frame.stack[-n:]
            self.frame.stack[-n:] = []  # 这样就相当于将后面n个元素都删除了
            return ret
        else:
            return []
    
    def parse_byte_and_args(self):
        f = self.frame
        oppffset = f.last_instruction  # 获取当前帧的最后一个指令
        byteCode = f.code_obj.co_code[oppffset]  
        f.last_instruction += 1
        byte_name = dis.opname[byteCode]
        if byteCode >= dis.HAVE_ARGUMENT:
            # 字节码需要参数的情况
            arg = f.code.obj.co_code[f.last_instruction: f.last_instruction + 2]
            # 从字节码中获取参数值
            f.last_instruction += 2 # 将指令指针向后移动两位
            arg_val = arg[0] + (arg[1] * 256)
            if byteCode in dis.hasconst: # 常量引用
                arg = f.code_obj.co_consts[arg_val]
            elif byteCode in dis.hasname:  # 名称引用
                arg = f.code_obj.co_names[arg_val]  # 根据参数值获取名称对象
            elif byteCode in dis.haslocal:  # 局部变量引用
                arg = f.code_obj.co_varnames[arg_val]
            elif byteCode in dis.hasjrel: # 相对跳转
                arg = f.last_instruction + arg_val  # 计算相对跳转的目标地址
            else:
                arg = arg_val  # 参数值直接赋给arg
            argument = [arg]   # 将参数放入列表中
        else:
            argument = []  # 无参数情况
        return byte_name, argument # 返回指令名称和参数

    def dispath(self, byte_name, argument):
        why = None
        try:
            bytecode_fn = getattr(self, 'byte_%s' % byte_name, None)
            if bytecode_fn is None:
                if byte_name.startswith('UNARY_'):
                    self.unaryOperator(byte_name[6:])
                elif byte_name.startswith(['BINARY_']):
                    self.biinaryOperator(byte_name[7:])
                else:
                    raise VirtualMachineError(
                        "unsupported bytecode type: %s" %byte_name
                    )
            else:
                why = bytecode_fn(*argument)
        except:
            # deal with exceptions encountered while executing the op.
            self.last_exception = sys.exc_info()[:2] + (None,)
            why = 'exception'
        
        return why

    # Block stack manipulation
    
    def push_block(self, b_type, handler=None):
        level = len(self.frame.stack)
        self.frame.block_stack.append(Block(b_type, handler, stack_height))  # 这个stack_height未定义，不知道为何
    
    def pop_block(self):
        return self.frame.block_stack.pop()
    
    def unwind_block(self, block):
        """Unwind the values on the data stack corresponding to a given block"""
        if block.type == 'except-handler':
            # The exception itself is on the stack as type, value, and traceback.
            offset = 3
        else:
            offset = 0
        
        while len(self.frame.stack) > block.level + offset:
            self.pop()
        
        if block.type == 'except-handler':
            traceback, value, exctype = self.popn(3)
            self.last_exception = exctype, value, traceback
            
        
    def manage_block_stack(self, why):
        """ """
        frame = self.frame
        block = frame.block_stack[-1]
        if block.type == 'loop' and why == 'continue':
            self.jump(block.handler)
            why = None
            return why
        
        self.pop_block()
        self.unwind_block(block)
        
        if block.type == 'loop' and why == 'break':
            why = None
            self.jump(block.handler)
            return why
        
        if (block.type in ['setup-except', 'finally'] and why == 'exception'):
            self.push_block('except-handler')
            exctype, value, tb = self.last_exception
            self.push(tb, value, exctype)
            self.push(tb, value, exctype)  # yes, twice
            why = None
            self.jump(block.handler)
            return why
        
        elif block.type == 'finally':
            if why in ('return', 'continue'):
                self.push(self.return_value)
            
            self.push(why)
            
            why = None
            self.jump(block.handler)
            return why
        return why
    
    


class Frame(object):
    def __init__(self, code_obj, gloabl_names, local_names, prev_frame):
        self.code_obj = code_obj
        self.global_names = gloabl_names
        self.local_names = local_names
        self.prev_frame = prev_frame
        self.stack = []
        if prev_frame:
            self.builtin_names = prev_frame.builtin_names
        else:
            self.builtin_names = local_names['__builtins__']
            if hasattr(self.builtin_names, '__dict__'):
                self.builtin_names = self.builtin_names.__dict__
        
        self.last_instruction = 0
        self.block_stack = []
        
            
class Function(object):
    """
    Create a realistic function object, defining the things the interpreter expects.
    """
    __slots__ = [
        'func_code', 'func_name', 'func_defaults', 'func_globals',
        'func_locals', 'func_dict', 'func_closure',
        '__name__', '__dict__', '__doc__', '_vm', '_func',
    ]
    
    def __init__(self, name, code, globs, defaults, closure, vm):
        """You don't need to follow this closely to understand the interpreter."""
        self._vm = vm
        self.func_code = code
        self.func_name = self.__name__ = name or code.co_name
        self.func_defaults = tuple(defaults)
        self.func_globals = globs
        self.func_locals = self._vm.frame.f_locals
        self.__dict__ = {}
        self.func_closure = closure
        self.__doc__ = code.co_consts[0] if code.co_consts else None
        
        # Sometimes, we need a real Python function, This is for that.
        kw = {
            'argdefs' : self.func_defaults,
        }
        if closure:
            kw['closure'] = tuple(make_cell(0) for _ in closure)
        self._func = types.FunctionType(code, globs, **kw)
        
    def __call__(self, *args, **kwargs):
        """When calling a function, make a new frame and run it"""
        callargs = inspect.getcallargs(self._func, *args, **kwargs)
        frame = self._vm.make_frames(
            self.func_code, callargs, self.func_globals, {}
        )
        return self._vm.run_frame(frame)
        
        
def make_cell(value):
    """Create a real Python closure and grab a cell."""
    fn = (lambda x: lambda: x)(value)
    return fn.__closure__[0]

