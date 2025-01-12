"""
time - time
hora - time
"""

import random

import logfire
import pytz
import requests
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from eduzenbot.decorators import create_user

BASE_URL = "http://worldtimeapi.org/api/timezone/"


def find_timezone(city: str = "buenos_aires") -> str | None:
    """Find the timezone for a given city."""
    if isinstance(city, list):
        city = "_".join(city)

    for timezone in pytz.all_timezones:
        if city.replace(" ", "_").lower() in timezone.lower():
            return timezone
    return None


@create_user
async def time(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: int, **kwargs: str) -> None:
    """Handle /time or /hora command to get the current time for a city."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    if not context.args:
        timezone = find_timezone()
    else:
        timezone = find_timezone(" ".join(context.args))

    if not timezone:
        info = f"Mmmm... I couldn't find {context.args}. Let's pick a random timezone..."
        timezone = random.choice(pytz.all_timezones)
        await update.message.reply_text(f"{info} {timezone}")

    try:
        response = requests.get(f"{BASE_URL}{timezone}")
        response.raise_for_status()
        data = response.json()
        formatted_datetime = data["datetime"].replace("T", "\n")
        info = f"Timezone {timezone}:\n{formatted_datetime}"
        await update.message.reply_text(info)
    except KeyError:
        await update.message.reply_text(f"No encontramos nada con '{context.args}'")
    except requests.RequestException as e:
        logfire.error(f"Error fetching timezone data: {e}")
        await update.message.reply_text("Error retrieving time information. Please try again later.")
