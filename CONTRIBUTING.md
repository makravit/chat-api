# Contributing to FastAPI Chat API (concise)

Thanks for contributing! This document keeps only the essentials and points to the README for full details.

For architecture, setup, run modes (Docker vs local), environment variables, and migration workflows, see README.md.

## Prerequisites
- Python 3.13
- Poetry (dependency + virtualenv)
- Docker (optional)

Install Poetry (one-time): see README for commands or use Homebrew on macOS:
```sh
brew install poetry
```

## Quick start
```sh
poetry install
poetry run pre-commit install
```

To run the app or database locally (and for Docker Compose usage), follow the instructions in README.md.

## Local checks (before every commit)
```sh
poetry run pre-commit run --all-files
poetry run ruff check .
poetry run ruff format .
poetry run pyright app tests
poetry run pytest --cov=app --cov-report=term-missing --cov-report=html
```

Guidelines:
- Style: Ruff is canonical (including import sorting). Absolute imports only.
- Docstrings: Google style for public modules/classes/functions under `app/**`.
- Typing: Pyright must pass with zero errors (app and tests).
  - Use `from __future__ import annotations`.
  - Put type-only imports under `if TYPE_CHECKING:`.
  - For frameworks that evaluate annotations at runtime (e.g., SQLAlchemy), ensure referenced names exist at runtime (runtime alias) or use a minimal targeted ignore where appropriate.

## Tests
- Keep tests small and focused. Use helpers in `tests/utils.py`.
- CI expects 100% coverage for `app/**`.

## Migrations
- Alembic is used for migrations. See README for the full workflow.

## Security
- Never commit secrets. Use environment variables (`.env`).
- Update `.env.example` when introducing new config.

## Pull requests
- Small, focused changes with tests.
- Ensure the local checks above pass.
- Include docstrings for new/changed public APIs.
- Add migrations or `.env.example` updates when needed.

## CI (summary)
- On push/PR to `main`:
  - Pre-commit hooks
  - Pytest with coverage (100% enforced)
  - Build Docker image (push from `main` when secrets available)

Questions? Open an issue or a draft PR and ask for feedback.
