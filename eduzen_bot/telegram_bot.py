import datetime
import logging
import os
import pkgutil
from functools import partial

import attr
import pytz
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CommandHandler,
    Filters,
    InlineQueryHandler,
    MessageHandler,
    Updater,
)

from eduzen_bot.models import Report
from eduzen_bot.plugins.job_queue.alarms.command import alarm

logger = logging.getLogger("rich")

here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)


@attr.s(auto_attribs=True)
class TelegramBot:
    """Just a class for python-telegram-bot"""

    token: str
    eduzen_id: str = "3652654"
    heroku: int = 0
    port: int = 80
    workers: int = 4
    use_context: bool = True
    updater: Updater = None

    def __attrs_post_init__(self):
        try:
            self.updater = Updater(token=self.token, workers=self.workers, use_context=self.use_context)
        except TelegramError as exc:
            logger.exception("Something went wrong...")
            raise SystemExit(exc.message)

        logger.info("[bold green]Created updater for %s" % self.updater.bot.name, extra={"markup": True})
        self.updater.dispatcher.add_error_handler(self.error)
        self._load_plugins()

    def start(self):
        if not self.heroku:
            self.updater.start_polling()
        else:
            self.updater.start_webhook(listen="0.0.0.0", port=self.port, url_path=self.token)
            self.updater.bot.setWebhook(f"https://eduzenbot.herokuapp.com/{self.token}")
        self.send_msg_to_eduzen("eduzen_bot reiniciado!")
        self.configure_cronjobs()
        self.updater.idle()

    @staticmethod
    def error(update, context):
        """Log Errors caused by Updates."""
        try:
            raise context.error
        except Unauthorized:
            # remove update.message.chat_id from conversation list
            logger.error("Unauthorized error")
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

    def add_handler(self, handler):
        self.updater.dispatcher.add_handler(handler)

    def add_list_of_handlers(self, handlers):
        for handler in handlers:
            self.add_handler(handler)

    def send_msg(self, msg):
        self.updater.bot.send_message(msg)

    def send_msg_to_eduzen(self, msg):
        logger.info("aviso a eduzen")
        self.updater.bot.send_message(self.eduzen_id, msg)

    def configure_cronjobs(self):
        for report in Report.select():
            when = datetime.time(hour=report.hour, minute=report.min, tzinfo=pytz.timezone("Europe/Amsterdam"))
            chat_id = report.chat_id
            self.updater.job_queue.run_daily(alarm, when, days=range(7), context=chat_id, name=str(chat_id))
            msg = "hey, I'm just restarted. Remember that you have a crypto report" f" everyday at {report.hour}."
            self.updater.bot.send_message(chat_id, msg)
            self.updater.bot.send_message(self.eduzen_id, f"Crypto report in Chat_id {report.chat_id}")

    def create_command(self, name, func):
        return CommandHandler(name, func, pass_args=True, pass_chat_data=True, run_async=True)

    def create_command_args(self, name, func, pass_args=True, pass_job_queue=True, pass_chat_data=True):
        return CommandHandler(
            name,
            func,
            pass_args=pass_args,
            pass_job_queue=pass_job_queue,
            pass_chat_data=pass_chat_data,
            run_async=True,
        )

    @staticmethod
    def create_inlinequery(func):
        return InlineQueryHandler(func)

    def create_list_of_commands(self, kwargs):
        return [self.create_command(key, value) for key, value in kwargs.items()]

    @staticmethod
    def create_msg(func, filters=Filters.text):
        return MessageHandler(filters, func)

    def create_list_of_msg_handlers(self, args):
        return [self.create_msg(value) for value in args]

    def register_commands(self, kwargs):
        commands = self.create_list_of_commands(kwargs)
        self.add_list_of_handlers(commands)

    def register_message_handler(self, args):
        msgs = self.create_list_of_msg_handlers(args)
        self.add_list_of_handlers(msgs)

    def _get_commands(self, plugin):
        plugins = {}
        for line in plugin.__doc__.strip().splitlines():
            command = [substring.strip() for substring in line.strip().split("-")]
            plugins[command[0]] = getattr(plugin, command[1])
        return plugins

    def _get_plugins(self):
        plugins = {}
        plugins_path = get_path("plugins/commands")
        for importer, package_name, _ in pkgutil.iter_modules([plugins_path]):
            logger.info(f"Loading {package_name}...")
            sub_modules = get_path(plugins_path, package_name)
            importer.find_module(package_name).load_module(package_name)
            for importer, package_name, _ in pkgutil.iter_modules([sub_modules]):
                plugin = importer.find_module(package_name).load_module(package_name)
                if not plugin.__doc__:
                    continue

                plugins.update(self._get_commands(plugin))

        return plugins

    def _load_plugins(self):
        logger.info("Loading plugins...")
        plugins = self._get_plugins()
        logger.info("Registering commands!")
        self.register_commands(plugins)
        logger.info("Commands added!")
