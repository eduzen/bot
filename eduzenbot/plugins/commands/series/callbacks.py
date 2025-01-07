from functools import lru_cache
from typing import Any

import logfire
import requests
from telegram import InputMediaPhoto, Update
from telegram.ext import ContextTypes

from eduzenbot.plugins.commands.series import keyboards
from eduzenbot.plugins.commands.series.api import (
    get_all_seasons,
    get_poster_url,
    prettify_serie,
)
from eduzenbot.plugins.commands.series.constants import EZTV_API_ERROR, EZTV_NO_RESULTS


def monospace(text: str) -> str:
    return f"```\n{text}\n```"


def prettify_episode(ep) -> str:
    """Episodes have name, season, episode, torrent, magnet, size, seeds and released attributes"""
    # Some episodes do not have a torrent download. But they do have a magnet link.
    # Since magnet links are not clickable on telegram, we leave them as a fallback.
    if ep.torrent:
        header = f"[{ep.name}]({ep.torrent})\n"
    elif ep.magnet:
        header = f"Magnet: {monospace(ep.magnet)}"
    else:
        header = "No torrent nor magnet available for this episode."

    return f"{header} 🌱 Seeds: {ep.seeds} | 🗳 Size: {ep.size or '-'}"


def prettify_episodes(episodes, header=None) -> str:
    episodes = "\n\n".join(prettify_episode(ep) for ep in episodes)
    if header:
        episodes = "\n".join((header, episodes))

    return episodes


@lru_cache(5)
def prettify_torrents(torrents) -> str:
    return "\n".join(prettify_torrent(*torrent) for torrent in torrents if prettify_torrent(*torrent))


def prettify_torrent(name: str, torrent_url: str, seeds: str, size: str) -> str:
    name = name.replace("[", "").replace("]", "")
    return f"🏴‍☠️ [{name}]({torrent_url})\n" f"🌱 Seeds: {seeds} | 🗳 Size: {size}MB\n"


def _minify_torrents(torrents: list[dict[str, Any]]) -> tuple[str, str, str, str]:
    """Returns a torrent name, url, seeds and size from json response"""
    minified_torrents = []
    for torrent in torrents:
        try:
            MB = 1024 * 1024
            size_float = int(torrent["size_bytes"]) / MB
            size = f"{size_float:.2f}"
            minified_torrents.append((torrent["title"], torrent["torrent_url"], torrent["seeds"], size))
        except Exception:
            logfire.exception(f"Error parsing torrent from eztv api. <{torrent}>")
            continue

    return tuple(minified_torrents)


