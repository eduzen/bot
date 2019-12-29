import os
import structlog

from functools import wraps
from telegram import Update
from telegram.ext import CallbackContext

logger = structlog.get_logger(filename=__name__)


def restricted(func):
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        user = update.effective_user
        if user.id == int(os.getenv("EDUZEN_ID")):
            return func(update, context, *args, **kwargs)

        logger.error(f"{func.__name__} - Unauthorized access denied for {user}.")
        return

    return wrapped
