import structlog
import tmdbsimple as tmdb

from eduzen_bot.keys import TMDB
from eduzen_bot.plugins.commands.movies.constants import IMDB_LINK
from eduzen_bot.plugins.commands.movies.api import get_yts_torrent_info, get_yt_trailer


logger = structlog.get_logger(filename=__name__)

tmdb.API_KEY = TMDB["API_KEY"]


def get_movie_imdb(update, context, **kwargs):
    imdb_id = context["data"]["imdb_id"]
    answer = f"[IMDB]({IMDB_LINK.format(imdb_id)}"

    update.callback_query.bot.send_message(
        chat_id=update.callback_query.message.chat_id, text=answer, parse_mode="markdown"
    )


def get_movie_youtube(update, context, **kwargs):
    movie = context["data"]
    answer = "\n".join(get_yt_trailer(movie["videos"]))
    update.callback_query.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text=answer,
        parse_mode="markdown",
        disable_web_page_preview=True,
    )


def get_movie_torrent(update, context, **kwargs):
    movie = context["data"]
    torrent = get_yts_torrent_info(movie["imdb_id"])
    if torrent:
        url, seeds, size, quality = torrent
        answer = (
            f"🏴‍☠️ [{movie['title']}]({url})\n\n"
            f"🌱 Seeds: {seeds}\n\n"
            f"🗳 Size: {size}\n\n"
            f"🖥 Quality: {quality}"
        )
    else:
        answer = "🚧 No torrent available for this movie."

    update.callback_query.bot.send_message(
        chat_id=update.callback_query.message.chat_id, text=answer, parse_mode="markdown"
    )
