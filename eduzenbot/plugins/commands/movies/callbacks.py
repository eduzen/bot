import os

import logfire
import tmdbsimple as tmdb
from telegram import Update
from telegram.ext import ContextTypes

from eduzenbot.plugins.commands.movies.api import get_yt_trailer, get_yts_torrent_info
from eduzenbot.plugins.commands.movies.constants import IMDB_LINK

tmdb.API_KEY = os.getenv("TMDB_API_KEY")


async def get_movie_imdb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the IMDb link for the selected movie."""
    imdb_id = context.chat_data["data"]["imdb_id"]
    answer = f"[IMDB]({IMDB_LINK.format(imdb_id)})"

    logfire.info(f"Sending IMDb link for {imdb_id}: {answer}")
    await update.callback_query.bot.send_message(
        chat_id=update.effective_chat.id,
        text=answer,
        parse_mode="Markdown",
    )


async def get_movie_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send YouTube trailer links for the selected movie."""
    movie = context.chat_data["data"]
    answer = "\n".join(get_yt_trailer(movie["videos"]))

    await update.callback_query.bot.send_message(
        chat_id=update.effective_chat.id,
        text=answer,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )


async def get_movie_torrent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send torrent information for the selected movie."""
    movie = context.chat_data["data"]
    torrent = get_yts_torrent_info(movie["imdb_id"])
    if torrent:
        url, seeds, size, quality = torrent
        answer = f"🏴‍☠️ [{movie['title']}]({url})\n\n" f"🌱 Seeds: {seeds}\n" f"🗳 Size: {size}\n" f"🖥 Quality: {quality}"
    else:
        answer = "🚧 No torrent available for this movie."

    await update.callback_query.bot.send_message(
        chat_id=update.effective_chat.id,
        text=answer,
        parse_mode="Markdown",
    )
