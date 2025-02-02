"""
news - get_news
"""

import os

import httpx
import logfire
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from eduzenbot.decorators import create_user

MAX_MESSAGE_LENGTH = 4096

client = httpx.AsyncClient()


async def _get_news(country="ar"):
    api_key = os.getenv("NEWS_API_KEY")
    base_url = "https://newsapi.org/v2/top-headlines"

    params = {
        "apiKey": api_key,
    }

    if country == "ar":
        params["sources"] = "infobae,la-nacion"
    elif country == "nl":
        params["sources"] = "rtl-nieuws"
    else:
        params["sources"] = "bbc-news,techcrunch,techradar"

    response = await client.get(base_url, params=params)
    news_data = response.json()
    articles = news_data.get("articles", [])

    news_list = []
    for article in articles[:5]:
        title = article.get("title", "No title available")
        description = article.get("description", "")
        article_url = article.get("url", "")
        news_list.append(rf"- [{title}]({article_url}): {description}")

    return "\n".join(news_list)


@create_user
async def get_news(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: int, **kwargs: str) -> None:
    """
    /news country
    Retrieves the latest bot events from the EventLog.
    """
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        logfire.error("No valid chat_id. Could not send events.")
        return

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    country = context.args[0] if context.args else "us"

    try:
        news = await _get_news(country)
        if not news:
            await context.bot.send_message(
                chat_id=chat_id, text=f"No news for {country}", disable_web_page_preview=True
            )
            return

        # If the news text is too long, split it into chunks.
        if len(news) > MAX_MESSAGE_LENGTH:
            for i in range(0, len(news), MAX_MESSAGE_LENGTH):
                chunk = news[i : i + MAX_MESSAGE_LENGTH]
                await context.bot.send_message(
                    chat_id=chat_id, text=chunk, parse_mode="Markdown", disable_web_page_preview=True
                )
        else:
            await context.bot.send_message(
                chat_id=chat_id, text=news, parse_mode="Markdown", disable_web_page_preview=True
            )

    except Exception:
        logfire.exception("Error retrieving news")
        await context.bot.send_message(chat_id=chat_id, text="No hay noticias.", disable_web_page_preview=True)
