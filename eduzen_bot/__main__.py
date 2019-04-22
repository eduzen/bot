""" eduzen_bot: a python telgram bot

Usage:
    __main__.py [-q | -v] [--log_level=level] [--config=<path>]
    __main__.py -h | --help
    __main__.py --version

Options:
    -h --help           Show this.
    --version           Show version.
    --log_level=level   Level of logging ERROR DEBUG INFO WARNING.
    --config=config     Config file path.
    -q, --quiet         Less stdout as an additional output for logging. [default: info]
    -v, --verbose       More stdout as an additional output for logging. [default: info]

"""
import os
import sys
import logging
from threading import Thread

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from dotenv import load_dotenv
from docopt import docopt
from telegram.ext import Filters
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler

from eduzen_bot import initialize_logging, set_handler
from eduzen_bot.telegram_bot import TelegramBot
from eduzen_bot.callbacks_handler import callback_query

from plugins.job_queue.alarms.command import set_timer, unset
from plugins.messages.inline import code_markdown
from plugins.messages.unknown import unknown
from plugins.messages.message import (parse_msgs)

load_dotenv()

sentry_logging = LoggingIntegration(
    level=logging.DEBUG,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN", ''),
    integrations=[sentry_logging],
    release=os.environ.get("RELEASE", 'eduzen_bot@1.0')
)


def main():
    bot = TelegramBot()

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        logging.info("Restarting eduzen_bot...\n")
        bot.updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="Bot is restarting...")
        Thread(target=stop_and_restart).start()

    bot.add_handler(
        CommandHandler("restart", restart, filters=Filters.user(username="@eduzen"))
    )

    message_handlers = [parse_msgs]

    bot.register_message_handler(message_handlers)

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

    bot.add_handler(CallbackQueryHandler(callback_query, pass_chat_data=True))
    bot.start()


if __name__ == "__main__":
    arguments = docopt(__doc__, version=os.environ.get("RELEASE", 'eduzen_bot@1.0')
    stream = arguments.get("--stream")
    level = arguments.get("--log_level")
    config = arguments.get("--config")
    verbose = set_handler(arguments)
    initialize_logging(verbose=verbose, level=level)

    try:
        logging.info("Starting main...")
        main()
    except Exception:
        logging.exception("bye bye")
