"""
transito - transito
"""
import structlog
from api import get_transito
from telegram import ChatAction

from eduzen_bot.decorators import create_user

logger = structlog.get_logger(filename=__name__)


@create_user
def transito(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    text = get_transito()
    if not text:
        context.bot.send_message(chat_id=update.message.chat_id, text="Ups, no pudimos conseguir la info")
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=text)
