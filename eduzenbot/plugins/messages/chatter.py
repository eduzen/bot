import logging

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import CallbackContext

logger = logging.getLogger("rich")


def code(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query

    if not query:
        return

    query = f"```\n{query}\n```"

    results = [
        InlineQueryResultArticle(
            id=query.upper(),
            title="Chat",
            input_message_content=InputTextMessageContent(query, "MARKDOWN"),
        )
    ]
    context.bot.answer_inline_query(update.inline_query.id, results)
