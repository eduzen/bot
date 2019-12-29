def unknown(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id, text="Che, no te entiendo, no existe ese comando!"
    )
