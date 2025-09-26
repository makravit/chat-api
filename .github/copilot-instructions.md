<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->


# FastAPI Chat API – Copilot Instructions

## Purpose
This file provides future-facing guidelines for contributors and Copilot to implement new features in a scalable, secure, and maintainable way. Do not use this file to explain current features; focus on principles, patterns, and requirements for future development.

## Technologies
- FastAPI (API framework)
- Pydantic (data validation)
- Poetry (dependency management)
- Alembic (database migrations)
- Docker (containerization)

## Folder Structure
- `app/api/`: Route definitions
- `app/core/`: Core utilities (auth, config, database, logging, exceptions)
- `app/models/`: ORM models
- `app/schemas/`: Pydantic schemas
- `app/services/`: Business logic and data access

## Coding Guidelines
- Use dependency injection via FastAPI's `Depends` for services and repositories
- Handle errors with custom exception handlers
- Organize code for readability and maintainability
- Use type hints and Pydantic models for data validation
- Keep business logic in `services/`, not in API routes
- Implement security best practices for authentication, refresh tokens, and session management (see user stories)

## Extending the App
When adding new endpoints or features:
- Follow the modular folder structure
- Add corresponding unit and integration tests in `tests/`
- Document new environment variables in `.env.example`
- Use Pydantic models for request/response validation
- Add docstrings and OpenAPI documentation
- Ensure new code is covered by tests and passes linting

### New endpoint checklist
- Define request/response models under `app/schemas/*`.
- Keep route handlers thin; implement logic in `app/services/*`.
- Authentication/authorization: clarify requirements and enforce in dependencies.
- Map domain errors to consistent API errors (see README error schema); document status codes.
- Add unit tests for services and focused route tests; keep 100% coverage.
- Provide clear docstrings and OpenAPI descriptions; include examples when helpful.

### Database change checklist
- Update SQLAlchemy models under `app/models/*`.
- Generate Alembic migration with `--autogenerate`, review carefully, and ensure safe downgrade.
- Include data backfills as explicit ops (don’t hide them in autogenerate).
- Update tests and fixtures affected by schema changes.

## Contribution & Maintenance
- Keep code modular, well-documented, and consistent with best practices
- Update README and copilot-instructions for onboarding and automation
- Use pre-commit hooks to enforce code quality
- Ensure CI/CD checks pass before merging or deploying

## Tooling & Workflow
 - Use `ruff` for linting and code style
 - Let Ruff manage import sorting (enable isort rules via Ruff)
 - Use Poetry for dependency management
 - Use Alembic for database migrations
 - Use Docker for local development and deployment
 - Use Pyright for static type checking across `app/**` and `tests/**`

### Linting, formatting, and static analysis (Ruff)
The project’s canonical style and checks are enforced by Ruff (configured in `pyproject.toml`). Key rules and conventions you must follow when adding or modifying code:

- Python version and formatting
	- Target Python 3.13 for lint semantics (`target-version = py313`).
	- Line length 88. Use double quotes and spaces for indentation.
	- Prefer absolute imports and tidy import style. Relative imports are banned (flake8-tidy-imports).
	- Pyright is enforced; prefer modern typing and `from __future__ import annotations`.
	- Place type-only imports under `if TYPE_CHECKING:` to satisfy `TCH` rules. If a framework evaluates annotations at runtime (e.g., SQLAlchemy), ensure referenced names exist at runtime (e.g., provide a runtime alias or use a targeted `# noqa: TCH003`).
- Docstrings and documentation
	- Google-style docstrings are required for modules, functions, classes, and methods under `app/**`.
	- Pyright must pass with zero errors locally and in CI.
	- Docstrings are not required in tests (`tests/**`) and small helper scripts (`scripts/**`).

- Security and secrets
	- Security checks from Bandit (`S` rules) are enabled.
	- Tests: `assert` is allowed (S101 ignored). Avoid asserting in app code.
	- Dev defaults may exist only in `app/core/config.py` (per-file S105 ignore) and the constant token type in `app/schemas/user.py` (per-file S105 ignore). Real secrets must come from environment variables (`.env`), not source code.

- Testing style and patterns
	- Pytest style rules (`PT`) are enforced: prefer `pytest.mark.parametrize`, avoid bare asserts only in non-tests, and keep tests small and readable.
	- Boolean positional args are disallowed in app code (`FBT`), but allowed in tests (per-file ignore) for fixtures/helpers.

- Async and return flow
	- `ASYNC` and `RET` families guide proper async usage and clean return paths.

- Exceptions and raising
	- Use `RSE` and `TRY` rules for clear exception raising and handling patterns.

- Readability and performance
	- Use `SIM`, `PERF`, and `C4` (comprehensions) for simpler, faster code.

