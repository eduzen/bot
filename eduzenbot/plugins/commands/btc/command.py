"""
btc - btc
report - daily_report
"""
import calendar
import logging
from typing import Any

import pendulum
import requests
import yfinance
from cachetools import TTLCache, cached
from telegram import ChatAction, Update
from telegram.ext import CallbackContext

from eduzenbot.decorators import create_user
from eduzenbot.plugins.commands.dolar.api import get_bluelytics
from eduzenbot.plugins.commands.hackernews.command import hackernews
from eduzenbot.plugins.commands.weather.api import get_klima

logger = logging.getLogger("rich")


CITY_AMSTERDAM = "amsterdam"
CITY_BUENOS_AIRES = "buenos aires"
CITY_HEIDELBERG = "heidelberg,de"
COINGECKO_ALL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin,ethereum,dogecoin,solana,cardano,shiba-inu,decentraland,kava,kusama&vs_currencies=usd"
)

client = requests.Session()


def _process_coingecko(data: dict[str, Any]) -> str:
    try:
        btc = str(round(float(data["bitcoin"]["usd"]), 2))
        btc = f"₿ 1 btc == USD {btc} 💵"
        logger.debug(f"btc: {btc}")

        eth = str(round(float(data["ethereum"]["usd"]), 2))
        eth = f"⧫ 1 eth == USD {eth} 💵"
        logger.debug(f"eth: {eth}")

        sol = str(round(float(data["solana"]["usd"]), 2))
        sol = f"☀️ 1 sol == USD {sol} 💵"
        logger.debug(f"sol: {sol}")

        ada = str(round(float(data["cardano"]["usd"]), 2))
        ada = f"🧚‍♀️ 1 ada == USD {ada} 💵"
        logger.debug(f"ada: {ada}")

        dog = str(round(float(data["dogecoin"]["usd"]), 2))
        dog = f"🐶 1 doge == USD {dog} 💵"
        logger.debug(f"dog: {dog}")

        shi = str(round(float(data["shiba-inu"]["usd"]), 12))
        shi = f"🐕 1 shiba == USD {shi} 💵"
        logger.debug(f"shi: {shi}")

        dcl = str(round(float(data["decentraland"]["usd"]), 2))
        dcl = f"💥 1 mana == USD {dcl} 💵"
        logger.debug(f"dcl: {dcl}")

        kava = str(round(float(data["kava"]["usd"]), 2))
        kava = f"♦️ 1 kava == USD {kava} 💵"
        logger.debug(f"dcl: {dcl}")

        return f"{btc}\n{eth}\n{dog}\n{sol}\n{ada}\n{kava}\n{shi}\n{dcl}"
    except Exception:
        logger.exception("Something went wrong processing coingecko data")
    return "Something went wrong processing coingecko data"


def coingecko_all_crypto() -> str:
    try:
        response = client.get(COINGECKO_ALL)
    except requests.exceptions.ConnectionError:
        return "Perdón! No hay ninguna api disponible for crypto!"

    if response.status_code != 200:
        return "Perdón! No hay ninguna api disponible for crypto!"

    try:
        data = response.json()
        return _process_coingecko(data)
    except Exception:
        logger.exception("Something went wrong when it gets all crypto")

    return "Something went wrong for the crypto api!"


def melistock(name: str) -> str:
    try:
        stock = yfinance.Ticker(name)
        short_name = stock.info.get("shortName")
        mkt_price = str(round(stock.info.get("regularMarketPrice", 0), 2))
        market = stock.info.get("market")
        avg_price = str(round(stock.info.get("fiftyDayAverage", 0), 2))

        txt = f"{short_name}\n" f"U$D {mkt_price} for {market}\n" f"55 days average price U$D {avg_price}\n"
        return txt
    except Exception:
        logger.exception(f"Error getting stock price for {name}")
        return f"No encontramos nada con '{name}'"


@cached(cache=TTLCache(maxsize=2048, ttl=600))
def get_crypto_report() -> str:
    crypto = coingecko_all_crypto()
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
def btc(update: Update, context: CallbackContext, *args: int, **kwargs: str) -> None:
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    text = coingecko_all_crypto()

    context.bot.send_message(chat_id=update.message.chat_id, text=text)


@create_user
def daily_report(update: Update, context: CallbackContext, *args: int, **kwargs: str) -> None:
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    report = get_crypto_report()

    context.bot.send_message(
        chat_id=update.message.chat_id, text=report, parse_mode="Markdown", disable_web_page_preview=True
    )
