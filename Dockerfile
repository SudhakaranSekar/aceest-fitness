# ---- Stage 1: Base ----
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DB_PATH=/data/aceest_fitness.db

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Stage 2: Application ----
FROM base AS app

COPY app.py .

# Create data directory for SQLite persistence
RUN mkdir -p /data

EXPOSE 5000

# Non-root user for security
RUN adduser --disabled-password --no-create-home appuser && \
    chown -R appuser /data
USER appuser

# Initialise DB then start server
ENTRYPOINT ["sh", "-c", "python -c 'from app import init_db; init_db()' && python app.py"]
