import structlog
import requests
from functools import lru_cache
from eduzen_bot.plugins.commands.series import keyboards
from eduzen_bot.plugins.commands.series.api import prettify_serie, get_all_seasons

EZTV_NO_RESULTS = (
    "Eztv api did not return any torrent result for the series❕\n" "Please notice it's still in beta mode 🐣\n"
)
EZTV_API_ERROR = (
    "EZTV api failed to respond with latest torrents." "Try 'Load all episodes' option and look for latest episode."
)

logger = structlog.getLogger(filename=__name__)


@lru_cache(5)
def prettify_torrents(torrents):
    return "\n".join(prettify_torrent(*torrent) for torrent in torrents if prettify_torrent(*torrent))


def prettify_torrent(name, torrent_url, seeds, size):
    return f"🏴‍☠️ [{name}]({torrent_url})\n" f"🌱 Seeds: {seeds} | 🗳 Size: {size}MB\n"


def _minify_torrents(torrents):
    """Returns a torrent name, url, seeds and size from json response"""
    minified_torrents = []
    for torrent in torrents:
        try:
            MB = 1024 * 1024
            size_float = int(torrent["size_bytes"]) / MB
            size = f"{size_float:.2f}"
            minified_torrents.append((torrent["title"], torrent["torrent_url"], torrent["seeds"], size))
        except Exception:
            logger.exception("Error parsing torrent from eztv api. <%s>", torrent)
            continue

    return tuple(minified_torrents)


def go_back(bot, update, **context):
    # Remove season and episode context so we can start the search again if the user wants to download another episode.
    context.pop("selected_season_episodes", None)

    # Resend series basic description
    serie = context["data"]["serie"]
    response = prettify_serie(serie)
    keyboard = keyboards.serie_keyboard()
    # tothink: Maybe implement relative go back. chat_data context should be more intelligent to support that.
    # temp key on chat_data (active_season) that resets after each episode go back?
    # update.callback_query.answer(text='')
    # update.callback_query.message.edit_text('🤬')

    original_text = update.callback_query.message.text
    if response != original_text:
        update.callback_query.edit_message_text(
            text=response, reply_markup=keyboard, parse_mode="markdown", disable_web_page_preview=True
        )
    else:
        logger.info(
            "Selected option '%s' would leave text as it is." "Ignoring to avoid exception. '%s' " % (answer, response)
        )


def get_torrents_by_id(imdb_id, limit=None):
    """Request torrents from api and return a minified torrent representation."""
    try:
        r = requests.get("https://eztv.ag/api/get-torrents", params={"imdb_id": imdb_id, "limit": limit})
        if r.status_code != 200:
            return
        data = r.json()

        if not data or data["torrents_count"] == 0:
            return

        torrents = sorted(r.json()["torrents"], key=lambda d: (d["season"], d["episode"]))
    except KeyError:
        logger.info("No torrents in eztv api for this serie. Response %s", r.json())
        return
    except Exception:
        logger.exception("Error requesting torrents for %s", imdb_id)
        return

    return _minify_torrents(torrents)


def latest_episodes(bot, update, **context):
    logger.info("Called latest episodes")

    if not context:
        message = f"Lpm, no pude responder a tu pedido.\n" f"Probá invocando de nuevo el comando a ver si me sale 😊"
        logger.info(f"Conflicting update: '{update.to_dict()}'. Chat data: {chat_data}")
        bot.send_message(chat_id=update.callback_query.message.chat_id, text=message, parse_mode="markdown")
        # Notify telegram we have answered
        update.callback_query.answer(text="")
        return

    # Get user selection
    answer = update.callback_query.data
    query = update.callback_query

    # Get latest episodes from eztv api
    # update.callback_query.answer(text='Getting latest episodes..')

    data = context["data"]["serie"]
    imdb_id = data["imdb_id"]
    torrents = get_torrents_by_id(imdb_id)

    if not torrents:
        logger.info(f"No torrents for {data['name']}")
        update.callback_query.edit_message_text(text=EZTV_NO_RESULTS, reply_markup=keyboards.serie_go_back_keyboard())
        return

    pretty_torrents = prettify_torrents(torrents)
    response = pretty_torrents if pretty_torrents else EZTV_API_ERROR

    # update.callback_query.answer(text='🤫')

    original_text = update.callback_query.message.text
    if response != original_text:
        update.callback_query.edit_message_text(
            text=response,
            reply_markup=keyboards.serie_go_back_keyboard(),
            parse_mode="markdown",
            disable_web_page_preview=True,
        )
    else:
        logger.info(
            "Selected option '%s' would leave text as it is." "Ignoring to avoid exception. '%s' " % (answer, response)
        )


