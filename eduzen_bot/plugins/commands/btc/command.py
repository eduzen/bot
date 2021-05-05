"""
btc - btc
"""
import structlog
from api import get_btc, get_dogecoin, get_eth
from telegram import ChatAction

from eduzen_bot.decorators import create_user

logger = structlog.get_logger()


@create_user
def btc(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    btc = get_btc() or ""
    dog = get_dogecoin() or ""
    eth = get_eth() or ""

    text = "\n".join([dog, eth, btc])

    context.bot.send_message(chat_id=update.message.chat_id, text=text)
