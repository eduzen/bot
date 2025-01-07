import os
from collections.abc import Callable, Sequence
from functools import partial
from typing import Any

import attr
import logfire
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, InlineQueryHandler, MessageHandler

from eduzenbot.adapters.plugin_loader import load_plugins
from eduzenbot.adapters.telegram_error_handler import telegram_error_handler
from eduzenbot.domain.report_scheduler import schedule_reports

here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)


@attr.s(auto_attribs=True)
class TelegramBot:
    """Class for python-telegram-bot with PTB 20.x"""

    token: str
    eduzen_id: str = "3652654"
    polling: bool = False
    port: int = 80
    workers: int = 4

    def __attrs_post_init__(self) -> None:
        try:
            self.application = Application.builder().token(self.token).build()
        except TelegramError as exc:
            logfire.exception("Something went wrong initializing the application...")
            raise SystemExit(exc.message)

        logfire.info(f"Application created for token ending in {self.token[-4:]}")

        # Register the error handler
        self.application.add_error_handler(telegram_error_handler)

        # Load and register plugins
        self._load_plugins()

    def start(self) -> None:
        if not self.polling:
            logfire.info("Starting bot with polling...")
            self.application.run_polling()
        else:
            logfire.info("Starting bot with webhook...")
            self.application.run_webhook(
                listen="0.0.0.0",
                port=self.port,
                webhook_url=f"https://eduzenbot.herokuapp.com/{self.token}",
            )

        # Notify the developer
        self.send_msg_to_eduzen("eduzenbot reiniciado!")

        # Now schedule any daily jobs
        schedule_reports(
            self.application.job_queue,
            self.send_msg_to_chatid,
            self.eduzen_id,
        )

    def add_handler(self, handler) -> None:
        self.application.add_handler(handler)

    def add_list_of_handlers(self, handlers: Sequence[CommandHandler | MessageHandler]) -> None:
        for handler in handlers:
            self.add_handler(handler)

    async def send_msg(self, msg: str) -> None:
        await self.application.bot.send_message(chat_id=self.eduzen_id, text=msg)

    async def send_msg_to_chatid(self, chatid: str, msg: str) -> None:
        await self.application.bot.send_message(chat_id=chatid, text=msg)

    async def send_msg_to_eduzen(self, msg: str) -> None:
        logfire.info("Aviso a eduzen")
        await self.send_msg_to_chatid(self.eduzen_id, msg)

    def create_command(self, name: str, func: Callable) -> CommandHandler:
        return CommandHandler(name, func)

    def create_inlinequery(self, func: Callable) -> InlineQueryHandler:
        return InlineQueryHandler(func)

    def create_list_of_commands(self, kwargs: dict[Any, Any]) -> list[CommandHandler]:
        return [self.create_command(key, value) for key, value in kwargs.items()]

    def create_msg(self, func: Callable) -> MessageHandler:
        return MessageHandler(filters=MessageHandler.FILTERS.text, callback=func)

    def create_list_of_msg_handlers(self, funcs: list[Callable]) -> list[MessageHandler]:
        return [self.create_msg(func) for func in funcs]

    def register_commands(self, kwargs: dict[Any, Any]) -> None:
        commands = self.create_list_of_commands(kwargs)
        self.add_list_of_handlers(commands)

    def register_message_handler(self, funcs: list[Callable]) -> None:
        msgs = self.create_list_of_msg_handlers(funcs)
        self.add_list_of_handlers(msgs)

    def _load_plugins(self) -> None:
        logfire.info("Loading plugins...")
        plugins_path = get_path("./plugins/commands")
        commands = load_plugins(plugins_path)
        logfire.info("Registering commands!")
        self.register_commands(commands)
        logfire.info("Commands added!")
