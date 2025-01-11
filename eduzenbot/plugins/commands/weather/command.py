"""
clima - weather
klima - klima
"""

from api import get_klima, get_weather
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from eduzenbot.decorators import create_user


@create_user
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: int, **kwargs: str) -> None:
    """Handle /weather command to fetch weather for a specific city or default location."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    if not context.args:
        text = get_weather()
    else:
        city = " ".join(context.args)
        text = get_klima(city)

    if not text:
        return

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


@create_user
async def klima(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: int, **kwargs: str) -> None:
    """Handle /klima command to fetch detailed weather for a specific city or default."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    if not context.args:
        text = get_klima()
    else:
        city = " ".join(context.args)
        text = get_klima(city)

    if not text:
        return

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="Markdown")
