#!/usr/bin/env python3

import logging
import os

import sentry_sdk
from rich.logging import RichHandler
from sentry_sdk.integrations.tornado import TornadoIntegration
from telegram.ext import CallbackQueryHandler, CommandHandler, Filters

from eduzenbot.callbacks_handler import callback_query
from eduzenbot.models import db
from eduzenbot.plugins.job_queue.alarms.command import set_timer, unset
from eduzenbot.plugins.messages.inline import code_markdown
from eduzenbot.plugins.messages.unknown import unknown
from eduzenbot.scripts.initialize_db import create_db_tables
from eduzenbot.telegram_bot import TelegramBot

TOKEN = os.environ["TOKEN"]
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
EDUZEN_ID = os.environ["EDUZEN_ID"]
PORT = int(os.getenv("PORT", 5000))
LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR")


logging.basicConfig(
    level=logging.getLevelName(LOG_LEVEL),
    format="%(message)s",
    datefmt="[%d-%m-%y %X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger()

sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=0.8,
    integrations=[TornadoIntegration()],
)


def main() -> None:
    create_db_tables()
    bot = TelegramBot(token=TOKEN, eduzen_id=EDUZEN_ID, polling=False, port=PORT)
    db.connect(reuse_if_open=True)

    bot.add_handler(CommandHandler("set", set_timer))
    bot.add_handler(CommandHandler("config_reporte", set_timer))
    bot.add_handler(CommandHandler("unset", unset))

    message_handlers: list[str] = []  # parse_msgs

    bot.register_message_handler(message_handlers)

    code_handler = bot.create_inlinequery(code_markdown)
    bot.add_handler(code_handler)

    unknown_handler = bot.create_msg(unknown, Filters.command)
    bot.add_handler(unknown_handler)

    bot.add_handler(CallbackQueryHandler(callback_query, pass_chat_data=True))

    bot.start()


if __name__ == "__main__":
    main()
