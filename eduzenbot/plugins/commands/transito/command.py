"""
transito - transito
"""
import logging

from api import get_transito
from telegram import ChatAction, Update

from eduzenbot.decorators import create_user

logger = logging.getLogger("rich")


@create_user
def transito(update: Update, context: object, *args: int, **kwargs: str):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    text = get_transito()
    if not text:
        context.bot.send_message(chat_id=update.message.chat_id, text="Ups, no pudimos conseguir la info")
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=text)
