FROM python:3.11-slim

WORKDIR /app

# 禁用 passlib 的 wrap bug 检测，避免密码长度超过 72 字节的错误
ENV PASSLIB_NO_BYPASS_WRAP_BUG=1

# basic_server.py 只使用内置库，不需要安装额外依赖

COPY . .

EXPOSE 8009

CMD ["python", "basic_server.py"]
