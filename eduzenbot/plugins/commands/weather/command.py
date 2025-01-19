"""
clima - klima
klima - klima
"""

import logfire
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from eduzenbot.decorators import create_user

from .api import get_klima


@create_user
async def klima(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: int, **kwargs: str) -> None:
    chat_id = str(update.effective_chat.id) if update.effective_chat else None

    if not chat_id:
        logfire.error("Failed to get chat_id. Update does not have effective_chat.")
        return

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    if not context.args:
        text = await get_klima()
    else:
        city = " ".join(context.args)
        text = await get_klima(city)

    if not text:
        return

    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
