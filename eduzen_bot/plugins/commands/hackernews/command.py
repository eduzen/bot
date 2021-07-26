"""
hn - get_hackernews
"""
import datetime as dt
from enum import Enum
from types import SimpleNamespace

import requests
from telegram import ChatAction

from eduzen_bot.decorators import create_user

session = requests.Session()


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
    return f"Get the {story_type} stories from hackernews.\n"


def hackernews(story_type=STORIES.TOP, limit=10):
    text_stories = []
    for story_id in get_top_stories(story_type, limit):
        raw_story = get_item(story_id)
        story = SimpleNamespace(**raw_story)
        date = dt.datetime.utcfromtimestamp(story.time).strftime("%Y-%m-%d %H:%M:%S")
        story_text = f"[{story.title}]({story.url})\n Score: {story.score} Time: {date}"
        text_stories.append(story_text)

    title = get_hackernews_help(story_type=story_type)
    return title + "\n".join(text_stories)


@create_user
def get_hackernews(update, context, *args, **kwargs):
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

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
