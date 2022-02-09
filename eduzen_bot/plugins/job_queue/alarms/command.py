"""
set - Setear alarma
reporte - Reporte de criptomonedas
unset - Sacar alarma
"""
import datetime
import logging

import pytz
from telegram import Update
from telegram.ext import CallbackContext

from eduzen_bot.auth.restricted import restricted
from eduzen_bot.decorators import create_user
from eduzen_bot.models import Report
from eduzen_bot.plugins.commands.btc.command import get_crypto_report

logger = logging.getLogger("rich")


def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    text = get_crypto_report()
    context.bot.send_message(job.context, text=text, parse_mode="Markdown")


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


@create_user
@restricted
def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    report, _ = Report.get_or_create(chat_id=chat_id)

    try:
        # args[0] should contain the time for the timer in seconds
        hour = int(context.args[0])
        if 0 < hour > 24:
            update.message.reply_text("Perdón no podemos volver al futuro!")
            return

        # Add job to queue
        job_removed = remove_job_if_exists(str(chat_id), context)

        report.hour = hour
        report.min = 0
        report.save()

        when = datetime.time(hour=hour, minute=0, tzinfo=pytz.timezone("Europe/Amsterdam"))
        # context.job_queue.run_once(alarm, due, context=chat_id, name=str(chat_id))
        context.job_queue.run_daily(alarm, when, days=range(7), context=chat_id, name=str(chat_id))
        text = "Timer successfully set!"

        if job_removed:
            text += " Old one was removed."
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text("Usage: /set <seconds>")


def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    update.message.reply_text(text)
