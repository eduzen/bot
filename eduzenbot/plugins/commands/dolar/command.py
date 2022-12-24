"""
dolar - get_dolar
"""
import logging

from api import get_bluelytics, get_dolar_blue, get_dollar, parse_bnc
from telegram import ChatAction, Update
from telegram.ext import CallbackContext

from eduzenbot.decorators import create_user

logger = logging.getLogger("rich")


@create_user
def get_dolar(update: Update, context: CallbackContext) -> None:
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    flag = False

    data = get_dolar_blue()
    if data:
        flag = True
        context.bot.send_message(chat_id=update.message.chat_id, text=data)

    data = get_bluelytics()
    if data:
        flag = True
        context.bot.send_message(chat_id=update.message.chat_id, text=data)

    data = get_dollar()
    if data:
        flag = True
        context.bot.send_message(chat_id=update.message.chat_id, text=data)

    data = parse_bnc()
    if not data:
        flag = True
        context.bot.send_message(chat_id=update.message.chat_id, text=data)

    if not flag:
        context.bot.send_message(chat_id=update.message.chat_id, text="No pudimos conseguir la info")
