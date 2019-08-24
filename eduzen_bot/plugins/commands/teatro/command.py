"""
teatro - get_ranking
"""
import structlog
from telegram import ChatAction
from telegram.ext.dispatcher import run_async

from api import parse_alternativa

logger = structlog.get_logger(filename=__name__)


@run_async
def get_ranking(bot, update, args, **kwargs):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Teatro... by {update.message.from_user.name}")

    data = parse_alternativa()
    if not data:
        return

    if not args:
        logger.info(data)
        text = "\n".join(data[:5])
        text = (
            f"Ranking de lo más buscado en teatro:\n{text}\nBy http://www.alternativateatral.com/"
        )
        bot.send_message(chat_id=update.message.chat_id, text=text)
        return

    try:
        amount = int(args[0])
    except (ValueError, TypeError):
        bot.send_message(
            chat_id=update.message.chat_id, text="El primer parametro tiene que ser un número"
        )

    text = "\n".join(data[:amount])
    text = f"Ranking de lo más buscado en teatro:\n{text}\nBy http://www.alternativateatral.com/"

    bot.send_message(chat_id=update.message.chat_id, text=text)
    return
