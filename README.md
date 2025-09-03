# ⚠️ DISCLAIMER — PLEASE READ

This entire application was generated using GitHub Copilot in agent mode, without a single line of code written manually and without any prior experience with Python or FastAPI.

Both the application logic and automated tests were created solely through natural language instructions and iterative refinement with Copilot. This project demonstrates the power and potential of AI-assisted software development.



# AI Chatbot API

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

- User registration: `POST /users/register`
- User login (JWT): `POST /users/login`
- Authenticated chat: `POST /chat`

- Modular, production-ready FastAPI structure
- SQLAlchemy ORM for database access (PostgreSQL only)
- Pydantic for data validation and configuration management (with pydantic-settings)
- JWT authentication (using `python-jose`)
- Password hashing (using `passlib[bcrypt]`)
- Full unit and integration test suite (pytest)
- 100% code coverage enforced (pytest-cov)
- Integration tests use Testcontainers for ephemeral PostgreSQL DBs; no Docker Compose needed for testing.
- All environment variables are loaded from a `.env` file in the project root. To set up your environment variables, copy `.env.example` to `.env` and update the values as needed:

  ```sh
  cp .env.example .env
  # Edit .env and set your secrets and configuration
  ```
- The test database is created automatically using the `POSTGRES_MULTIPLE_DATABASES` variable and custom entrypoint scripts.
- Alembic migration scripts (`alembic/`) and config (`alembic.ini`) are mounted into containers for Alembic to work.


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

1. Build and start the app and database with Docker Compose:
   ```sh
   docker compose up --build
   ```
   - The app will be available at [http://localhost:8000](http://localhost:8000)
   - Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Database migrations are applied automatically on startup.

2. To stop and remove containers:
   ```sh
   docker compose down
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
poetry run isort .
poetry run ruff .
```


### Auto-fix code style issues


To automatically fix issues detected by Ruff and isort, run:

```sh
poetry run ruff check --fix .
poetry run isort .
```

- Ruff will auto-fix most lint and formatting issues.
- isort will auto-fix import sorting and formatting.

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


## API Overview

- **POST /api/v1/users/register** — Register a new user (name, email, password)
- **POST /api/v1/users/login** — Log in and receive a JWT token
- **POST /api/v1/chat** — Send a chat message (requires JWT in Authorization header)
- **GET /live** — Liveness probe. Returns `{ "status": "alive" }` if the app is running.
- **GET /ready** — Readiness probe. Returns `{ "status": "ready" }` if the app and DB are ready, or `{ "status": "not ready" }` and HTTP 503 if not.
- **GET /health** — Detailed health check. Returns `{ "status": "ok"|"error", "db": "ok"|"down" }`.
- **GET /metrics** — Prometheus metrics endpoint. Returns service and application metrics in Prometheus text format for monitoring and observability. Use with Prometheus, Grafana, or other monitoring tools. Only expose internally or protect with authentication if public.

See the OpenAPI docs at `/docs` for full details and try out the endpoints interactively.


## Security Notes

- Passwords are hashed using bcrypt before storage
- JWT tokens are used for authentication; keep your `SECRET_KEY` safe in production
- The provided Dockerfile runs the app as a non-root user for security


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
- isort
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

- Automated tests, linting, import sorting (isort), and code style (ruff) are enforced via pre-commit hooks and GitHub Actions.
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
