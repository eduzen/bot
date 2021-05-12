"""
set - Setear alarma
unset - Sacar alarma
"""
import logging

from eduzen_bot.decorators import create_user

logger = logging.getLogger("rich")


@create_user
def alarm(context):
    """Send the alarm message."""
    context.bot.send_message(context.job.context, text="Beep!")
    context.bot.send_document(context.job.context, document="https://media.giphy.com/media/d3yxg15kJppJilnW/giphy.gif")


@create_user
def set_timer(update, context, *args, **kwargs):
    """Add a job to the queue."""

    chat_id = update.message.chat_id
    job_queue = kwargs.get("job_queue")
    chat_data = kwargs.get("chat_data")
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(args[0])
        if due < 0:
            update.message.reply_text("Perdón no podemos volver al futuro!")
            return

        # Add job to queue
        job = job_queue.run_once(alarm, due, context=chat_id)
        chat_data["job"] = job

        update.message.reply_text("Timer configurado correctamente!")

    except (IndexError, ValueError):
        update.message.reply_text("Usage: /set <seconds>")


@create_user
def unset(update, context, *args, **kwargs):
    """Remove the job if the user changed their mind."""
    chat_data = kwargs["chat_data"]
    if "job" not in kwargs["chat_data"]:
        update.message.reply_text("No hay timers activados!")
        return

    job = chat_data["job"]
    job.schedule_removal()
    del chat_data["job"]

    update.message.reply_text("Timer desactivado!")
