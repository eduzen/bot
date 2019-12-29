"""
code - code
"""
import structlog
from telegram import ChatAction

from eduzen_bot.auth.restricted import restricted

logger = structlog.get_logger(filename=__name__)


@restricted
def code(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Code... by {update.message.from_user.name}")

    if not context.args:
        return

    args = " ".join(context.args)

    args = f"```python\n{args} \n```"

    context.bot.send_message(
        chat_id=update.message.chat_id, text=args, parse_mode="Markdown", disable_notification=True
    )
