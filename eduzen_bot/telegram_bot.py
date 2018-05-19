import glob
import os
from pluginbase import PluginBase
import structlog

from telegram.ext import (
    CommandHandler, MessageHandler, Filters, InlineQueryHandler, Updater
)
from telegram.error import (
    TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError
)
from keys import TOKEN

logger = structlog.get_logger(filename=__name__)

PLUGINS_CMD_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "plugins/commands"
)


class TelegramBot(object):
    """Just a class for python-telegram-bot"""

    def __init__(self, workers=4):
        self.plugin_base = PluginBase(package="eduzen_bot.plugins")
        self.updater = Updater(token=TOKEN, workers=workers)
        logger.info("Created updater for %s" % (self.updater.bot.name))
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_error_handler(self.error)
        self._load_plugins()

    def start(self):
        self.updater.start_polling()
        self.updater.idle()

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        try:
            raise error

        except Unauthorized:
            # remove update.message.chat_id from conversation list
            logger.error("Update caused Unauthorized error")
        except BadRequest:
            # handle malformed requests - read more below!
            logger.error('Update "%s" caused error "%s"', (update, error))
        except TimedOut:
            # handle slow connection problems
            logger.warning('Update "%s" caused TimedOut "%s"', (update, error))
        except NetworkError:
            # handle other connection problems
            logger.error('Update "%s" caused error "%s"', (update, error))
        except ChatMigrated as e:
            # the chat_id of a group has changed, use e.new_chat_id instead
            logger.error('Update "%s" caused error "%s"', (update, error))
        except TelegramError:
            # handle all other telegram related errors
            logger.error('Update "%s" caused error "%s"', (update, error))

    def add_handler(self, handler):
        self.dispatcher.add_handler(handler)

    def add_list_of_handlers(self, handlers):
        for handler in handlers:
            self.add_handler(handler)

    def create_command(self, name, func):
        return CommandHandler(name, func, pass_args=True)

    def create_command_args(
        self, name, func, pass_args=True, pass_job_queue=True, pass_chat_data=True
    ):
        return CommandHandler(
            name,
            func,
            pass_args=pass_args,
            pass_job_queue=pass_job_queue,
            pass_chat_data=pass_chat_data,
        )

    def create_inlinequery(self, func):
        return InlineQueryHandler(func)

    def create_list_of_commands(self, kwargs):
        return [self.create_command(key, value) for key, value in kwargs.items()]

    def create_msg(self, func, filters=Filters.text):
        return MessageHandler(filters, func)

    def create_list_of_msg_handlers(self, args):
        return [self.create_msg(value) for value in args]

    def register_commands(self, kwargs):
        commands = self.create_list_of_commands(kwargs)
        self.add_list_of_handlers(commands)

    def register_message_handler(self, args):
        msgs = self.create_list_of_msg_handlers(args)
        self.add_list_of_handlers(msgs)

    def _get_plugins(self):
        plugins = {}
        for plugin_path in os.scandir(PLUGINS_CMD_PATH):
            if not (
                "pycache" not in plugin_path.path and "init" not in plugin_path.path
            ):
                continue

            logger.info(f"{plugin_path.path} found!")

            plugin_source = self.plugin_base.make_plugin_source(
                searchpath=[plugin_path.path]
            )

            plugin = plugin_source.load_plugin("command")
            if not plugin.__doc__:
                logger.info(f"Plugin.__doc__ not found!")
                continue

            for line in plugin.__doc__.strip().splitlines():
                command = [substring.strip() for substring in line.strip().split("-")]
                plugins[command[0]] = getattr(plugin, command[1])

        return plugins

    def _load_plugins(self):
        logger.info("Loading plugins...")
        plugins = self._get_plugins()
        logger.info(f"Registering commands!")
        self.register_commands(plugins)
