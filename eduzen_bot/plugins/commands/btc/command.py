"""
btc - btc
"""
import structlog
from telegram import ChatAction
from eduzen_bot.decorators import create_user

from api import get_btc

logger = structlog.get_logger()


@create_user
def btc(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    text = get_btc()

    context.bot.send_message(chat_id=update.message.chat_id, text=text)
