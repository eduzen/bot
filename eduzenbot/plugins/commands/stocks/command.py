"""
stock - stock
"""

import datetime as dt

import yfinance as yf
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from eduzenbot.decorators import create_user


@create_user
async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: int, **kwargs: str) -> None:
    """Handle /stock command to fetch stock information."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    if not context.args:
        await update.message.reply_text("Se usa: /stock meli")
        return

    name = context.args[0]
    stock = yf.Ticker(name)

    try:
        info = (
            f"{stock.info.get('shortName')} 📈\n"
            f"{dt.datetime.today().strftime('%Y-%m-%d')} \n"
            f"U$D {stock.info.get('regularMarketPrice')} 💵 for {stock.info.get('market')}\n"
            f"55 days average price {stock.info.get('fiftyDayAverage')}\n"
        )

        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=stock.info.get("logo_url"),
            caption=info,
        )
    except KeyError:
        await update.message.reply_text(f"No encontramos nada con '{name}'")
    except Exception as e:
        await update.message.reply_text("Ocurrió un error al obtener la información.")
        raise e
