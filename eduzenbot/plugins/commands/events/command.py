"""
events - get_events
usage - get_usage
"""

import logfire
from peewee import fn
from tabulate import tabulate
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
            EventLog.select(
                EventLog.command,
                EventLog.user_id,
                fn.Count(EventLog.user_id).alias("count"),
            )
            .group_by(EventLog.user_id, EventLog.command)
            .having(fn.Count(EventLog.user_id) > 2)
            .order_by(fn.Count(EventLog.user_id).desc())
            .limit(80)
        )
        # Prepare table headers
        table_data = [["Count", "Command", "User"]]
        # Populate rows
        for event in queryset:
            # event.user might be None if there's no related user, so handle that
            user_repr = event.user.username if event.user and event.user.username else event.user_id
            table_data.append([event.count, event.command, user_repr])

        if len(table_data) == 1:
            return "No hay eventos"

        # Use tabulate for a fancy table
        return tabulate(table_data, headers="firstrow", tablefmt="fancy_grid")
    except Exception:
        logfire.exception("DB problem with get_users_usage")
        return "Ocurrió un error al obtener datos."


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
    table_text = get_users_usage()

    # Optionally wrap in code block for Markdown
    response = f"```\n{table_text}\n```"
    await context.bot.send_message(chat_id=chat_id, text=response, parse_mode="Markdown")
