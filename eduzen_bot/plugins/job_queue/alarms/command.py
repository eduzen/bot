"""
set - Setear alarma
unset - Sacar alarma
"""
import logging

from telegram import Update
from telegram.ext import CallbackContext

from eduzen_bot.decorators import create_user
from eduzen_bot.plugins.commands.btc.command import get_btc

logger = logging.getLogger("rich")


def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text=get_btc())


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


@create_user
def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id

    # job_queue = kwargs.get("job_queue")
    # chat_data = kwargs.get("chat_data")
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text("Perdón no podemos volver al futuro!")
            return

        # Add job to queue
        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, context=chat_id, name=str(chat_id))

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
