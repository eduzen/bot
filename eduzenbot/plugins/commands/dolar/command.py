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
    chat_id = update.effective_chat.id if update.effective_chat else None
    if not chat_id:
        logfire.error("Failed to get chat_id. Update does not have effective_chat.")
        return

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await context.bot.send_message(chat_id=chat_id, text="Getting dolar info...")

    try:
        geeklab = await get_dolar_blue_geeklab()
        if geeklab:
            await context.bot.send_message(chat_id=chat_id, text=geeklab)

        bluelytics = await get_bluelytics()
        if bluelytics:
            await context.bot.send_message(chat_id=chat_id, text=bluelytics)

        banco_nacion = await get_banco_nacion()
        if banco_nacion:
            await context.bot.send_message(chat_id=chat_id, text=banco_nacion)

    except Exception:
        logfire.exception("Error getting dolar info")
        await context.bot.send_message(chat_id=chat_id, text="Algo salió mal, intenta más tarde.")
