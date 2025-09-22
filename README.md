# ⚠️ DISCLAIMER — PLEASE READ

This entire application was generated using GitHub Copilot in agent mode, without a single line of code written manually and without any prior experience with Python or FastAPI.

Both the application logic and automated tests were created solely through natural language instructions and iterative refinement with Copilot. This project demonstrates the power and potential of AI-assisted software development.



# AI Chatbot API

[![CI Pipeline](https://github.com/makravit/chat-api/actions/workflows/ci.yml/badge.svg)](https://github.com/makravit/chat-api/actions/workflows/ci.yml)

This project is a REST API for an AI-powered chatbot service, built with FastAPI (Python). It provides secure user registration, authentication (JWT), and a chat endpoint for interacting with an AI bot. The API is designed for extensibility, maintainability, and follows industry best practices. All code is fully tested (unit and integration) with 100% coverage enforced via pytest.

- Database schema is managed and versioned using Alembic migrations.
- Migrations are applied automatically in the app container and during tests.


## Purpose

Enable users to:
- Register and create an account (data stored in a real database via SQLAlchemy)
- Log in and obtain a JWT token
- Send chat messages to an AI bot (authentication required)

See [`docs/user-stories.md`](docs/user-stories.md) for detailed requirements and acceptance criteria.



## Features

- User registration: `POST /api/v1/users/register`
- User login (JWT + refresh token): `POST /api/v1/users/login`
- Refresh access token: `POST /api/v1/users/refresh-token`
  - Secure random refresh tokens (not JWTs), single-use per session/device
  - Rotation: each refresh request invalidates the used token and issues a new one
  - Sliding expiration: expiry is extended on each rotation, up to a configurable max lifetime
  - Session metadata: user agent and IP are stored for each token
  - Suspicious activity logging: all invalid, expired, revoked token use, and user agent/IP anomalies are logged
  - Error handling: invalid, expired, or reused tokens return `401 Unauthorized` with a generic error message
Logout: `POST /api/v1/users/logout` — Revokes the current session's refresh token (requires valid token from cookie or header; does not revoke all sessions)
Logout everywhere: `POST /api/v1/users/logout-all` — Revokes all refresh tokens for the user (logout everywhere)
  - Both endpoints log suspicious activity for invalid, expired, or revoked token use
- Authenticated chat: `POST /api/v1/chat`

- Modular, production-ready FastAPI structure
- SQLAlchemy ORM for database access (PostgreSQL only)
- Pydantic for data validation and configuration management (with pydantic-settings)
- JWT authentication (using `python-jose`)
- Secure refresh token implementation:
  - Refresh tokens are secure random strings (not JWTs)
  - Only one valid refresh token per user/session/device
  - Tokens are single-use and rotated on each refresh
  - Sliding expiration: each rotation extends expiry up to a maximum lifetime
  - Session metadata (user agent, IP) is stored for each token
  - Logout endpoint supports per-session and "logout everywhere" revocation
- Password hashing (using `passlib[bcrypt]`)
- Full unit and integration test suite (pytest)
- 100% code coverage enforced (pytest-cov)
- Integration tests use Testcontainers for ephemeral PostgreSQL DBs; no Docker Compose needed for testing.
- All environment variables are loaded from a `.env` file in the project root. To set up your environment variables, copy `.env.example` to `.env` and update the values as needed:

  ```sh
  cp .env.example .env
  # Edit .env and set your secrets and configuration
  ```

> **Note:** You can configure the JWT token expiration (in minutes) using the `JWT_EXPIRE_MINUTES` environment variable. The default is 15 minutes if not set. Refresh token expiration is configurable via `REFRESH_TOKEN_EXPIRE_DAYS` (default: 7 days).
- The test database is created automatically using the `POSTGRES_MULTIPLE_DATABASES` variable and custom entrypoint scripts.
- Alembic migration scripts (`alembic/`) and config (`alembic.ini`) are mounted into containers for Alembic to work.

## Development

See CONTRIBUTING for full details: [CONTRIBUTING.md](CONTRIBUTING.md)

Quick start for contributors:

```sh
# Install dependencies (requires Poetry)
poetry install

# Install pre-commit hooks and run them
poetry run pre-commit install
poetry run pre-commit run --all-files

# Run tests with coverage (CI enforces 100%)
poetry run pytest --cov=app --cov-report=term-missing --cov-report=html
```

### Contributor checklist

Before opening a PR, please:

- [ ] Run pre-commit hooks: `poetry run pre-commit run --all-files`
- [ ] Ensure tests pass locally with 100% coverage
- [ ] Follow Ruff style rules (py313, line length 88, double quotes); no `print`/debugger
- [ ] Use absolute imports only (relative imports are banned by Ruff)
- [ ] Add Google-style docstrings for new/changed code under `app/**`
- [ ] Keep dependency constraints within-major (e.g., `>=2.7.1,<3.0.0`), and run `poetry update`
- [ ] Update docs and `.env.example` for new env vars or behavior
- [ ] Include Alembic migration if the schema changed


## Project Structure

```
app/
  main.py         # FastAPI app entrypoint
  api/            # API route definitions (users, chat)
  models/         # SQLAlchemy ORM models
  schemas/        # Pydantic schemas (request/response validation)
  services/       # Business logic (user, chat)
  core/           # Core utilities (auth, security, database)
tests/            # Unit and integration tests (pytest)
pyproject.toml    # Poetry dependency and tool configuration
poetry.lock       # Locked dependency versions
Dockerfile        # Production-ready multistage Dockerfile
docker-compose.yml # Multi-service dev/test environment
docs/
  user-stories.md   # User stories and acceptance criteria
```


## Quickstart

You can run the app in two ways:

### Option A — Docker Compose

1. Build and start the app and database with Docker Compose:
  ```sh
  docker compose up --build
  ```
  - The app will be available at [http://localhost:8000](http://localhost:8000)
  - Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
  - Database migrations are applied automatically on startup.
  - Note: Inside containers, the app connects to the database at host `db` (Compose network).

2. To stop and remove containers:
  ```sh
  docker compose down
  ```

### Option B — Run locally with Poetry

Use this when you want to develop without Docker:

1. Ensure dependencies are installed:
  ```sh
  poetry install
  ```
2. Ensure your local `.env` has a host connection string (localhost):
  ```env
  DATABASE_URL=postgresql://chatbot:chatbotpass@localhost:5432/chatbotdb
  ```
3. Run the app with auto-reload:
  ```sh
  poetry run uvicorn app.main:app --reload
  ```
  - API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
  - Apply migrations as needed:
    ```sh
    poetry run alembic upgrade head
    ```
   - Prerequisite: make sure a local PostgreSQL server is running and reachable at the
     connection string above. Docker Compose handles starting Postgres for you, but
     when running locally you must provide your own database instance.


## Dependency Management

**Poetry must be installed globally before running any project commands.**

To install Poetry (recommended method):

```sh
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

To make Poetry available in all terminal sessions, add this line to your shell profile (for zsh):

```sh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

After installing Poetry, set your project to use Python 3.13:

```sh
poetry env use 3.13
```

All dependencies are managed with Poetry. To install them:

```sh
poetry install
```
## Updating Packages

To update all dependencies to their latest allowed versions, run:

```bash
poetry update
```

This will update the packages specified in `pyproject.toml` and refresh the `poetry.lock` file. To update a specific package, use:

```bash
poetry update <package-name>
```

For more details, see the [Poetry documentation](https://python-poetry.org/docs/cli/#update).


## Database Migrations

Alembic is used for schema migrations. To create a new migration:

```sh
poetry run alembic revision --autogenerate -m "Your migration message"
```

To apply migrations:

```sh
poetry run alembic upgrade head
```

### Rollback (downgrade) examples

Sometimes you need to roll back a migration. Here are common Alembic
downgrade patterns (all commands run via Poetry):

```sh
# Show migration history (oldest → newest)
poetry run alembic history --verbose

# Show current revision applied to the database
poetry run alembic current

# Downgrade a single step (undo the last migration)
poetry run alembic downgrade -1

# Downgrade to a specific revision (replace <rev> with the revision id)
poetry run alembic downgrade <rev>

# Downgrade all the way back to base (empty schema)
poetry run alembic downgrade base

# Re-apply all migrations after a rollback
poetry run alembic upgrade head
```


## Running Tests & Code Quality

All test, lint, and formatting commands should be run via Poetry:


### Run tests

```sh
poetry run pytest
```

### Run coverage

```sh
poetry run pytest --cov=app --cov-report=term-missing --cov-report=html
```
The HTML coverage report will be available in the `htmlcov/` directory.


### Lint and format

```sh
poetry run ruff check .
poetry run ruff format .
```


### Auto-fix code style issues

To automatically fix issues detected by Ruff (including import sorting), run:

```sh
poetry run ruff check --fix .
poetry run ruff format .
```

- Ruff will auto-fix lint issues and sort imports (isort rules) when configured.
- Ruff Format applies consistent code formatting (Black-compatible).

You can run these commands before committing code or as part of your workflow to keep your codebase clean and consistent.


### Pre-commit hooks

Install and run pre-commit hooks:
```sh
poetry run pre-commit install
poetry run pre-commit run --all-files
```


### Suppress DeprecationWarnings during tests (optional)

To hide deprecation warnings in your test output, add a `pytest.ini` file to your project root with:

```ini
[pytest]
filterwarnings =
    ignore::DeprecationWarning
```

### Testing helpers

To keep tests small and consistent, use the helper factories in `tests/utils.py`:

- `make_dummy_db()`
  - Use when a DB object is required but not inspected (e.g., repositories are patched and no query/commit behavior is asserted).

- `make_db_query_first(result)`
  - Use when code under test calls `db.query(...).filter(...).first()` and you need to control the returned value.

- `make_db_query_all(results)`
  - Use when code under test calls `db.query(...).filter(...).all()` and you need to control the returned list.

- `make_db_commit_mock()`
  - Use when you want a convenient assertion that `db.commit()` was called exactly once via `db.assert_committed_once()`.

These helpers reduce ad-hoc stubs and keep tests focused on the behavior under test.

Where they’re used in this repo:
- `make_dummy_db` — see usages in `tests/unit/test_user_service.py` and `tests/unit/test_core_auth.py`
- `make_db_query_first` — see `tests/unit/test_core_auth.py::test_get_current_user_user_none`
- `make_db_query_all` — see `tests/unit/test_refresh_token_repository.py::test_get_valid_tokens_found`
- `make_db_commit_mock` — see revoke tests in `tests/unit/test_refresh_token_repository.py`

When not to use:
- Prefer tailored fakes when the test benefits from exercising nuanced behavior. For example, `tests/unit/test_user_repository.py` defines `make_db_with_users` to validate repository-specific query/filter logic and side effects.

Examples:

```python
# make_dummy_db: pass a DB placeholder when repos are patched
from tests.utils import make_dummy_db
with patch("app.services.user_service.UserRepository", return_value=repo_mock):
  result = register_user("Test", "t@example.com", "Password1!", make_dummy_db())
```

```python
# make_db_query_first: control .first() return value
from tests.utils import make_db_query_first
db = make_db_query_first(result=None)
assert RefreshTokenRepository(db).get_valid_token("nope") is None
```

```python
# make_db_query_all: control .all() return list
from tests.utils import make_db_query_all
db = make_db_query_all(results=[token1, token2])
assert RefreshTokenRepository(db).get_valid_tokens(1) == [token1, token2]
```

```python
# make_db_commit_mock: assert commit exactly once
from tests.utils import make_db_commit_mock
db = make_db_commit_mock()
RefreshTokenRepository(db).revoke_all_tokens(123)
db.assert_committed_once()
```


## House rules (style & policy)

Keep contributions aligned with these core rules (enforced by Ruff and CI):

- Python 3.13 target; Ruff target-version is py313.
- Formatting: line length 88, double quotes, spaces for indentation.
- Imports are sorted by Ruff (isort rules); prefer absolute imports; first-party is `app`.
- Docstrings: Google style required under `app/**`; tests and scripts don’t require docstrings.
- Security: Bandit rules enabled; tests may use `assert` (S101 ignored in `tests/**`).
  - Allowed per-file exceptions only:
    - `app/core/config.py`: S105 for dev/local defaults (no real secrets).
    - `app/schemas/user.py`: S105 for `TokenResponse.token_type` constant ("bearer").
- No `print` or debugger statements in committed code (T20/T10).
- Favor simple, readable code: SIM/PERF/C4 rules; McCabe complexity ≤ 10.
- Testing: 100% coverage required; prefer parametrize and clean pytest style.
- Dependencies: use within-major version ranges (e.g., `>=2.7.1,<3.0.0`).
  - Update to latest allowed versions with:

    ```sh
    poetry update
    ```


## Policy quick links

| Topic | Reference |
| --- | --- |
| Style, lint, formatting, ignores | [.github/copilot-instructions.md](.github/copilot-instructions.md) |
| Contribution workflow & guidance | [CONTRIBUTING.md](CONTRIBUTING.md) |


## API Overview

- **POST /api/v1/users/register** — Register a new user (name, email, password)
- **POST /api/v1/users/login** — Log in and receive a JWT token and refresh token
  - Accepts email and password
  - On success, returns a JWT access token and a secure random refresh token
  - Multiple sessions/devices supported (no global revocation on login)
  - Refresh token is stored with session metadata (user agent, IP)
  - On failure, returns `401 Unauthorized` with a generic error message

- **POST /api/v1/users/refresh-token** — Refresh access token using a refresh token
  - Accepts a valid refresh token (from cookie or header)
  - On success, returns a new JWT access token and a new refresh token
  - Previous refresh token is invalidated (single-use)
  - Sliding expiration: expiry is extended on rotation, up to max lifetime
  - Session metadata and anomaly detection (user agent, IP)
  - Suspicious activity logging for invalid, expired, revoked, or anomalous token use
  - On failure, returns `401 Unauthorized` with a generic error message

**POST /api/v1/users/logout** — Log out and revoke the current session's refresh token
  - Requires a valid refresh token (from cookie or header)
  - Revokes only the current session's refresh token; does not revoke all sessions
  - Suspicious activity logging for invalid, expired, revoked token use
  - On success, returns `204 No Content`
  - On failure (missing or invalid token), returns `401 Unauthorized` with a generic error message

**POST /api/v1/users/logout-all** — Log out everywhere (revoke all refresh tokens)
  - Revokes all refresh tokens for the user (logout everywhere)
  - Suspicious activity logging for invalid, expired, revoked token use
  - On success, returns `204 No Content`
  - On failure (no valid tokens), returns `401 Unauthorized` with a generic error message

- **POST /api/v1/chat** — Send a chat message (requires JWT in Authorization header)
- **GET /live** — Liveness probe. Returns `{ "status": "alive" }` if the app is running.
- **GET /ready** — Readiness probe. Returns `{ "status": "ready" }` if the app and DB are ready, or `{ "status": "not ready" }` and HTTP 503 if not.
- **GET /health** — Detailed health check. Returns `{ "status": "ok"|"error", "db": "ok"|"down" }`.
- **GET /metrics** — Prometheus metrics endpoint. Returns service and application metrics in Prometheus text format for monitoring and observability. Use with Prometheus, Grafana, or other monitoring tools. Only expose internally or protect with authentication if public.

See the OpenAPI docs at `/docs` for full details and try out the endpoints interactively.


## Security Notes

- Passwords are hashed using bcrypt before storage
- JWT tokens are used for authentication; keep your `SECRET_KEY` safe in production
- Refresh tokens are secure random strings, single-use, rotated on each refresh, and tied to session metadata (user agent, IP)
- Sliding expiration is enforced: each rotation extends expiry up to a max lifetime
- Suspicious activity logging is implemented for all refresh token operations
- The provided Dockerfile runs the app as a non-root user for security

Cookie policy: The refresh cookie lifetime is derived from REFRESH_TOKEN_EXPIRE_DAYS (in seconds). For security, HttpOnly, Secure, and SameSite=strict are hardcoded and cannot be relaxed. The cookie is rotated alongside the refresh token on /refresh-token.


## Extending the App

- Add more endpoints, business logic, or AI integrations as needed
- Write additional tests in the `tests/` folder


## Dependencies

All dependencies (production and development) are declared in `pyproject.toml` and locked in `poetry.lock`. Use `poetry add <package>` or `poetry add --group dev <package>` to manage them.

Key production dependencies:
- Python 3.13+
- fastapi
- uvicorn[standard]
- python-jose
- passlib[bcrypt]
- pydantic[email]
- pydantic-settings
- sqlalchemy
- psycopg2-binary
- starlette
- typing-extensions
- structlog
- alembic  # Alembic is now a production dependency for migrations

Key development dependencies:
- cython
- httpx
- pre-commit
- pytest
- pytest-asyncio
- pytest-cov
- ruff
- setuptools
- testcontainers[postgresql]
- wheel


## Poetry & Docker builds

If you change dependencies in `pyproject.toml`, always run:

```sh
poetry lock
```

before building Docker images. This ensures `poetry.lock` matches your dependencies and avoids build errors.


## CI/CD

- Automated tests, linting, import sorting, and code style (via Ruff) are enforced via pre-commit hooks and GitHub Actions.
- The CI pipeline runs pre-commit checks and tests on every push and pull request, ensuring code quality and consistency before builds.
- Production Docker images are built using a multistage Dockerfile that only installs production dependencies from Poetry.
- Development dependencies are not included in the production image for security and size.


## License

MIT


## Metrics Endpoint Authentication

The `/metrics` endpoint is protected with Basic Authentication. Credentials are loaded from environment variables in your `.env` file. See `.env.example` for required variables and example values.

These variables are also passed to the app container via `docker-compose.yml`.

To access `/metrics`, use your monitoring tool (e.g., Prometheus) with the configured username and password. Update these values in `.env` for production security.

Example request:

```sh
curl -u <METRICS_USER>:<METRICS_PASS> http://localhost:8000/metrics
```

If authentication fails, the endpoint returns HTTP 401 Unauthorized.

---

## Securing Sensitive Information in Production


This application uses several sensitive values (e.g., database credentials, JWT secret keys, metrics credentials) loaded from environment variables in the `.env` file. **Never commit real secrets to version control.**

For production deployments, use secure secret management solutions such as:

- **Azure Key Vault** (recommended for Azure)
- **AWS Secrets Manager**
- **HashiCorp Vault**
- **Docker secrets** (for Swarm)
- **Kubernetes secrets**

Configure your deployment platform to inject secrets as environment variables at runtime, and restrict access to only necessary services. Rotate secrets regularly and audit access.

For more details, see:
- [Azure Key Vault documentation](https://learn.microsoft.com/en-us/azure/key-vault/general/overview)
- [12 Factor App: Store config in the environment](https://12factor.net/config)
