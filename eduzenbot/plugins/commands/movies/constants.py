from collections import namedtuple

IMDB_LINK = "https://www.imdb.com/title/{}"
YT_LINK = "https://www.youtube.com/watch?v={}"
BASEURL_IMAGE = "http://image.tmdb.org/t/p/original{}"
YTS_API = "https://yts.am/api/v2/list_movies.json"

Pelicula = namedtuple("Pelicula", ["title", "original_title", "rating", "overview", "year", "image"])
