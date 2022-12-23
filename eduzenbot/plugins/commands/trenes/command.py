"""
trenes - trenes
"""
import logging

from api import get_trenes
from telegram import ChatAction

from eduzenbot.decorators import create_user

logger = logging.getLogger("rich")


@create_user
def trenes(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Trenes... by {update.message.from_user.name}")

    text = get_trenes()
    if not text:
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=text)