def all_episodes(bot, update, **context):
    serie = context["data"]["serie"]

    seasons = serie.get("seasons")
    if not seasons:
        update.callback_query.answer(text="Loading episodes... this may take a while")
        seasons = get_all_seasons(serie["name"], serie["original_name"])
        serie["seasons"] = seasons

    response = "Choose a season to see its episodes."
    keyboard = keyboards.serie_season(seasons)

    original_text = update.callback_query.message.text
    if response != original_text:
        update.callback_query.edit_message_text(
            text=response, reply_markup=keyboard, parse_mode="markdown", disable_web_page_preview=True
        )
    else:
        logger.info(
            "Selected option '%s' would leave text as it is." "Ignoring to avoid exception. '%s' " % (answer, response)
        )


def get_season(bot, update, **context):
    serie = context["data"]["serie"]
    answer = update.callback_query.data
    season_choice = answer.split("_")[-1]

    update.callback_query.answer(text=f"Loading episodes from season {season_choice}")

    season_episodes = serie["seasons"][int(season_choice)]
    serie["selected_season_episodes"] = season_episodes
    response = f"You chose season {season_choice}."
    logger.info(f"Season {season_choice} episodes {sorted(tuple(season_episodes.keys()))}")
    keyboard = keyboards.serie_episodes(season_episodes)

    original_text = update.callback_query.message.text
    if response != original_text:
        update.callback_query.edit_message_text(
            text=response, reply_markup=keyboard, parse_mode="markdown", disable_web_page_preview=True
        )
    else:
        logger.info(
            f"Selected option '{answer}' would leave text as it is. Ignoring to avoid exception. '{response}' "
        )

def get_episode(bot, update, **context):
    serie = context["data"]["serie"]
    answer = update.callback_query.data
    episode = answer.split("_")[-1]

    # update.callback_query.answer(text=f"Loading torrents of episode {episode}")
    episode_list = serie["selected_season_episodes"][int(episode)]
    the_episodes = prettify_episodes(episode_list)
    response = the_episodes if the_episodes else "No episodes found."
    keyboard = keyboards.serie_go_back_keyboard()

    original_text = update.callback_query.message.text
    if response != original_text:
        update.callback_query.edit_message_text(
            text=response, reply_markup=keyboard, parse_mode="markdown", disable_web_page_preview=True
        )
    else:
        logger.info(
            f"Selected option '{answer}' would leave text as it is. Ignoring to avoid exception. '{response}' "
        )

    return
    if response:
        # Remove season and episode context so we can start the search again if the user wants to download another episode.
        context.pop("selected_season_episodes", None)

        # Resend series basic description
        message = context["data"]["message_info"]
        response = prettify_serie(*message)
        keyboard = serie_keyboard()
        # tothink: Maybe implement relative go back. chat_data context should be more intelligent to support that.
        # temp key on chat_data (active_season) that resets after each episode go back?

    elif answer == LOAD_EPISODES:
        # Load all episodes parsing eztv web page
        # They should be loaded by now but just in case.
        seasons = chat_data["context"].get("seasons")
        if not seasons:
            update.callback_query.answer(text="Loading episodes.. this may take a while")
            seasons = chat_data["context"]["seasons"] = get_all_seasons(
                context["data"]["series_name"], context["data"]["series_raw_name"]
            )

        response = "Choose a season to see its episodes."
        keyboard = serie_season_keyboard(seasons)
    else:
        keyboard = serie_go_back_keyboard()
        response = "Unknown button %s" % answer
        logger.info("We shouldn't be here. chat_data=%s, answer=%s", chat_data, answer)
