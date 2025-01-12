from collections.abc import Callable
from functools import wraps
from typing import Any

import logfire
import peewee
from telegram import Update
from telegram import User as TelegramUser
from telegram.ext import ContextTypes

from eduzenbot.models import EventLog
from eduzenbot.models import User as UserModel


def get_or_create_user(telegram_user: TelegramUser) -> UserModel | None:
    """
    Retrieves an existing user or creates a new one if not found.

    Args:
        telegram_user (TelegramUser): The user object from Python Telegram Bot.

    Returns:
        Optional[UserModel]: The retrieved or newly created user, or None if an error occurred.
    """
    try:
        # Prepare default data from the Telegram user object
        data = {
            "username": telegram_user.username or str(telegram_user.id),
            "first_name": telegram_user.first_name,
            "last_name": telegram_user.last_name,
            "is_bot": telegram_user.is_bot,
            "language_code": telegram_user.language_code,
        }

        # Attempt to get or create the user in the DB
        user_model, created = UserModel.get_or_create(
            id=telegram_user.id,
            defaults=data,
        )

        # If the user already existed, you can optionally update fields
        # in case they changed their username or other info
        if not created:
            user_model.username = data["username"]
            user_model.first_name = data["first_name"]
            user_model.last_name = data["last_name"]
            user_model.is_bot = data["is_bot"]
            user_model.language_code = data["language_code"]
            user_model.save()

        return user_model

    except peewee.IntegrityError as exc:
        logfire.exception(
            "IntegrityError occurred while creating or retrieving user.",
            extra={"telegram_id": telegram_user.id, "error": str(exc)},
        )
    except peewee.PeeweeException as exc:
        logfire.exception(
            "Database error in 'get_or_create_user'.", extra={"telegram_id": telegram_user.id, "error": str(exc)}
        )
    return None


def log_event(user_model: UserModel, command: str) -> None:
    """
    Logs the execution of a command by a user.

    Args:
        user_model (UserModel): The user who executed the command.
        command (str): The command executed.
    """
    try:
        EventLog.create(user=user_model, command=command)
    except peewee.PeeweeException as exc:
        logfire.exception(
            "Database error while logging the event.",
            extra={"user_id": user_model.id, "command": command, "error": str(exc)},
        )


def create_user(func: Callable) -> Callable:
    """
    Decorator factory to ensure a user is created in the database and logs the command execution.

    Returns:
        A decorator which wraps the Telegram handler function.
    """

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: Any, **kwargs: Any) -> Any:
        command = func.__name__

        user_data = update.effective_user
        if not user_data:
            logfire.warn(f"{command} executed by an unknown user.")
            return await func(update, context, *args, **kwargs)

        try:
            user_model = get_or_create_user(user_data)
            if not user_model:
                logfire.error(f"Error creating user: {user_data}")
                return

            log_event(user_model, command=command)
            logfire.info(f"{command} executed by {user_model.username or user_model.id}")

        except peewee.PeeweeException as db_exc:
            logfire.exception(
                "Database error occurred in 'create_user' decorator.",
                extra={"user_data": user_data.to_dict(), "command": command, "error": str(db_exc)},
            )
        except Exception as exc:
            logfire.exception(
                "Unexpected error occurred in 'create_user' decorator.",
                extra={"user_data": user_data.to_dict(), "command": command, "error": str(exc)},
            )

        return await func(update, context, *args, **kwargs)

    return wrapper
