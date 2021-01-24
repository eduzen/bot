"""
code - code
"""
import structlog
from telegram import ChatAction

from eduzen_bot.auth.restricted import restricted
from eduzen_bot.decorators import create_user

logger = structlog.get_logger(filename=__name__)


@restricted
@create_user
def code(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    if not context.args:
        return

    args = " ".join(context.args)

    args = f"```python\n{args} \n```"

    context.bot.send_message(
        chat_id=update.message.chat_id, text=args, parse_mode="Markdown", disable_notification=True
    )
