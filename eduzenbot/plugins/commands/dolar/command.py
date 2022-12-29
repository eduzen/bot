"""
dolar - get_dolar
"""
import logging

from telegram import ChatAction, Update
from telegram.ext import CallbackContext
from telegram.ext import ExtBot as Bot

from eduzenbot.decorators import create_user

from .api import get_bluelytics, get_dolar_blue, get_dollar, parse_bnc

logger = logging.getLogger("rich")


def send_msg(bot: Bot, chat_id: str, msg: str, provider: str) -> str:
    if not msg:
        return f"No hay datos para mostrar de {provider}"
    bot.send_message(chat_id=chat_id, text=msg)


@create_user
def get_dolar(update: Update, context: CallbackContext) -> None:
    bot = context.bot
    chat_id = update.message.chat_id
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    try:
        dolarblue = get_dolar_blue()
        send_msg(bot, chat_id, dolarblue, "Dolar Blue")
        bluelytics = get_bluelytics()
        send_msg(bot, chat_id, bluelytics, "Bluelytics")
        banco_nacion = parse_bnc()
        send_msg(bot, chat_id, banco_nacion, "Banco Nacion")
        dolar = get_dollar()
        send_msg(bot, chat_id, dolar, "Openexchangerates")
    except Exception:
        logger.exception("Error getting dolar info")
        bot.send_message(chat_id=chat_id, text="Algo salió mal, intenta más tarde.")
