from unittest.mock import MagicMock

import pytest
from telegram import Update

from eduzenbot.auth.restricted import restricted
from eduzenbot.decorators import create_user
from eduzenbot.models import EventLog, User


@pytest.mark.usefixtures("setup_db")
@pytest.mark.asyncio
async def test_restricted_then_create_user_does_not_create_records_for_unauthorized(monkeypatch):
    monkeypatch.setenv("EDUZEN_ID", "42")

    mock_update = MagicMock(spec=Update)
    mock_update.effective_user.id = 99
    mock_context = MagicMock()

    @restricted
    @create_user
    async def protected(update, context):
        return "ok"

    assert User.select().count() == 0
    assert EventLog.select().count() == 0

    result = await protected(mock_update, mock_context)

    # Unauthorized: no records created and returns None
    assert result is None
    assert User.select().count() == 0
    assert EventLog.select().count() == 0
