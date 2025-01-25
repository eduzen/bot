from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


async def code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query

    if not query:
        return

    formatted_query = f"```\n{query}\n```"

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Chat",
            input_message_content=InputTextMessageContent(formatted_query, parse_mode=ParseMode.MARKDOWN),
        )
    ]

    await context.bot.answer_inline_query(update.inline_query.id, results)
