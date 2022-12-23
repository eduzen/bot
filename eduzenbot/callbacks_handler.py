import logging

from eduzenbot.plugins.commands.movies import callbacks as movies_callbacks
from eduzenbot.plugins.commands.series import callbacks as series_callbacks

log = logging.getLogger("rich")

handlers = {
    "latest_episodes": series_callbacks.latest_episodes,
    "go_back_serie": series_callbacks.go_back,
    "all_episodes": series_callbacks.all_episodes,
    "get_season": series_callbacks.get_season,
    "get_episode": series_callbacks.get_episode,
    "get_movie_imdb": movies_callbacks.get_movie_imdb,
    "get_movie_youtube": movies_callbacks.get_movie_youtube,
    "get_movie_torrent": movies_callbacks.get_movie_torrent,
}


def _select_handler(key):
    if key.startswith("get_season"):
        return handlers["get_season"]

    if key.startswith("get_episode"):
        return handlers["get_episode"]

    return handlers.get(key)


def callback_query(update, context, **kwargs):
    query = update.callback_query

    func = _select_handler(query.data)
    if not func:
        context.bot.edit_message_text(
            text=f"Selected option: {query.data} doesn't work yet",
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
        )
        return

    if not context.chat_data:
        txt = "_Errare humanum est._\n" "Algo paso en el medio.\n" "Empecemos de nuevo con el commando original"
        context.bot.edit_message_text(
            text=txt,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            parse_mode="Markdown",
        )
        return

    chat_context = context.chat_data["context"]
    log.info(f"from {chat_context['command']} - {query.data}")

    try:
        func(update, chat_context, **kwargs)
    except Exception as exc:
        log.exception(f"El callback se rompió... {exc} {exc.args}")
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text="En el medio sucedieron cosas... _Errare humanum est._",
            parse_mode="Markdown",
        )
