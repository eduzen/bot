import structlog
from eduzen_bot.plugins.commands.series.callbacks import latest_episodes

log = structlog.getLogger(filename=__name__)

handlers = {
    "latest_episodes": latest_episodes
}

def callback_query(bot, update, **kwargs):
    query = update.callback_query
    log.info(query.data)
    log.info(kwargs)

    func = handlers.get(query.data)
    if not func:
        bot.edit_message_text(
            text=f"Selected option: {query.data} doesn't work yet",
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
        return

    func(bot, update, kwargs)
