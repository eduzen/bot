import logging
import os
from functools import wraps
from typing import Callable

from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger("rich")

EDUZEN_ID = int(os.environ["EDUZEN_ID"])


def restricted(func: Callable):
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args: int, **kwargs: str) -> Callable:
        user = update.effective_user
        if user.id == EDUZEN_ID:
            return func(update, context, *args, **kwargs)

        logger.info(f"{func.__name__} - Unauthorized access denied for {user}.")
        return

    return wrapped
