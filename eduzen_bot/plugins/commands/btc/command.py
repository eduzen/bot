"""
btc - btc
report - daily_report
"""
import logging
from datetime import datetime as dt

from telegram import ChatAction

from eduzen_bot.decorators import create_user
from eduzen_bot.plugins.commands.btc.api import get_btc, get_dogecoin, get_eth
from eduzen_bot.plugins.commands.dolar.api import get_bluelytics, parse_bnc
from eduzen_bot.plugins.commands.stocks.command import get_stock_price
from eduzen_bot.plugins.commands.weather.api import get_klima

logger = logging.getLogger()


def get_crypto_report():
    btc = get_btc() or ""
    dog = get_dogecoin() or ""
    eth = get_eth() or ""
    blue = get_bluelytics() or ""
    oficial = parse_bnc() or ""
    meli = get_stock_price("MELI") or ""

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
        "Stocks:\n"
        f"{meli}\n\n"
        "bye!"
    )
    return text


@create_user
def btc(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    btc = get_btc() or ""
    dog = get_dogecoin() or ""
    eth = get_eth() or ""

    text = "\n".join([dog, eth, btc])

    context.bot.send_message(chat_id=update.message.chat_id, text=text)


@create_user
def daily_report(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    report = get_crypto_report()

    context.bot.send_message(chat_id=update.message.chat_id, text=report, parse_mode="Markdown")
