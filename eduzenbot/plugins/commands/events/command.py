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
    """
    Retrieve a summary of user command usage.

    This function is synchronous because all DB operations
    are performed with Peewee, and there's no async I/O here.
    """
    try:
        queryset = (
            EventLog.select(EventLog.command, EventLog.user_id, fn.Count(EventLog.user_id).alias("count"))
            .group_by(EventLog.user_id, EventLog.command)
            .having(fn.Count(EventLog.user_id) > 2)
            .order_by(fn.Count(EventLog.user_id).desc())
        )

        txt = "\n".join(
            f"{event.count:<4} | {event.command:<20} | {event.user.username or event.user_id:<10}" for event in queryset
        )
        if not txt:
            txt = "No hay eventos"
    except Exception:
        logfire.exception("DB problem with get_users_usage")
        txt = "Ocurrió un error al obtener datos."

    return txt


@restricted
@create_user
async def get_events(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: int, **kwargs: str) -> None:
    """
    /events command
    Retrieves the latest bot events from the EventLog.
    """
    # Safely get the chat_id
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        logfire.error("No valid chat_id. Could not send events.")
        return

    # Indicate that the bot is "typing"
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    try:
        events = EventLog.select().order_by(EventLog.timestamp.desc()).limit(50)
        txt = "\n".join([event.telegram for event in events]) if events else "No hay eventos"
    except Exception:
        logfire.exception("DB problem retrieving events")
        txt = "No hay eventos (ocurrió un error al acceder a la base de datos)."

    await context.bot.send_message(chat_id=chat_id, text=txt)


@restricted
@create_user
async def get_usage(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: int, **kwargs: str) -> None:
    """
    /usage command
    Retrieves a summary of user command usage.
    """
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        logfire.error("No valid chat_id. Could not send usage stats.")
        return

    # Indicate that the bot is "typing"
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    # get_users_usage is synchronous, so just call it normally
    txt = get_users_usage()

    await context.bot.send_message(chat_id=chat_id, text=txt)
