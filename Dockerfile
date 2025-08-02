# syntax=docker/dockerfile:1

## --- Builder stage ---
FROM python:3.13-slim-bullseye AS builder

WORKDIR /app

## Install build dependencies for wheels
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc && rm -rf /var/lib/apt/lists/*


## Copy Poetry files and install Poetry
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi


## Remove build dependencies to reduce image size
RUN apt-get purge -y --auto-remove build-essential gcc && rm -rf /var/lib/apt/lists/*

## --- Final stage ---
FROM python:3.13-slim-bullseye

WORKDIR /app


## Copy app source
COPY ./app ./app
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi


## Expose port
EXPOSE 8000


## Run as non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser


## Start the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
