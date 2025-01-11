# eduzenbot/adapters/telegram_error_handler.py
import logfire
from telegram import Update
from telegram.error import (
    BadRequest,
    ChatMigrated,
    Forbidden,
    NetworkError,
    TelegramError,
    TimedOut,
)
from telegram.ext import ContextTypes


async def telegram_error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Log and handle errors caused by updates.
    This function will handle exceptions raised during updates and log them appropriately.
    """
    logfire.error("Exception while handling an update", exc_info=context.error)

    # Detailed error handling
    try:
        raise context.error
    except Forbidden as e:
        logfire.warning(f"Unauthorized error: {e}")
    except BadRequest as e:
        logfire.warning(f"BadRequest error: {e}")
        logfire.debug(f"Details: {e}")
    except TimedOut as e:
        logfire.warning(f"TimedOut error: {e}")
        logfire.debug(f"Details: {e}")
    except NetworkError as e:
        logfire.warning(f"NetworkError: {e}")
        logfire.debug(f"Details: {e}")
    except ChatMigrated as e:
        logfire.warning(f"ChatMigrated error: {e}")
        logfire.debug(f"Details: {e}")
    except TelegramError as e:
        logfire.warning(f"TelegramError: {e}")
        logfire.debug(f"Details: {e}")
    except Exception as e:
        logfire.exception(f"Unhandled exception: {e}")

    # Optionally, notify the developer or admin about the error
    if update and update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="An unexpected error occurred. Please try again later.",
        )
