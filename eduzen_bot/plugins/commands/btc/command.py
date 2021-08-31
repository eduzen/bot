"""
btc - btc
report - daily_report
"""
import logging

import yfinance
from telegram import ChatAction
from telegram.utils.helpers import escape_markdown

from eduzen_bot.decorators import create_user
from eduzen_bot.plugins.commands.btc.api import get_btc, get_dogecoin, get_eth
from eduzen_bot.plugins.commands.dolar.api import get_bluelytics, parse_bnc
from eduzen_bot.plugins.commands.weather.api import get_klima

logger = logging.getLogger()


def melistock(name):
    try:
        stock = yfinance.Ticker(name)
        short_name = stock.info.get("shortName")
        mkt_price = round(stock.info.get("regularMarketPrice", 0), 2)
        market = stock.info.get("market")
        avg_price = round(stock.info.get("fiftyDayAverage", 0), 2)

        txt = f"{short_name}\n" f"U$D {mkt_price} for {market}\n" f"55 days average price U$D {avg_price}\n"
        return txt
    except Exception:
        logger.exception(f"Error getting stock price for {name}")
        return f"No encontramos nada con '{name}'"


def get_crypto_report():
    btc = get_btc() or ""
    dog = get_dogecoin() or ""
    eth = get_eth() or ""
    blue = get_bluelytics() or ""
    oficial = escape_markdown(parse_bnc() or "")
    try:
        meli = escape_markdown(melistock("MELI"))
    except Exception as e:
        logger.error(e)
        meli = ""

    clima = get_klima("buenos aires").replace("By api.openweathermap.org", "")
    amsterdam = get_klima("amsterdam").replace("By api.openweathermap.org", "")

    text = "\n".join([dog, eth, btc])
    import datetime  # noqa

    hoy = datetime.datetime.today().strftime("%d %B del %Y")
    text = (
        f"Buenas buenas hoy es {hoy}:\n\n"
        f"{clima}"
        f"{amsterdam}"
        "\nel blue:\n"
        f"{blue}\n"
        "el oficial:\n"
        f"{oficial}\n"
        "\nLas crypto:\n"
        f"{text}\n"
        "\nStocks:\n"
        f"{meli}\n"
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
