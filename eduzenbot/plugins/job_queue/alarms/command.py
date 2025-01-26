"""
set - set_timer
"""

import datetime

import logfire
import pytz
from peewee import DoesNotExist
from telegram import Update
from telegram.ext import ContextTypes

from eduzenbot.auth.restricted import restricted
from eduzenbot.decorators import create_user
from eduzenbot.models import Report
from eduzenbot.plugins.commands.btc.command import get_crypto_report


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    chat_id = job.data if hasattr(job, "data") else None

    if not chat_id:
        logfire.error("Alarm job missing chat_id.")
        return

    try:
        report, _ = Report.get_or_create(chat_id=chat_id)
        text = await get_crypto_report(report)
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    except Exception as e:
        logfire.error(f"Failed to send alarm: {e}")


async def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)

    if not current_jobs:
        logfire.info(f"No jobs found for chat_id={name}.")
        return False

    for job in current_jobs:
        logfire.info(f"Removing job {job.name}")
        job.schedule_removal()

    return True


@create_user
@restricted
async def schedule_daily_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /configurereport <time> [flags...]

    Example:
      /set 07.30 weather crypto -dollar
    Means:
      - Alarm at 07:30
      - show_weather = True
      - show_crypto = True
      - show_dollar = False

    Time format: HH.MM in 24-hour format (0-23.59)
    Prefix a feature with '-' to disable, otherwise it's enabled.
    Available features: weather, dollar, crypto, news, etc.
    """
    chat_id = str(update.effective_chat.id) if update.effective_chat else None

    if not chat_id:
        logfire.error("Failed to get chat_id. Update does not have effective_chat.")
        return

    # We expect at least one argument for time, plus optional flags
    if not context.args:
        usage_msg = (
            "Usage: /configurereport <time> [flags...]\n"
            "Example: /set 07.30 weather -crypto\n"
            "(Enables weather, disables crypto, alarm at 07:30)"
        )
        await context.bot.send_message(chat_id=chat_id, text=usage_msg)
        return

    # 1) Parse time (first argument)
    time_arg = context.args[0]  # e.g. "07.30"
    try:
        hour_minute = float(time_arg)
        hour = int(hour_minute)
        minute = int(round((hour_minute - hour) * 100))

        if not (0 <= hour <= 23) or not (0 <= minute <= 59):
            raise ValueError("Invalid time range")
    except ValueError:
        await context.bot.send_message(
            chat_id=chat_id, text="Please provide a valid time in the format HH.MM (0-23.59)."
        )
        return

    # 2) Parse feature flags (remaining arguments)
    #    Example: "weather", "-crypto", "dollar"
    feature_args = context.args[1:]

    # Fetch or create the user's report config
    try:
        report, _ = Report.get_or_create(chat_id=str(chat_id))
    except DoesNotExist:
        # Should never happen with get_or_create, but just in case
        report = Report.create(chat_id=str(chat_id))

    for arg in feature_args:
        arg = arg.lower()
        # Remove leading '-' if present
        if arg.startswith("-"):
            flag = arg[1:]
            if flag == "weather":
                report.show_weather = False
            elif flag == "dollar":
                report.show_dollar = False
            elif flag == "crypto":
                report.show_crypto = False
            elif flag == "news":
                report.show_news = False
        else:
            # Enable
            if arg == "weather":
                report.show_weather = True
            elif arg == "dollar":
                report.show_dollar = True
            elif arg == "crypto":
                report.show_crypto = True
            elif arg == "news":
                report.show_news = True

    # Save the updated preferences
    report.hour = hour
    report.min = minute
    report.save()

    # Remove existing job if any
    job_removed = await remove_job_if_exists(str(chat_id), context)
    if job_removed:
        await context.bot.send_message(chat_id=chat_id, text="Previous daily timer canceled.")

    # 3) Schedule the new daily job
    when = datetime.time(hour=hour, minute=minute, tzinfo=pytz.timezone("Europe/Amsterdam"))
    context.job_queue.run_daily(alarm, when, name=str(chat_id), data=str(chat_id))

    # Notify user
    # 4) Build a response message to confirm
    prefs_msg = (
        f"✅ Your daily report is set for {hour:02d}:{minute:02d}.\n\n"
        f"Weather: {'Yes' if report.show_weather else 'No'}\n"
        f"Dollar: {'Yes' if report.show_dollar else 'No'}\n"
        f"Crypto: {'Yes' if report.show_crypto else 'No'}\n"
        f"News: {'Yes' if report.show_news else 'No'}"
    )
    await context.bot.send_message(chat_id=chat_id, text=prefs_msg)
    logfire.info(f"Daily report set for chat_id={chat_id} at {when.isoformat()}.")

    try:
        # Validate and parse hour input
        time_input = context.args[0]  # type: ignore
        hour_minute = float(time_input)

        hour = int(hour_minute)  # Extract hour
        minute = int(round((hour_minute - hour) * 100))  # Extract minute

        if not (0 <= hour <= 23) or not (0 <= minute <= 59):
            await context.bot.send_message(
                chat_id=chat_id, text="Please provide a valid time in the format HH.MM (0-23.59)."
            )
            return

    except (ValueError, IndexError):
        await context.bot.send_message(chat_id=chat_id, text="Usage: /configurereport <hour> (0-24)")
        return


@create_user
async def cancel_daily_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.effective_chat.id if update.effective_chat else None
    if not chat_id:
        logfire.error("Failed to get chat_id. Update does not have effective_chat.")
        return

    job_removed = await remove_job_if_exists(str(chat_id), context)

    # Now, remove the record from the DB if it exists
    try:
        # Convert chat_id to string if your DB stores it that way
        report = Report.get(Report.chat_id == str(chat_id))
        report.delete_instance()
        logfire.info(f"Deleted report record for chat_id={chat_id}")
    except Report.DoesNotExist:
        logfire.info(f"No Report record to delete for chat_id={chat_id}")

    # Notify user
    if job_removed:
        await context.bot.send_message(chat_id=chat_id, text="Timer successfully cancelled, and preferences removed!")
    else:
        await context.bot.send_message(chat_id=chat_id, text="You have no active timer. Preferences removed if any.")
