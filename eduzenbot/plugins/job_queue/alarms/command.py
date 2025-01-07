"""
set - Setear alarma
reporte - Reporte de criptomonedas
unset - Sacar alarma
"""

import datetime

import logfire
import pytz
from telegram import Update
from telegram.ext import ContextTypes

from eduzenbot.auth.restricted import restricted
from eduzenbot.decorators import create_user
from eduzenbot.models import Report
from eduzenbot.plugins.commands.btc.command import get_crypto_report


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    try:
        text = get_crypto_report()
        await context.bot.send_message(job.context, text=text, parse_mode="Markdown")  # type: ignore
    except Exception as e:
        logfire.error(f"Failed to send alarm: {e}")


async def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = await context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


@create_user
@restricted
async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        report, _ = Report.get_or_create(chat_id=chat_id)
    except Exception as e:
        logfire.error(f"Failed to retrieve or create report for chat_id={chat_id}: {e}")
        await update.message.reply_text("Error initializing the report. Try again later.")
        return

    try:
        # Validate and parse hour input
        hour = int(context.args[0])  # type: ignore
        if not (0 <= hour <= 24):
            await update.message.reply_text("Please provide a valid hour (0-24).")
            return
    except (ValueError, IndexError):
        await update.message.reply_text("Usage: /set <hour> (0-24)")
        return

    try:
        # Save report details
        report.hour = hour
        report.min = 0
        report.save()

        # Remove existing job if necessary
        job_removed = remove_job_if_exists(str(chat_id), context)

        # Set up the daily alarm
        when = datetime.time(hour=hour, minute=0, tzinfo=pytz.timezone("Europe/Amsterdam"))
        context.job_queue.run_daily(alarm, when, days=range(7), context=chat_id, name=str(chat_id))  # type: ignore

        # Notify user
        text = f"Daily alarm successfully set for {hour}:00!"
        if job_removed:
            text += " The previous alarm was removed."
        await update.message.reply_text(text)
        logfire.info(f"Alarm set for chat_id={chat_id} at {when.isoformat()}.")

    except Exception as e:
        logfire.error(f"Error setting alarm for chat_id={chat_id}: {e}")
        await update.message.reply_text("An error occurred while setting the alarm. Please try again.")


async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)
    logfire.info(f"Unset timer for chat_id={chat_id}: {'removed' if job_removed else 'none found'}.")
