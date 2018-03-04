import logging
import requests
from collections import defaultdict

from keys import TOKEN
from api_expenses import send_expense
from api_dolar import get_dolar
from db import User, Question
from telegram_bot import TelegramBot

from commands import (
    btc, caps, ayuda, dolar, start,
    get_questions, get_users, add_question
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def main():
    logger.info("Starting main...")
    bot = TelegramBot()
    commands = {
        'btc': btc,
        'caps': caps,
        'ayuda': ayuda,
        'dolar': dolar,
        'start': start,
        'users': get_users,
        'questions': get_questions,
        'gasto': expense,
        'add_question': add_question
    }
    bot.register_commands(commands)
    bot.start()
    """
    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    inline_caps_handler = InlineQueryHandler(inline_caps)
    dispatcher.add_handler(inline_caps_handler)
    """


if __name__ == '__main__':
    try:
        main()
    except Exception:
        logger.exception('bye bye')
