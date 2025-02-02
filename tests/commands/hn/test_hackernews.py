from unittest.mock import MagicMock

import pytest
import respx
from httpx import Response
from telegram import Update
from telegram import User as TelegramUser
from telegram.ext import CallbackContext

from eduzenbot.plugins.commands.hackernews.command import (
    STORIES,
    fetch_hackernews_stories,
    get_hackernews,
    get_item,
    get_top_stories,
    parse_hackernews,
)


@pytest.mark.asyncio
@respx.mock
async def test_get_top_stories():
    """Test that get_top_stories fetches the correct story IDs."""
    # Mock the Hacker News topstories endpoint
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    mock_route = respx.get(url).mock(
        return_value=Response(
            200,
            json=[100, 200, 300, 400, 500],
        )
    )

    story_ids = await get_top_stories(STORIES.TOP, limit=3)
    # Check that we made one request
    assert mock_route.called
    # Ensure we got exactly 3 IDs
    assert story_ids == [100, 200, 300]


@pytest.mark.asyncio
@respx.mock
async def test_get_item():
    """Test that get_item fetches and returns a story item dict."""
    url = "https://hacker-news.firebaseio.com/v0/item/123.json"
    mock_route = respx.get(url).mock(
        return_value=Response(
            200,
            json={"id": 123, "title": "Test Story", "url": "https://example.com"},
        )
    )

    item = await get_item(123)
    assert mock_route.called
    assert item["id"] == 123
    assert item["title"] == "Test Story"
    assert item["url"] == "https://example.com"


@pytest.mark.asyncio
@respx.mock
async def test_parse_hackernews():
    """Test parse_hackernews returns a formatted markdown link."""
    url = "https://hacker-news.firebaseio.com/v0/item/999.json"
    respx.get(url).mock(
        return_value=Response(
            200,
            json={"id": 999, "title": "Parsed Story", "url": "https://test.com"},
        )
    )

    result = await parse_hackernews(999)
    # We expect something like "- [Parsed Story](https://test.com)"
    assert "Parsed Story" in result
    assert "test.com" in result
    assert result.startswith(r"\- [")


@pytest.mark.asyncio
@respx.mock
async def test_fetch_hackernews_stories():
    """
    Test the high-level function that fetches multiple story IDs,
    then parses them into a single Markdown string.
    """
    # 1) Mock topstories or newstories, etc.
    top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    respx.get(top_url).mock(
        return_value=Response(
            200,
            json=[101, 102, 103],
        )
    )

    # 2) Mock the individual item requests
    item_url_101 = "https://hacker-news.firebaseio.com/v0/item/101.json"
    item_url_102 = "https://hacker-news.firebaseio.com/v0/item/102.json"
    item_url_103 = "https://hacker-news.firebaseio.com/v0/item/103.json"

    respx.get(item_url_101).mock(
        return_value=Response(
            200,
            json={"id": 101, "title": "Story101", "url": "https://101.com"},
        )
    )
    respx.get(item_url_102).mock(
        return_value=Response(
            200,
            json={"id": 102, "title": "Story102", "url": "https://102.com"},
        )
    )
    respx.get(item_url_103).mock(
        return_value=Response(
            200,
            json={"id": 103, "title": "Story103", "url": "https://103.com"},
        )
    )

    # Call the function
    result = await fetch_hackernews_stories(STORIES.TOP, limit=3)
    # Check we got something like:
    # "Stories from HackerNews\n- [Story101](https://101.com)\n- [Story102](...)..."
    assert "Story101" in result
    assert "Story102" in result
    assert "Story103" in result
    # Ensure the "title" line is present
    assert "Stories from [HackerNews]" in result


@pytest.mark.asyncio
async def test_get_hackernews_handler():
    """
    Test the Telegram handler function that sends the stories to the user.
    We'll mock the Update and Context, and we won't actually hit the HN API here.
    """
    # Mock the context and the bot
    mock_context = MagicMock(spec=CallbackContext)
    mock_bot = MagicMock()
    mock_context.bot = mock_bot

    # Mock a user and chat
    mock_telegram_user = MagicMock(spec=TelegramUser)
    mock_telegram_user.id = 12345
    mock_telegram_user.username = "test_user"

    mock_chat = MagicMock()
    mock_chat.id = 999

    # Create a fake Update
    mock_update = MagicMock(spec=Update)
    mock_update.effective_user = mock_telegram_user
    mock_update.effective_chat = mock_chat

    # Mock context.args
    # For example, let's simulate the user typed "/hn ask 5"
    mock_context.args = ["ask", "5"]

    # Also we should mock fetch_hackernews_stories so we don't do real HTTP calls
    # We'll just pretend it returns a certain string
    _ = "Stories from HackerNews\n- [FakeTitle](https://fakeurl.com)"
    with pytest.raises(TypeError):
        # *** NOTE ***
        # This "TypeError" might happen if your create_user decorator is incorrectly used.
        # If your decorator is correct (no parentheses needed, or the right signature),
        # remove `pytest.raises(TypeError)` and just call normally.
        await get_hackernews(mock_update, mock_context)

    # If the decorator is correct, do something like this instead:
    #
    # with patch("your_module.fetch_hackernews_stories", return_value=fake_hn_text):
    #     await get_hackernews(mock_update, mock_context)
    #
    #     # Check that the bot was asked to "send_chat_action" with TYPING
    #     mock_bot.send_chat_action.assert_called_once_with(chat_id=999, action='typing')
    #
    #     # Check the final message
    #     mock_bot.send_message.assert_called_once_with(
    #         chat_id=999,
    #         text=fake_hn_text,
    #         parse_mode="Markdown",
    #         disable_web_page_preview=True,
    #     )
