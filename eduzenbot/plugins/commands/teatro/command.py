"""
teatro - get_ranking
"""

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from eduzenbot.decorators import create_user

from .api import parse_alternativa


@create_user
async def get_ranking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /teatro [optional_number]

    Without arguments -> show top 5.
    With an integer argument -> show top N results.
    """
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        return

    # Send the "typing..." chat action
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    data = parse_alternativa()
    if not data:
        await context.bot.send_message(chat_id=chat_id, text="No se pudo obtener información de teatro.")
        return

    # Default number of items if no argument provided
    amount = 5

    # If the user supplied an argument, parse it
    if context.args:
        try:
            amount = int(context.args[0])
        except (ValueError, TypeError):
            await context.bot.send_message(
                chat_id=chat_id,
                text="El primer parámetro debe ser un número.",
            )
            return

    # Safeguard if 'amount' is larger than the data available
    amount = min(amount, len(data))

    # Format the text
    text = "\n".join(data[:amount])
    text = f"Ranking de lo más buscado en teatro:\n{text}\n" "By http://www.alternativateatral.com/"

    # Send the final message
    await context.bot.send_message(chat_id=chat_id, text=text)
