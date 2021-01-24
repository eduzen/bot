"""
cambio - get_cotizaciones
dolar - get_dolar
dolarhoy - get_dolarhoy
dolarfuturo - get_dolarfuturo
"""
import structlog
from telegram import ChatAction

from telegram import Update
from telegram.ext import CallbackContext
from eduzen_bot.decorators import create_user

from api import parse_bnc, get_dollar, get_dolar_blue, parse_dolarhoy, parse_dolarfuturo

logger = structlog.get_logger(filename=__name__)


@create_user
def get_dolarhoy(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    data = parse_dolarhoy()
    if not data:
        context.bot.send_message(chat_id=update.message.chat_id, text="No pudimos conseguir la info")
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=data, parse_mode="markdown")


@create_user
def get_dolarfuturo(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    data = parse_dolarfuturo()
    if not data:
        context.bot.send_message(chat_id=update.message.chat_id, text="No pudimos conseguir la info")
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=data, parse_mode="markdown")


@create_user
def get_dolar(update: Update, context: CallbackContext) -> None:
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

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


@create_user
def get_cotizaciones(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    data = get_dolar_blue()
    if data:
        context.bot.send_message(chat_id=update.message.chat_id, text=data)

    data = parse_bnc()
    if not data:
        context.bot.send_message(chat_id=update.message.chat_id, text="No pudimos conseguir la info")
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=data)
