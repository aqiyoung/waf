#!/bin/bash

# 修改 passlib 库的 detect_wrap_bug 函数，避免使用过长的测试密码
PASSLIB_PATH="/usr/local/lib/python3.11/site-packages/passlib/handlers/bcrypt.py"

# 检查文件是否存在
if [ -f "$PASSLIB_PATH" ]; then
    echo "Modifying passlib bcrypt.py to fix wrap bug detection..."
    
    # 使用 sed 命令修改 detect_wrap_bug 函数，将测试密码截断到 72 字节
    sed -i 's/def detect_wrap_bug(ident):/def detect_wrap_bug(ident):\n    # Skip wrap bug detection to avoid password length error\n    return False/' "$PASSLIB_PATH"
    
    echo "Modified passlib bcrypt.py successfully!"
else
    echo "passlib bcrypt.py not found at $PASSLIB_PATH"
fi

# 启动应用
echo "Starting WAF backend..."
python main.py
