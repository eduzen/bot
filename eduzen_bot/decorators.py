import functools
from functools import wraps

import peewee
import structlog

from eduzen_bot.models import User

logger = structlog.get_logger(filename=__name__)


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
        args = tuple([HDict(arg) if isinstance(arg, dict) else arg for arg in args])
        kwargs = {k: HDict(v) if isinstance(v, dict) else v for k, v in kwargs.items()}
        return func(*args, **kwargs)

    return wrapped


def get_or_create_user(user):
    data = user.to_dict()
    logger.warn(data)
    try:
        user, created = User.get_or_create(username=data.get("username"), defaults=data)
        if not created:
            user.save()
        return user
    except peewee.IntegrityError:
        logger.warn("User already created")


def create_user(func):
    """
    Decorator that creates and logs user.
    """

    @wraps(func)
    def wrapper(update, context, *args, **kwarg):
        if not update.message.from_user:
            logger.warn(f"{func.__name__}... by unknown user")
            return func(update, context, *args, **kwarg)
        
        user = get_or_create_user(update.message.from_user)
        if user:
            logger.info(f"{func.__name__}... by {user} - {user.created_at}")
        else:
            logger.warn(f"{func.__name__}... by unknown user")
        result = func(update, context, *args, **kwarg)
        return result

    return wrapper
