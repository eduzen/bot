"""
btc - btc
"""
import structlog
from telegram import ChatAction

from .api import get_btc

logger = structlog.get_logger()


def btc(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Btc... by {update.message.from_user.name}")

    text = get_btc()

    bot.send_message(chat_id=update.message.chat_id, text=text)
