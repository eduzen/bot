# eduzenbot/domain/report_scheduler.py
import datetime

import logfire
import pytz
from telegram import Bot
from telegram.ext import JobQueue

from eduzenbot.models import Report
from eduzenbot.plugins.job_queue.alarms.command import alarm


async def schedule_reports(job_queue: JobQueue, bot: Bot, eduzen_id: str) -> None:
    """
    Schedules all the daily reports stored in the database.
    On bot startup, it:
      1) Queries the Report table
      2) Schedules each entry as a run_daily job
      3) Notifies the user and the owner about the scheduled report
    """

    # Fetch all reports
    reports = Report.select()
    if not reports.exists():
        # If no reports, just notify the owner.
        try:
            await bot.send_message(chat_id=eduzen_id, text="No reports were found to schedule.")
        except Exception as e:
            logfire.error(f"Could not notify owner about empty reports: {e}")
        return

    for report in reports:
        chat_id = report.chat_id
        when = datetime.time(
            hour=report.hour,
            minute=report.min,
            tzinfo=pytz.timezone("Europe/Amsterdam"),
        )

        # Schedule the daily job
        job_queue.run_daily(
            callback=alarm,
            time=when,
            days=tuple(range(7)),  # Every day
            name=str(chat_id),
            data=chat_id,
        )

        # Notify the user about the restart and next scheduled time
        user_msg = (
            "Hey, I just restarted.\n" f"You have a report scheduled daily at {report.hour:02d}:{report.min:02d}!"
        )
        try:
            await bot.send_message(chat_id=chat_id, text=user_msg)
        except Exception as e:
            logfire.error(f"Could not send schedule notification to chat_id={chat_id}: {e}")

        # Also notify the bot owner
        owner_msg = f"Report scheduled for chat_id={chat_id} at {report.hour:02d}:{report.min:02d}."
        try:
            await bot.send_message(chat_id=eduzen_id, text=owner_msg)
        except Exception as e:
            logfire.error(f"Could not send schedule info to owner (eduzen_id={eduzen_id}): {e}")
