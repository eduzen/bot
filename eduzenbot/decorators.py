import functools
from collections.abc import Callable
from functools import wraps
from typing import Any

import logfire
import peewee
from telegram import Update
from telegram.ext import CallbackContext

from eduzenbot.models import EventLog, User


def hash_dict(func: Callable) -> Callable:
    """Transform mutable dictionnary
    Into immutable
    Useful to be compatible with cache
    """

    class HDict(dict):
        def __hash__(self) -> str:
            return hash(frozenset(self.items()))

    @functools.wraps(func)
    def wrapped(*args: int, **kwargs: str) -> Callable:
        args = tuple(HDict(arg) if isinstance(arg, dict) else arg for arg in args)
        kwargs = {k: HDict(v) if isinstance(v, dict) else v for k, v in kwargs.items()}
        return func(*args, **kwargs)

    return wrapped


def get_or_create_user(user: User) -> User | None:
    try:
        data = user.to_dict()
        if not data.get("username"):
            data["username"] = data.get("id")

        user, _ = User.get_or_create(id=data.get("id"), defaults=data)
        return user
    except peewee.IntegrityError:
        logfire.exception("Peweeeeeeerror")
    except Exception:
        logfire.exception("'get_or_create_user' is not working")


def log_event(user: User, command: str) -> None:
    try:
        EventLog.create(user=user, command=command)
    except Exception:
        logfire.exception("We couldn't log the event")


def create_user(func: Callable) -> Callable:
    """
    Decorator that creates and logs user.
    """

    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args: int, **kwarg: dict[Any, Any]) -> Callable:
        command = func.__name__
        if not update.message.from_user:
            logfire.warn(f"{command}... by unknown user")
            log_event(user=None, command=command)
            return func(update, context, *args, **kwarg)

        try:
            user = get_or_create_user(update.message.from_user)
            if user:
                logfire.warn(f"{command}... by {user}")
                log_event(user, command=command)
            else:
                logfire.warn(f"{command}... by unknown user {update.message.from_user}")
        except Exception:
            logfire.exception("Something went wrong with create_user decorator")

        result = func(update, context, *args, **kwarg)
        return result

    return wrapper
