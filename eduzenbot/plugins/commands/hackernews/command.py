"""
hn - get_hackernews
"""

from enum import Enum
from types import SimpleNamespace
from typing import Any

import httpx
import logfire
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

from eduzenbot.decorators import create_user

client = httpx.AsyncClient()


class STORIES(Enum):
    """
    The types of stories that can be retrieved.
    """

    TOP = "topstories"
    NEW = "newstories"
    BEST = "beststories"
    ASK = "askstories"
    JOBS = "jobstories"

    def __str__(self) -> str:
        return self.value


async def get_top_stories(story_type: STORIES = STORIES.TOP, limit: int | None = 10) -> list[Any]:
    """
    Get the top stories from Hacker News.

    :param limit: The number of stories to get.
    :return: A list of stories.
    """
    if story_type not in STORIES:
        raise ValueError(f"Invalid story type: {story_type}")

    url = f"https://hacker-news.firebaseio.com/v0/{story_type}.json"
    response = await client.get(url)
    response.raise_for_status()
    data = response.json()
    return data[:limit]


async def get_item(id: int) -> dict[Any, Any]:
    """
    Get the story with the given ID.

    :param id: The ID of the story.
    :return: A dictionary containing the story.
    """
    url = f"https://hacker-news.firebaseio.com/v0/item/{id}.json"
    response = await client.get(url)
    response.raise_for_status()
    return response.json()


async def parse_hackernews(story_id: int) -> str:
    """
    Parse a story's details into a formatted string.
    """
    raw_story = await get_item(story_id)
    story = SimpleNamespace(**raw_story)

    title = getattr(story, "title", "No Title")
    url = getattr(story, "url", "")

    safe_title = escape_markdown(title, version=2)
    safe_url = escape_markdown(url, version=2, entity_type="text_link") if url else ""

    if not url:
        return rf"\- {safe_title}"

    return rf"\- [{safe_title}]({safe_url})"


async def fetch_hackernews_stories(story_type: STORIES = STORIES.TOP, limit: int = 5) -> str:
    """
    Fetch and format top Hacker News stories.
    """
    text_stories = []
    top_stories = await get_top_stories(story_type, limit)
    for story_id in top_stories:
        try:
            story = await parse_hackernews(story_id)
            text_stories.append(story)
        except Exception:
            logfire.exception("Failed to parse story.")
            continue

    title = "Stories from [HackerNews](https://news.ycombinator.com)\n"
    return title + "\n".join(text_stories)


@create_user
async def get_hackernews(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Get and send the top stories from Hacker News.
    """
    chat_id = update.effective_chat.id if update.effective_chat else None
    if not chat_id:
        logfire.error("Failed to get chat_id. Update does not have effective_chat.")
        return

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    type_story = context.args[0] if context.args else STORIES.TOP
    try:
        story_type = STORIES[type_story.upper()]
    except (KeyError, AttributeError):
        story_type = STORIES.TOP

    text = await fetch_hackernews_stories(story_type)
    print(text)
    logfire.info(f"Sending HackerNews {text}", text=text)

    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="MarkdownV2",
        disable_web_page_preview=True,
    )
