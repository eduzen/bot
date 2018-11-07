import requests
import structlog
import tmdbsimple as tmdb

from eduzen_bot.keys import TMDB

tmdb.API_KEY = TMDB["API_KEY"]
YT_LINK = 'https://www.youtube.com/watch?v={}'
logger = structlog.get_logger(filename=__name__)


def tmdb_movie_search(bot, chat_id, chat_data, query):
    search = tmdb.Search()
    response = search.movie(query=query)
    if not response["results"]:
        return

    return response["results"]


def prettify_movie(movie_dict):
    movie_info = get_basic_info(movie_dict)
    message, image = prettify_basic_movie_info(*movie_info)

    return message, image


def get_basic_info(movie):
    title = movie.get("title") or movie.get("original_title")
    rating = movie["vote_average"]
    overview = movie["overview"]
    year = movie["release_date"].split("-")[0]  # "2016-07-27" -> 2016
    image_link = movie.get("backdrop_path") or movie.get("poster_path")
    poster = f"http://image.tmdb.org/t/p/original{image_link}" if image_link else None
    return title, rating, overview, year, poster


def rating_stars(rating):
    """Transforms int rating into stars with int"""
    stars = int(rating // 2)
    rating_stars = f"{'⭐' * stars} ~ {rating}"
    return rating_stars


def prettify_basic_movie_info(title, rating, overview, year, image):
    stars = rating_stars(rating)
    return (f"{title} ({year})\n" f"{stars}\n\n" f"{overview}\n\n"), image


def get_yt_trailer(videos):
    key = videos["results"][-1]["key"]
    return YT_LINK.format(key)


def get_yts_torrent_info(imdb_id):
    yts_api = "https://yts.am/api/v2/list_movies.json"
    try:
        r = requests.get(yts_api, params={"query_term": imdb_id})
    except requests.exceptions.ConnectionError:
        logger.info("yts api no responde.")
        return None
    if r.status_code == 200:
        torrent = r.json()  # <Dar url en lugar de hash.
        try:
            movie = torrent["data"]["movies"][0]["torrents"][0]
            url = movie["url"]
            seeds = movie["seeds"]
            size = movie["size"]
            quality = movie["quality"]

            return url, seeds, size, quality

        except (IndexError, KeyError) as e:
            logger.exception("There was a problem with yts api response")
