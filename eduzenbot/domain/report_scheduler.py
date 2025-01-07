# eduzenbot/domain/report_scheduler.py
import datetime

import pytz

from eduzenbot.models import Report
from eduzenbot.plugins.job_queue.alarms.command import alarm


def schedule_reports(job_queue, send_msg_func, eduzen_id: str):
    """
    Schedules all the daily reports stored in the database.
    :param job_queue: The python-telegram-bot job queue instance
    :param send_msg_func: A callback function used to send messages (adapter-provided)
    :param eduzen_id: An ID to send developer/owner messages to
    """
    for report in Report.select():
        when = datetime.time(
            hour=report.hour,
            minute=report.min,
            tzinfo=pytz.timezone("Europe/Amsterdam"),
        )
        chat_id = report.chat_id
        job_queue.run_daily(
            alarm,
            when,
            days=range(7),
            context=chat_id,
            name=str(chat_id),
        )
        msg = f"Hey, I've just restarted. " f"Remember that you have a crypto report every day at {report.hour}."
        # We call the function that the Telegram adapter (bot) provides:
        send_msg_func(chat_id, msg)

        # Also notify the developer/owner:
        send_msg_func(eduzen_id, f"Crypto report scheduled for Chat_id {chat_id}")
