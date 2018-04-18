"""
Usage:
    __main__.py [-q | -v] [--log_level=<level>] [--database=<path>]
    __main__.py -h | --help
    __main__.py --version

Options:
    -h --help       Show this.
    --version       Show version.
    --log_level     Level of logging ERROR DEBUG INFO WARNING.
    --database      database path.
    -q, --quiet     Less stdout as an additional output for logging. [default: info]
    -v, --verbose   More stdout as an additional output for logging. [default: info]

"""
import os
import sys
from threading import Thread
from pathlib import Path

import structlog
from docopt import docopt
from telegram.ext import Filters
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler

from __init__ import initialize_logging, set_handler
from db import create_db_tables
from config import db_path
from handlers.commands.alarm import set_timer, unset
from handlers.commands import COMMANDS
from handlers.messages.inline import code_markdown
from handlers.messages.unknown import unknown
from handlers.commands.questions import q_menu, button
from handlers.messages.message import (parse_msgs)
from telegram_bot import TelegramBot


logger = stream.get_logger()


def main():

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        bot.updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="Bot is restarting...")
        Thread(target=stop_and_restart).start()

    logger.info("Starting main...")

    message_handlers = [parse_msgs]

    bot = TelegramBot()
    bot.register_commands(COMMANDS)
    bot.register_message_handler(message_handlers)

    bot.add_handler(
        CommandHandler("restart", restart, filters=Filters.user(username="@eduzen"))
    )

    set_handler = bot.create_command_args(
        "set", set_timer, pass_args=True, pass_job_queue=True, pass_chat_data=True
    )
    bot.add_handler(set_handler)

    unset_handler = bot.create_command_args(
        "unset", unset, pass_args=False, pass_job_queue=False, pass_chat_data=True
    )
    bot.add_handler(unset_handler)

    code_handler = bot.create_inlinequery(code_markdown)
    bot.add_handler(code_handler)

    unknown_handler = bot.create_msg(unknown, Filters.command)
    bot.add_handler(unknown_handler)

    bot.add_handler(CallbackQueryHandler(button))
    bot.start()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='eduzen_bot 1.0')
    stream = arguments.get('--stream')
    level = arguments.get('--log_level')
    database = arguments.get('--database')
    verbose = set_handler(arguments)
    initialize_logging(verbose=verbose, level=level)

    if database:
        db_path = Path(database)

    try:
        if not db_path.exists():
            logger.info(f'Database {db_path} does not exist')
            create_db_tables(db_path)

        main(logger)
    except Exception:
        logger.exception("bye bye")
