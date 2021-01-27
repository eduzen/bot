"""Top-level package for eduzen_bot."""

import os
from logging import config as logging_config
from os.path import abspath, dirname

import structlog
import yaml

timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")

pre_chain = [
    # Add the log level and a timestamp to the event_dict if the log entry
    # is not from structlog.
    structlog.stdlib.add_log_level,
    timestamper,
]

LOGGING_CONFIG = os.path.join(dirname(abspath(__file__)), "logging.yml")

_LOG_LEVEL_STRINGS = {"debug": "DEBUG", "info": "INFO", "error": "ERROR"}


def initialize_logging(verbose=False, level="INFO"):
    """
    Initialize the loggers from the
    YAML configuration.
    """
    structlog.configure(
        processors=[structlog.processors.KeyValueRenderer(key_order=["uuid", "event"])],
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    with open(LOGGING_CONFIG) as infile:
        config = yaml.load(infile)
        config["root"]["level"] = "INFO"
        if verbose:
            # Requires that there is a stdout handler defined at
            # logger configuration
            config["formatters"]["colored"]["()"] = structlog.stdlib.ProcessorFormatter
            config["formatters"]["colored"]["foreign_pre_chain"] = pre_chain
            config["formatters"]["colored"]["processor"] = structlog.dev.ConsoleRenderer(colors=True)
            config["root"]["handlers"].append("stdout")

        logging_config.dictConfig(config)


def set_handler(arguments):
    if arguments.get("--verbose") or arguments.get("-v"):
        return True

    elif arguments.get("--quiet") or arguments.get("-q"):
        return False

    return False


__all__ = [
    "models",
    "keys",
    "auth",
    "menus",
]
