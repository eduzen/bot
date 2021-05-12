import logging
from functools import lru_cache

import requests
from telegram import InputMediaPhoto

from eduzen_bot.plugins.commands.series import keyboards
from eduzen_bot.plugins.commands.series.api import (
    get_all_seasons,
    get_poster_url,
    prettify_serie,
)
from eduzen_bot.plugins.commands.series.constants import EZTV_API_ERROR, EZTV_NO_RESULTS

logger = logging.getLogger("rich")


def monospace(text):
    return f"```\n{text}\n```"


def prettify_episode(ep):
    """Episodes have name, season, episode, torrent, magnet, size, seeds and released attributes"""
    # Some episodes do not have a torrent download. But they do have a magnet link.
    # Since magnet links are not clickable on telegram, we leave them as a fallback.
    if ep.torrent:
        header = f"[{ep.name}]({ep.torrent})\n"
    elif ep.magnet:
        header = f"Magnet: {monospace(ep.magnet)}"
    else:
        header = "No torrent nor magnet available for this episode."

    return f"{header}" f"🌱 Seeds: {ep.seeds} | 🗳 Size: {ep.size or '-'}"


def prettify_episodes(episodes, header=None):
    episodes = "\n\n".join(prettify_episode(ep) for ep in episodes)
    if header:
        episodes = "\n".join((header, episodes))

    return episodes


@lru_cache(5)
def prettify_torrents(torrents):
    return "\n".join(prettify_torrent(*torrent) for torrent in torrents if prettify_torrent(*torrent))


def prettify_torrent(name, torrent_url, seeds, size):
    name = name.replace("[", "").replace("]", "")
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


def go_back(update, context, **kwargs):
    # Remove season and episode context so we can start the search again if the user wants to download another episode.
    context.pop("selected_season_episodes", None)
    answer = update.callback_query.data

    # Resend series basic description
    serie = context["data"]
    response = prettify_serie(serie)
    keyboard = keyboards.serie()
    # tothink: Maybe implement relative go back. chat_data context should be more intelligent to support that.
    # temp key on chat_data (active_season) that resets after each episode go back?
    # update.callback_query.answer(text='')
    # update.callback_query.message.edit_text('🤬')

    original_text = update.callback_query.message.text
    if response != original_text:
        update.callback_query.edit_message_text(
            text=response,
            reply_markup=keyboard,
            parse_mode="markdown",
            disable_web_page_preview=True,
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


def latest_episodes(update, context, **kwargs):
    logger.info("Called latest episodes")

    if not context:
        message = "Lpm, no pude responder a tu pedido.\nProbá invocando de nuevo el comando a ver si me sale 😊"
        logger.info(f"Conflicting update: '{update.to_dict()}'")
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=message, parse_mode="markdown")
        # Notify telegram we have answered
        update.callback_query.answer(text="")
        return

    # Get user selection
    answer = update.callback_query.data

    # Get latest episodes from eztv api
    # update.callback_query.answer(text='Getting latest episodes..')

    data = context["data"]
    imdb_id = data["imdb_id"]
    torrents = get_torrents_by_id(imdb_id)

    if not torrents:
        logger.info(f"No torrents for {data['name']}")
        update.callback_query.edit_message_text(text=EZTV_NO_RESULTS, reply_markup=keyboards.serie_go_back_keyboard())
        return

    pretty_torrents = prettify_torrents(torrents)
    response = pretty_torrents if pretty_torrents else EZTV_API_ERROR

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


def all_episodes(update, context, **kwargs):
    serie = context["data"]
    answer = update.callback_query.data

    seasons = serie.get("seasons")
    if not seasons:
        update.callback_query.answer(text="Loading episodes... this may take a while")
        seasons = get_all_seasons(serie["name"], serie["original_name"], serie["number_of_seasons"])
        serie["seasons"] = seasons

    response = "Choose a season to see its episodes."
    keyboard = keyboards.serie_season(seasons)

    original_text = update.callback_query.message.text
    if response != original_text:
        update.callback_query.edit_message_text(
            text=response,
            reply_markup=keyboard,
            parse_mode="markdown",
            disable_web_page_preview=True,
        )
    else:
        logger.info(
            "Selected option '{}' would leave text as it is. Ignoring to avoid exception. '{}' ".format(
                answer, response
            )
        )


def get_season(update, context, **kwargs):
    serie = context["data"]
    poster_chat = context["poster_chat"]
    answer = update.callback_query.data
    season_choice = int(answer.split("_")[-1])

    update.callback_query.answer(text=f"Loading episodes from season {season_choice}")

    season_overview = serie["seasons_info"][season_choice - 1]["overview"]

    try:
        url = get_poster_url(serie["seasons_info"][season_choice - 1])
        poster = InputMediaPhoto(url)
        poster_chat.edit_media(poster)
    except Exception:
        logger.info("No hay poster para esta temporada")

    season_episodes = serie["seasons"][season_choice]
    serie["selected_season_episodes"] = season_episodes
    response = f"You chose season {season_choice}.\n{season_overview}"
    logger.info(f"Season {season_choice} episodes {sorted(tuple(season_episodes.keys()))}")
    keyboard = keyboards.serie_episodes(season_episodes)

    original_text = update.callback_query.message.text
    if response != original_text:

        update.callback_query.edit_message_text(
            text=response,
            reply_markup=keyboard,
            parse_mode="markdown",
            disable_web_page_preview=True,
        )
    else:
        logger.info(f"Selected option '{answer}' would leave text as it is. Ignoring to avoid exception. {response}")


def get_episode(update, context, **kwargs):
    serie = context["data"]
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
            text=response,
            reply_markup=keyboard,
            parse_mode="markdown",
            disable_web_page_preview=True,
        )
    else:
        logger.info(f"Selected option '{answer}' would leave text as it is. Ignoring to avoid exception. {response}")


def load_episodes(update, context, **kwargs):
    serie = context["data"]
    seasons = serie.get("seasons")
    answer = update.callback_query.data

    if not seasons:
        update.callback_query.answer(text="Loading episodes.. this may take a while")
        serie["seasons"] = get_all_seasons(serie["name"], serie["raw_name"])
        seasons = serie["seasons"]

    response = "Choose a season to see its episodes."
    keyboard = keyboards.serie_season(seasons)

    original_text = update.callback_query.message.text
    if response != original_text:
        update.callback_query.edit_message_text(
            text=response,
            reply_markup=keyboard,
            parse_mode="markdown",
            disable_web_page_preview=True,
        )
    else:
        logger.info(f"Selected option '{answer}' would leave text as it is. Ignoring to avoid exception. {response}")
