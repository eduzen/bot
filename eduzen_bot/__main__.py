#!/usr/bin/env python3

import logging
import os
import sys
from threading import Thread

import sentry_sdk
from rich.logging import RichHandler
from sentry_sdk.integrations.tornado import TornadoIntegration
from telegram.ext import CallbackQueryHandler, CommandHandler, Filters

from eduzen_bot.callbacks_handler import callback_query
from eduzen_bot.plugins.job_queue.alarms.command import set_timer, unset
from eduzen_bot.plugins.messages.inline import code_markdown
from eduzen_bot.plugins.messages.message import parse_msgs
from eduzen_bot.plugins.messages.unknown import unknown
from eduzen_bot.scripts.initialize_db import create_db_tables
from eduzen_bot.telegram_bot import TelegramBot

TOKEN = os.getenv("TOKEN")
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
EDUZEN_ID = os.getenv("EDUZEN_ID")
PORT = int(os.getenv("PORT", 5000))
HEROKU = int(os.getenv("HEROKU", 0))
LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR")

FORMAT = "%(message)s"

logging.basicConfig(
    level=logging.getLevelName(LOG_LEVEL),
    format=FORMAT,
    datefmt="[%d-%m-%y %X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger()

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[TornadoIntegration()],
)


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
    bot.add_handler(CommandHandler("set", set_timer))
    bot.add_handler(CommandHandler("unset", unset))

    message_handlers = [parse_msgs]

    bot.register_message_handler(message_handlers)

    code_handler = bot.create_inlinequery(code_markdown)
    bot.add_handler(code_handler)

    unknown_handler = bot.create_msg(unknown, Filters.command)
    bot.add_handler(unknown_handler)

    bot.add_handler(CallbackQueryHandler(callback_query, pass_chat_data=True))

    bot.start()


if __name__ == "__main__":
    main()
