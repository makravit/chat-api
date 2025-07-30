# syntax=docker/dockerfile:1

# --- Builder stage ---
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc && rm -rf /var/lib/apt/lists/*

# Install pipenv or poetry if you use it, otherwise just requirements.txt
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --user --no-cache-dir -r requirements.txt

# --- Final stage ---
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH="/root/.local/bin:$PATH"

# Copy app source
COPY ./app ./app
COPY ./requirements.txt ./requirements.txt

# Expose port
EXPOSE 8000

# Run as non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Start the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
