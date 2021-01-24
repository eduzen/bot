"""
clima - weather
klima - klima
"""
from eduzen_bot.decorators import create_user
import structlog
from telegram import ChatAction


from api import get_weather, get_klima

logger = structlog.get_logger()


@create_user
def weather(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    text = get_weather()
    if not text:
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=text)


@create_user
def klima(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    if not context.args:
        text = get_klima()
    else:
        city = "".join(args)
        text = get_klima(city)

    if not text:
        return

    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode="markdown")
