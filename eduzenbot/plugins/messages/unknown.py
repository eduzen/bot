from telegram import Update
from telegram.ext import CallbackContext


def unknown(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.message.chat_id, text="Che, no te entiendo, no existe ese comando!")
