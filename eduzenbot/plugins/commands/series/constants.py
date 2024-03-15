import re
from collections import namedtuple

BASEURL_IMAGE = "http://image.tmdb.org/t/p/original"

BASEURL = "https://www.themoviedb.org/"

LANG = {
    "es": "español",
    "en": "english",
    "de": "deutsch",
    "it": "italiano",
    "fr": "francais",
}

SEASON_REGEX = re.compile(r"S(\d{1,})E(\d{1,})")  # S01E15

ALT_SEASON_REGEX = re.compile(r"(\d{1,})x(\d{1,})")  # 1x15

EPISODE_PATTERNS = [SEASON_REGEX, ALT_SEASON_REGEX]

Episode = namedtuple(
    "Episode",
    ["name", "season", "episode", "magnet", "torrent", "size", "released", "seeds"],
)

NAME, SIZE, RELEASED, SEEDS = 0, 2, 3, 4

MAGNET, TORRENT = 0, 1

EZTV_NO_RESULTS = (
    "Eztv api did not return any torrent result for the series❕\n"
    "Please notice it's still in beta mode 🐣\n"
)
EZTV_API_ERROR = (
    "EZTV api failed to respond with latest torrents.\n"
    "Try 'Load all episodes' option and look for latest episode."
)
