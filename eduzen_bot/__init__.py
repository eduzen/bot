# -*- coding: utf-8 -*-
"""Top-level package for eduzen_bot."""

import os
from os.path import abspath, dirname
from logging import config as logging_config

import structlog
import yaml


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
            config["root"]["handlers"].append("stdout")

        logging_config.dictConfig(config)


def set_handler(arguments):
    if arguments.get("--verbose") or arguments.get("-v"):
        return True

    elif arguments.get("--quiet") or arguments.get("-q"):
        return False

    return False
