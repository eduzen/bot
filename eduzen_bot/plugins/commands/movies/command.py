"""
peli - get_movie
movie - get_movie
pelicula - get_movie
"""
import structlog
from eduzen_bot.decorators import create_user
from eduzen_bot.plugins.commands.movies.api import (
    tmdb_movie_search,
    prettify_movie,
    get_movie_detail,
)
from eduzen_bot.plugins.commands.movies import keyboards
from eduzen_bot.plugins.commands.movies.constants import IMDB_LINK

logger = structlog.get_logger(filename=__name__)


@create_user
def get_movie(update, context, **kwargs):
    args = context.args
    chat_data = context.chat_data
    chat_id = update.message.chat_id
    if not context.args:
        context.bot.send_message(
            chat_id=chat_id,
            text="Necesito que me pases una pelicula. `/pelicula <nombre>`",
            parse_mode="markdown",
        )
        return

    query = " ".join(args)
    movies = tmdb_movie_search(query)

    if not movies:
        context.bot.send_message(chat_id=chat_id, text="No encontré info sobre %s" % query)
        return

    movie = movies[0]

    movie_object = get_movie_detail(movie["id"])
    external_data = movie_object.external_ids()

    try:
        imdb_id = external_data["imdb_id"]  # tt<id> -> <id>
    except (KeyError, AttributeError):
        logger.info("imdb id for the movie not found")
        context.bot.send_message(
            chat_id=chat_id,
            text="👎 No encontré el id de imdb de esta serie, imposible de bajar por acá",
            parse_mode="markdown",
        )
        return
    videos = movie_object.videos()
    movie.update({"imdb_id": imdb_id, "imdb_link": IMDB_LINK.format(imdb_id), "videos": videos["results"]})

    movie_details, poster = prettify_movie(movie, movie_object)

    poster_chat = None
    if poster:
        poster_chat = context.bot.send_photo(chat_id=update.message.chat_id, photo=poster)

    chat_data["context"] = {
        "data": movie,
        "command": "movie",
        "edit_original_text": True,
        "poster_chat": poster_chat,
    }

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=movie_details,
        reply_markup=keyboards.pelis(),
        parse_mode="markdown",
        disable_web_page_preview=True,
    )
