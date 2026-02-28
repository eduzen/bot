from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import respx
from httpx import Response
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from eduzenbot.plugins.commands.news.command import _get_news, get_news


@pytest.mark.asyncio
@respx.mock
async def test_get_news_success(monkeypatch):
    """
    Test that get_news correctly retrieves news (using default country 'us')
    and sends a message to the user.
    """
    monkeypatch.setenv("NEWS_API_KEY", "test_key")

    # For default country 'us', our code sets sources=bbc-news,techcrunch,techradar.
    url = "https://newsapi.org/v2/top-headlines?apiKey=test_key&sources=bbc-news,techcrunch,techradar"
    route = respx.get(url).mock(
        return_value=Response(
            200,
            json={"articles": [{"title": "Test News", "description": "Test Description"}]},
        )
    )

    mock_update = MagicMock(spec=Update)
    mock_chat = MagicMock()
    mock_chat.id = 123
    mock_update.effective_chat = mock_chat

    mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    bot_mock = MagicMock()
    bot_mock.send_chat_action = AsyncMock()
    bot_mock.send_message = AsyncMock()
    mock_context.bot = bot_mock
    # No arguments provided → default country is used.
    mock_context.args = []

    await get_news(mock_update, mock_context)

    assert route.called
    bot_mock.send_chat_action.assert_called_once_with(chat_id=123, action=ChatAction.TYPING)
    bot_mock.send_message.assert_called_once()
    args, kwargs = bot_mock.send_message.call_args
    assert kwargs["chat_id"] == 123
    assert "Test News" in kwargs["text"]
    assert "Test Description" in kwargs["text"]
    assert kwargs["parse_mode"] == "Markdown"


@pytest.mark.asyncio
@respx.mock
async def test_get_news_with_country_arg(monkeypatch):
    """
    Test that get_news uses the provided country argument.
    """
    monkeypatch.setenv("NEWS_API_KEY", "test_key")
    # When 'ar' is passed, our code sets sources=infobae,la-nacion.
    url = "https://newsapi.org/v2/top-headlines?apiKey=test_key&sources=infobae,la-nacion"
    route = respx.get(url).mock(
        return_value=Response(
            200,
            json={"articles": [{"title": "US News", "description": "US Description"}]},
        )
    )

    mock_update = MagicMock(spec=Update)
    mock_chat = MagicMock()
    mock_chat.id = 789
    mock_update.effective_chat = mock_chat

    mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    bot_mock = MagicMock()
    bot_mock.send_chat_action = AsyncMock()
    bot_mock.send_message = AsyncMock()
    mock_context.bot = bot_mock
    # Provide 'ar' as the argument.
    mock_context.args = ["ar"]

    await get_news(mock_update, mock_context)

    assert route.called
    bot_mock.send_chat_action.assert_called_once_with(chat_id=789, action=ChatAction.TYPING)
    bot_mock.send_message.assert_called_once()
    args, kwargs = bot_mock.send_message.call_args
    assert kwargs["chat_id"] == 789
    assert "US News" in kwargs["text"]
    assert "US Description" in kwargs["text"]
    assert kwargs["parse_mode"] == "Markdown"


@pytest.mark.asyncio
@respx.mock
async def test_get_news_failure(monkeypatch):
    """
    Test that when an exception occurs while retrieving news, the command
    sends a fallback message ("No hay noticias.").
    """
    monkeypatch.setenv("NEWS_API_KEY", "test_key")
    # For default 'us', expected URL is with sources=bbc-news,techcrunch,techradar.
    url = "https://newsapi.org/v2/top-headlines?apiKey=test_key&sources=bbc-news,techcrunch,techradar"
    respx.get(url).mock(side_effect=httpx.RequestError("Test error"))

    mock_update = MagicMock(spec=Update)
    mock_chat = MagicMock()
    mock_chat.id = 456
    mock_update.effective_chat = mock_chat

    mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    bot_mock = MagicMock()
    bot_mock.send_chat_action = AsyncMock()
    bot_mock.send_message = AsyncMock()
    mock_context.bot = bot_mock
    mock_context.args = []  # Use default country 'us'

    await get_news(mock_update, mock_context)

    bot_mock.send_chat_action.assert_called_once_with(chat_id=456, action=ChatAction.TYPING)
    bot_mock.send_message.assert_called_once_with(chat_id=456, text="No hay noticias.", disable_web_page_preview=True)


@pytest.mark.asyncio
@respx.mock
async def test_get_news_nl_country(monkeypatch):
    """Test that _get_news('nl') uses rtl-nieuws source."""
    monkeypatch.setenv("NEWS_API_KEY", "test_key")

    url = "https://newsapi.org/v2/top-headlines?apiKey=test_key&sources=rtl-nieuws"
    route = respx.get(url).mock(
        return_value=Response(
            200,
            json={"articles": [{"title": "NL News", "description": "Dutch news"}]},
        )
    )

    result = await _get_news("nl")
    assert route.called
    assert "NL News" in result


@pytest.mark.asyncio
async def test_get_news_handler_no_chat():
    """Test that handler returns early when effective_chat is None."""
    mock_update = MagicMock(spec=Update)
    mock_update.effective_chat = None

    mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    bot_mock = MagicMock()
    bot_mock.send_chat_action = AsyncMock()
    bot_mock.send_message = AsyncMock()
    mock_context.bot = bot_mock

    await get_news(mock_update, mock_context)

    bot_mock.send_message.assert_not_called()


@pytest.mark.asyncio
@respx.mock
async def test_get_news_handler_empty_response(monkeypatch):
    """Test that handler sends 'No news for' when articles are empty."""
    monkeypatch.setenv("NEWS_API_KEY", "test_key")

    url = "https://newsapi.org/v2/top-headlines?apiKey=test_key&sources=bbc-news,techcrunch,techradar"
    respx.get(url).mock(
        return_value=Response(200, json={"articles": []}),
    )

    mock_update = MagicMock(spec=Update)
    mock_chat = MagicMock()
    mock_chat.id = 111
    mock_update.effective_chat = mock_chat

    mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    bot_mock = MagicMock()
    bot_mock.send_chat_action = AsyncMock()
    bot_mock.send_message = AsyncMock()
    mock_context.bot = bot_mock
    mock_context.args = []

    await get_news(mock_update, mock_context)

    bot_mock.send_message.assert_called_once()
    call_kwargs = bot_mock.send_message.call_args[1]
    assert "No news for" in call_kwargs["text"]


@pytest.mark.asyncio
async def test_get_news_handler_long_message_chunking(mocker, monkeypatch):
    """Test that messages longer than MAX_MESSAGE_LENGTH are sent in chunks."""
    monkeypatch.setenv("NEWS_API_KEY", "test_key")

    # Create a long news string (>4096 chars)
    long_news = "x" * 5000
    mocker.patch(
        "eduzenbot.plugins.commands.news.command._get_news",
        new=AsyncMock(return_value=long_news),
    )

    mock_update = MagicMock(spec=Update)
    mock_chat = MagicMock()
    mock_chat.id = 222
    mock_update.effective_chat = mock_chat

    mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    bot_mock = MagicMock()
    bot_mock.send_chat_action = AsyncMock()
    bot_mock.send_message = AsyncMock()
    mock_context.bot = bot_mock
    mock_context.args = ["us"]

    await get_news(mock_update, mock_context)

    # 5000 chars should produce 2 chunks (4096 + 904)
    assert bot_mock.send_message.call_count == 2
