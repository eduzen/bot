import logging

from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import Updater
from keys import TOKEN

logger = logging.getLogger(__name__)


class TelegramBot(object):
    """Just a class for python-telegram-bot"""

    def __init__(self):
        self.updater = Updater(token=TOKEN)
        logger.info("Created updater for %s", self.updater.bot.name)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_error_handler(self.error)

    def start(self):
        self.updater.start_polling()
        self.updater.idle()

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    def add_handler(self, handler):
        self.dispatcher.add_handler(handler)

    def add_list_of_handlers(self, handlers):
        for handler in handlers:
            self.add_command(handler)

    def create_command(self, name, func):
        return CommandHandler(name, func, pass_args=True)

    def create_list_of_commands(self, kwargs):
        return [
            self.create_command(key, value)
            for key, value in kwargs.items()
        ]

    def create_msg(self, name, func):
        return MessageHandler(name, func, pass_args=True)

    def create_list_of_msg_handlers(self, kwargs):
        return [
            self.create_msg(key, value)
            for key, value in kwargs.items()
        ]

    def register_commands(self, kwargs):
        commands = self.create_list_of_commands(kwargs)
        self.add_list_of_handlers(commands)

    def register_message_handler(self, kwargs):
        msgs = self.create_list_of_msg_handlers(kwargs)
        self.add_list_of_handlers(msgs)
