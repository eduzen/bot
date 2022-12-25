"""
hn - get_hackernews
"""
import logging
from enum import Enum
from types import SimpleNamespace

import pendulum
import requests
from cachetools import TTLCache, cached
from telegram import ChatAction, Update

from eduzenbot.decorators import create_user

session = requests.Session()

logger = logging.getLogger("rich")


class STORIES(Enum):
    """
    The types of stories that can be retrieved.
    """

    TOP = "topstories"
    NEW = "newstories"
    BEST = "beststories"
    ASK = "askstories"
    JOBS = "jobstories"

    def __str__(self):
        return self.value


def get_top_stories(story_type=STORIES.TOP, limit=10):
    """
    Get the top stories from hackernews.

    :param limit: The number of stories to get.
    :return: A list of stories.
    """
    if story_type not in STORIES:
        raise ValueError(f"Invalid story type: {story_type}")

    url = f"https://hacker-news.firebaseio.com/v0/{story_type}.json"
    response = session.get(url)
    response.raise_for_status()
    return response.json()[:limit]


def get_item(id):
    """
    Get the story with the given id.

    :param id: The id of the story.
    :return: A dictionary containing the story.
    """
    url = f"https://hacker-news.firebaseio.com/v0/item/{id}.json"
    response = session.get(url)
    response.raise_for_status()
    return response.json()


def get_hackernews_help(story_type):
    return f"*{str(story_type).capitalize()} stories from* [HackerNews](https://news.ycombinator.com)\n\n"


def parse_hackernews(story_id: int):
    raw_story = get_item(story_id)
    story = SimpleNamespace(**raw_story)
    now = pendulum.now()
    date = now - pendulum.from_timestamp(story.time)
    try:
        url = story.url
    except AttributeError:
        url = ""
    story_text = f"[{story.title}]({url})\n Score: {story.score} Hace: {date.in_words()}"
    return story_text


@cached(cache=TTLCache(maxsize=1024, ttl=10800))
def hackernews(story_type=STORIES.TOP, limit=5):
    text_stories = []
    for story_id in get_top_stories(story_type, limit):
        try:
            story = parse_hackernews(story_id)
            text_stories.append(story)
        except Exception as e:
            logger.exception(e)
            continue

    title = get_hackernews_help(story_type=story_type)
    return title + "\n".join(text_stories)


@create_user
def get_hackernews(update: Update, context: object, *args: int, **kwargs: str):
    """
    Get the top stories from hackernews.

    :param limit: The number of stories to get.
    :return: A list of stories.
    """
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    type_story = context.args
    if type_story:
        text = hackernews(type_story)
    else:
        text = hackernews()

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )
