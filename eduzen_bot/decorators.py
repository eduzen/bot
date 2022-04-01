import functools
import logging
from functools import wraps

import peewee

from eduzen_bot.models import EventLog, User

logger = logging.getLogger("rich")


def hash_dict(func):
    """Transform mutable dictionnary
    Into immutable
    Useful to be compatible with cache
    """

    class HDict(dict):
        def __hash__(self):
            return hash(frozenset(self.items()))

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        args = tuple(HDict(arg) if isinstance(arg, dict) else arg for arg in args)
        kwargs = {k: HDict(v) if isinstance(v, dict) else v for k, v in kwargs.items()}
        return func(*args, **kwargs)

    return wrapped


def get_or_create_user(user):
    try:
        data = user.to_dict()
        if not data.get("username"):
            data["username"] = data.get("id")

        user, _ = User.get_or_create(id=data.get("id"), defaults=data)
        return user
    except peewee.IntegrityError:
        logger.exception("Peweeeeeeerror")
    except Exception:
        logger.exception("'get_or_create_user' is not working")


def log_event(user, command):
    try:
        EventLog.create(user=user, command=command)
    except Exception:
        logger.exception("We couldn't log the event")


def create_user(func):
    """
    Decorator that creates and logs user.
    """

    @wraps(func)
    def wrapper(update, context, *args, **kwarg):
        command = func.__name__
        if not update.message.from_user:
            logger.warn(f"{command}... by unknown user")
            log_event(user=None, command=command)
            return func(update, context, *args, **kwarg)

        try:
            user = get_or_create_user(update.message.from_user)
            if user:
                logger.warn(f"{command}... by {user}")
                log_event(user, command=command)
            else:
                logger.warn(f"{command}... by unknown user {update.message.from_user}")
        except Exception:
            logger.exception("Something went wrong with create_user decorator")

        result = func(update, context, *args, **kwarg)
        return result

    return wrapper
