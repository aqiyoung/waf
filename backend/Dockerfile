FROM python:3.11-slim

WORKDIR /app

# 禁用 passlib 的 wrap bug 检测，避免密码长度超过 72 字节的错误
ENV PASSLIB_NO_BYPASS_WRAP_BUG=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 给 start.sh 添加执行权限
RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
