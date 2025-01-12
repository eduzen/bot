# tests/test_decorators.py
from unittest.mock import MagicMock

import pytest
from telegram import Update
from telegram import User as TelegramUser
from telegram.ext import CallbackContext

from eduzenbot.decorators import create_user, get_or_create_user, log_event
from eduzenbot.models import EventLog
from eduzenbot.models import User as UserModel


@pytest.mark.usefixtures("setup_db")
class TestGetOrCreateUser:
    """
    Tests for the get_or_create_user function.
    """

    def test_create_new_user(self):
        # Mock a TelegramUser
        telegram_user = MagicMock(spec=TelegramUser)
        telegram_user.id = 12345
        telegram_user.username = "testuser"
        telegram_user.first_name = "Test"
        telegram_user.last_name = "User"
        telegram_user.is_bot = False
        telegram_user.language_code = "en"

        user_model = get_or_create_user(telegram_user)
        assert user_model is not None, "Should return a user model"
        assert user_model.id == 12345
        assert user_model.username == "testuser"
        assert user_model.first_name == "Test"
        assert user_model.last_name == "User"
        assert user_model.is_bot is False
        assert user_model.language_code == "en"

    def test_get_existing_user(self):
        # First, create a user in DB
        UserModel.create(
            id=12345,
            username="existing",
            first_name="Ex",
            last_name="Isting",
            is_bot=False,
            language_code="en",
        )

        # Mock a TelegramUser with updated info
        telegram_user = MagicMock(spec=TelegramUser)
        telegram_user.id = 12345
        telegram_user.username = "newusername"
        telegram_user.first_name = "NewName"
        telegram_user.last_name = "UpdatedLast"
        telegram_user.is_bot = True
        telegram_user.language_code = "es"

        # This should update the existing user
        user_model = get_or_create_user(telegram_user)
        assert user_model is not None, "Should return the existing user model"
        assert user_model.id == 12345
        # Confirm it updated fields
        assert user_model.username == "newusername"
        assert user_model.first_name == "NewName"
        assert user_model.last_name == "UpdatedLast"
        assert user_model.is_bot is True
        assert user_model.language_code == "es"


@pytest.mark.usefixtures("setup_db")
class TestLogEvent:
    """
    Tests for the log_event function.
    """

    def test_log_event_creates_record(self):
        user_model = UserModel.create(id=999, username="logger")
        assert EventLog.select().count() == 0

        log_event(user_model, command="test_command")
        assert EventLog.select().count() == 1
        event = EventLog.select().first()
        assert event.user == user_model
        assert event.command == "test_command"


@pytest.mark.usefixtures("setup_db")
class TestCreateUserDecorator:
    """
    Tests for the create_user decorator.
    """

    @pytest.mark.asyncio
    async def test_decorator_flow(self):
        """
        Test that the decorator:
          1. Creates a user if needed.
          2. Logs the event.
          3. Calls the decorated function.
        """
        # Setup a dummy Telegram Update and context
        mock_telegram_user = MagicMock(spec=TelegramUser)
        mock_telegram_user.id = 111
        mock_telegram_user.username = "decorated_user"
        mock_telegram_user.first_name = "Deco"
        mock_telegram_user.last_name = "Rated"
        mock_telegram_user.is_bot = False
        mock_telegram_user.language_code = "en"

        mock_update = MagicMock(spec=Update)
        mock_update.effective_user = mock_telegram_user

        mock_context = MagicMock(spec=CallbackContext)

        # Dummy async function to be decorated
        @create_user()
        async def dummy_handler(update, context):
            return "handler_called"

        # Confirm no users exist yet
        assert UserModel.select().count() == 0
        # Confirm no events exist yet
        assert EventLog.select().count() == 0

        # Call the decorated function
        result = await dummy_handler(mock_update, mock_context)

        # Check the decorated function actually returned
        assert result == "handler_called"

        # The user should now be created in the DB
        assert UserModel.select().count() == 1
        user_in_db = UserModel.select().first()
        assert user_in_db.username == "decorated_user"

        # The event log should also be created
        assert EventLog.select().count() == 1
        event_in_db = EventLog.select().first()
        assert event_in_db.user == user_in_db
        # The command is the name of the function
        assert event_in_db.command == "dummy_handler"

    @pytest.mark.asyncio
    async def test_decorator_unknown_user(self):
        """
        Test that if update.effective_user is None, it just logs a warning
        and calls the function without creating a user or event.
        """
        mock_update = MagicMock(spec=Update)
        mock_update.effective_user = None
        mock_context = MagicMock(spec=CallbackContext)

        @create_user()
        async def dummy_handler_no_user(update, context):
            return "handler_called_no_user"

        result = await dummy_handler_no_user(mock_update, mock_context)
        assert result == "handler_called_no_user"
        assert UserModel.select().count() == 0
        assert EventLog.select().count() == 0
