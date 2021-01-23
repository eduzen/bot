"""
clima - weather
klima - klima
"""
import structlog
from telegram import ChatAction


from api import get_weather, get_klima

logger = structlog.get_logger()


def weather(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Weather... by {update.message.from_user.name}")

    text = get_weather()
    if not text:
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=text)


def klima(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Klima... by {update.message.from_user.name}")

    if not context.args:
        text = get_klima()
    else:
        city = "".join(args)
        text = get_klima(city)

    if not text:
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode="markdown")
