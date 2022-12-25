"""
btc - btc
report - daily_report
"""
import calendar
import logging

import pendulum
import yfinance
from cachetools import TTLCache, cached
from telegram import ChatAction, Update

from eduzenbot.decorators import create_user
from eduzenbot.plugins.commands.btc.api import get_all
from eduzenbot.plugins.commands.dolar.api import get_bluelytics
from eduzenbot.plugins.commands.hackernews.command import hackernews
from eduzenbot.plugins.commands.weather.api import get_klima

logger = logging.getLogger()


CITY_AMSTERDAM = "amsterdam"
CITY_BUENOS_AIRES = "buenos aires"
CITY_HEIDELBERG = "heidelberg,de"


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


@cached(cache=TTLCache(maxsize=2048, ttl=600))
def get_crypto_report():
    crypto = get_all()
    blue = get_bluelytics() or "-"
    # oficial = escape_markdown(parse_bnc() or "")

    clima = get_klima(city_name=CITY_BUENOS_AIRES).replace("By api.openweathermap.org", "")
    amsterdam = get_klima(city_name=CITY_AMSTERDAM).replace("By api.openweathermap.org", "")
    heidelberg = get_klima(city_name=CITY_HEIDELBERG).replace("By api.openweathermap.org", "")

    today = pendulum.today()
    week_day = calendar.day_name[today.weekday()]
    try:
        hn = hackernews()
    except Exception:
        hn = ""

    today = today.strftime("%d %B del %Y")
    text = (
        f"*Buenas hoy es {week_day}, {today}:*\n\n"
        f"{clima}"
        f"{amsterdam}"
        f"{heidelberg}"
        f"{hn}\n"
        "\n*Dólar 💸*\n"
        f"{blue}\n"
        "\n*Las crypto:*\n"
        f"{crypto}\n"
    )
    return text


@create_user
def btc(update: Update, context: object, *args: int, **kwargs: str):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    text = get_all()

    context.bot.send_message(chat_id=update.message.chat_id, text=text)


@create_user
def daily_report(update: Update, context: object, *args: int, **kwargs: str):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    report = get_crypto_report()

    context.bot.send_message(
        chat_id=update.message.chat_id, text=report, parse_mode="Markdown", disable_web_page_preview=True
    )
