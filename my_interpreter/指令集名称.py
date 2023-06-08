# 将常见的指令集的名字列在这里，然后为了之后的what_to_execute做准备
name = [
    "LOAD_CONST",     # 加载常数，主要是数值和字符串
    "LOAD_FAST",      # 加载变量，主要是自己定义的变量
    "LOAD_GLOBAL"     # 加载全局变量, 比如print，range等都是global
    
    "STORE_FAST",     # 存储变量，发生在常数赋值给变量时, 将CONST栈顶的值放到指定的变量中
    
    "BINARY_ADD",     # +运算，即普通的加法
    "BINARY_MULTIPLY",# 运算符，即普通的乘法
    "BINARY_MODULO",  # %运算    
    
    "RETURN_VALUE",   # 函数最后的返回值

    # 下面是for循环中出现的
    "GET_ITER",       # *生成一个迭代器
    "FOR_ITER",       # *进行循环迭代
    "JUMP_ABSOLUTE",  # 跳转迭代
    
    # 下面是while循环中出现的
    "COMPARE_OP",
    "POP_JUMP_IF_FALSE",
    "CALL_FUNCTION",
    
]


# *一些构思
"""
针对 CONST 写一个 [] 来存储所有的 CONST
针对 FAST  写一个 [] 来存储所有的 FAST
针对 FAST的变量, 再写一个FAST_val = [] 来保存每一个变量的值, 方便后续调用的时候继续使用

需不需要针对GLOBAL写一个呢, 我觉得不需要吧


基础的版本：

一个类: 
class interpreter:
    def __init__(self):
        self.const = []    # 常量栈
        self.fast  = []    # 变量数组
        self.fast_val = [] # 变量数组的值
    
    def run_code(self, codes):
        # codes就是反汇编出来的结果, 然后自己构建一个结构, 方便后面进行读取各种指令
        for code in codes:  # 对codes进行遍历
            获取当前的指令集
            判断这个指令集是否支持
            支持就实施这一步的操作
            不支持就直接报错
            
        
    
    # 之后就是各种指令集的堆叠
    def LOAD_CONST(self, x):
        pass
    
    def LOAD_FAST(self, x):
        pass
        
"""



# *codes的格式
"""
codes的每一个数据主要有四个部分: 
    行号row_num,     int 
    指令instruction, str
    第几个num,       int
    内容content      str






"""



# *如何实现需要跳转的指令?
"""


"""