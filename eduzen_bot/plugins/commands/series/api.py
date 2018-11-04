import structlog
import re
from collections import defaultdict, namedtuple
from bs4 import BeautifulSoup
import requests
from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button
from functools import lru_cache
from eduzen_bot.keys import TMDB
import tmdbsimple as tmdb
from eduzen_bot.plugins.commands.series.keyboards import serie_keyboard

logger = structlog.get_logger(filename=__name__)

baseurl_image = "http://image.tmdb.org/t/p/original"
baseurl = "https://www.themoviedb.org/"
tmdb.API_KEY = TMDB["API_KEY"]

SEASON_REGEX = re.compile(r"S(\d{1,})E(\d{1,})")  # S01E15
ALT_SEASON_REGEX = re.compile(r"(\d{1,})x(\d{1,})")  # 1x15
EPISODE_PATTERNS = [SEASON_REGEX, ALT_SEASON_REGEX]
Episode = namedtuple("Episode", ["name", "season", "episode", "magnet", "torrent", "size", "released", "seeds"])
NAME, SIZE, RELEASED, SEEDS = 0, 2, 3, 4
MAGNET, TORRENT = 0, 1
lang = {"es": "español", "en": "english", "de": "deutsch", "it": "italiano"}


@lru_cache(20)
def get_all_seasons(series_name, raw_user_query):
    """Parses eztv search page in order to return all episodes of a given series.
    Args:
        series_name: Full series name as it is on tmdb
        raw_user_query: The user query, with possible typos or the incomplete series_name
    Unlike get_latest_episodes handler function, this does not communicate directly
    with the eztv api because the api is in beta mode and has missing season and episode info
    for many episodes.
    In order to present the series episodes in an orderly manner, we need to rely on
    that information consistency and completeness. Neither of those requirements
    are satisfied by the api. That's why we parse the web to get consistent results.
    Quite a paradox..
    Returns:
        {
            1: # season
                1: [ # episode
                    {Episode()},
                    {Episode()},
                    ...
                ],
                2: [
                    {Episode()},
                    {Episode()},
                    ...
                ]
            2:
                1: [
                    {Episode()},
                    {Episode()},
                    ...
                ],
                ...
            ...
        }
    """
    series_episodes = defaultdict(lambda: defaultdict(list))

    def get_link(links, key):
        try:
            link = links[key]["href"]
        except (IndexError, AttributeError):
            link = ""

        return link

    def get_episode_info(torrent):
        """Parse html to return an episode data.
        Receives an html row, iterates its tds
        (leaving the first and last values out).
        and returns an episode namedtuple
        """

        # First and last cell contain useless info (link with info and forum link)
        torrent = torrent.find_all("td")[1:-1]
        links = torrent[1].find_all("a")
        name = torrent[0].text.strip()

        # Filter fake results that include series name but separated between other words.
        # For example, a query for The 100 also returns '*The* TV Show S07E00 Catfish Keeps it *100*' which we don't want
        # We also use the raw_user_query because sometimes the complete name from tmdb is not the same name used on eztv.
        if not series_name.lower() in name.lower() and not raw_user_query.lower() in name.lower():
            # The tradeoff is that we don't longer work for series with typos. But it's better than giving fake results.
            logger.info(f"Fake result '{name}' for query '{series_name}'")
            return None

        for pattern in EPISODE_PATTERNS:
            match = pattern.search(name)
            if match:
                season, episode = match.groups()
                break
        else:
            # No season and episode found
            logger.info(f"Could not read season and episode data from torrent '{name}'")
            return None

        return Episode(
            name=name.replace("[", "").replace("]", ""),
            season=int(season),
            episode=int(episode),
            magnet=get_link(links, MAGNET),
            torrent=get_link(links, TORRENT),
            size=torrent[SIZE].text.strip(),
            released=torrent[RELEASED].text.strip(),
            seeds=torrent[SEEDS].text.strip(),
        )

    # Parse episodes from web
    series_query = raw_user_query.replace(" ", "-")
    r = requests.get(f"https://eztv.ag/search/{series_query}")
    soup = BeautifulSoup(r.text, "html.parser")
    torrents = soup.find_all("tr", {"class": "forum_header_border"})

    # Build the structured dict
    for torrent in torrents:
        episode_info = get_episode_info(torrent)
        if not episode_info:
            # We should skip torrents if they don't belong to a season
            continue

        season, episode = episode_info.season, episode_info.episode
        # Attach the episode under the season key, under the episode key, in a list of torrents of that episode
        series_episodes[season][episode].append(episode_info)

    logger.info(f"'{series_name}' series episodes retrieved. Seasons: {series_episodes.keys()}")

    return series_episodes


def rating_stars(rating):
    """Transforms int rating into stars with int"""
    stars = int(rating // 2)
    rating_stars = f"{'⭐' * stars} ~ {rating}"
    return rating_stars


def prettify_serie(serie):
    name = serie["name"]
    if serie.get("first_air_date"):
        l = lang.get(serie["original_language"], serie["original_language"])
        name = f"[{name}]({baseurl}tv/{serie['id']}) " f"({serie['first_air_date']}) | lang: {l}"
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

    image = f"{baseurl_image}{serie['backdrop_path'] or serie['poster_path']}"
    response = prettify_serie(serie)

    # We reply here with basic info because further info may take a while to process.
    bot.send_photo(chat_id, image)

    bot_reply = bot.send_message(chat_id=chat_id, text=response, parse_mode="markdown", disable_web_page_preview=True)

    r = requests.get(
        f"https://api.themoviedb.org/3/tv/{serie['id']}/external_ids", params={"api_key": TMDB["API_KEY"]}
    )
    if r.status_code != 200:
        logger.info("Request for imdb id was not succesfull.")
        bot.send_message(chat_id=chat_id, text="La api de imdb se puso la gorra 👮", parse_mode="markdown")
        return

    data = r.json()
    if not data:
        return

    try:
        imdb_id = data["imdb_id"].replace("t", "")  # tt<id> -> <id>
    except (KeyError, AttributeError):
        logger.info("imdb id for the movie not found")
        bot.send_message(
            chat_id=chat_id,
            text="👎 No encontré el id de imdb de esta serie, imposible de bajar por acá",
            parse_mode="markdown",
        )
        return

    serie.update({"imdb_id": imdb_id})
    # Build context based on the imdb_id
    chat_data["context"] = {"data": {"serie": serie}, "command": "serie", "edit_original_text": True}

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
