"""
stock - stock
"""
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
    info = f"{name} U$D {stock.info['regularMarketDayHigh']} regular market day high"

    update.message.reply_text(info)
    # context.bot.send_message(chat_id=update.message.chat_id, text=info)
