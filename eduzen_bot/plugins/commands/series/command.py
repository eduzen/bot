"""
serie - search_serie
series - search_serie
"""
import structlog
from telegram.ext import run_async
from telegram import ChatAction

from api import get_related_series, get_keyboard, get_serie_detail, get_poster_url, prettify_serie

logger = structlog.get_logger(filename=__name__)


@run_async
def search_serie(bot, update, **kwargs):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    args = kwargs.get("args")
    chat_data = kwargs.get("chat_data")
    if not args:
        bot.send_message(chat_id=update.message.chat_id, text="Te faltó pasarme el nombre de la serie. /serie <serie>")
        return

    query = " ".join(args)
    chat_id = update.message.chat_id

    logger.info(f"Search serie {args}")
    results = get_related_series(query)

    if not results:
        bot_reply = bot.send_message(
            chat_id=chat_id,
            text=(f"No encontré información en imdb sobre _'{query}'_." " Está bien escrito el nombre?"),
            parse_mode="markdown",
        )
        return

    serie = results[0]
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    serie_object = get_serie_detail(serie["id"])
    external_ids = serie_object.external_ids()

    try:
        imdb_id = external_ids["imdb_id"].replace("t", "")  # tt<id> -> <id>
    except (KeyError, AttributeError):
        logger.info("imdb id for the movie not found")
        bot.send_message(
            chat_id=chat_id,
            text="👎 No encontré el id de imdb de esta serie, imposible de bajar por acá",
            parse_mode="markdown",
        )
        return

    extra_info = serie_object.info()
    next_episode = "unannounced"
    if extra_info.get("next_episode_to_air"):
        next_episode = extra_info["next_episode_to_air"].get("air_date",  "unannounced")

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
    poster_chat = bot.send_photo(chat_id, poster_url)
    bot_reply = bot.send_message(chat_id=chat_id, text=response, parse_mode="markdown", disable_web_page_preview=True)

    chat_data["context"] = {"data": serie, "command": "serie", "edit_original_text": True, "poster_chat": poster_chat}

    bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=bot_reply.message_id,
        text=bot_reply.caption,
        reply_markup=get_keyboard(),
        parse_mode="markdown",
        disable_web_page_preview=True,
    )
