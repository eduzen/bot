"""
clima - weather
klima - klima
"""
import logging

from api import get_klima, get_weather
from telegram import ChatAction, Update
from telegram.ext import CallbackContext

from eduzenbot.decorators import create_user

logger = logging.getLogger()


@create_user
def weather(update: Update, context: CallbackContext, *args: int, **kwargs: str) -> None:
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    if not context.args:
        text = get_weather()
    else:
        city = " ".join(context.args)
        text = get_klima(city)

    if not text:
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=text)


@create_user
def klima(update: Update, context: CallbackContext, *args: int, **kwargs: str) -> None:
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    if not context.args:
        text = get_klima()
    else:
        city = " ".join(context.args)
        text = get_klima(city)

    if not text:
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode="Markdown")
