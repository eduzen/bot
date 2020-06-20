import os
from collections import defaultdict
from functools import lru_cache

import requests
import structlog
import tmdbsimple as tmdb
from bs4 import BeautifulSoup


from eduzen_bot.plugins.commands.series import keyboards
from eduzen_bot.plugins.commands.series.constants import (
    BASEURL,
    BASEURL_IMAGE,
    EPISODE_PATTERNS,
    LANG,
    MAGNET,
    RELEASED,
    SEEDS,
    SIZE,
    TORRENT,
    Episode,
)

logger = structlog.get_logger(filename=__name__)

tmdb.API_KEY = os.getenv("TMDB_API_KEY")


@lru_cache(20)
def get_all_seasons(series_name, raw_user_query, number_of_seasons):
    """Parses eztv search page in order to return all episodes of a given series.
    context.args:
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

        # First cell contain useless info (link with info)
        torrent = torrent.find_all("td")[1:]
        links = torrent[1].find_all("a")
        name = torrent[0].text.strip()

        # Filter fake results that include series name but separated between other words.
        # For example, a query for The 100 also returns
        # '*The* TV Show S07E00 Catfish Keeps it *100*' which we don't want
        # We also use the raw_user_query because sometimes the complete name from
        # tmdb is not the same name used on eztv.
        if not series_name.lower() in name.lower() and not raw_user_query.lower() in name.lower():
            # The tradeoff is that we don't longer work for series with typos.
            # But it's better than giving fake results.
            logger.info(f"Fake result '{name}' for query '{series_name}'")
            return

        for pattern in EPISODE_PATTERNS:
            match = pattern.search(name)
            if match:
                season, episode = match.groups()
                break
        else:
            # No season and episode found
            logger.info(f"Could not read season and episode data from torrent '{name}'")
            return

        if not season or int(season) > number_of_seasons:
            return

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
    name = f"[{serie['name']}]({BASEURL}tv/{serie['id']})"
    original_name = f"*Original name*: {serie['original_name']}"
    number_of_seasons = f"*Number of seasons*: {serie['number_of_seasons']}"
    number_of_episodes = f"*Number of episodes*: {serie['number_of_episodes']}"
    next_episode = f"*Next episode*: {serie['next_episode']}"
    lang = LANG.get(serie["original_language"], serie["original_language"])
    lang = f"*Lang*: {lang}"
    first_air_date = f"({serie.get('first_air_date', 'unannounced')})"
    stars = rating_stars(serie["vote_average"])
    title = f"{name} | {first_air_date} | {lang}"
    data = f"{number_of_seasons} | {number_of_episodes}"
    response = "\n".join((title, original_name, stars, serie["overview"], data, next_episode))

    return response


def get_related_series(query):
    search = tmdb.Search()
    response = search.tv(query=query)

    return response["results"]


def get_full_image_path(relativpath):
    return f"{BASEURL_IMAGE}{relativpath}"


def get_poster_url(serie):
    poster = serie.get("backdrop_path") or serie.get("poster_path")
    return get_full_image_path(poster)


def get_keyboard():
    return keyboards.serie()


def get_serie_detail(pk):
    return tmdb.TV(pk)
