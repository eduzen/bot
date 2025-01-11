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


async def send_msg(context: ContextTypes.DEFAULT_TYPE, chat_id: str, msg: str, provider: str) -> str | None:
    """Send a message to the user with dolar information."""
    if not msg:
        return f"No hay datos para mostrar de {provider}"
    await context.bot.send_message(chat_id=chat_id, text=msg)


@create_user
async def get_dolar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch and send the latest dolar information."""
    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await context.bot.send_message(chat_id=chat_id, text="Getting dolar info...")

    try:
        geeklab = get_dolar_blue_geeklab()
        await send_msg(context, chat_id, geeklab, "geeklab")
        bluelytics = get_bluelytics()
        await send_msg(context, chat_id, bluelytics, "Bluelytics")
        banco_nacion = get_banco_nacion()
        await send_msg(context, chat_id, banco_nacion, "Banco Nacion")
    except Exception:
        logfire.exception("Error getting dolar info")
        await context.bot.send_message(chat_id=chat_id, text="Algo salió mal, intenta más tarde.")
