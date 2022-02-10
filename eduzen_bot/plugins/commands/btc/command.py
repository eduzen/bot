"""
btc - btc
report - daily_report
"""
import calendar
import logging

import pendulum
import yfinance
from telegram import ChatAction

from eduzen_bot.decorators import create_user
from eduzen_bot.plugins.commands.btc.api import get_all, get_btc, get_dogecoin, get_eth
from eduzen_bot.plugins.commands.dolar.api import get_bluelytics
from eduzen_bot.plugins.commands.weather.api import get_klima

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


def get_crypto_report():
    crypto = get_all()
    blue = get_bluelytics() or ""
    # oficial = escape_markdown(parse_bnc() or "")

    clima = get_klima(city_name=CITY_BUENOS_AIRES).replace("By api.openweathermap.org", "")
    amsterdam = get_klima(city_name=CITY_AMSTERDAM).replace("By api.openweathermap.org", "")
    heidelberg = get_klima(city_name=CITY_HEIDELBERG).replace("By api.openweathermap.org", "")

    today = pendulum.today()
    week_day = calendar.day_name[today.weekday()]
    today = today.strftime("%d %B del %Y")
    text = (
        f"*Buenas hoy es {week_day}, {today}:*\n\n"
        f"{clima}"
        f"{amsterdam}"
        f"{heidelberg}"
        f"{blue}\n"
        "\n*Las crypto:*\n"
        f"{crypto}\n"
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
