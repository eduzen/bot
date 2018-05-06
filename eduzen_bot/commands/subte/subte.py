import structlog

from telegram import ChatAction

from .api import get_subte
from .crawlers import get_estado_del_subte, get_estado_metrovias_html

logger = structlog.get_logger(filename=__name__)


def subte_novedades(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Weather... by {update.message.from_user.name}")

    try:
        amount = int(args[0])
    except Exception:
        amount = 4

    text = get_subte(amount)
    if not text:
        return

    bot.send_message(chat_id=update.message.chat_id, text=text)


def subte(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Subte... by {update.message.from_user.name}")

    estadosubte = get_estado_del_subte()
    metrovias = get_estado_metrovias_html()
    if not estadosubte and not metrovias:
        return

    estadosubte = f"En el subte:\n{estadosubte}\nWeb metrovias:\n{metrovias}"

    bot.send_message(chat_id=update.message.chat_id, text=estadosubte)
