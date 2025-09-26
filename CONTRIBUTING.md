# Contributing to FastAPI Chat API

Thanks for contributing! This guide is intentionally lean. For setup, architecture, commands, and migrations, see README.md.

## Contributor Checklist

Before opening a PR, please ensure:

- [ ] Run pre-commit hooks: `poetry run pre-commit run --all-files`
- [ ] Ensure tests pass locally with 100% coverage
- [ ] Follow Ruff style rules (py313, line length 88, double quotes); no `print`/debugger
- [ ] Use absolute imports only (relative imports are banned by Ruff)
- [ ] Add Google-style docstrings for new/changed code under `app/**`
- [ ] Keep dependency constraints within-major (e.g., `>=2.7.1,<3.0.0`), and run `poetry update`
- [ ] Update docs and `.env.example` for new env vars or behavior
- [ ] Include Alembic migration if the schema changed

## Quality gates

CI enforces linting, type-checking, and 100% test coverage. Keep PRs small and focused with tests.

Questions? Open an issue or a draft PR for feedback.
