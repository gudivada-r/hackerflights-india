# Use slim Python 3.11 (fixes the 3.8 type hint issues entirely)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (cached layer)
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Create a writable directory for SQLite
RUN mkdir -p /data

# Cloud Run injects PORT env var — expose it
ENV PORT=8080
ENV DB_PATH=/data/hackerflights.db

EXPOSE 8080

# Start command — reads $PORT from environment
CMD ["sh", "-c", "python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
