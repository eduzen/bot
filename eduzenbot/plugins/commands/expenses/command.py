"""
gasto - expense
"""

import logfire
from api import send_expense
from telegram import ChatAction, Update
from telegram.ext import ContextTypes

from eduzenbot.auth.restricted import restricted
from eduzenbot.decorators import create_user


@restricted
@create_user
async def expense(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: int, **kwargs: str) -> None:
    """Handle /gasto command to log an expense."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    if update.effective_user.username != "eduzen":
        await update.message.reply_text(
            f"Mmm... no es para ti! Humano {update.effective_user.first_name}, "
            "inferior ya callate! No es un comando que tu puedas usar."
        )
        return

    if not context.args:
        await update.message.reply_text("Mmm... no enviaste nada!")
        return

    try:
        amount = float(context.args[0])
    except (ValueError, IndexError):
        logfire.error("No pudimos convertir %s", context.args)
        await update.message.reply_text("Error: No pudimos convertir el monto. Por favor, revisa tu entrada.")
        return

    try:
        title = " ".join(context.args[1:])
    except IndexError:
        title = "gasto desconocido"

    try:
        response = send_expense(title, amount)
    except Exception as e:
        logfire.exception("Algo pasó: %s", e)
        await update.message.reply_text("Chequea que algo pasó y no pudimos enviar el gasto!")
        return

    if response.status_code != 201:
        await update.message.reply_text("Chequea que algo pasó y no pudimos enviar el gasto!")
        return

    await update.message.reply_text(f"¡Joya {update.effective_user.first_name}! Gasto agendado.")
