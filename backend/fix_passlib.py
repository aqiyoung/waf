import os
import sys
import importlib

# 确保在导入 passlib 之前设置环境变量
os.environ['PASSLIB_NO_BYPASS_WRAP_BUG'] = '1'

# 尝试直接修改 passlib 库的代码
try:
    # 导入 passlib 库的模块
    from passlib.handlers import bcrypt
    
    # 保存原始的 detect_wrap_bug 函数
    original_detect_wrap_bug = bcrypt.detect_wrap_bug
    
    # 定义一个新的 detect_wrap_bug 函数，直接返回 False
    def fixed_detect_wrap_bug(ident):
        return False
    
    # 替换原始函数
    bcrypt.detect_wrap_bug = fixed_detect_wrap_bug
    print("Successfully fixed passlib detect_wrap_bug function")
except Exception as e:
    print(f"Failed to fix passlib: {e}")
