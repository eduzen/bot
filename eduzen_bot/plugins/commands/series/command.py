"""
serie - search_serie
"""
import structlog
from api import tmdb_search

logger = structlog.get_logger(filename=__name__)


@run_async
def search_serie(bot, update, **kwargs):
    args = kwargs.get('args')
    chat_data = kwargs.get('chat_data')
    if not args:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Te faltó pasarme el nombre de la serie. /serie <serie>',
        )
        return

    query = ' '.join(args)
    logger.info(f"Search serie {args}")
    tmdb_search(bot, update.message.chat_id, chat_data, query)
