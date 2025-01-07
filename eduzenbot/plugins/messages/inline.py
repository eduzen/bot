from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown


async def code_markdown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query

    if not query:
        return

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Code",
            input_message_content=InputTextMessageContent(f"```\n{query}\n```", parse_mode=ParseMode.MARKDOWN),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Caps",
            input_message_content=InputTextMessageContent(query.upper()),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Bold",
            input_message_content=InputTextMessageContent(f"*{escape_markdown(query)}*", parse_mode=ParseMode.MARKDOWN),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Italic",
            input_message_content=InputTextMessageContent(f"_{escape_markdown(query)}_", parse_mode=ParseMode.MARKDOWN),
        ),
    ]

    await context.bot.answer_inline_query(update.inline_query.id, results)
