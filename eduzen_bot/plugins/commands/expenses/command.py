"""
gasto - expense
"""
from telegram import ChatAction
from eduzen_bot.auth.restricted import restricted
from eduzen_bot.decorators import create_user
import structlog

from api import send_expense

logger = structlog.get_logger(filename=__name__)


@restricted
@create_user
def expense(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    if not update.message.from_user.name == "@eduzen":
        update.message.reply_text(
            f"Mmm... no es para ti! Humano {update.message.from_user.name} "
            "inferior ya callate! No es un comando que tu pueadas usar"
        )
        return

    if not context.args:
        update.message.reply_text("mmm no enviaste nada!")
        return

    try:
        amount = float(args[0])
    except Exception:
        logger.error("No pudimos convertir %s", args)

    try:
        title = args[1]
    except Exception:
        title = "gasto desconocido"

    try:
        r = send_expense(title, amount)
    except Exception:
        logger.exception("algo paso")
        update.message.reply_text("Chequea que algo paso y no pudimos enviar el gasto!")
        return

    if r.status_code != 201:
        update.message.reply_text("Chequea que algo paso y no pudimos enviar el gasto!")
        return

    update.message.reply_text(f"Joya {update.message.from_user.name}! Gasto agendado!")
