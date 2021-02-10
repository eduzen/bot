"""
events - get_events
usage - get_usage
"""
import structlog
from telegram import ChatAction

from eduzen_bot.auth.restricted import restricted
from eduzen_bot.decorators import create_user
from eduzen_bot.models import EventLog, db

logger = structlog.get_logger(filename=__name__)


def get_users_usage():
    try:
        cursor = db.execute_sql(
            "select count(e.user_id) as total, e.command, u.username "
            'from "eventlog" as e inner join "user" as u '
            "on e.user_id = u.id "
            "group by e.user_id, e.command, u.username "
            "order by total desc, u.username asc;"
        )
        txt = "\n".join(f"{row[0]: <3} | {row[1]: <20} | {row[2]: <10}" for row in cursor.fetchall())
    except Exception:
        logger.exception("DB problem")
        txt = "No hay eventos"
    return txt


@restricted
@create_user
def get_events(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    try:
        txt = "\n".join([event.telegram for event in EventLog.select().limit(50)])
    except Exception:
        logger.exception("DB problem")
        txt = "No hay eventos"

    context.bot.send_message(chat_id=update.message.chat_id, text=txt)


@create_user
def get_usage(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    txt = get_users_usage()
    context.bot.send_message(chat_id=update.message.chat_id, text=txt)
