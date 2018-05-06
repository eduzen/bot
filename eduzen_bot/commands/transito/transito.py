import structlog
from telegram import ChatAction

from .api import get_transito

logger = structlog.get_logger(filename=__name__)


def transito(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Tránsito... by {update.message.from_user.name}")

    text = get_transito()
    if not text:
        bot.send_message(chat_id=update.message.chat_id, text="Ups, no pudimos conseguir la info")
        return

    bot.send_message(chat_id=update.message.chat_id, text=text)
