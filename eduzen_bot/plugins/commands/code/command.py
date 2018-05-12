import structlog
from telegram import ChatAction

from auth.restricted import restricted

logger = structlog.get_logger(filename=__name__)


@restricted
def code(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Code... by {update.message.from_user.name}")

    if not args:
        return

    args = " ".join(list(args))

    args = f"```python\n{args} \n```"

    bot.send_message(
        chat_id=update.message.chat_id,
        text=args,
        parse_mode="Markdown",
        disable_notification=True,
    )
