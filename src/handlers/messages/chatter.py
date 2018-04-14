import logging

from telegram import InlineQueryResultArticle, InputTextMessageContent

logger = logging.getLogger()


def code(bot, update):
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
    bot.answer_inline_query(update.inline_query.id, results)
