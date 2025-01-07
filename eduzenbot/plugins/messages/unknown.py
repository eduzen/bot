from telegram import Update
from telegram.ext import ContextTypes


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.chat_id,
        text="Che, no te entiendo, no existe ese comando!",
    )
