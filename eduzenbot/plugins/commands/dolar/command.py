"""
dolar - get_dolar
"""

import logfire
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from eduzenbot.decorators import create_user
from eduzenbot.plugins.commands.dolar.api import (
    get_banco_nacion,
    get_bluelytics,
    get_dolar_blue_geeklab,
)


@create_user
async def get_dolar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch and send the latest dolar information."""
    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await context.bot.send_message(chat_id=chat_id, text="Getting dolar info...")

    try:
        geeklab = get_dolar_blue_geeklab()
        await context.bot.send_message(chat_id=chat_id, text=geeklab)

        bluelytics = get_bluelytics()
        await context.bot.send_message(chat_id=chat_id, text=bluelytics)

        banco_nacion = get_banco_nacion()
        await context.bot.send_message(chat_id=chat_id, text=banco_nacion)

    except Exception:
        logfire.exception("Error getting dolar info")
        await context.bot.send_message(chat_id=chat_id, text="Algo salió mal, intenta más tarde.")
