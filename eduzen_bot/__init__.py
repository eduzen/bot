"""Top-level package for eduzen_bot."""
import datetime as dt
import logging


def add_timestamp(_, __, event_dict):
    event_dict["timestamp"] = dt.datetime.utcnow()
    return event_dict


LEVELS = {
    "NOTSET": logging.NOTSET,
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


__all__ = [
    "models",
    "keys",
    "auth",
    "menus",
]
