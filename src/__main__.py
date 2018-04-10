"""
Usage:
    __main__.py [--stream] [--log_level=<level>] [--database=<path>]
    __main__.py -h | --help
    __main__.py --version
    __main__.py --stream

Options:
    -h --help   Show this.
    --version   Show version.
    --stream    Log to stdout.
    --log_level Level of logging ERROR DEBUG INFO WARNING.
    --database database path.
"""
import os
import sys
from threading import Thread
from pathlib import Path

from __init__ import get_log
from docopt import docopt
from telegram.ext import Filters
from telegram.ext import CommandHandler

from db import create_db_tables
from handlers.commands.alarm import set_timer, unset
from handlers.commands import COMMANDS
from handlers.messages.inline import code_markdown
from handlers.messages.unknown import unknown
from handlers.messages.message import (
    parse_msgs
)
from config import db_path
from telegram_bot import TelegramBot


def main(logger):
    message_handlers = [parse_msgs, ]

    bot = TelegramBot()
    bot.register_commands(COMMANDS)
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

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        bot.updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(bot, update):
        bot.update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    bot.add_handler(CommandHandler('r', restart, filters=Filters.user(username='@eduzen')))
    bot.start()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='eduzen_bot 1.0')
    stream = arguments.get('--stream')
    level = arguments.get('--log_level')
    database = arguments.get('--database')
    logger = get_log(level=level, stream=stream)

    if database:
        db_path = Path(database)

    try:
        if not db_path.exists():
            logger.info(f'Database {db_path} does not exist')
            create_db_tables(db_path)

        main(logger)
    except Exception:
        logger.exception('bye bye')
