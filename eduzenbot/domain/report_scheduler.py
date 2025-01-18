# eduzenbot/domain/report_scheduler.py
import datetime
from collections.abc import Callable

import logfire
import pytz
from telegram import Bot
from telegram.ext import ContextTypes, JobQueue

from eduzenbot.models import Report
from eduzenbot.plugins.job_queue.alarms.command import alarm


async def schedule_reports(
    job_queue: JobQueue,
    bot: Bot,
    eduzen_id: str,
    send_msg_func: Callable[[int | str, str], None | ContextTypes.DEFAULT_TYPE] = None,
) -> None:
    """
    Schedules all the daily reports stored in the database.

    :param job_queue: The python-telegram-bot JobQueue instance
    :param bot: The Bot instance for sending messages
    :param eduzen_id: The chat ID (or user ID) to send developer/owner notifications to
    :param send_msg_func: (Optional) A callback for sending messages. If omitted,
                          we'll default to bot.send_message() directly.
    """

    # If no external send_msg_func is provided, define a default using bot.send_message
    if send_msg_func is None:

        async def send_msg_func(chat_id: int | str, text: str) -> None:
            await bot.send_message(chat_id=chat_id, text=text)

    # Retrieve each scheduled report from the DB
    reports = Report.select()
    if not reports:
        await send_msg_func(eduzen_id, "No reports were found to schedule.")
        return

    for report in reports:
        chat_id = report.chat_id
        when = datetime.time(
            hour=report.hour,
            minute=report.min,
            tzinfo=pytz.timezone("Europe/Amsterdam"),
        )

        # Schedule the daily job
        # NOTE: In python-telegram-bot v20, you typically pass 'data=...' instead of 'context=...'
        job_queue.run_daily(
            callback=alarm,
            time=when,
            days=range(7),  # Runs every day of the week
            name=str(chat_id),  # So we can remove or update it later
            data=chat_id,  # We'll retrieve it in alarm via context.job.data
        )

        # Notify the user chat
        msg = (
            "Hey, I just restarted.\n"
            f"Remember you have a crypto report every day at {report.hour:02d}:{report.min:02d}!"
        )
        try:
            await send_msg_func(chat_id, msg)
        except Exception as e:
            # For instance, user might have blocked the bot, etc.
            logfire.error(f"Could not send schedule notification to chat_id={chat_id}: {e}")

        # Also notify the developer/owner
        owner_msg = f"Crypto report scheduled for chat_id={chat_id} at {report.hour:02d}:{report.min:02d}."
        try:
            await send_msg_func(eduzen_id, owner_msg)
        except Exception as e:
            logfire.error(f"Could not send schedule info to owner (eduzen_id={eduzen_id}): {e}")
