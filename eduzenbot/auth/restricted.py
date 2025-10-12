import os
from collections.abc import Callable
from functools import wraps
from typing import Any

import logfire
from telegram import Update
from telegram.ext import ContextTypes


def get_edu():
    return int(os.environ["EDUZEN_ID"])


def restricted(func: Callable[..., Any]) -> Callable[..., Any]:
    """Allow only the configured user to run the command.

    Ensures an async wrapper so handler awaiting never fails. When unauthorized,
    the wrapper exits gracefully without returning a non-awaitable.
    """

    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: Any, **kwargs: Any) -> Any:
        EDUZEN_ID = get_edu()

        user = update.effective_user
        if user and user.id == EDUZEN_ID:
            return await func(update, context, *args, **kwargs)

        logfire.info(f"{func.__name__} - Unauthorized access denied for {user}.")
        # Optionally, you could send a friendly denial message here.
        return None

    return wrapped
