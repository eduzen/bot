# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Bot
- **Local development**: `just run` or `uv run python -m eduzenbot`
- **Docker development**: `just start` (starts with docker-compose)
- **Debug mode**: `just start-debug` (interactive docker session)

### Testing
- **Run tests**: `just test` (Docker) or `uv run coverage run -m pytest` (local)
- **Coverage report**: `just coverage` or `uv run coverage report`

### Code Quality
- **Lint and format**: `just format` or `pre-commit run --all-files`
- **Pre-commit hooks**: Auto-run ruff (linting/formatting), isort, pyupgrade, and validation checks

### Database
- Database migrations and table creation are handled automatically in `__main__.py` during startup
- Uses Peewee ORM with SQLite by default, PostgreSQL for production

### Environment Setup
- Copy `.env.sample` to `.env` and configure required environment variables
- Required: `TOKEN` (Telegram bot token), `EDUZEN_ID` (admin user ID)
- Optional: `SENTRY_DSN`, `DATABASE_URL`, `LOG_LEVEL`

## Architecture

### Plugin System
The bot uses a dynamic plugin loading system:

- **Plugin Location**: `eduzenbot/plugins/commands/<plugin_name>/`
- **Plugin Structure**: Each plugin requires:
  - `command.py`: Main plugin logic
  - `__init__.py`: Plugin initialization
  - **Command Registration**: Use docstring format in `command.py`:
    ```python
    """
    command_name - function_name
    another_command - another_function
    """
    ```

### Core Components
- **Main Application**: `eduzenbot/__main__.py` - Bot initialization, plugin loading, startup logic
- **Models**: `eduzenbot/models.py` - Database models (User, EventLog, Report) using Peewee ORM
- **Plugin Loader**: `eduzenbot/adapters/plugin_loader.py` - Dynamic plugin discovery and registration
- **Error Handler**: `eduzenbot/adapters/telegram_error_handler.py` - Telegram API error handling
- **Report Scheduler**: `eduzenbot/domain/report_scheduler.py` - Automated daily reports

### Database Models
- **User**: Telegram user information with automatic timestamp management
- **EventLog**: Command usage tracking and audit logs
- **Report**: Scheduled daily report configurations per chat

### Decorators
- `@create_user`: Automatically creates/updates user records from Telegram updates (in `decorators.py`)

### Dependencies
- **Core**: python-telegram-bot, peewee, logfire (observability)
- **External APIs**: yfinance (stocks), beautifulsoup4 (web scraping)
- **Development**: pytest, coverage, ruff, mypy, pre-commit

### Testing
- Uses pytest with asyncio support
- Factory Boy for test data generation
- Respx for HTTP mocking
- Coverage reporting configured to ignore scripts and version files
