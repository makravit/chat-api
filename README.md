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

See [`user-stories.md`](user-stories.md) for detailed requirements and acceptance criteria.

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
- All environment variables (e.g., `DATABASE_URL`, `SECRET_KEY`, `POSTGRES_USER`, etc.) are loaded from a `.env` file in the project root.
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
requirements.txt  # Python dependencies
Dockerfile        # Production-ready multistage Dockerfile
docker-compose.yml # Multi-service dev/test environment
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



## Database Migrations

Alembic is used for schema migrations. To create a new migration:

```bash
alembic revision --autogenerate -m "Your migration message"
```

To apply migrations:

```bash
alembic upgrade head
```





## Running Tests (Local Environment)

1. Set up your Python environment:
   ```sh
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. Run all tests:
   ```sh
   pytest --cov=app --cov-report=term-missing --cov-report=html tests/unit tests/integration
   ```
   Testcontainers will manage the test database automatically during local pytest runs.

   The HTML coverage report will be available in the `htmlcov/` directory.

## API Overview

- **POST /api/v1/users/register** — Register a new user (name, email, password)
- **POST /api/v1/users/login** — Log in and receive a JWT token
- **POST /api/v1/chat** — Send a chat message (requires JWT in Authorization header)
- **GET /live** — Liveness probe. Returns `{ "status": "alive" }` if the app is running.
- **GET /ready** — Readiness probe. Returns `{ "status": "ready" }` if the app and DB are ready, or `{ "status": "not ready" }` and HTTP 503 if not.
- **GET /health** — Detailed health check. Returns `{ "status": "ok"|"error", "db": "ok"|"down" }`.

See the OpenAPI docs at `/docs` for full details and try out the endpoints interactively.


## Security Notes

- Passwords are hashed using bcrypt before storage
- JWT tokens are used for authentication; keep your `SECRET_KEY` safe in production
- The provided Dockerfile runs the app as a non-root user for security


## Extending the App

- Add more endpoints, business logic, or AI integrations as needed
- Write additional tests in the `tests/` folder

## Requirements


- Python 3.8+
- FastAPI
- Uvicorn
- SQLAlchemy
- passlib[bcrypt]
- python-jose
- pydantic
- psycopg2-binary (for PostgreSQL)
- pytest, pytest-cov
- pytest-asyncio (for async test support)

## License

MIT
