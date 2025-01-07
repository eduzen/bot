# eduzenbot/adapters/telegram_error_handler.py
import logfire
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import ContextTypes


def telegram_error_handler(update: ContextTypes.DEFAULT_TYPE, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log and handle Errors caused by Updates."""
    try:
        raise context.error
    except Unauthorized:
        logfire.warning("Unauthorized error")
    except BadRequest:
        logfire.warning("Update caused a BadRequest")
        logfire.debug(f"{context.error}")
    except TimedOut:
        logfire.warning("Update caused a TimedOut")
        logfire.debug(f"{context.error}")
    except NetworkError:
        logfire.warning("Update caused a NetworkError")
        logfire.debug(f"{context.error}")
    except ChatMigrated:
        logfire.warning("Update caused a ChatMigrated")
        logfire.debug(f"{context.error}")
    except TelegramError:
        logfire.warning("Update caused a TelegramError")
        logfire.debug(f"{context.error}")
    except Exception:
        logfire.exception(f"Unhandled issue: {context.error}")
