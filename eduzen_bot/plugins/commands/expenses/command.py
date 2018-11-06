"""
gasto - expense
"""
from telegram import ChatAction
from auth.restricted import restricted
import structlog

from api import send_expense

logger = structlog.get_logger(filename=__name__)


@restricted
def expense(bot, update, args, **kwargs):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"expenses... by {update.message.from_user.name}")
    if not update.message.from_user.name == "@eduzen":
        update.message.reply_text(
            f"Mmm... no es para ti! Humano {update.message.from_user.name} "
            "inferior ya callate! No es un comando que tu pueadas usar"
        )
        return

    if not args:
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
