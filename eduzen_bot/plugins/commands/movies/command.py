"""
peli - get_movie
movie - get_movie
pelicula - get_movie
"""
import structlog
from telegram.ext import run_async

from eduzen_bot.plugins.commands.movies.api import tmdb_movie_search, prettify_movie
from eduzen_bot.plugins.commands.movies import keyboards


logger = structlog.get_logger(filename=__name__)


@run_async
def get_movie(bot, update, **kwargs):
    args = kwargs.get('args')
    chat_data = kwargs.get('chat_data')
    if not args:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Necesito que me pases una pelicula. `/pelicula <nombre>`',
            parse_mode='markdown'
        )
        return

    query = ' '.join(args)
    movie = tmdb_movie_search(bot, update.message.chat_id, chat_data, query)

    if not movie:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='No encontré info sobre %s' % query,
        )
        return

    # Give context to button handlers
    chat_data['movie'] = movie[0]

    movie_details, poster = prettify_movie(movie[0])
    if poster:
        bot.send_photo(chat_id=update.message.chat_id, photo=poster)

    bot.send_message(
        chat_id=update.message.chat_id,
        text=movie_details,
        reply_markup=keyboards.pelis(),
        parse_mode='markdown',
        disable_web_page_preview=True,
    )
