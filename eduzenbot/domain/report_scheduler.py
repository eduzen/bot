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
            await bot.send_message(chat_id=eduzen_id, text="No reports were found to schedule. 🤷‍♂️")
        except Exception as e:
            logfire.error(f"Could not notify owner about empty reports: {e}")
        return

    try:
        await bot.send_message(chat_id=eduzen_id, text="Hey @eduzen, I just restarted! 🚀")
    except Exception as e:
        logfire.error(f"Could not notify owner on restart: {e}")

    scheduled_jobs = []
    scheduled_reports_info = []

    for report in reports:
        chat_id = report.chat_id

        # Construct the time object (handle time zone carefully)
        scheduled_time = datetime.time(
            hour=report.hour,
            minute=report.min,
            tzinfo=pytz.timezone("Europe/Amsterdam"),
        )

        # Schedule the daily job
        job = job_queue.run_daily(
            callback=alarm,
            time=scheduled_time,
            days=tuple(range(7)),  # Every day of the week
            name=str(chat_id),
            data=chat_id,
        )
        scheduled_jobs.append(job)

        # Collect info for logging or messaging
        scheduled_reports_info.append(f" - chat_id={chat_id} at {report.hour:02d}:{report.min:02d} 🕗")

    # Send a single summary to owner instead of multiple messages
    summary = "The following reports have been scheduled 🎉:\n" + "\n".join(scheduled_reports_info)
    try:
        await bot.send_message(chat_id=eduzen_id, text=summary)
    except Exception as e:
        logfire.error(f"Could not send schedule info to owner: {e}")

    # Optionally: return the list of job objects if you'd like
    return scheduled_jobs
