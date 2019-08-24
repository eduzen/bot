import structlog
from functools import wraps

from keys import LIST_OF_ADMINS

logger = structlog.get_logger(filename=__name__)


def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user = update.effective_user
        if user.id not in LIST_OF_ADMINS:
            logger.error(f"{func.__name__} - Unauthorized access denied for {user}.")
            return

        return func(bot, update, *args, **kwargs)

    return wrapped
