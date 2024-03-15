"""
events - get_events
usage - get_usage
"""

import logging

from peewee import fn
from telegram import ChatAction, Update
from telegram.ext import CallbackContext

from eduzenbot.auth.restricted import restricted
from eduzenbot.decorators import create_user
from eduzenbot.models import EventLog

logger = logging.getLogger("rich")


def get_users_usage():
    txt = "No hay eventos"
    try:
        queryset = (
            EventLog.select(
                EventLog.command, EventLog.user_id, fn.Count(EventLog.user_id)
            )
            .group_by(EventLog.user_id, EventLog.command)
            .having(fn.Count(EventLog.user_id) > 2)
            .order_by(fn.Count(EventLog.user_id).desc())
        )
        txt = "\n".join(
            f"{event.count: <4} | {event.command: <20} | "
            f"{event.user.username or event.user_id: <10}"
            for event in queryset
        )
    except Exception:
        logger.exception("DB problem with get_users_usage")
    return txt


@restricted
@create_user
def get_events(update: Update, context: CallbackContext, *args: int, **kwargs: str):
    context.bot.send_chat_action(
        chat_id=update.message.chat_id, action=ChatAction.TYPING
    )

    try:
        txt = "\n".join(
            [
                event.telegram
                for event in EventLog.select()
                .order_by(EventLog.timestamp.desc())
                .limit(50)
            ]
        )
    except Exception:
        logger.exception("DB problem")
        txt = "No hay eventos"

    context.bot.send_message(chat_id=update.message.chat_id, text=txt)


@restricted
@create_user
def get_usage(update: Update, context: CallbackContext, *args: int, **kwargs: str):
    context.bot.send_chat_action(
        chat_id=update.message.chat_id, action=ChatAction.TYPING
    )
    txt = get_users_usage()
    context.bot.send_message(chat_id=update.message.chat_id, text=txt)
