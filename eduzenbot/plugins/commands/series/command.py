"""
serie - search_serie
series - search_serie
show - search_serie
"""

import logfire
from api import (
    get_keyboard,
    get_poster_url,
    get_related_series,
    get_serie_detail,
    prettify_serie,
)
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from eduzenbot.decorators import create_user


@create_user
async def search_serie(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs: str) -> None:
    """Handle /serie, /series, and /show commands to fetch TV series information."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Te faltó pasarme el nombre de la serie. /serie <serie>",
        )
        return

    query = " ".join(context.args)
    chat_id = update.effective_chat.id

    logfire.info("Search serie", args=context.args)
    results = get_related_series(query)

    if not results:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(f"No encontré información en IMDb sobre _'{query}'_. ¿Está bien escrito el nombre?"),
            parse_mode="Markdown",
        )
        return

    serie = results[0]
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    serie_object = get_serie_detail(serie["id"])
    external_ids = serie_object.external_ids()

    try:
        imdb_id = external_ids["imdb_id"].replace("t", "")  # tt<id> -> <id>
    except (KeyError, AttributeError):
        logfire.info("IMDb ID for the series not found.")
        await context.bot.send_message(
            chat_id=chat_id,
            text="👎 No encontré el ID de IMDb de esta serie, imposible de bajar por acá.",
            parse_mode="Markdown",
        )
        return

    extra_info = serie_object.info()
    next_episode = "unannounced"
    if extra_info.get("next_episode_to_air"):
        next_episode = extra_info["next_episode_to_air"].get("air_date", "unannounced")

    serie.update(
        {
            "imdb_id": imdb_id,
            "seasons_info": extra_info["seasons"],
            "number_of_episodes": extra_info["number_of_episodes"],
            "number_of_seasons": extra_info["number_of_seasons"],
            "next_episode": next_episode,
            "original_name": extra_info.get("original_name"),
        }
    )
    response = prettify_serie(serie)

    poster_url = get_poster_url(serie)
    poster_chat = await context.bot.send_photo(chat_id, poster_url)
    bot_reply = await context.bot.send_message(
        chat_id=chat_id,
        text=response,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

    context.chat_data["context"] = {
        "data": serie,
        "command": "serie",
        "edit_original_text": True,
        "poster_chat": poster_chat,
    }

    await context.bot.edit_message_reply_markup(
        chat_id=update.effective_chat.id,
        message_id=bot_reply.message_id,
        reply_markup=get_keyboard(),
    )
