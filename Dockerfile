# 1. --- Python 基础镜像 ---
FROM python:3.10-slim as python-base
# 设置工作目录
WORKDIR /app

# 2. --- Node.js 构建器 ---
FROM node:alpine as frontend-builder
WORKDIR /app/frontend
# 复制 package 文件和 LOCK 文件
COPY frontend/package.json ./
COPY frontend/package-lock.json ./
# 使用 npm ci (Clean Install)
RUN npm ci
# 复制所有前端代码并构建
COPY frontend/. ./
RUN npm run build

# 3. --- 最终的 Python 应用镜像 ---
FROM python-base
# 复制后端依赖文件并安装
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# 复制后端代码
COPY backend/. ./backend/
# 从构建器阶段复制前端静态文件
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist/

# 暴露端口
EXPOSE 7860

CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--chdir", "backend", "app:app"]