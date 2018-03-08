import os
import logging

from telegram.ext import Filters

from handlers.commands.commands import (
    btc, caps, ayuda, dolar, start, expense,
    get_questions, get_users, add_question,
    add_answer
)
from db import create_db_tables
from handlers.messages.message import (
    parse_msg, unknown
)
from telegram_bot import TelegramBot

logger = logging.getLogger()

handler = logging.StreamHandler()
fh = logging.FileHandler('bot.log')

formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def main():
    logger.info("Starting main...")
    commands = {
        'btc': btc,
        'caps': caps,
        'ayuda': ayuda,
        'dolar': dolar,
        'start': start,
        'users': get_users,
        'questions': get_questions,
        'gasto': expense,
        'add_question': add_question,
        'add_answer': add_answer,
    }
    message_handlers = [parse_msg, ]

    bot = TelegramBot()
    bot.register_commands(commands)
    bot.register_message_handler(message_handlers)
    unknown_handler = bot.create_msg(unknown, Filters.command)
    bot.add_handler(unknown_handler)
    bot.start()


if __name__ == '__main__':
    try:
        if not os.path.exists('my_database.db'):
            create_db_tables()
        main()
    except Exception:
        logger.exception('bye bye')
