import logging
import os
from collections.abc import Callable
from functools import wraps

from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger("rich")


def get_edu():
    return int(os.environ["EDUZEN_ID"])


def restricted(func: Callable):
    @wraps(func)
    def wrapped(
        update: Update, context: CallbackContext, *args: int, **kwargs: str
    ) -> Callable:
        EDUZEN_ID = get_edu()

        user = update.effective_user
        if user.id == EDUZEN_ID:
            return func(update, context, *args, **kwargs)

        logger.info(f"{func.__name__} - Unauthorized access denied for {user}.")
        return

    return wrapped
