"""
transito - transito
"""

from api import get_transito
from telegram import ChatAction, Update
from telegram.ext import CallbackContext

from eduzenbot.decorators import create_user


@create_user
def transito(update: Update, context: CallbackContext, *args: int, **kwargs: str) -> None:
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    text = get_transito()
    if not text:
        context.bot.send_message(chat_id=update.message.chat_id, text="Ups, no pudimos conseguir la info")
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=text)
