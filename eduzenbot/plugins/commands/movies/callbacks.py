import logging
import os

import tmdbsimple as tmdb
from telegram import Update
from telegram.ext import CallbackContext

from eduzenbot.plugins.commands.movies.api import get_yt_trailer, get_yts_torrent_info
from eduzenbot.plugins.commands.movies.constants import IMDB_LINK

logger = logging.getLogger("rich")

tmdb.API_KEY = os.getenv("TMDB_API_KEY")


def get_movie_imdb(update: Update, context: CallbackContext) -> None:
    imdb_id = context["data"]["imdb_id"]  # type: ignore
    answer = f"[IMDB]({IMDB_LINK.format(imdb_id)}"

    logger.info(f"Sending IMDB link for {imdb_id} {answer}")
    update.callback_query.bot.send_message(
        chat_id=update.callback_query.message.chat_id, text=answer, parse_mode="Markdown"
    )


def get_movie_youtube(update: Update, context: CallbackContext) -> None:
    movie = context["data"]  # type: ignore
    answer = "\n".join(get_yt_trailer(movie["videos"]))
    update.callback_query.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text=answer,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )


def get_movie_torrent(update: Update, context: CallbackContext, **kwargs: str) -> None:
    movie = context["data"]
    torrent = get_yts_torrent_info(movie["imdb_id"])
    if torrent:
        url, seeds, size, quality = torrent
        answer = (
            f"🏴‍☠️ [{movie['title']}]({url})\n\n" f"🌱 Seeds: {seeds}\n\n" f"🗳 Size: {size}\n\n" f"🖥 Quality: {quality}"
        )
    else:
        answer = "🚧 No torrent available for this movie."

    update.callback_query.bot.send_message(
        chat_id=update.callback_query.message.chat_id, text=answer, parse_mode="Markdown"
    )
