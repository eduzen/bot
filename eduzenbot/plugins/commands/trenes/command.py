"""
trenes - trenes
"""

import logfire
from api import get_trenes
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from eduzenbot.decorators import create_user


@create_user
async def trenes(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: int, **kwargs: str) -> None:
    """Handle /trenes command to fetch train status."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    logfire.info(f"Trenes... by {update.effective_user.username}")

    text = get_trenes()
    if not text:
        return

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
