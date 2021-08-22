"""
btc - btc
"""
import logging
from datetime import datetime as dt

from telegram import ChatAction

from eduzen_bot.decorators import create_user
from eduzen_bot.plugins.commands.btc.api import get_btc, get_dogecoin, get_eth
from eduzen_bot.plugins.commands.dolar.api import get_dolar_blue, parse_bnc
from eduzen_bot.plugins.commands.weather.api import get_klima

logger = logging.getLogger()


@create_user
def btc(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    btc = get_btc() or ""
    dog = get_dogecoin() or ""
    eth = get_eth() or ""

    text = "\n".join([dog, eth, btc])

    context.bot.send_message(chat_id=update.message.chat_id, text=text)


def get_crypto_report():
    btc = get_btc() or ""
    dog = get_dogecoin() or ""
    eth = get_eth() or ""
    blue = get_dolar_blue() or ""
    oficial = parse_bnc() or ""

    clima = get_klima("buenos aires").replace("By api.openweathermap.org", "")
    amsterdam = get_klima("amsterdam").replace("By api.openweathermap.org", "")

    text = "\n".join([dog, eth, btc])
    hoy = dt.today().strftime("%d %B del %Y")
    text = (
        f"Buenas buenas hoy es {hoy}:\n\n"
        f"{clima}"
        f"{amsterdam}"
        "el blue:\n\n"
        f"{blue}\n\n"
        "el oficial:\n\n"
        f"{oficial}\n\n"
        "Las crypto:\n\n"
        f"{text}\n\n"
        "bye!"
    )
    return text
