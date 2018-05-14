import structlog
from telegram import ChatAction

from .api import parse_bnc

logger = structlog.get_logger(filename=__name__)


def dolar(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Dollar... by {update.message.from_user.name}")

    data = parse_bnc()

    if not data:
        bot.send_message(
            chat_id=update.message.chat_id, text="No pudimos conseguir la info"
        )
        return

    bot.send_message(chat_id=update.message.chat_id, text=data)


def cotizaciones(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"cotizaciones... by {update.message.from_user.name}")

    data = parse_bnc()

    if not data:
        bot.send_message(
            chat_id=update.message.chat_id, text="No pudimos conseguir la info"
        )
        return

    bot.send_message(chat_id=update.message.chat_id, text=data)
