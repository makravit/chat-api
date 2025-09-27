# ⚠️ DISCLAIMER — PLEASE READ

This entire application was generated using GitHub Copilot in agent mode, without a single line of code written manually and without any prior experience with Python or FastAPI.

Both the application logic and automated tests were created solely through natural language instructions and iterative refinement with Copilot. This project demonstrates the power and potential of AI-assisted software development.



# AI Chatbot API

[![CI Pipeline](https://github.com/makravit/chat-api/actions/workflows/ci.yml/badge.svg)](https://github.com/makravit/chat-api/actions/workflows/ci.yml)

This project is a REST API for an AI-powered chatbot service, built with FastAPI (Python). It provides secure user registration, authentication (JWT), session management with secure refresh tokens, a profile endpoint, health/readiness endpoints, a Prometheus metrics endpoint, and a chat endpoint for interacting with an AI bot. The API is designed for extensibility and maintainability, follows industry best practices, and is fully tested (unit and integration) with 100% coverage enforced via pytest.

- Database schema is managed and versioned using Alembic migrations.
- Migrations are applied automatically in the app container and during tests.


## Purpose

Enable users to:
- Register and create an account (data stored in a real database via SQLAlchemy)
- Log in and obtain a JWT access token (with secure refresh tokens)
- Retrieve their own profile (id, name, email)
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
- Logout: `POST /api/v1/users/logout` — revokes the current session's refresh token; idempotent and returns 204 even if no active session (clears cookie)
- Logout everywhere: `POST /api/v1/users/logout-all` — revokes all refresh tokens for the user (logout everywhere)
  - Both endpoints log suspicious activity for invalid, expired, or revoked token use
- My profile: `GET /api/v1/users/me` — returns the authenticated user's profile (id, name, email)
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
- Password hashing (using Argon2id via Passlib)
- Full unit and integration test suite (pytest)
- 100% code coverage enforced (pytest-cov)
- Integration tests use Testcontainers for ephemeral PostgreSQL DBs; no Docker Compose needed for testing.
- All environment variables are loaded from a `.env` file in the project root. To set up your environment variables, copy `.env.example` to `.env` and update the values as needed:

  ```sh
  cp .env.example .env
  # Edit .env and set your secrets and configuration
  ```

> **Note:** You can configure the JWT token expiration (in minutes) using the `JWT_EXPIRE_MINUTES` environment variable. The default is 5 minutes if not set. Refresh token expiration is configurable via `REFRESH_TOKEN_EXPIRE_DAYS` (default: 1 day). The maximum refresh token lifetime is configurable via `REFRESH_TOKEN_MAX_LIFETIME_DAYS` (default: 30 days). Argon2id hashing parameters are configurable via `ARGON2_TIME_COST`, `ARGON2_MEMORY_COST` (KiB), and `ARGON2_PARALLELISM`.
>
> Identity claim: Access tokens include both `uid` (the numeric user id) and `sub` (the email). The backend resolves the current user strictly by `uid`; tokens missing `uid` are rejected.
- Alembic migration scripts (`alembic/`) and config (`alembic.ini`) are mounted into containers for Alembic to work.

## Development

See CONTRIBUTING for full details: [CONTRIBUTING.md](CONTRIBUTING.md)



## Project Structure

```
app/
  main.py         # FastAPI app entrypoint
  api/            # API route definitions (users, chat, health, metrics)
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


## Running the app locally

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
2. Ensure your local `.env` has local database settings (localhost):
  ```env
  DATABASE_HOST=localhost
  DATABASE_PORT=5432
  DATABASE_USER=chatbot
  DATABASE_PASSWORD=chatbotpass
  DATABASE_NAME=chatbotdb
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

### Type checking (Pyright)

Pyright enforces static typing across `app/**` and `tests/**`.

```sh
poetry run pyright app tests
```

Conventions used in this repo:
- Prefer `from __future__ import annotations` and modern typing (`|`, `list[T]`).
- Place type-only imports under `if TYPE_CHECKING:` to satisfy Ruff’s `TCH` rules.
- When a framework evaluates annotations at runtime (e.g., SQLAlchemy), ensure names referenced in annotations exist at runtime. For example, provide a runtime alias for modules used only in annotations, or add a targeted `# noqa: TCH003` if you choose a simpler import.


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

Pre-commit runs Ruff, Pyright, and other checks. Fixes may be applied automatically by Ruff; re-run until all hooks pass.


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

- Endpoints quick reference

| Method | Path                     | Auth          | Description |
|-------:|--------------------------|---------------|-------------|
| POST   | /api/v1/users/register   | No            | Register a new user (name, email, password) |
| POST   | /api/v1/users/login      | No            | Log in and receive JWT access token; sets secure refresh cookie |
| POST   | /api/v1/users/refresh-token | No (cookie) | Rotate refresh token (from secure cookie) and return new access token |
| POST   | /api/v1/users/logout     | Bearer        | Revoke current session’s refresh token (uses cookie); clears cookie |
| POST   | /api/v1/users/logout-all | Bearer        | Revoke all refresh tokens for the user; clears cookie |
| GET    | /api/v1/users/me         | Bearer        | Get the authenticated user’s profile (id, name, email) |
| POST   | /api/v1/chat             | Bearer        | Send a chat message to the AI bot |
| GET    | /live                    | No            | Liveness probe |
| GET    | /ready                   | No            | Readiness probe (checks DB) |
| GET    | /health                  | No            | Health check (app + DB status) |
| GET    | /metrics                 | Basic Auth    | Prometheus metrics |

- **POST /api/v1/users/register** — Register a new user (name, email, password)
- **POST /api/v1/users/login** — Log in and receive a JWT token and refresh token
  - Accepts email and password
  - On success, returns a JWT access token and sets a secure random refresh token in an HttpOnly cookie (the refresh token is not returned in the response body)
  - Multiple sessions/devices supported (no global revocation on login)
  - Refresh token is stored with session metadata (user agent, IP)
  - On failure, returns `401 Unauthorized` with a generic error message

- **POST /api/v1/users/refresh-token** — Refresh access token using a refresh token
  - Accepts a valid refresh token (from secure cookie)
  - On success, returns a new JWT access token and a new refresh token
  - Previous refresh token is invalidated (single-use)
  - Sliding expiration: expiry is extended on rotation, up to max lifetime
  - Session metadata and anomaly detection (user agent, IP)
  - Suspicious activity logging for invalid, expired, revoked, or anomalous token use
  - On failure, returns `401 Unauthorized` with a generic error message

**POST /api/v1/users/logout** — Log out and revoke the current session's refresh token
  - Requires authentication via Bearer access token; uses the refresh token from the secure cookie if present
  - Revokes only the current session's refresh token; does not revoke all sessions
  - Suspicious activity logging for invalid, expired, revoked token use
  - On success, returns `204 No Content`
  - Idempotent: returns `204 No Content` even if the refresh token is missing/invalid/expired/revoked; the cookie is cleared

**POST /api/v1/users/logout-all** — Log out everywhere (revoke all refresh tokens)
  - Revokes all refresh tokens for the user (logout everywhere)
  - Suspicious activity logging for invalid, expired, revoked token use
  - On success, returns `204 No Content`
  - Idempotent: returns `204 No Content` even if there are no active sessions/tokens to revoke; `401` is only returned when the request is unauthenticated

- **POST /api/v1/chat** — Send a chat message (requires JWT in Authorization header)
- **GET /api/v1/users/me** — Get the authenticated user's profile (id, name, email)
- **GET /live** — Liveness probe. Returns `{ "status": "alive" }` if the app is running.
- **GET /ready** — Readiness probe. Returns `{ "status": "ready" }` if the app and DB are ready, or `{ "status": "not ready" }` and HTTP 503 if not.
- **GET /health** — Detailed health check. Returns `{ "status": "ok"|"error", "db": "ok"|"down" }`.
- **GET /metrics** — Prometheus metrics endpoint. Returns service and application metrics in Prometheus text format for monitoring and observability. Use with Prometheus, Grafana, or other monitoring tools. Only expose internally or protect with authentication if public.

See the OpenAPI docs at `/docs` for full details and try out the endpoints interactively.


## Auth flows

A quick overview of how authentication and session flows work. Refresh tokens are only ever sent/stored in a secure, HttpOnly cookie; access tokens are returned in responses and used as Bearer tokens.

- Login
  - Input: email + password
  - Output: access token in response body; sets refresh token cookie (HttpOnly, Secure, SameSite=Strict)

  ```text
  Client -> Server: POST /api/v1/users/login { email, password }
  Server -> Client: 200 { access_token }
                     Set-Cookie: refresh_token=<secure_random>; HttpOnly; Secure; SameSite=Strict; Max-Age=...
  ```

- Refresh
  - Input: refresh token from secure cookie
  - Output: new access token; rotates refresh cookie (single-use; sliding expiration up to max lifetime)
  - Failure: 401 Unauthorized with generic message when missing/invalid/expired/reused

  ```text
  Client -> Server: POST /api/v1/users/refresh-token
                    Cookie: refresh_token=<current>
  Server -> Client: 200 { access_token }
                     Set-Cookie: refresh_token=<rotated>; HttpOnly; Secure; SameSite=Strict; Max-Age=...
  ```

- Logout (single session)
  - Requires: valid Bearer access token
  - Behavior: idempotent; returns 204 even if cookie is missing/invalid/expired/revoked; clears cookie

  ```text
  Client -> Server: POST /api/v1/users/logout
                    Authorization: Bearer <access>
                    Cookie: refresh_token=<may be present>
  Server -> Client: 204 No Content
                     Set-Cookie: refresh_token=; Max-Age=0; HttpOnly; Secure; SameSite=Strict
  ```

- Logout everywhere (all sessions)
  - Requires: valid Bearer access token
  - Behavior: idempotent; revokes all user refresh tokens; returns 204 even if none are active; clears cookie
  - 401 Unauthorized is only returned when the request is unauthenticated

  ```text
  Client -> Server: POST /api/v1/users/logout-all
                    Authorization: Bearer <access>
  Server -> Client: 204 No Content
                     Set-Cookie: refresh_token=; Max-Age=0; HttpOnly; Secure; SameSite=Strict
  ```


## Exception handling and error schema

This API centralizes exception handling and returns a consistent error response shape for failures:

```json
{ "detail": "Human-readable message", "code": "machine_readable_code" }
```

- Domain/service errors (subclasses of `AppError`) are mapped with appropriate HTTP statuses and codes, e.g.:
  - `invalid_credentials` — 401 Unauthorized
  - `email_already_registered` — 409 Conflict
- Framework-level `HTTPException`s are logged and returned with `code: "http_error"`.
  - If the exception has a custom detail, the JSON includes both `detail` and `code`.
  - If no custom detail is provided (i.e., `detail=None` or it equals the default HTTP status phrase such as "Unauthorized" for 401), the response omits `detail` and returns `{ "code": "http_error" }` only.
  - Any headers on the exception (e.g., `WWW-Authenticate`) are preserved on the response.
- Unhandled exceptions are logged and returned as 500 with `code: "internal_error"`.

Logout specifics:
- `/api/v1/users/logout` is idempotent. Missing/invalid/expired/used tokens do not cause a 401 response; the endpoint responds with `204 No Content` and clears the `refresh_token` cookie.
- On `invalid_credentials` scenarios generally, the API proactively clears the `refresh_token` cookie to avoid leaving stale session state on the client.
  - 204 responses return no body.


## Security Notes

- Passwords are hashed using Argon2id before storage
- Password hashing and transparent upgrades
  - Algorithm: Argon2id via Passlib (argon2-cffi). Default parameters are environment-driven and can be tuned without code changes:
    - `ARGON2_TIME_COST` (default: 3)
    - `ARGON2_MEMORY_COST` in KiB (default: 65536 — 64 MiB)
    - `ARGON2_PARALLELISM` (default: 2)
  - Rehash-on-verify: when a password is successfully verified but the stored hash is considered outdated (e.g., weaker algorithm/parameters), the hash is transparently re-computed and persisted best-effort during login. Authentication is never blocked by a failed rehash persist; the event is logged at debug level.
  - Rationale: avoids bcrypt’s 72-byte truncation pitfalls and allows progressive hardening over time without forcing password resets.
- JWT tokens are used for authentication; keep your `SECRET_KEY` safe in production
- Refresh tokens are secure random strings, single-use, rotated on each refresh, and tied to session metadata (user agent, IP)
- Sliding expiration is enforced: each rotation extends expiry up to a max lifetime
- Suspicious activity logging is implemented for all refresh token operations
- The provided Dockerfile runs the app as a non-root user for security

### Argon2 defaults (keep it simple)

To avoid environment drift and keep behavior consistent, we recommend using the same
baseline across all environments (dev, CI, prod) and only tuning if you actually
observe performance issues:

- `ARGON2_TIME_COST=3`
- `ARGON2_MEMORY_COST=65536` (64 MiB)
- `ARGON2_PARALLELISM=2`

Notes:
- Memory cost is in KiB. Higher values increase CPU/memory per hash. On very small
  runners or containers, you can temporarily reduce `ARGON2_TIME_COST` to 2 after
  measuring test duration. For most setups, the baseline above is sufficient.
- Rehash-on-verify means increasing these values later will transparently upgrade
  stored hashes on the next successful login without forcing password resets.

Auth tokens and identity:
- Access tokens include both `uid` and `sub`. The API uses `uid` as the canonical identity claim to load users by primary key. This avoids ambiguity if emails change. If a token lacks `uid` or references a non-existent user id, the request is rejected with 401.

Cookie policy: The refresh cookie lifetime is derived from `REFRESH_TOKEN_EXPIRE_DAYS` (in seconds). For security, HttpOnly, Secure, and SameSite=strict are enforced. The cookie is rotated alongside the refresh token on `/api/v1/users/refresh-token` and cleared on logout endpoints.


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
- passlib (with argon2-cffi)
- pydantic[email]
- pydantic-settings
- sqlalchemy
- psycopg2-binary
- starlette
- typing-extensions
- structlog
- alembic  # Alembic is now a production dependency for migrations
- prometheus-client

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
- pyright


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
