# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Bot
- **Local development**: `just run` or `uv run python -m eduzenbot`
- **Docker development**: `just start` (starts with docker-compose, then tails logs)
- **Debug mode**: `just start-debug` (interactive docker session)
- **IPython shell**: `just shell` (interactive Python shell in Docker)

### Testing
- **Local tests**: `just uv-test` or `uv run coverage run -m pytest`
- **Docker tests**: `just test`
- **Single test**: `uv run pytest path/to/test.py::test_name`
- **Coverage report**: `just coverage` (runs `coverage combine` then `coverage report`)
- Tests use an autouse fixture (`tests/conftest.py`) that binds all models to an in-memory SQLite DB per test function — no setup needed
- Factory Boy factories for User and EventLog are in `tests/factories.py`
- HTTP mocking uses `respx` (for `httpx`-based API calls)

### Code Quality
- **Lint and format**: `just format` (or `just fmt`) — runs `uv run pre-commit run --all-files`
- **Pre-commit hooks**: ruff (lint + format), isort (profile=black), pyupgrade (py311+), plus standard checks (check-ast, trailing-whitespace, etc.)
- **Ruff config**: target Python 3.13, line-length 120

### Environment Setup
- Copy `.env.sample` to `.env` and configure required environment variables
- **Required**: `TOKEN` (Telegram bot token), `EDUZEN_ID` (admin user ID)
- **Optional**: `SENTRY_DSN`, `DATABASE_URL`, `LOG_LEVEL`, `openweathermap_token`, `NEWS_API_KEY`, `TMDB_API_KEY`

## Architecture

### Bot Initialization Flow (`eduzenbot/__main__.py`)
1. Load `.env`, init Sentry + Logfire, create/migrate DB tables
2. Build `Application` with `ExtBot` and set `post_init = on_startup`
3. `on_startup`: loads plugins via `load_and_register_plugins()`, registers hardcoded handlers (`set`, `configure_report`, `cancel_report`), registers unknown command fallback, sets bot commands in Telegram, schedules existing reports from DB
4. Start polling

### Plugin System (`eduzenbot/adapters/plugin_loader.py`)
Plugins are discovered dynamically from `eduzenbot/plugins/commands/<plugin_name>/`.

Each plugin folder requires a `command.py` with a **module-level docstring** mapping commands to functions:
```python
"""
clima - klima
klima - klima
"""

@create_user
async def klima(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ...
```

The loader parses the docstring (`command_name - function_name` per line), finds the function by name, and creates `CommandHandler` instances. Commands must be unique across all plugins.

Plugins that call external APIs typically split logic into a separate `api.py` in the same folder (e.g., `weather/api.py`, `btc/api.py`, `dolar/api.py`).

### Key Decorators
- **`@create_user`** (`eduzenbot/decorators.py`): Wraps command handlers to upsert the Telegram user in the DB, log the command to `EventLog`, and instrument with Logfire. Does not block the handler on DB errors.
- **`@restricted`** (`eduzenbot/auth/restricted.py`): Limits command access to the `EDUZEN_ID` user only. Silently returns `None` for unauthorized users.
- Decorator stacking order matters: `@create_user` should be outermost, `@restricted` inside it (see `schedule_daily_report` for example).

### Database
- Uses Peewee ORM with `ThreadSafeDatabaseMetadata`
- SQLite in-memory by default (`:memory:` if no `DATABASE_URL`), PostgreSQL via `psycopg` for production
- Models: `User`, `EventLog`, `Report` — all in `eduzenbot/models.py`
- Tables created/migrated automatically at startup via `eduzenbot/scripts/initialize_db.py`

### Job Queue / Scheduled Reports
- `eduzenbot/plugins/job_queue/alarms/command.py`: Handles `/set` and `/cancel_report` commands for daily scheduled reports
- `eduzenbot/domain/report_scheduler.py`: On startup, reads all `Report` records and schedules `run_daily` jobs (timezone: Europe/Amsterdam)
- Reports are configurable with feature flags: weather, crypto, dollar, news

### Other Structure
- `eduzenbot/plugins/messages/unknown.py`: Fallback handler for unrecognized commands
- `eduzenbot/scripts/`: DB initialization and data loading utilities
