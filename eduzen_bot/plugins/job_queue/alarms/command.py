"""
set - Setear alarma
unset - Sacar alarma
"""


def alarm(context):
    """Send the alarm message."""
    context.bot.send_message(context.job.context, text="Beep!")
    context.bot.send_document(
        context.job.context, document="https://media.giphy.com/media/d3yxg15kJppJilnW/giphy.gif"
    )


def set_timer(update, context, *args, job_queue, chat_data):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
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


def unset(update, context, chat_data):
    """Remove the job if the user changed their mind."""
    if "job" not in chat_data:
        update.message.reply_text("No hay timers activados!")
        return

    job = chat_data["job"]
    job.schedule_removal()
    del chat_data["job"]

    update.message.reply_text("Timer desactivado!")
