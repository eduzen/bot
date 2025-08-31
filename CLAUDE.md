# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Bot
- **Local development**: `just run` or `uv run python -m eduzenbot`
- **Docker development**: `just start` (starts with docker-compose)
- **Debug mode**: `just start-debug` (interactive docker session)
- **Docker shell**: `just dockershell` (bash session in container)
- **IPython shell**: `just shell` (interactive Python shell)

### Testing
- **Run tests**: `just test` (Docker) or `uv run coverage run -m pytest` (local)
- **Single test**: `uv run pytest path/to/test.py::test_name`
- **Coverage report**: `just coverage` or `uv run coverage report`

### Code Quality
- **Lint and format**: `just format` or `pre-commit run --all-files`
- **Pre-commit hooks**: Auto-run ruff (linting/formatting), isort, pyupgrade, and validation checks
- Pre-commit installs via: `pre-commit install`

### Database
- Database migrations and table creation are handled automatically in `__main__.py` during startup via `create_db_tables()` and `migrate_tables()`
- Uses Peewee ORM with SQLite by default (`:memory:` if no DATABASE_URL), PostgreSQL for production
- Connection string format: `postgresext+pool://user:pass@host/db?max_connections=20&stale_timeout=3000`

### Environment Setup
- Copy `.env.sample` to `.env` and configure required environment variables
- **Required**: `TOKEN` (Telegram bot token), `EDUZEN_ID` (admin user ID)
- **Optional**: `SENTRY_DSN`, `DATABASE_URL`, `LOG_LEVEL`, `openweathermap_token`, `NEWS_API_KEY`, `TMDB_API_KEY`

## Architecture

### Bot Initialization Flow (`eduzenbot/__main__.py`)
1. Load environment variables from `.env`
2. Initialize Sentry SDK and Logfire for observability
3. Create/migrate database tables via `create_db_tables()` and `migrate_tables()`
4. Build Application with `ExtBot` and `Application.builder()`
5. Set `app.post_init = on_startup` to run startup tasks
6. During `on_startup`:
   - Send startup message to admin (EDUZEN_ID)
   - Load plugins via `load_and_register_plugins()`
   - Register hardcoded handlers (`set`, `configure_report`, `cancel_report`)
   - Register unknown command handler
   - Set bot commands in Telegram with `set_my_commands()`
   - Schedule existing reports from database with `schedule_reports()`
7. Add error handler and start polling

### Plugin System
The bot uses a **dynamic plugin loading system** (`eduzenbot/adapters/plugin_loader.py`):

- **Plugin Location**: `eduzenbot/plugins/commands/<plugin_name>/`
- **Plugin Structure**: Each plugin requires:
  - `command.py`: Main plugin logic with handler functions
  - `__init__.py`: Plugin initialization (can be empty)
- **Command Registration**: Commands are registered via **docstring format** at the top of `command.py`:
  ```python
  """
  command_name - function_name
  another_command - another_function
  """

  async def function_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
      # Handler logic
  ```
- **Loading Process**:
  1. `load_and_register_plugins()` scans `eduzenbot/plugins/commands/` for folders with `command.py`
  2. Dynamically imports each module via `importlib.util`
  3. Parses module docstring to extract command-to-function mappings
  4. Creates `CommandHandler` instances for each command
  5. Returns list of handlers to be registered in `__main__.py`

### Core Components
- **Main Application**: `eduzenbot/__main__.py` - Entry point, bot initialization, plugin loading, startup orchestration
- **Models**: `eduzenbot/models.py` - Database models (User, EventLog, Report) using Peewee ORM with thread-safe metadata
- **Plugin Loader**: `eduzenbot/adapters/plugin_loader.py` - Dynamic plugin discovery and CommandHandler registration
- **Decorators**: `eduzenbot/decorators.py` - `@create_user` decorator for automatic user tracking
- **Error Handler**: `eduzenbot/adapters/telegram_error_handler.py` - Centralized Telegram API error handling
- **Report Scheduler**: `eduzenbot/domain/report_scheduler.py` - Schedules daily reports from database on startup

### Database Models (Peewee ORM)
- **BaseModel**: Base class with `todict()`/`to_dict()` helpers and thread-safe metadata
- **User**: Telegram user info (id, username, first_name, last_name, is_bot, language_code) with automatic `updated_at` on save
- **EventLog**: Tracks command usage (user, command, data, timestamp) for audit logs
- **Report**: Stores scheduled daily report configurations (chat_id, hour, min, show_weather, show_crypto, show_dollar, show_news)

### Decorators (`eduzenbot/decorators.py`)
- **`@create_user`**: Wraps command handlers to:
  - Extract user from `update.effective_user`
  - Call `get_or_create_user()` to ensure user exists in DB and update fields
  - Log command execution to `EventLog` table
  - Log to Logfire for observability
  - Return handler result (does not block on errors)

### Dependencies
- **Core**: python-telegram-bot (with job-queue), peewee, logfire (observability), sentry-sdk
- **External APIs**: yfinance (stocks), beautifulsoup4 (web scraping), httpx (async HTTP)
- **Development**: pytest, pytest-asyncio, pytest-mock, pytest-randomly, coverage, factory-boy, respx (HTTP mocking), pre-commit, ruff, mypy, ipython, ipdb

### Testing
- Uses pytest with asyncio support (`pytest-asyncio`)
- Factory Boy for test data generation
- Respx for HTTP request mocking
- Coverage configured to ignore `eduzenbot/__about__.py` and `eduzenbot/scripts/*`
- Run single test: `uv run pytest path/to/test.py::test_function_name`
