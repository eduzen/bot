"""
code - code
"""
import logging

from telegram import ChatAction, Update

from eduzenbot.auth.restricted import restricted
from eduzenbot.decorators import create_user

logger = logging.getLogger("rich")


@restricted
@create_user
def code(update: Update, context: object, *args: int, **kwargs: str):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    if not context.args:
        return

    args = " ".join(context.args)

    args = f"```python\n{args} \n```"

    context.bot.send_message(
        chat_id=update.message.chat_id, text=args, parse_mode="Markdown", disable_notification=True
    )
