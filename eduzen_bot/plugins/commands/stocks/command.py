"""
stock - stock
"""
import datetime as dt

import structlog
import yfinance as yf
from telegram import ChatAction

from eduzen_bot.decorators import create_user

logger = structlog.get_logger()


@create_user
def stock(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    if not context.args:
        update.message.reply_text("Se usa: /stock meli")
        return
    name = context.args[0]
    stock = yf.Ticker(name)

    try:
        info = (
            f"{stock.info.get('shortName')} 📈\n"
            f"{dt.datetime.today().strftime('%Y-%m-%d')} \n"
            f"U$D {stock.info.get('regularMarketPrice')} 💵 for {stock.info.get('quoteSourceName')}\n"
            f"55 days average price {stock.info.get('fiftyDayAverage')}\n"
        )

        context.bot.send_photo(chat_id=update.message.chat_id, photo=stock.info.get("logo_url"), caption=info)
    except KeyError:
        update.message.reply_text(f"No encontramos nada con '{name}'")
