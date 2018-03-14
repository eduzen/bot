import os
import logging

from telegram.ext import Filters

from db import create_db_tables
from handlers.commands.alarm import set_timer, unset
from handlers.commands.commands import (
    btc, caps, ayuda, dolar, start, expense,
    get_questions, get_users, add_question,
    add_answer, cotizaciones, weather, code,
    subte, subte_novedades, remove_question
)
from handlers.messages.inline import code_markdown
from handlers.messages.unknown import unknown
from handlers.messages.message import (
    parse_msgs
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
        'cambio': cotizaciones,
        'clima': weather,
        'code': code,
        'subte': subte,
        'subtenews': subte_novedades,
        'remove': remove_question,
    }
    message_handlers = [parse_msgs, ]

    bot = TelegramBot()
    bot.register_commands(commands)
    bot.register_message_handler(message_handlers)

    set_handler = bot.create_command_args(
        'set', set_timer, pass_args=True, pass_job_queue=True, pass_chat_data=True
    )
    bot.add_handler(set_handler)

    unset_handler = bot.create_command_args(
        'unset', unset, pass_args=False, pass_job_queue=False, pass_chat_data=True
    )
    bot.add_handler(unset_handler)

    code_handler = bot.create_inlinequery(code_markdown)
    bot.add_handler(code_handler)

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
