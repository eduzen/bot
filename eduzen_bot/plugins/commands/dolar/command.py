"""
cambio - get_cotizaciones
dolar - get_dolar
dolarhoy - get_dolarhoy
dolarfuturo - get_dolarfuturo
"""
import structlog
from telegram import ChatAction
from telegram.ext.dispatcher import run_async

from api import parse_bnc, get_dollar, get_dolar_blue, parse_dolarhoy, parse_dolarfuturo

logger = structlog.get_logger(filename=__name__)


@run_async
def get_dolarhoy(bot, update, args, **kwargs):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Dollar... by {update.message.from_user.name}")

    data = parse_dolarhoy()
    if not data:
        bot.send_message(
            chat_id=update.message.chat_id, text="No pudimos conseguir la info"
        )
        return

    bot.send_message(chat_id=update.message.chat_id, text=data, parse_mode='markdown')



@run_async
def get_dolarfuturo(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Dolla... by {update.message.from_user.name}")

    data = parse_dolarfuturo()
    if not data:
        bot.send_message(
            chat_id=update.message.chat_id, text="No pudimos conseguir la info"
        )
        return

    bot.send_message(chat_id=update.message.chat_id, text=data, parse_mode='markdown')


@run_async
def get_dolar(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Dollar... by {update.message.from_user.name}")

    if not args:
        data = parse_bnc()
        if data:
            bot.send_message(chat_id=update.message.chat_id, text=data)
            return

    if "v" not in args:
        data = get_dollar()
        if data:
            bot.send_message(chat_id=update.message.chat_id, text=data)
        return

    data = get_dollar()
    if data:
        bot.send_message(chat_id=update.message.chat_id, text=data)

    data = get_dolar_blue()
    if data:
        bot.send_message(chat_id=update.message.chat_id, text=data)

    data = parse_bnc()
    if not data:
        bot.send_message(
            chat_id=update.message.chat_id, text="No pudimos conseguir la info"
        )
        return

    bot.send_message(chat_id=update.message.chat_id, text=data)


@run_async
def get_cotizaciones(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"cotizaciones... by {update.message.from_user.name}")

    data = get_dolar_blue()
    if data:
        bot.send_message(chat_id=update.message.chat_id, text=data)

    data = parse_bnc()
    if not data:
        bot.send_message(
            chat_id=update.message.chat_id, text="No pudimos conseguir la info"
        )
        return

    bot.send_message(chat_id=update.message.chat_id, text=data)
