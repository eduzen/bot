"""
teatro - get_ranking
"""

from api import parse_alternativa
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import CallbackContext

from eduzenbot.decorators import create_user


@create_user
def get_ranking(update: Update, context: CallbackContext, *args: int, **kwargs: str) -> None:
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    data = parse_alternativa()
    if not data:
        return

    if not context.args:
        text = "\n".join(data[:5])
        text = f"Ranking de lo más buscado en teatro:\n{text}\nBy http://www.alternativateatral.com/"
        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return

    try:
        amount = int(context.args[0])
    except (ValueError, TypeError):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="El primer parametro tiene que ser un número",
        )

    try:
        text = "\n".join(data[:amount])
    except IndexError:
        text = "\n".join(data[:9])

    text = f"Ranking de lo más buscado en teatro:\n{text}\nBy http://www.alternativateatral.com/"

    context.bot.send_message(chat_id=update.message.chat_id, text=text)
    return
