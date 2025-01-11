"""
subte - subte
subtenews - subte_novedades
"""

from api import get_subte
from emoji import emojize
from subte.crawlers import get_estado_del_subte, get_estado_metrovias_html
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from eduzenbot.decorators import create_user

metro = emojize(":metro:")


@create_user
async def subte_novedades(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: int, **kwargs: str) -> None:
    """Handle /subtenews command to fetch the latest subway news."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        amount = int(context.args[0])  # Use `context.args` to fetch arguments.
    except (ValueError, IndexError):
        amount = 4  # Default value if no argument is provided.

    text = get_subte(amount)
    if not text:
        return

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{metro} {text}")


@create_user
async def subte(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: int, **kwargs: str) -> None:
    """Handle /subte command to fetch subway status."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    estadosubte = get_estado_del_subte()
    if estadosubte:
        estadosubte = f"{metro} En el subte:\n{estadosubte}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=estadosubte)

    metrovias = get_estado_metrovias_html()
    if metrovias:
        metrovias = f"Web metrovias {metro}:\n{metrovias}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=metrovias)
