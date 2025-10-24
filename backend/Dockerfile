FROM python:3.12-slim as python-base

# 2. --- Frontend Builder ---
FROM node:20-slim as frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json ./
COPY frontend/package-lock.json ./
RUN npm install
COPY frontend./
RUN npm run build

# 3. --- Final Application Image ---
FROM python-base
WORKDIR /app
# Copy backend code from the context
COPY backend/ ./backend/
# Copy built frontend from the builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist/

# Install Python dependencies
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

# Expose port and run the application
EXPOSE 7860
CMD ["python", "app.py"]
