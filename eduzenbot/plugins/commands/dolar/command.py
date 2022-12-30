"""
dolar - get_dolar
"""
import logging

from telegram import ChatAction, Update
from telegram.ext import CallbackContext
from telegram.ext import ExtBot as Bot

from eduzenbot.decorators import create_user
from eduzenbot.plugins.commands.dolar.api import (
    get_banco_nacion,
    get_bluelytics,
    get_dolar_blue_geeklab,
)

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
    bot.send_message(chat_id=chat_id, text="Getting dolar info...")
    try:
        geeklab = get_dolar_blue_geeklab()
        send_msg(bot, chat_id, geeklab, "geeklab")
        bluelytics = get_bluelytics()
        send_msg(bot, chat_id, bluelytics, "Bluelytics")
        banco_nacion = get_banco_nacion()
        send_msg(bot, chat_id, banco_nacion, "Banco Nacion")
    except Exception:
        logger.exception("Error getting dolar info")
        bot.send_message(chat_id=chat_id, text="Algo salió mal, intenta más tarde.")
