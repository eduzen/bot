import logging

from telegram.ext import CommandHandler
from telegram.ext import Updater
from keys import eduzenbot as TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


class TelegramBot(object):
    """docstring for TelegramBot"""

    def __init__(self):
        self.updater = Updater(token=TOKEN)
        logger.info("Created updater for %s", self.updater.bot.name)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_error_handler(self.error)

    def start(self):
        logger.info('starting')

        self.updater.start_polling()
        self.updater.idle()

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    def add_command(self, command):
        self.dispatcher.add_handler(command)

    def add_list_of_commands(self, commands):
        for command in commands:
            self.add_command(command)

    def create_command(self, name, func):
        return CommandHandler(name, func, pass_args=True)

    def create_list_of_commands(self, kwargs):
        commands = []
        for key, value in kwargs.items():
            commands.append(self.create_command(key, value))
        return commands

    def register_commands(self, kwargs):
        commands = self.create_list_of_commands(kwargs)
        self.add_list_of_commands(commands)
