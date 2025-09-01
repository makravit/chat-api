<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This is a FastAPI-based chat API project. Use these guidelines for Copilot suggestions:

## Project Purpose
Robust RESTful API for chat, user management, health checks, and metrics, built with FastAPI for scalability and maintainability.

## Technologies
- FastAPI: API framework
- Pydantic: Data validation and typing
- Poetry: Dependency management
- Alembic: Database migrations
- Docker: Containerization and deployment

## Folder Structure & Best Practices
	- `api/`: Route definitions (chat, users, health, metrics)
	- `core/`: Core utilities (auth, config, database, logging, exceptions)
	- `models/`: ORM models
	- `schemas/`: Pydantic schemas
	- `services/`: Business logic and data access

## Coding Guidelines
Follow Python and FastAPI best practices:
- Use dependency injection via FastAPI's `Depends` for services and repositories
- Handle errors with custom exception handlers
- Organize code for readability and maintainability
- Use type hints and Pydantic models for data validation
- Keep business logic in `services/`, not in API routes

## Example Code Patterns
Example: Dependency injection, authentication, Pydantic models, and business logic separation:
```python
from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import process_chat

router = APIRouter(tags=["Chat"])

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, user=Depends(get_current_user)):
	# Logging, authentication, and business logic separation
	return process_chat(request, user)
```

Example: Error handling with custom exceptions and global exception handler:
```python
from fastapi import FastAPI
from app.core.exception_handlers import app_exception_handler
from app.core.exceptions import AppException

app = FastAPI()
app.add_exception_handler(AppException, app_exception_handler)
```

Define custom exceptions for domain-specific errors (e.g., `EmailAlreadyRegistered`, `InvalidCredentials`).
Register a global exception handler to map exceptions to appropriate HTTP responses and log details.

## Testing
Write tests in the `tests/` folder:
- Use pytest for unit and integration tests
- Maintain high test coverage
- Use fixtures for setup and teardown
- Mock external dependencies in unit tests
- Run tests before committing code

## Naming Conventions
- Use snake_case for files and functions, PascalCase for classes.
- Prefix API routers with their domain (e.g., `chat.py`, `users.py`).

## Linting & Formatting
Use `ruff` for linting and code style, and `isort` for import sorting.
Run `poetry run isort .` and `poetry run ruff .` before committing code.

## Environment Variables
Set the following variables in your `.env` file before running the application:
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Secret for authentication
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name
- `LOG_LEVEL`: Logging level
- `METRICS_USER`: Metrics endpoint username
- `METRICS_PASS`: Metrics endpoint password

Document all required environment variables in `.env.example`:
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Secret for authentication
- Add any other variables used for third-party integrations or configuration

## Dependency Management
Poetry is used for dependency management. To update all packages, run:
	```bash
	poetry update
	```

## Python Version
The project requires Python 3.13. Ensure your environment matches this version.
Set your Poetry environment to Python 3.13:
```sh
poetry env use 3.13
```

## Setup Instructions
Refer to the README for detailed setup steps, including Poetry installation and environment setup.
To run the app and database with Docker Compose:
```sh
docker compose up --build
```

## Database Migrations
Alembic is used for migrations. Migration scripts are located in the `alembic/` folder.
Run Alembic migrations with:
```sh
poetry run alembic upgrade head
```

## Testing Coverage
Maintain high test coverage. Use pytest and coverage tools as needed.
Run coverage with:
```sh
poetry run pytest --cov=app --cov-report=html
```
To suppress deprecation warnings in test output, add a `pytest.ini` file:
```ini
[pytest]
filterwarnings =
    ignore::DeprecationWarning
```

## Docker Usage
Docker is supported for containerization and deployment. See the README for usage instructions.

## API Documentation
- Use FastAPI's built-in OpenAPI/Swagger docs.
- Document endpoints with docstrings and Pydantic models.
- API endpoints are versioned under `/api/v1/`.

## Security Guidelines
- Store secrets securely (never commit them).
- Use authentication and authorization for protected endpoints.
- Validate and sanitize all user input.

## Contribution & Maintenance
- Follow Python and FastAPI best practices
- Keep code modular and well-documented
- Keep both README and copilot-instructions updated and in sync for onboarding and automation.

## Extending the App
- When adding new endpoints or features, follow the existing modular structure and ensure corresponding unit and integration tests are added in the `tests` folder.

## License
- This project is licensed under the MIT License.

## User Stories & Requirements
- See `docs/user-stories.md` for requirements and acceptance criteria.

## Pre-commit Hooks
- Use pre-commit hooks to enforce code quality before pushing.

## Security Reminder
- Do not commit `.env` files with secrets to version control.

## CI/CD
- Automated tests, linting, and code style checks are enforced via pre-commit hooks and GitHub Actions. Ensure all checks pass before merging or deploying.
