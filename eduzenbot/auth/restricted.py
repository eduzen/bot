import logging
import os
from functools import wraps

from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger("rich")


def restricted(func):
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        user = update.effective_user
        if user.id == int(os.getenv("EDUZEN_ID")):
            return func(update, context, *args, **kwargs)

        logger.info(f"{func.__name__} - Unauthorized access denied for {user}.")
        return

    return wrapped
