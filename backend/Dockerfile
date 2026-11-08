# Backend image for the FIFA World Cup Intelligence Platform.
# Read-only app: the data is a committed SQLite file baked into the image, so no
# external database is required. Works on Render, Fly.io, Hugging Face Spaces, etc.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code + the baked-in SQLite database (app/data/fifa.db)
COPY app ./app

# Production defaults (override CORS_ORIGINS in the host dashboard).
ENV DATABASE_URL="sqlite+aiosqlite:////app/app/data/fifa.db" \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO

EXPOSE 8000

# Hosts (Render/Fly/HF) inject $PORT; default to 8000 locally.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
