# Repository Guidelines

## Project Structure & Module Organization
- `eduzenbot/`: Bot package. Key areas: `plugins/` (commands, messages, job_queue), `adapters/` (integration helpers), `domain/` (core logic), `auth/`, and `scripts/` (DB/bootstrap utilities). Entry point: `python -m eduzenbot`.
- `tests/`: Pytest suite with async tests under `tests/commands/*` plus shared fixtures in `tests/conftest.py`.
- Tooling: `pyproject.toml` (deps, coverage, ruff), `.pre-commit-config.yaml` (lint/format), `Dockerfile`, `docker-compose.yml`, `justfile` (task runner).

## Build, Test, and Development Commands
- `just run`: Start the bot locally via `uv run python -m eduzenbot`.
- `just start`: Build and run with Docker Compose in the background; tails logs.
- `just test` / `just uv-test`: Run pytest with coverage (Compose vs local uv).
- `just coverage`: Combine and report coverage.
- `just format` (alias `just fmt`): Run pre-commit formatters/linters.
- `just build`, `just logs`, `just restart`, `just start-debug`: Common Docker workflows.

## Coding Style & Naming Conventions
- Python 3.13, ruff target `py313`, line length 120; imports sorted with isort (black profile). Run `just format` before pushing.
- Prefer type hints; keep functions small and pure in `domain/`.
- Plugins: follow `eduzenbot/plugins/commands/<name>/{command.py,api.py,__init__.py}`. Tests mirror structure under `tests/commands/<name>/` with `test_*.py`.

## Testing Guidelines
- Frameworks: pytest, pytest-asyncio, respx; coverage enabled with branch tracking.
- Naming: `tests/test_*.py` or `tests/commands/<area>/test_*.py`. Use fixtures from `tests/conftest.py`.
- Run: `just uv-test` (local) or `just test` (Compose). Generate reports with `just coverage`.

## Commit & Pull Request Guidelines
- Commits: Short, imperative subject lines; include scope when helpful. Emoji prefixes (e.g., `:arrow_up: Bump ...`) are OK for dependency updates. Reference issues/PRs (e.g., `(#123)`).
- PRs: Include a concise description, testing steps, and screenshots/log snippets if relevant. Require green CI, `just format` clean, and tests passing.

## Security & Configuration Tips
- Copy `.env.sample` to `.env` (or run `just check_env`). Never commit secrets or `db.sqlite3`.
- Use Docker/Compose for parity; volumes persist state. Configure tokens/DB via `.env`.
