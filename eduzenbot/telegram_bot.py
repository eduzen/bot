import datetime
import logging
import os
import pkgutil
from collections.abc import Callable, Sequence
from functools import partial
from typing import Any

import attr
import pytz
from telegram import Update
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    InlineQueryHandler,
    MessageHandler,
    Updater,
)

from eduzenbot.models import Report
from eduzenbot.plugins.job_queue.alarms.command import alarm

logger = logging.getLogger("rich")

here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)


@attr.s(auto_attribs=True)
class TelegramBot:
    """Just a class for python-telegram-bot"""

    token: str
    eduzen_id: str = "3652654"
    polling: bool = False
    port: int = 80
    workers: int = 4
    use_context: bool = True

    def __attrs_post_init__(self) -> None:
        try:
            self.updater = Updater(
                token=self.token, workers=self.workers, use_context=self.use_context
            )
        except TelegramError as exc:
            logger.exception("Something went wrong...")
            raise SystemExit(exc.message)

        bot = self.updater.bot  # type: ignore
        logger.info(
            f"[bold green]Created updater for {bot.name}", extra={"markup": True}
        )
        self.updater.dispatcher.add_error_handler(self.error)  # type: ignore
        self._load_plugins()

    def start(self) -> None:
        if not self.polling:
            self.updater.start_polling()
        else:
            self.updater.start_webhook(
                listen="0.0.0.0", port=self.port, url_path=self.token
            )
            self.updater.bot.setWebhook(f"https://eduzenbot.herokuapp.com/{self.token}")  # type: ignore
        self.send_msg_to_eduzen("eduzenbot reiniciado!")
        self.configure_cronjobs()
        self.updater.idle()

    @staticmethod
    def error(update: Update, context: CallbackContext) -> None:
        """Log Errors caused by Updates."""
        try:
            raise context.error  # type: ignore
        except Unauthorized:
            # remove update.message.chat_id from conversation list
            logger.warning("Unauthorized error")
        except BadRequest:
            # handle malformed requests - read more below!
            logger.warning("Update caused a BadRequest")
            logger.debug(f"{context.error}")
        except TimedOut:
            # handle slow connection problems
            logger.warning("Update caused a TimedOut")
            logger.debug(f"{context.error}")
        except NetworkError:
            # handle other connection problems
            logger.warning("Update caused a NetworkError")
            logger.debug(f"{context.error}")
        except ChatMigrated:
            # the chat_id of a group has changed, use e.new_chat_id instead
            logger.warning("Update caused a ChatMigrated")
            logger.debug(f"{context.error}")
        except TelegramError:
            # handle all other telegram related errors
            logger.warning("Update caused a TelegramError")
            logger.debug(f"{context.error}")
        except Exception:
            logger.exception(f"Unhandled issue: {context.error}")

    def add_handler(self, handler) -> None:
        dispatcher = self.updater.dispatcher  # type: ignore
        dispatcher.add_handler(handler)

    def add_list_of_handlers(
        self, handlers: Sequence[CommandHandler | MessageHandler]
    ) -> None:
        for handler in handlers:
            self.add_handler(handler)

    def send_msg(self, msg: str) -> None:
        bot = self.updater.bot  # type: ignore
        bot.send_message(msg)

    def send_msg_to_chatid(self, chatid: str, msg: str) -> None:
        bot = self.updater.bot  # type: ignore
        bot.send_message(chatid, msg)

    def send_msg_to_eduzen(self, msg: str) -> None:
        logger.info("aviso a eduzen")
        self.send_msg_to_chatid(self.eduzen_id, msg)

    def configure_cronjobs(self) -> None:
        for report in Report.select():
            when = datetime.time(
                hour=report.hour,
                minute=report.min,
                tzinfo=pytz.timezone("Europe/Amsterdam"),
            )
            chat_id = report.chat_id
            job_queue = self.updater.job_queue  # type: ignore
            job_queue.run_daily(
                alarm, when, days=range(7), context=chat_id, name=str(chat_id)
            )
            msg = f"hey, I've just restarted. Remember that you have a crypto report everyday at {report.hour}."
            self.send_msg_to_chatid(chat_id, msg)
            self.send_msg_to_eduzen(f"Crypto report in Chat_id {report.chat_id}")

    def create_command(self, name: str, func: Callable) -> CommandHandler:
        return CommandHandler(
            name, func, pass_args=True, pass_chat_data=True, run_async=True
        )

    def create_command_args(
        self,
        name: str,
        func: Callable,
        pass_args=True,
        pass_job_queue=True,
        pass_chat_data=True,
    ) -> CommandHandler:
        return CommandHandler(
            name,
            func,
            pass_args=pass_args,
            pass_job_queue=pass_job_queue,
            pass_chat_data=pass_chat_data,
            run_async=True,
        )

    @staticmethod
    def create_inlinequery(func: Callable) -> InlineQueryHandler:
        return InlineQueryHandler(func)

    def create_list_of_commands(self, kwargs: dict[Any, Any]) -> list[CommandHandler]:
        return [self.create_command(key, value) for key, value in kwargs.items()]

    @staticmethod
    def create_msg(
        func: Callable, filters: Filters._Text = Filters.text
    ) -> MessageHandler:
        return MessageHandler(filters, func)

    def create_list_of_msg_handlers(
        self, funcs: list[Callable]
    ) -> list[MessageHandler]:
        return [self.create_msg(func) for func in funcs]

    def register_commands(self, kwargs: dict[Any, Any]) -> None:
        commands = self.create_list_of_commands(kwargs)
        self.add_list_of_handlers(commands)

    def register_message_handler(self, funcs: list[Callable]) -> None:
        msgs = self.create_list_of_msg_handlers(funcs)
        self.add_list_of_handlers(msgs)

    def _get_commands(self, plugin: dict[Any, Any]) -> dict[Any, Any]:
        plugins = {}
        for line in plugin.__doc__.strip().splitlines():  # type: ignore
            command = [substring.strip() for substring in line.strip().split("-")]
            plugins[command[0]] = getattr(plugin, command[1])
        return plugins

    def _find_modules(self, paths: list[str]) -> dict[str, Any]:
        plugins = {}
        for importer, package_name, _ in pkgutil.iter_modules(paths):
            plugin = importer.find_module(package_name).load_module(package_name)  # type: ignore
            if not plugin.__doc__:
                continue

            plugins.update(self._get_commands(plugin))  # type: ignore
        return plugins

    def _get_plugins(self) -> dict[Any, Any]:
        plugins = {}
        plugins_path = get_path("plugins/commands")

        for importer, package_name, _ in pkgutil.iter_modules([plugins_path]):
            logger.info(f"Loading {package_name}...")
            sub_modules = get_path(plugins_path, package_name)
            importer.find_module(package_name).load_module(package_name)  # type: ignore
            plugin_modules = self._find_modules([sub_modules])
            plugins.update(plugin_modules)

        return plugins

    def _load_plugins(self) -> None:
        logger.info("Loading plugins...")
        plugins = self._get_plugins()
        logger.info("Registering commands!")
        self.register_commands(plugins)
        logger.info("Commands added!")
