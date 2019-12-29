import logging
from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent, ParseMode
from telegram.utils.helpers import escape_markdown

logger = logging.getLogger()


def code_markdown(update, context):
    query = update.inline_query.query

    if not query:
        return

    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="code",
            input_message_content=InputTextMessageContent(
                f"```\n{query}\n```", parse_mode=ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(), title="Caps", input_message_content=InputTextMessageContent(query.upper())
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Bold",
            input_message_content=InputTextMessageContent(
                "*{}*".format(escape_markdown(query)), parse_mode=ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Italic",
            input_message_content=InputTextMessageContent(
                "_{}_".format(escape_markdown(query)), parse_mode=ParseMode.MARKDOWN
            ),
        ),
    ]
    context.bot.answer_inline_query(update.inline_query.id, results)
