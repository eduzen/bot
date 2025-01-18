#!/usr/bin/env python3
import os
from pathlib import Path

import logfire
import sentry_sdk
from dotenv import load_dotenv
from telegram.error import InvalidToken
from telegram.ext import Application, CommandHandler, ExtBot, MessageHandler, filters

from eduzenbot.adapters.plugin_loader import load_and_register_plugins
from eduzenbot.adapters.telegram_error_handler import telegram_error_handler
from eduzenbot.models import db
from eduzenbot.plugins.job_queue.alarms.command import (
    cancel_daily_report,
    schedule_daily_report,
)
from eduzenbot.plugins.messages.unknown import unknown
from eduzenbot.scripts.initialize_db import create_db_tables

# Load environment variables from .env file
env_path = Path("../.env")
load_dotenv(env_path)

TOKEN = os.environ["TOKEN"]
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
EDUZEN_ID = os.environ["EDUZEN_ID"]
PORT = int(os.getenv("PORT", 5000))
LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR")


logfire.configure()

sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=0.8,
)


async def send_startup_message(bot: ExtBot):
    """Sends a message to a specific chat when the bot starts."""
    await bot.send_message(chat_id=EDUZEN_ID, text="🤖 Bot has started and is running!")


async def on_startup(app: Application):
    await send_startup_message(app.bot)


def main():
    create_db_tables()
    db.connect(reuse_if_open=True)
    try:
        bot = ExtBot(token=TOKEN)
        app = Application.builder().bot(bot).build()
    except InvalidToken:
        logfire.exception("Invalid token")
        return

    app.post_init = on_startup
    app.add_error_handler(telegram_error_handler)
    logfire.info("Application created")

    # Register command handlers
    app.add_handler(
        CommandHandler(
            "set",
        )
    )
    app.add_handler(CommandHandler("report", schedule_daily_report))
    app.add_handler(CommandHandler("cancelreport", cancel_daily_report))

    handlers = load_and_register_plugins()
    app.add_handlers(handlers)
    logfire.info("Plugins loaded!")

    app.add_handler(MessageHandler(filters.COMMAND, unknown))
    app.run_polling()


if __name__ == "__main__":
    main()
