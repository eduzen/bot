import structlog
from eduzen_bot.plugins.commands.series import callbacks
from eduzen_bot.plugins.commands.series.keyboards import serie_keyboard

log = structlog.getLogger(filename=__name__)

handlers = {
    "latest_episodes": callbacks.latest_episodes,
    "go_back_serie": callbacks.go_back,
    "all_episodes": callbacks.all_episodes,
    "get_season": callbacks.get_season,
}

def callback_query(bot, update, **kwargs):
    query = update.callback_query
    func = handlers.get(query.data)

    if query.data.startswith('get_season'):
        func = handlers["get_season"]

    if not func:
        bot.edit_message_text(
            text=f"Selected option: {query.data} doesn't work yet",
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
        return


    chat_data = kwargs.get('chat_data')
    if not chat_data:
        bot.edit_message_text(
            text=f"Perdoname che, algo paso en el medio. Empecemos de nuevo con el commando original",
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
        bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text="preguntame de nuevo",
            parse_mode='markdown'
        )
        return

    context = chat_data['context']
    log.info(f"from {context['command']} - {query.data}")

    try:
        func(bot, update, **context)
    except Exception:
        log.exception('Something went wrong')