async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Remove season and episode context so we can start the search again if the user wants to download another episode.
    context.pop("selected_season_episodes", None)  # type: ignore
    answer = update.callback_query.data

    # Resend series basic description
    serie = context["data"]  # type: ignore
    try:
        response = prettify_serie(serie)
    except KeyError:
        logfire.exception(f"Error prettifying serie. <{serie}>")
        response = "Error prettifying serie. Try again later."

    keyboard = keyboards.serie()
    # tothink: Maybe implement relative go back. chat_data context should be more intelligent to support that.
    # temp key on chat_data (active_season) that resets after each episode go back?
    # update.callback_query.answer(text='')
    # update.callback_query.message.edit_text('🤬')

    original_text = update.callback_query.message.text
    if response != original_text:
        await update.callback_query.edit_message_text(
            text=response,
            reply_markup=keyboard,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
    else:
        logfire.info(
            f"Selected option '{answer}' would leave text as it is." f"Ignoring to avoid exception. '{response}' "
        )


def get_torrents_by_id(imdb_id: int, limit: int | None = None) -> tuple[str, str, str, str] | None:
    """Request torrents from api and return a minified torrent representation."""
    try:
        r = requests.get(
            "https://eztv.ag/api/get-torrents",
            params={"imdb_id": imdb_id, "limit": limit},
        )
        if r.status_code != 200:
            return
        data = r.json()

        if not data or data["torrents_count"] == 0:
            return

        torrents = sorted(r.json()["torrents"], key=lambda d: (d["season"], d["episode"]))
    except KeyError:
        logfire.info(f"No torrents in eztv api for this serie. Response {r.json()}")
        return
    except Exception:
        logfire.exception(f"Error requesting torrents for {imdb_id}")
        return

    return _minify_torrents(torrents)


async def latest_episodes(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs: str) -> None:
    logfire.info("Called latest episodes")

    if not context:
        message = "Lpm, no pude responder a tu pedido.\nProbá invocando de nuevo el comando a ver si me sale 😊"
        logfire.info(f"Conflicting update: '{update.to_dict()}'")
        await context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=message,
            parse_mode="Markdown",
        )
        # Notify telegram we have answered
        update.callback_query.answer(text="")
        return

    # Get latest episodes from eztv api
    # update.callback_query.answer(text='Getting latest episodes..')

    data = context["data"]  # type: ignore
    imdb_id = data["imdb_id"]  # type: ignore
    torrents = get_torrents_by_id(imdb_id)

    if not torrents:
        logfire.info(f"No torrents for {data['name']}")
        update.callback_query.edit_message_text(text=EZTV_NO_RESULTS, reply_markup=keyboards.serie_go_back_keyboard())
        return

    pretty_torrents = prettify_torrents(torrents)
    response = pretty_torrents if pretty_torrents else EZTV_API_ERROR

    original_text = update.callback_query.message.text
    if response != original_text:
        await update.callback_query.edit_message_text(
            text=response,
            reply_markup=keyboards.serie_go_back_keyboard(),
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
    else:
        answer = update.callback_query.data
        logfire.info(
            f"Selected option '{answer}' would leave text as it is." f"Ignoring to avoid exception. '{response}' "
        )


async def all_episodes(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs: str) -> None:
    serie = context["data"]
    seasons = serie.get("seasons")
    if not seasons:
        await update.callback_query.answer(text="Loading episodes... this may take a while")
        seasons = get_all_seasons(serie["name"], serie["original_name"], serie["number_of_seasons"])
        serie["seasons"] = seasons

    response = "Choose a season to see its episodes."
    keyboard = keyboards.serie_season(seasons)

    original_text = update.callback_query.message.text
    if response != original_text:
        await update.callback_query.edit_message_text(
            text=response,
            reply_markup=keyboard,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )


async def get_season(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs: str) -> None:
    serie = context["data"]
    poster_chat = context["poster_chat"]  # type: ignore
    answer = update.callback_query.data
    season_choice = int(answer.split("_")[-1])

    update.callback_query.answer(text=f"Loading episodes from season {season_choice}")

    season_overview = serie["seasons_info"][season_choice - 1]["overview"]

    try:
        url = get_poster_url(serie["seasons_info"][season_choice - 1])
        poster = InputMediaPhoto(url)
        await poster_chat.edit_media(poster)
    except Exception:
        logfire.info("No hay poster para esta temporada")

    season_episodes = serie["seasons"][season_choice]
    serie["selected_season_episodes"] = season_episodes
    response = f"You chose season {season_choice}.\n{season_overview}"
    logfire.info(f"Season {season_choice} episodes {sorted(tuple(season_episodes.keys()))}")
    keyboard = keyboards.serie_episodes(season_episodes)

    original_text = update.callback_query.message.text
    if response != original_text:
        await update.callback_query.edit_message_text(
            text=response,
            reply_markup=keyboard,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
    else:
        logfire.info(f"Selected option '{answer}' would leave text as it is. Ignoring to avoid exception. {response}")


async def get_episode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    serie = context.chat_data.get("data")
    answer = update.callback_query.data
    episode = answer.split("_")[-1]
    episode_list = serie["selected_season_episodes"][int(episode)]
    the_episodes = prettify_episodes(episode_list)
    response = the_episodes if the_episodes else "No episodes found."
    keyboard = keyboards.serie_go_back_keyboard()
    original_text = update.callback_query.message.text

    if response != original_text:
        await update.callback_query.edit_message_text(
            text=response,
            reply_markup=keyboard,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )


def load_episodes(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs: str) -> None:
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
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
    else:
        logfire.info(f"Selected option '{answer}' would leave text as it is. Ignoring to avoid exception. {response}")
