import structlog
import requests
from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button
from functools import lru_cache
from eduzen_bot.keys import TMDB
import tmdbsimple as tmdb

logger = structlog.get_logger(filename=__name__)

baseurl_image = "http://image.tmdb.org/t/p/original"
baseurl = "https://www.themoviedb.org/"
tmdb.API_KEY = TMDB["API_KEY"]

lang = {
    'es': 'español',
    'en': 'english',
    'de': 'deutsch',
    'it': 'italiano',
}

def serie_keyboard():
    buttons = [
        [
            Button('Latest episodes', callback_data='latest_episodes'),
            Button('Load all episodes', callback_data='latest_episodes')
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def rating_stars(rating):
    """Transforms int rating into stars with int"""
    stars = int(rating // 2)
    rating_stars = f"{'⭐' * stars} ~ {rating}"
    return rating_stars


def prettify_serie(serie):
    name = serie["name"]
    if serie.get("first_air_date"):
        l = lang.get(serie['original_language'], serie['original_language'])
        name = (
            f"[{name}]({baseurl}tv/{serie['id']}) " f"({serie['first_air_date']}) | lang: {l}"
        )
    stars = rating_stars(serie["vote_average"])
    return "\n".join((name, stars, serie["overview"]))


def tmdb_search(bot, chat_id, chat_data, query):
    search = tmdb.Search()
    response = search.tv(query=query)

    if not response["results"]:
        bot_reply = bot.send_message(
            chat_id=chat_id,
            text=(f"No encontré información en imdb sobre _'{query}'_." " Está bien escrito el nombre?"),
            parse_mode="markdown",
        )

    serie = search.results[0]

    image = f"{baseurl_image}{serie['backdrop_path']}"
    response = prettify_serie(serie)

    # We reply here with basic info because further info may take a while to process.
    bot.send_photo(chat_id, image)
    bot_reply = bot.send_message(
        chat_id=chat_id, text=response, parse_mode="markdown", disable_web_page_preview=True
    )

    r = requests.get(
        f"https://api.themoviedb.org/3/tv/{serie['id']}/external_ids", params={"api_key": TMDB["API_KEY"]}
    )
    if r.status_code != 200:
        logger.info("Request for imdb id was not succesfull.")
        bot.send_message(
            chat_id=chat_id, text="La api de imdb se puso la gorra 👮", parse_mode="markdown"
        )
        return

    data = r.json()

    try:
        imdb_id = data["imdb_id"].replace("t", "")  # tt<id> -> <id>
    except KeyError:
        logger.info("imdb id for the movie not found")
        bot.send_message(
            chat_id=chat_id,
            text="No encontré el id de imdb de esta pelicula",
            parse_mode="markdown",
        )
        return

    serie.update({"imdb_id": imdb_id})
    # Build context based on the imdb_id
    chat_data["context"] = {
        "data": {
            'serie': serie,
        },
        "command": "serie",
        "edit_original_text": True,
    }

    # Now that i have the imdb_id, show buttons to retrieve extra info.
    keyboard = serie_keyboard()
    bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=bot_reply.message_id,
        text=bot_reply.caption,
        reply_markup=keyboard,
        parse_mode="markdown",
        disable_web_page_preview=True,
    )
