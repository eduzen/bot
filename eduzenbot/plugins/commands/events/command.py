"""
events - get_events
usage - get_usage
"""

import logfire
from peewee import fn
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from eduzenbot.auth.restricted import restricted
from eduzenbot.decorators import create_user
from eduzenbot.models import EventLog


def get_users_usage() -> str:
    """Retrieve a summary of user command usage."""
    txt = "No hay eventos"
    try:
        queryset = (
            EventLog.select(EventLog.command, EventLog.user_id, fn.Count(EventLog.user_id).alias("count"))
            .group_by(EventLog.user_id, EventLog.command)
            .having(fn.Count(EventLog.user_id) > 2)
            .order_by(fn.Count(EventLog.user_id).desc())
        )
        txt = "\n".join(
            f"{event.count: <4} | {event.command: <20} | {event.user.username or event.user_id: <10}"
            for event in queryset
        )
    except Exception:
        logfire.exception("DB problem with get_users_usage")
    return txt


@restricted
@create_user
async def get_events(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: int, **kwargs: str) -> None:
    """Retrieve the latest bot events."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        txt = "\n".join([event.telegram for event in EventLog.select().order_by(EventLog.timestamp.desc()).limit(50)])
    except Exception:
        logfire.exception("DB problem")
        txt = "No hay eventos"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=txt)


@restricted
@create_user
async def get_usage(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: int, **kwargs: str) -> None:
    """Retrieve a summary of user command usage."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    txt = get_users_usage()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=txt)
