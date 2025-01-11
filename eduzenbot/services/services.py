import os
from collections.abc import Callable, Sequence
from functools import partial
from typing import Any

import logfire
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    InlineQueryHandler,
    MessageHandler,
    filters,
)

from eduzenbot.adapters.plugin_loader import load_plugins

here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)


async def send_msg_to_chatid(application: Application, chat_id: str, msg: str) -> None:
    """Sends a plain text message to a chat_id."""
    await application.bot.send_message(chat_id=chat_id, text=msg)


async def send_msg_to_eduzen(context: ContextTypes.DEFAULT_TYPE, eduzen_id: str, msg: str) -> None:
    """Sends a message to eduzen_id, also logs an info message."""
    logfire.info("Aviso a eduzen")
    await context.bot.send_message(chat_id=eduzen_id, text=msg)


def add_handler(application: Application, handler) -> None:
    """Wraps application.add_handler to keep it consistent with old usage."""
    application.add_handler(handler)


def add_list_of_handlers(application: Application, handlers: Sequence[CommandHandler | MessageHandler]) -> None:
    """Adds a list of handlers to the application."""
    for handler in handlers:
        add_handler(application, handler)


def create_command(name: str, func: Callable) -> CommandHandler:
    """Given a command name and its function, returns a CommandHandler."""
    return CommandHandler(name, func)


def create_inlinequery(func: Callable) -> InlineQueryHandler:
    """Given a function for inline queries, returns an InlineQueryHandler."""
    return InlineQueryHandler(func)


def create_list_of_commands(commands_dict: dict[Any, Any]) -> list[CommandHandler]:
    """
    Given a dictionary of command_name -> command_function,
    returns a list of CommandHandlers.
    """
    return [create_command(name, cmd_func) for name, cmd_func in commands_dict.items()]


def create_msg(func: Callable) -> MessageHandler:
    """Given a function for text messages, returns a MessageHandler."""
    return MessageHandler(filters.TEXT & ~filters.COMMAND, func)


def create_list_of_msg_handlers(funcs: list[Callable]) -> list[MessageHandler]:
    """Given a list of functions, returns a list of MessageHandlers."""
    return [create_msg(func) for func in funcs]


def register_commands(application: Application, commands_dict: dict[Any, Any]) -> None:
    """Registers a dictionary of command_name -> command_function as handlers."""
    commands = create_list_of_commands(commands_dict)
    add_list_of_handlers(application, commands)


def register_message_handler(application: Application, funcs: list[Callable]) -> None:
    """Registers multiple text message handlers."""
    msgs = create_list_of_msg_handlers(funcs)
    add_list_of_handlers(application, msgs)


def load_and_register_plugins(application: Application) -> None:
    """Load plugin commands from disk and register them with the Application."""
    logfire.info("Loading plugins...")
    plugins_path = get_path("plugins/commands")
    commands = load_plugins(plugins_path)

    logfire.info("Registering commands!")
    register_commands(application, commands)
    logfire.info("Commands added!")
