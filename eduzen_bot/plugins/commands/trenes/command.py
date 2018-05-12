import structlog
from telegram import ChatAction

from trenes.api import get_trenes

logger = structlog.get_logger(filename=__name__)


def trenes(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Trenes... by {update.message.from_user.name}")

    text = get_trenes()
    if not text:
        return

    bot.send_message(chat_id=update.message.chat_id, text=text)
