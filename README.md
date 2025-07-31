# ⚠️ DISCLAIMER — PLEASE READ

This entire application was generated using GitHub Copilot in agent mode, without a single line of code written manually and without any prior experience with Python or FastAPI.

Both the application logic and automated tests were created solely through natural language instructions and iterative refinement with Copilot. This project demonstrates the power and potential of AI-assisted software development.


# AI Chatbot API


This project is a REST API for an AI-powered chatbot service, built with FastAPI (Python). It provides secure user registration, authentication (JWT), and a chat endpoint for interacting with an AI bot. The API is designed for extensibility, maintainability, and follows industry best practices. All code is fully tested (unit and integration) with 100% coverage enforced via Docker Compose.

- Database schema is managed and versioned using Alembic migrations.
- Migrations are applied automatically in the app and test-run containers.

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
- Automated test-runner via Docker Compose
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


## Quickstart (Local Development)


1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   > **Note:** This project uses [pydantic-settings](https://pydantic-docs.helpmanual.io/usage/pydantic_settings/) for configuration management (Pydantic v2+). All environment variables (e.g., `DATABASE_URL`, `SECRET_KEY`) are loaded via `app/core/config.py` using a `.env` file or your shell environment.


2. Set environment variables (optional, overrides defaults):
   ```bash
   export DATABASE_URL=postgresql://chatbot:chatbotpass@localhost:5432/chatbotdb
   export SECRET_KEY=your-secret-key
   export LOG_LEVEL=info
   # Or use a .env file in the project root
   ```

3. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Visit the interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

5. To run all tests and check coverage locally:
   ```bash
   pytest --cov=app --cov-report=term-missing --cov-report=html tests/unit tests/integration
   ```
   > **Note:** Async tests are supported via `pytest-asyncio`. No extra configuration is needed; simply run `pytest` as above.



## Database Migrations

Alembic is used for schema migrations. To create a new migration:

```bash
alembic revision --autogenerate -m "Your migration message"
```

To apply migrations:

```bash
alembic upgrade head
```

## Running with Docker Compose (Recommended)

The included `docker-compose.yml` runs the FastAPI app, a PostgreSQL database, and a test-runner service for automated testing and coverage.

```bash
docker compose up --build
```

This will:
- Start a PostgreSQL 15 database (user: `chatbot`, password: `chatbotpass`, db: `chatbotdb`)
- Start the FastAPI app, automatically connected to the database
- Expose the API at [http://localhost:8000](http://localhost:8000)
- Run all unit and integration tests in the `test-run` service, enforcing 100% coverage

You can change database credentials in `docker-compose.yml` as needed. **Only PostgreSQL is supported.**

To run tests and see the coverage report:
```bash
docker compose run --rm test-run
```
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