- Naming and annotations
	- `N` (pep8-naming), `A` (no shadowing builtins), and `ANN` (annotation coverage) are enabled. Keep type hints complete and accurate.

- Confusables and hygiene
	- `RUF001–RUF003` prevent ambiguous Unicode; `RUF100` removes stale `noqa`.

- Misc
	- Disallow `print` and debugger calls in committed code (`T20`, `T10`).
	- Type-checking import placement is optimized (`TCH`).
	- `UP`/`pyupgrade` modernizes syntax; keep runtime typing as configured.
	- McCabe complexity max is 10; refactor if you exceed it.

- Per-file ignores (summary)
	- `alembic/**`: docstrings not enforced (generated/ops-focused).
	- `scripts/**`: docstrings not enforced (small helper scripts).
	- `tests/**`: docstrings not enforced; allow boolean positional args (`FBT`); allow `assert` (S101).
	- `app/core/config.py`: allow S105 (dev/local defaults only; no real secrets).
	- `app/schemas/user.py`: allow S105 for constant token type ("bearer").

Commands: see README “Running Tests & Code Quality” for the canonical Poetry invocations (tests, lint/format, type-check).

CI and local development both expect 100% test coverage. Keep code changes small and tested.

## Testing Guidelines
- Write focused, behavior-driven tests under `tests/` (unit and integration). Keep route handlers thin; test business logic in `services/` directly.
- Prefer standard mocking utilities over hand-rolled stubs:
	- Use `unittest.mock.MagicMock` and `types.SimpleNamespace` for lightweight doubles.
	- Patch repositories/services with `unittest.mock.patch` at import paths used by the subject under test (e.g., `app.services.user_service.UserRepository`).
- Reuse the shared helpers in `tests/utils.py` to keep tests concise and consistent:
	- `make_dummy_db()` — a placeholder DB when no DB behavior is asserted (repos are patched).
	- `make_db_query_first(result)` — returns a DB where `query().filter().first()` yields `result`.
	- `make_db_query_all(results)` — returns a DB where `query().filter().all()` yields `results`.
	- `make_db_commit_mock()` — returns a DB with `db.assert_committed_once()` to assert a single commit.
- When not to use the helpers: if the test specifically validates repository query/filter behavior, create a tailored fake (see `tests/unit/test_user_repository.py`).
- Style & quality gates:
	- Enforce 100% coverage (pytest-cov) and keep tests readable and small.
	- Ruff is the single source of truth for lint/format/import sort. Line length 88 is enforced—wrap long strings/docstrings.
	- Keep imports at top of test files; avoid in-block imports.
- Integration tests: Prefer Testcontainers for Postgres when exercising real DB paths. Keep integration tests focused and deterministic.

## Dependency policy (Poetry)

- Use Poetry for dependency management. The project pins versions as "within-major" ranges (e.g., `>=2.7.1,<3.0.0`).
- To update all packages to the latest allowed versions within their major, run:

```sh
poetry update
```

- Do not introduce caret (`^`) or overly permissive constraints; prefer explicit `>=,<` ranges to avoid accidental major upgrades. If a major bump is needed, coordinate it as a dedicated change with full validation.

Examples (concise):

```python
# Control .first()
from tests.utils import make_db_query_first
db = make_db_query_first(result=None)
assert repo(db).get_valid_token("nope") is None
```

```python
# Assert a single commit
from tests.utils import make_db_commit_mock
db = make_db_commit_mock()
repo(db).revoke_all_tokens(123)
db.assert_committed_once()
```

## Security & Compliance
- Store secrets securely (never commit them)
- Validate and sanitize all user input
- Use authentication and authorization for protected endpoints

## Logging & Metrics
- Use structlog; never use `print` or debugger statements in committed code.
- Do not log secrets, access tokens, or refresh tokens.
- When adding metrics, keep labels low-cardinality and stable.

## Configuration
- Any new env var must be added to `.env.example` and documented in the README.
- Keep dev defaults only in `app/core/config.py`; real secrets come from the environment.
- Validate configuration via Pydantic settings; fail fast on missing required values.

## API Documentation
- Use FastAPI's built-in OpenAPI/Swagger docs
- Version endpoints under `/api/v1/`

## References
- See `docs/user-stories.md` for requirements and acceptance criteria
- See README for setup and usage instructions

## Authoritative sources
- Commands and local workflows: README → “Running Tests & Code Quality”, “Running the app locally”, and “Database Migrations”.
- Contribution workflow & checklist: `CONTRIBUTING.md`.
- Style, linting, ignores, and policy: this file and `pyproject.toml` (Ruff/Pyright).

## Import Organization
Always import libraries only at the top of each file. Group imports in this order:
1. Standard library imports
2. Third-party imports
3. Local application imports

All code changes and suggestions must be consistent with this import grouping and placement.
