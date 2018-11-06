"""
transito - transito
"""
import structlog
from telegram import ChatAction
from telegram.ext.dispatcher import run_async

from api import get_transito

logger = structlog.get_logger(filename=__name__)


@run_async
def transito(bot, update, args, **kwargs):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Tránsito... by {update.message.from_user.name}")

    text = get_transito()
    if not text:
        bot.send_message(
            chat_id=update.message.chat_id, text="Ups, no pudimos conseguir la info"
        )
        return

    bot.send_message(chat_id=update.message.chat_id, text=text)
