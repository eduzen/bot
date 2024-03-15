"""
subte - subte
subtenews - subte_novedades
"""

import logging

from api import get_subte
from emoji import emojize
from subte.crawlers import get_estado_del_subte, get_estado_metrovias_html
from telegram import ChatAction, Update
from telegram.ext import CallbackContext

from eduzenbot.decorators import create_user

logger = logging.getLogger("rich")
metro = emojize(":metro:")


@create_user
def subte_novedades(
    update: Update, context: CallbackContext, *args: int, **kwargs: str
) -> None:
    context.bot.send_chat_action(
        chat_id=update.message.chat_id, action=ChatAction.TYPING
    )

    try:
        amount = int(args[0])
    except Exception:
        amount = 4

    text = get_subte(amount)
    if not text:
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=f"{metro} {text}")


@create_user
def subte(update: Update, context: CallbackContext, *args: int, **kwargs: str) -> None:
    context.bot.send_chat_action(
        chat_id=update.message.chat_id, action=ChatAction.TYPING
    )

    estadosubte = get_estado_del_subte()
    if estadosubte:
        estadosubte = f"{metro} En el subte:\n{estadosubte}"
        context.bot.send_message(chat_id=update.message.chat_id, text=estadosubte)

    metrovias = get_estado_metrovias_html()
    if metrovias:
        metrovias = f"Web metrovias {metro}:\n{metrovias}"
        context.bot.send_message(chat_id=update.message.chat_id, text=metrovias)
