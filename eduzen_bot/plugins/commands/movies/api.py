import requests
import structlog
import tmdbsimple as tmdb

from eduzen_bot.keys import TMDB
from eduzen_bot.plugins.commands.movies.constants import BASEURL_IMAGE, YT_LINK, YTS_API


logger = structlog.get_logger(filename=__name__)

tmdb.API_KEY = TMDB["API_KEY"]


def tmdb_movie_search(query):
    search = tmdb.Search()
    response = search.movie(query=query)
    if not response["results"]:
        return

    return response["results"]


def get_director(obj):
    cred = obj.credits()
    directors = [crew['name'] for crew in cred['crew'] if 'director' == crew['job'].lower()]

    return ", ".join(directors)


def prettify_movie(movie, obj):
    movie_info = get_basic_info(movie)
    directors = get_director(obj)
    message, image = prettify_basic_movie_info(*movie_info, directors)
    return message, image


def get_basic_info(movie):
    title = f"[{movie.get('title') or movie.get('original_title')}]({movie['imdb_link']})"
    rating = movie["vote_average"]
    overview = movie["overview"]
    year = movie["release_date"].split("-")[0]  # "2016-07-27" -> 2016
    image_link = movie.get("backdrop_path") or movie.get("poster_path")
    poster = BASEURL_IMAGE.format(image_link if image_link else None)
    return title, rating, overview, year, poster


def rating_stars(rating):
    """Transforms int rating into stars with int"""
    stars = int(rating // 2)
    rating_stars = f"{'⭐' * stars} ~ {rating}"
    return rating_stars


def prettify_basic_movie_info(title, rating, overview, year, image, directors):
    stars = rating_stars(rating)
    return (f"{title} ({year}) - {directors}\n" f"{stars}\n\n" f"{overview}\n\n"), image


def get_movie_detail(pk):
    return tmdb.Movies(pk)


def get_yt_trailer(videos):
    youtube_videos = [f"[{video['name']}]({YT_LINK.format(video['key'])})" for video in videos]
    return youtube_videos


def get_yts_torrent_info(imdb_id):
    try:
        r = requests.get(YTS_API, params={"query_term": imdb_id})
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
