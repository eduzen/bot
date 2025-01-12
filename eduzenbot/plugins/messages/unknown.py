import logfire
from telegram import Update
from telegram.ext import ContextTypes


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    logfire.info(f"Unknown command: {update.message.text}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Che, no te entiendo, no existe ese comando!",
    )
