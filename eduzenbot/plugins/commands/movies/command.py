"""
peli - get_movie
movie - get_movie
pelicula - get_movie
"""

import logfire
from telegram.ext import ContextTypes

from eduzenbot.decorators import create_user
from eduzenbot.plugins.commands.movies import keyboards
from eduzenbot.plugins.commands.movies.api import (
    get_movie_detail,
    prettify_movie,
    tmdb_movie_search,
)
from eduzenbot.plugins.commands.movies.constants import IMDB_LINK


@create_user
async def get_movie(update: ContextTypes, context: ContextTypes.DEFAULT_TYPE, **kwargs: str) -> None:
    args = context.args
    chat_data = context.chat_data
    chat_id = update.effective_chat.id  # type: ignore

    if not context.args:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Necesito que me pases una pelicula. `/pelicula <nombre>`",
            parse_mode="Markdown",
        )
        return

    query = " ".join(args)
    logfire.debug(f"Searching for {query}")
    movies = tmdb_movie_search(query)

    if not movies:
        await context.bot.send_message(chat_id=chat_id, text="No encontré info sobre %s" % query)
        return

    movie = movies[0]

    logfire.debug(f"Found {movie}")

    movie_object = get_movie_detail(movie["id"])
    external_data = movie_object.external_ids()

    try:
        logfire.debug(f"Found {external_data['imdb_id']}")
        imdb_id = external_data["imdb_id"]  # tt<id> -> <id>
    except (KeyError, AttributeError):
        logfire.info("imdb id for the movie not found")
        await context.bot.send_message(
            chat_id=chat_id,
            text="👎 No encontré el id de imdb de esta serie, imposible de bajar por acá",
            parse_mode="Markdown",
        )
        return
    videos = movie_object.videos()
    movie.update(
        {
            "imdb_id": imdb_id,
            "imdb_link": IMDB_LINK.format(imdb_id),
            "videos": videos["results"],
        }
    )

    logfire.debug(f"Found {movie}")

    movie_details, poster = prettify_movie(movie, movie_object)

    poster_chat = None
    if poster:
        poster_chat = context.bot.send_photo(chat_id=chat_id, photo=poster)

    chat_data["context"] = {
        "data": movie,
        "command": "movie",
        "edit_original_text": True,
        "poster_chat": poster_chat,
    }

    logfire.debug(f"Found {movie_details}")

    await context.bot.send_message(
        chat_id=chat_id,
        text=movie_details,
        reply_markup=keyboards.pelis(),
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )
