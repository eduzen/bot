"""
alarms - show_daily_report
users - list_users
scheduled_reports - list_reports_configured
"""

import logfire
from tabulate import tabulate
from telegram import Update
from telegram.ext import ContextTypes

from eduzenbot.auth.restricted import restricted
from eduzenbot.decorators import create_user
from eduzenbot.models import Report, User

MAX_TELEGRAM_MESSAGE_LENGTH = 4096  # or ~4000 to leave some margin for markup


def chunk_text(text: str, chunk_size: int = 4000):
    """
    Yields successive chunk_size-length substrings from text.
    """
    for i in range(0, len(text), chunk_size):
        yield text[i : i + chunk_size]


@create_user
@restricted
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Shows a list of users in a formatted table.
    Usage: /list_users
    """
    chat_id = update.effective_chat.id if update.effective_chat else None
    if not chat_id:
        return  # or handle the error

    # Fetch users from the DB
    users = User.select()

    # Create the table headers
    table_data = [["ID", "First Name", "Last Name", "Username"]]

    # Populate the table rows
    for user in users:
        table_data.append(
            [
                user.id,
                user.first_name or "",
                user.last_name or "",
                user.username or "",
            ]
        )

    # Convert to a text table
    table_str = tabulate(table_data, headers="firstrow", tablefmt="fancy_grid")

    # Wrap in Markdown code block. We'll chunk *inside* the code block.
    # So we remove the code fences in chunk_text; we'll add them around each chunk.
    for chunk in chunk_text(table_str, chunk_size=4000):
        message_text = f"```\n{chunk}\n```"
        await context.bot.send_message(chat_id=chat_id, text=message_text, parse_mode="Markdown")


@create_user
@restricted
async def list_reports_configured(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Lists all configured reports in a formatted table.
    Usage: /list_reports
    """
    chat_id = update.effective_chat.id if update.effective_chat else None
    if not chat_id:
        return  # or handle the error

    try:
        reports = Report.select()
        if not reports.exists():
            await context.bot.send_message(chat_id=chat_id, text="No reports are currently configured.")
            return
    except Exception as e:
        logfire.error(f"Error fetching reports: {e}")
        await context.bot.send_message(chat_id=chat_id, text="Error retrieving reports from the database.")
        return

    # Create the table headers.  Include whichever fields you care about.
    table_data = [["Chat ID", "Hour", "Minute", "Weather?", "Dollar?", "Crypto?", "News?"]]

    # Populate rows
    for rep in reports:
        table_data.append(
            [
                rep.chat_id,
                rep.hour,
                rep.min,
                "Yes" if rep.show_weather else "No",
                "Yes" if rep.show_dollar else "No",
                "Yes" if rep.show_crypto else "No",
                "Yes" if rep.show_news else "No",
            ]
        )

    # Convert to a text table
    table_str = tabulate(table_data, headers="firstrow", tablefmt="fancy_grid")

    # Send in chunks if it's too large
    for chunk in chunk_text(table_str, chunk_size=4000):
        message_text = f"```\n{chunk}\n```"
        await context.bot.send_message(chat_id=chat_id, text=message_text, parse_mode="Markdown")


@create_user
async def show_daily_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the scheduled daily report configuration for this chat.
    Usage: /alarms
    """
    chat_id = update.effective_chat.id if update.effective_chat else None

    if not chat_id:
        logfire.error("Failed to get chat_id. Update does not have effective_chat.")
        return

    # Convert to string if you store the chat_id as str in your DB
    str_chat_id = str(chat_id)

    try:
        report = Report.get(Report.chat_id == str_chat_id)
    except Report.DoesNotExist:
        # No report is configured in the database
        await context.bot.send_message(chat_id=chat_id, text="No daily alarm is currently set.")
        return

    hour = report.hour
    minute = report.min

    # Optionally, you can check if there is an actual job in the job queue:
    jobs = context.job_queue.get_jobs_by_name(str_chat_id)

    if not jobs:
        text = (
            f"You have a daily alarm saved in the database for {hour:02d}:{minute:02d}, "
            "but it doesn't seem to be scheduled in the job queue."
        )
    else:
        text = f"You have a daily alarm set for {hour:02d}:{minute:02d}."

    await context.bot.send_message(chat_id=chat_id, text=text)
