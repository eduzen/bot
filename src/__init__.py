import logging

_LOG_LEVEL_STRINGS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'error': logging.ERROR,
}

logger = logging.getLogger()


def get_log(level=None, stream=None):
    logger.info("aca")
    handler = logging.FileHandler('bot.log')
    level = _LOG_LEVEL_STRINGS.get(level, logging.INFO)
    if stream:
        handler = logging.StreamHandler()

    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.setLevel(level)
    logger.info("aca 2")

    return logger
