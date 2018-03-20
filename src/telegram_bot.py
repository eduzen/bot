import logging

from telegram.ext import (
    CommandHandler, MessageHandler,
    Filters, InlineQueryHandler, Updater
)
from telegram.error import (
    TelegramError, Unauthorized, BadRequest,
    TimedOut, ChatMigrated, NetworkError
)
from keys import TOKEN

logger = logging.getLogger(__name__)


class TelegramBot(object):
    """Just a class for python-telegram-bot"""

    def __init__(self, workers=4):
        self.updater = Updater(token=TOKEN, workers=workers)
        logger.info("Created updater for %s", self.updater.bot.name)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_error_handler(self.error)

    def start(self):
        self.updater.start_polling()
        self.updater.idle()

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        try:
            raise error
        except Unauthorized:
            # remove update.message.chat_id from conversation list
            logger.error('Update caused Unauthorized error')
        except BadRequest:
            # handle malformed requests - read more below!
            logger.error('Update "%s" caused error "%s"', update, error)
        except TimedOut:
            # handle slow connection problems
            logger.warning('Update "%s" caused TimedOut "%s"', update, error)
        except NetworkError:
            # handle other connection problems
            logger.error('Update "%s" caused error "%s"', update, error)
        except ChatMigrated as e:
            # the chat_id of a group has changed, use e.new_chat_id instead
            logger.error('Update "%s" caused error "%s"', update, error)
        except TelegramError:
            # handle all other telegram related errors
            logger.error('Update "%s" caused error "%s"', update, error)

    def add_handler(self, handler):
        self.dispatcher.add_handler(handler)

    def add_list_of_handlers(self, handlers):
        for handler in handlers:
            self.add_handler(handler)

    def create_command(self, name, func):
        return CommandHandler(name, func, pass_args=True)

    def create_command_args(self, name, func, pass_args=True,
                            pass_job_queue=True, pass_chat_data=True):
        return CommandHandler(name, func, pass_args=pass_args, pass_job_queue=pass_job_queue,
                              pass_chat_data=pass_chat_data)

    def create_inlinequery(self, func):
        return InlineQueryHandler(func)

    def create_list_of_commands(self, kwargs):
        return [
            self.create_command(key, value)
            for key, value in kwargs.items()
        ]

    def create_msg(self, func, filters=Filters.text):
        return MessageHandler(filters, func)

    def create_list_of_msg_handlers(self, args):
        return [
            self.create_msg(value)
            for value in args
        ]

    def register_commands(self, kwargs):
        commands = self.create_list_of_commands(kwargs)
        self.add_list_of_handlers(commands)

    def register_message_handler(self, args):
        msgs = self.create_list_of_msg_handlers(args)
        self.add_list_of_handlers(msgs)
