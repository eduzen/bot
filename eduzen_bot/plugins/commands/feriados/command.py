"""
feriados - feriadosarg
"""
import logging
from datetime import datetime

import pytz

from eduzen_bot.decorators import create_user
from eduzen_bot.plugins.commands.feriados.api import (
    filter_feriados,
    get_feriados,
    prettify_feriados,
)

logger = logging.getLogger("rich")


@create_user
def feriadosarg(update, context, *args, **kwargs):
    today = datetime.now(pytz.timezone("America/Argentina/Buenos_Aires"))
    feriados = get_feriados(today.year)
    if not feriados:
        update.message.reply_text("🏳️ La api de feriados no responde")
        return

    following_feriados = filter_feriados(today, feriados)
    if following_feriados:
        msg = prettify_feriados(today, following_feriados)
    else:
        msg = "No hay más feriados este año"

    update.message.reply_text(msg, parse_mode="markdown")
