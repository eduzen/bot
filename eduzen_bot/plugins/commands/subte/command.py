"""
subte - subte
subtenews - subte_novedades
"""
import structlog

from telegram import ChatAction
from telegram.ext.dispatcher import run_async
from emoji import emojize

from api import get_subte
from subte.crawlers import get_estado_del_subte, get_estado_metrovias_html

logger = structlog.get_logger(filename=__name__)
metro = emojize(":metro:", use_aliases=True)


@run_async
def subte_novedades(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Subte_novedades... by {update.message.from_user.name}")

    try:
        amount = int(args[0])
    except Exception:
        amount = 4

    text = get_subte(amount)
    if not text:
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=f"{metro} {text}")


@run_async
def subte(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Subte... by {update.message.from_user.name}")

    estadosubte = get_estado_del_subte()
    if estadosubte:
        estadosubte = f"{metro} En el subte:\n{estadosubte}"
        context.bot.send_message(chat_id=update.message.chat_id, text=estadosubte)

    metrovias = get_estado_metrovias_html()
    if metrovias:
        metrovias = f"Web metrovias {metro}:\n{metrovias}"
        context.bot.send_message(chat_id=update.message.chat_id, text=metrovias)
