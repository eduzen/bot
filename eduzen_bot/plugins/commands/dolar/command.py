"""
cambio - get_cotizaciones
dolar - get_dolar
dolarhoy - get_dolarhoy
dolarfuturo - get_dolarfuturo
"""
import structlog
from telegram import ChatAction
from telegram.ext.dispatcher import run_async
from telegram import Update
from telegram.ext import CallbackContext

from api import parse_bnc, get_dollar, get_dolar_blue, parse_dolarhoy, parse_dolarfuturo

logger = structlog.get_logger(filename=__name__)


@run_async
def get_dolarhoy(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Dollar... by {update.message.from_user.name}")

    data = parse_dolarhoy()
    if not data:
        context.bot.send_message(chat_id=update.message.chat_id, text="No pudimos conseguir la info")
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=data, parse_mode='markdown')


@run_async
def get_dolarfuturo(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Dolla... by {update.message.from_user.name}")

    data = parse_dolarfuturo()
    if not data:
        context.bot.send_message(chat_id=update.message.chat_id, text="No pudimos conseguir la info")
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=data, parse_mode='markdown')


# @run_async
def get_dolar(update: Update, context: CallbackContext) -> None:
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Dollar... by {update.message.from_user.name}")

    if not context.args:
        data = parse_bnc()
        if data:
            context.bot.send_message(chat_id=update.message.chat_id, text=data)
            return

    if "v" not in context.args:
        data = get_dollar()
        if data:
            context.bot.send_message(chat_id=update.message.chat_id, text=data)
        return

    data = get_dollar()
    if data:
        context.bot.send_message(chat_id=update.message.chat_id, text=data)

    data = get_dolar_blue()
    if data:
        context.bot.send_message(chat_id=update.message.chat_id, text=data)

    data = parse_bnc()
    if not data:
        context.bot.send_message(chat_id=update.message.chat_id, text="No pudimos conseguir la info")
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=data)


@run_async
def get_cotizaciones(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"cotizaciones... by {update.message.from_user.name}")

    data = get_dolar_blue()
    if data:
        context.bot.send_message(chat_id=update.message.chat_id, text=data)

    data = parse_bnc()
    if not data:
        context.bot.send_message(chat_id=update.message.chat_id, text="No pudimos conseguir la info")
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=data)
