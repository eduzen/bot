"""
teatro - get_ranking
"""
import structlog
from telegram import ChatAction

from eduzen_bot.decorators import create_user
from api import parse_alternativa

logger = structlog.get_logger(filename=__name__)


@create_user
def get_ranking(update, context, *args, **kwargs):
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
        context.bot.send_message(chat_id=update.message.chat_id, text="El primer parametro tiene que ser un número")

    try:
        text = "\n".join(data[:amount])
    except IndexError:
        text = "\n".join(data[:9])

    text = f"Ranking de lo más buscado en teatro:\n{text}\nBy http://www.alternativateatral.com/"

    context.bot.send_message(chat_id=update.message.chat_id, text=text)
    return
