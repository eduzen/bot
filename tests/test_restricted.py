from unittest.mock import MagicMock

import pytest
from telegram import Update

from eduzenbot.auth.restricted import restricted


@pytest.mark.asyncio
async def test_restricted_unauthorized_is_async_safe(monkeypatch):
    monkeypatch.setenv("EDUZEN_ID", "42")

    # Build an Update with a different user id
    mock_update = MagicMock(spec=Update)
    mock_update.effective_user.id = 99
    mock_context = MagicMock()

    calls = {"count": 0}

    async def handler(update, context):
        calls["count"] += 1
        return "ran"

    wrapped = restricted(handler)

    # Should not raise when awaited; returns None and not call inner handler
    result = await wrapped(mock_update, mock_context)
    assert result is None
    assert calls["count"] == 0


@pytest.mark.asyncio
async def test_restricted_authorized_awaits_and_calls(monkeypatch):
    monkeypatch.setenv("EDUZEN_ID", "42")

    mock_update = MagicMock(spec=Update)
    mock_update.effective_user.id = 42
    mock_context = MagicMock()

    calls = {"count": 0}

    async def handler(update, context):
        calls["count"] += 1
        return "ran"

    wrapped = restricted(handler)

    result = await wrapped(mock_update, mock_context)
    assert result == "ran"
    assert calls["count"] == 1
