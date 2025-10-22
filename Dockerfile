FROM ubuntu:latest
LABEL authors="MarkBai"

# 1. 使用官方 Python 基础镜像
FROM python:3.10-slim

# 2. 设置工作目录
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 复制所有项目文件到工作目录

COPY . .

# 5. 声明服务端口
EXPOSE 7860

# 6. 配置启动命令 (ENTRYPOINT)

ENTRYPOINT ["python", "app.py"]