# Contributing to FastAPI Chat API

Thanks for taking the time to contribute! This guide explains how to set up your environment, code standards, how to run checks locally, and what CI enforces.

## Prerequisites
- Python 3.13
- Poetry (dependency + venv manager)
- Docker (optional, for building/running the image)

Install Poetry (one-time):
- macOS (Homebrew): `brew install poetry`
- Official installer: `curl -sSL https://install.python-poetry.org | python3 -`

## Project setup
1. Clone the repository and install dependencies:
   - `poetry install`
2. Activate the virtualenv for ad‑hoc commands (optional):
   - `poetry shell`
3. Install pre-commit hooks:
   - `poetry run pre-commit install`

## Running the app

You can run the service either with Docker Compose or locally with Poetry.

### Option A — Docker Compose

- Build and start:
  ```sh
  docker compose up --build
  ```
  - Migrations are applied automatically on container startup.
  - App: http://localhost:8000 — Docs: http://localhost:8000/docs

### Option B — Local with Poetry (no Docker)

- Ensure your `.env` has a host connection string:
  ```env
  DATABASE_URL=postgresql://chatbot:chatbotpass@localhost:5432/chatbotdb
  ```
- Start the API with auto-reload:
  ```sh
  poetry run uvicorn app.main:app --reload
  ```
- Apply migrations when models change:
  ```sh
  poetry run alembic upgrade head
  ```

Notes:
- In Docker Compose, the app connects to the DB host `db` (overridden in compose).
- Locally, use `localhost` in `DATABASE_URL` for Alembic, tests, and dev server.
 - Prerequisite: ensure a local PostgreSQL instance is running and accessible at the
   configured connection string. Compose starts Postgres for you, but for local runs
   you need to manage the database yourself (or connect to another instance).

## Linting, style, and docstrings
- Ruff is the single source of truth for linting and style (including import sorting).
- Absolute imports are required; relative imports are banned by Ruff (flake8-tidy-imports).
- Docstrings follow Google style (pydocstyle convention = google) and are enforced for public modules, packages, classes, and functions under `app/**`.
- Tests, alembic, and scripts folders do not enforce docstrings.
- Run all hooks locally:
  - `poetry run pre-commit run --all-files`

## Testing
- Run the full test suite with coverage:
  - `poetry run pytest --cov=app --cov-report=term-missing --cov-report=html`
- CI enforces 100% coverage for `app/**`. Keep tests small, focused, and readable.
- Use the shared helpers in `tests/utils.py` to keep tests concise and deterministic.

## Repository structure
- `app/api/`: Route handlers (thin). Use FastAPI dependencies; avoid business logic here.
- `app/services/`: Business logic. Keep it pure/testable; unit tests target this layer.
- `app/repositories/`: Data access. Keep queries isolated and covered by focused tests.
- `app/schemas/`: Pydantic models for request/response validation.
- `app/core/`: Cross-cutting concerns (config, auth, db, logging, exceptions, handlers).
- `models/`: ORM entities.

## Migrations
- Use Alembic for DB migrations.
- Create a new migration when models change:
  - `poetry run alembic revision --autogenerate -m "your message"`
- Verify generated SQL and upgrade/downgrade paths before committing.

Rollback (downgrade) quick references:

```sh
# List history and the current DB revision
poetry run alembic history --verbose
poetry run alembic current

# Downgrade a single step
poetry run alembic downgrade -1

# Downgrade to a specific revision (replace <rev>)
poetry run alembic downgrade <rev>

# Downgrade to base (empty schema) — destructive
poetry run alembic downgrade base

# Re-apply all migrations to head after testing a rollback
poetry run alembic upgrade head
```

## Security and secrets
- Never commit secrets. Use environment variables (`.env`) for local development.
- Document new env vars in `.env.example` when introducing configuration.

## Commit and PR guidelines
- Small, focused commits.
- Include/adjust tests with behavior changes.
- Keep public docstrings up to date; follow Google style.
- Before pushing, ensure:
  - `poetry run pre-commit run --all-files` passes
  - `poetry run pytest --cov=app --cov-fail-under=100` passes
- PR checklist:
  - [ ] Tests added/updated; coverage at 100%
  - [ ] Lint + pre-commit clean
  - [ ] Docstrings for new/changed public APIs
  - [ ] `.env.example` updated (if needed)
  - [ ] Migrations added (if needed)

## CI overview
- GitHub Actions runs on push/PR to `main`:
  - Pre-commit hooks (no auto-fix)
  - Pytest with coverage; enforced threshold 100%
  - Docker image build always; push to registry only on `main` with secrets available

Questions? Open an issue or draft a PR and ask for feedback.
