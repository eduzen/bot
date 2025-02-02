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

    # 1) Log the error (with stack trace) at the top level so we have a single place to see exceptions.
    #    exc_info=context.error will try to pull the traceback from the error in the context.
    #    Alternatively, exc_info=True if you want the logger to use the current exception info.
    logfire.error(
        "Exception while handling an update. {extra}",
        exc_info=context.error,
        extra={
            # It's often helpful to attach metadata for structured logging
            "update": update.to_dict() if update else None,
            "chat_id": update.effective_chat.id if update and update.effective_chat else None,
            "user_id": update.effective_user.id if update and update.effective_user else None,
        },
    )

    # 2) Attempt to raise context.error so we can differentiate known Telegram errors
    try:
        raise context.error
    except Forbidden as e:
        logfire.warn("Unauthorized error", exc_info=e, extra={"details": str(e)})
        # Possibly handle removing commands, or removing the user from internal records, etc.
    except BadRequest as e:
        logfire.warn("BadRequest error", exc_info=e, extra={"details": str(e)})
        # Example: This commonly indicates a message formatting or parse_mode issue.
    except TimedOut as e:
        logfire.warn("TimedOut error", exc_info=e, extra={"details": str(e)})
    except NetworkError as e:
        logfire.warn("NetworkError", exc_info=e, extra={"details": str(e)})
    except ChatMigrated as e:
        logfire.warn("ChatMigrated error", exc_info=e, extra={"details": str(e)})
        # Possibly handle migrating chat_id references here
    except TelegramError as e:
        logfire.warn("TelegramError", exc_info=e, extra={"details": str(e)})
    except Exception as e:
        # 3) Catch any other unknown errors
        #    logfire.exception automatically captures stack trace.
        logfire.exception("Unhandled exception", exc_info=e)

    # 4) Optionally, notify the user that something went wrong (avoid sending too much detail).
    #    This is useful if you want to let the user know you’re looking into the issue.
    if update and update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="An unexpected error occurred. Please try again later.",
        )
