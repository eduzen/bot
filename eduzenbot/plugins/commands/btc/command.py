"""
btc - btc
report - daily_report
"""

import calendar
from datetime import datetime

import logfire
import pytz
import yfinance
from cachetools import TTLCache, cached
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from eduzenbot.decorators import create_user
from eduzenbot.plugins.commands.btc.api import get_all
from eduzenbot.plugins.commands.dolar.api import get_bluelytics
from eduzenbot.plugins.commands.hackernews.command import fetch_hackernews_stories
from eduzenbot.plugins.commands.weather.api import get_klima

CITY_AMSTERDAM = "amsterdam,nl"
CITY_BUENOS_AIRES = "buenos aires,ar"
CITY_HEIDELBERG = "heidelberg,de"
CITY_DALLAS = "dallas"


def melistock(name: str) -> str:
    try:
        stock = yfinance.Ticker(name)
        short_name = stock.info.get("shortName")
        mkt_price = round(stock.info.get("regularMarketPrice", 0), 2)
        market = stock.info.get("market")
        avg_price = round(stock.info.get("fiftyDayAverage", 0), 2)

        txt = f"{short_name}\n" f"U$D {mkt_price} for {market}\n" f"55 days average price U$D {avg_price}\n"
        return txt
    except Exception:
        logfire.exception(f"Error getting stock price for {name}")
        return f"No encontramos nada con '{name}'"


@cached(cache=TTLCache(maxsize=2048, ttl=600))
async def get_crypto_report() -> str:
    crypto = await get_all()
    blue = await get_bluelytics() or "-"
    clima = await get_klima(city_name=CITY_BUENOS_AIRES).replace("By api.openweathermap.org", "")
    amsterdam = await get_klima(city_name=CITY_AMSTERDAM).replace("By api.openweathermap.org", "")
    dallas = await get_klima(city_name=CITY_DALLAS).replace("By api.openweathermap.org", "")

    now = datetime.now(pytz.timezone("America/Argentina/Buenos_Aires"))
    week_day = calendar.day_name[now.weekday()]
    today = now.strftime("%d %B del %Y")

    try:
        hn = await fetch_hackernews_stories()
    except Exception:
        hn = ""

    text = (
        f"*Buenas hoy es {week_day}, {today}:*\n\n"
        f"{clima}"
        f"{amsterdam}"
        f"{dallas}"
        "*Dólar 💸*\n"
        f"{blue}\n"
        f"\n{crypto}\n"
        f"\n{hn}\n"
    )
    return text


@create_user
async def btc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /btc command to get Bitcoin information."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    text = get_all()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


@create_user
async def daily_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /report command to send a daily report."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    report = await get_crypto_report()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=report,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )
