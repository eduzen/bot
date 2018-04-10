import logging

_LOG_LEVEL_STRINGS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'error': logging.ERROR,
}

logger = logging.getLogger()


def get_log(level=None, stream=None):
    handler = logging.StreamHandler()
    level = _LOG_LEVEL_STRINGS.get(level, logging.INFO)
    if not stream:
        handler = logging.FileHandler('bot.log')

    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.setLevel(level)

    return logger
