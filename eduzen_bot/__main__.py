#!/usr/bin/env python3

import logging
import os
import sys
from threading import Thread

import sentry_sdk
import structlog
from dotenv import load_dotenv
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.tornado import TornadoIntegration
from telegram.ext import CallbackQueryHandler, CommandHandler, Filters

from eduzen_bot import LEVELS, add_timestamp
from eduzen_bot.callbacks_handler import callback_query
from eduzen_bot.plugins.job_queue.alarms.command import set_timer, unset
from eduzen_bot.plugins.messages.inline import code_markdown
from eduzen_bot.plugins.messages.message import parse_msgs
from eduzen_bot.plugins.messages.unknown import unknown
from eduzen_bot.scripts.initialize_db import create_db_tables
from eduzen_bot.telegram_bot import TelegramBot

load_dotenv("../.env")

LOG_LEVEL = LEVELS[os.environ.get("LOG_LEVEL", "INFO").upper()]

sentry_logging = LoggingIntegration(level=LOG_LEVEL, event_level=logging.ERROR)

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", ""),
    integrations=[sentry_logging, TornadoIntegration()],
    traces_sample_rate=1,
    release=os.getenv("TAG"),
)
TOKEN = os.getenv("TOKEN")
EDUZEN_ID = os.getenv("EDUZEN_ID")
PORT = int(os.getenv("PORT", 5000))
HEROKU = int(os.getenv("HEROKU", 0))


def main():
    create_db_tables()
    bot = TelegramBot(TOKEN, EDUZEN_ID, HEROKU, PORT)

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        logger.info("Restarting eduzen_bot...")
        bot.updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(update, context):
        update.message.reply_text("Bot is restarting...")
        Thread(target=stop_and_restart).start()

    bot.add_handler(CommandHandler("restart", restart, filters=Filters.user(username="@eduzen")))

    message_handlers = [parse_msgs]

    bot.register_message_handler(message_handlers)

    set_handler = bot.create_command_args("set", set_timer, pass_args=True, pass_job_queue=True, pass_chat_data=True)
    bot.add_handler(set_handler)

    unset_handler = bot.create_command_args("unset", unset, pass_args=False, pass_job_queue=False, pass_chat_data=True)
    bot.add_handler(unset_handler)

    code_handler = bot.create_inlinequery(code_markdown)
    bot.add_handler(code_handler)

    unknown_handler = bot.create_msg(unknown, Filters.command)
    bot.add_handler(unknown_handler)

    bot.add_handler(CallbackQueryHandler(callback_query, pass_chat_data=True))
    bot.start()


if __name__ == "__main__":
    structlog.configure_once(
        processors=[
            add_timestamp,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(LOG_LEVEL),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )
    logger = structlog.get_logger(filename=__name__)
    try:
        logger.warn("Starting main...")
        main()
    except Exception:
        logger.exception("bye bye")
