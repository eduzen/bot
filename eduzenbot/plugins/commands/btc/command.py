"""
btc - btc
report - show_daily_report
"""

import calendar
from datetime import datetime

import logfire
import pytz
import yfinance
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from eduzenbot.decorators import create_user
from eduzenbot.models import Report
from eduzenbot.plugins.commands.btc.api import get_all
from eduzenbot.plugins.commands.dolar.api import get_dolarapi, get_euro_dolarapi
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

        txt = f"{short_name}\nU$D {mkt_price} for {market}\n55 days average price U$D {avg_price}\n"
        return txt
    except Exception:
        logfire.exception(f"Error getting stock price for {name}")
        return f"No encontramos nada con '{name}'"


def get_current_time() -> str:
    # Current date
    now = datetime.now(pytz.timezone("America/Argentina/Buenos_Aires"))
    week_day = calendar.day_name[now.weekday()]
    today = now.strftime("%d %B del %Y")
    return f"*Buenas hoy es {week_day}, {today}:*"


async def get_all_weather() -> str:
    buenos_aires = await get_klima(city_name=CITY_BUENOS_AIRES)
    amsterdam = await get_klima(city_name=CITY_AMSTERDAM)
    dallas = await get_klima(city_name=CITY_DALLAS)
    return f"{buenos_aires}\n{amsterdam}\n{dallas}"


async def get_crypto_report(report: Report) -> str:
    parts = []

    # Get the current time
    parts.append(get_current_time())

    if report.show_weather:
        parts.append(await get_all_weather())

    if report.show_dollar:
        dolar_parts = []
        dolarapi = await get_dolarapi()
        if dolarapi:
            # Remove the footer from dolarapi
            dolarapi_clean = dolarapi.rsplit("\n👊", 1)[0]
            dolar_parts.append(dolarapi_clean)

        euro_dolarapi = await get_euro_dolarapi()
        if euro_dolarapi:
            # Remove the footer from euro_dolarapi
            euro_clean = euro_dolarapi.rsplit("\n👊", 1)[0]
            dolar_parts.append(euro_clean)

        if dolar_parts:
            # Add single footer at the end
            combined = "\n\n".join(dolar_parts) + "\n👊 by dolarapi.com"
            parts.append(combined)

    if report.show_crypto:
        crypto = await get_all()
        parts.append(f"\n{crypto}\n")

    if report.show_news:
        # Use Markdown (v1) friendly formatting for HN inside the report
        hn = await fetch_hackernews_stories(md_version=1)
        parts.append(f"{hn}\n")

    return "\n".join(parts)


@create_user
async def btc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(update.effective_chat.id) if update.effective_chat else None

    if not chat_id:
        logfire.error("Failed to get chat_id. Update does not have effective_chat.")
        return

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    text = await get_all()

    await context.bot.send_message(chat_id=chat_id, text=text)


@create_user
async def show_daily_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(update.effective_chat.id) if update.effective_chat else None

    if not chat_id:
        logfire.error("Failed to get chat_id. Update does not have effective_chat.")
        return

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    try:
        # Fetch or create the report record
        report, _ = Report.get_or_create(chat_id=chat_id)
        report_text = await get_crypto_report(report)
    except Exception:
        logfire.exception("Error getting daily report")
        report_text = "Ocurrió un error al obtener el reporte diario."

    await context.bot.send_message(
        chat_id=chat_id,
        text=report_text,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )
