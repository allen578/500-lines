class interpreter(object):
    def __init__(self):
        self.const = []  # const栈，存放常数
        self.fast = []   # fast列表，存在变量
        self.fast_val = []
        
    def run_code(self, codes):
        instructions = codes["instructions"]
        for instruction in instructions:
            row_num, ins_name, idx, content = instruction
            if ins_name == "LOAD_CONST":
                self.LOAD_CONST(idx, codes['CONST'])
            elif ins_name == "LOAD_FAST":
                self.LOAD_FAST(idx)
            elif ins_name == "STORE_FAST":
                self.STORE_FAST(idx, codes['FAST'])
            elif ins_name == "BINARY_ADD":
                self.BINARY_ADD()
            elif ins_name == "BINARY_SUBTRACT":
                self.BINARY_SUBTRACT()
            elif ins_name == "RETURN_VALUE":
                self.RETURN_VALUE()
            else:
                print("This operator is not supported now! ")
               
    # 以下全是各种指令集的操作
    def LOAD_CONST(self, idx, const_list):
        """
        const_list : what_to_execute中的"CONST"列表
        idx : what_to_execute中的第三列
        """
        self.const.append(const_list[idx])
        
    def LOAD_FAST(self, idx):
        """
        读取self.fast中的变量值, 然后将值放到const中
        idx : what_to_execute中的第三列
        fast_list : what_to_execute中的变量列表
        """
        self.const.append(self.fast_val[idx]) 
    
    def STORE_FAST(self, idx, fast_list):
        """
        存储变量，发生在常数赋值给变量时, 将CONST栈顶的值放到指定的变量中
        将fast存到self.fast中
        idx : what_to_execute中的第三列
        fast_list : what_to_execute中的"FAST"列表
        """
        if fast_list[idx] not in self.fast:
            val = self.const.pop()
            self.fast.append(fast_list[idx])
            self.fast_val.append(val)
        else:  # 该变量已经存在了
            val = self.const.pop()
            self.fast_val[idx] = val
        
    def BINARY_ADD(self):
        """
        实现加法功能
        将栈顶的两个元素进行相加
        结果放回栈顶
        """
        val1 = self.const.pop()
        val2 = self.const.pop()
        self.const.append(val1 + val2)
        
    def BINARY_SUBTRACT(self):
        """
        实现减法功能
        将栈顶的元素相减
        """    
        val1 = self.const.pop()
        val2 = self.const.pop()
        self.const.append(val1 - val2)
    
    
    def RETURN_VALUE(self):
        val = self.const.pop() # 弹出栈顶元素
        print(val)

    def GET_ITER(self):
        pass
    
    def FOR_ITER(self):
        pass
    
    def CALL_FUNCTION(self):
        pass
    
    def JUMP_ABSOLUTE(self):
        pass
    