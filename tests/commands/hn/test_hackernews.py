from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import respx
from httpx import Response
from telegram import Chat, Update
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
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    mock_route = respx.get(url).mock(
        return_value=Response(
            200,
            json=[100, 200, 300, 400, 500],
        )
    )

    story_ids = await get_top_stories(STORIES.TOP, limit=3)
    assert mock_route.called
    assert story_ids == [100, 200, 300]


@pytest.mark.asyncio
async def test_get_top_stories_invalid_type():
    """Test that passing an invalid story type raises ValueError."""
    with pytest.raises(ValueError, match="Invalid story type"):
        await get_top_stories("not_a_valid_type")


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
    """Test parse_hackernews returns a formatted markdown link (v2)."""
    url = "https://hacker-news.firebaseio.com/v0/item/999.json"
    respx.get(url).mock(
        return_value=Response(
            200,
            json={"id": 999, "title": "Parsed Story", "url": "https://test.com"},
        )
    )

    result = await parse_hackernews(999)
    assert "Parsed Story" in result
    assert "test.com" in result
    assert result.startswith(r"\- [")


@pytest.mark.asyncio
@respx.mock
async def test_parse_hackernews_md_v1():
    """Test parse_hackernews with md_version=1 uses '- ' prefix."""
    url = "https://hacker-news.firebaseio.com/v0/item/888.json"
    respx.get(url).mock(
        return_value=Response(
            200,
            json={"id": 888, "title": "V1 Story", "url": "https://v1.com"},
        )
    )

    result = await parse_hackernews(888, md_version=1)
    assert result.startswith("- [")
    assert "V1 Story" in result


@pytest.mark.asyncio
@respx.mock
async def test_parse_hackernews_no_url():
    """Test parse_hackernews when item has no url key."""
    url = "https://hacker-news.firebaseio.com/v0/item/777.json"
    respx.get(url).mock(
        return_value=Response(
            200,
            json={"id": 777, "title": "Ask HN: Something"},
        )
    )

    result = await parse_hackernews(777)
    assert "Ask HN" in result
    # No URL means no markdown link, just the title
    assert "(" not in result


@pytest.mark.asyncio
@respx.mock
async def test_fetch_hackernews_stories():
    """Test the high-level function that fetches and formats stories."""
    top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    respx.get(top_url).mock(return_value=Response(200, json=[101, 102, 103]))

    for sid, title in [(101, "Story101"), (102, "Story102"), (103, "Story103")]:
        respx.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json").mock(
            return_value=Response(200, json={"id": sid, "title": title, "url": f"https://{sid}.com"})
        )

    result = await fetch_hackernews_stories(STORIES.TOP, limit=3)
    assert "Story101" in result
    assert "Story102" in result
    assert "Story103" in result
    assert "Stories from [HackerNews]" in result


@pytest.mark.asyncio
@respx.mock
async def test_fetch_hackernews_stories_with_failing_item():
    """Test that a failing individual item is gracefully skipped."""
    top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    respx.get(top_url).mock(return_value=Response(200, json=[201, 202]))

    # First item succeeds
    respx.get("https://hacker-news.firebaseio.com/v0/item/201.json").mock(
        return_value=Response(200, json={"id": 201, "title": "Good Story", "url": "https://good.com"})
    )
    # Second item fails
    respx.get("https://hacker-news.firebaseio.com/v0/item/202.json").mock(
        side_effect=httpx.RequestError("Connection failed")
    )

    result = await fetch_hackernews_stories(STORIES.TOP, limit=2)
    assert "Good Story" in result
    # Should not crash, just skip the failed item


@pytest.mark.asyncio
async def test_get_hackernews_handler(mocker):
    """Test the Telegram handler sends stories to the user."""
    mock_context = AsyncMock(spec=CallbackContext)
    mock_bot = AsyncMock()
    mock_context.bot = mock_bot

    mock_user = TelegramUser(id=12345, first_name="TestUser", is_bot=False)
    mock_chat = Chat(id=999, type="private")

    mock_update = AsyncMock(spec=Update)
    mock_update.effective_user = mock_user
    mock_update.effective_chat = mock_chat

    mock_context.args = ["ask"]

    fake_hn_text = "Stories from HackerNews\n- [FakeTitle](https://fakeurl.com)"
    mocker.patch(
        "eduzenbot.plugins.commands.hackernews.command.fetch_hackernews_stories",
        new=AsyncMock(return_value=fake_hn_text),
    )

    await get_hackernews(mock_update, mock_context)

    mock_bot.send_chat_action.assert_called_once()
    mock_bot.send_message.assert_called_once()
    call_kwargs = mock_bot.send_message.call_args[1]
    assert call_kwargs["chat_id"] == 999
    assert "FakeTitle" in call_kwargs["text"]


@pytest.mark.asyncio
async def test_get_hackernews_handler_no_chat():
    """Test handler returns early when effective_chat is None."""
    mock_update = MagicMock(spec=Update)
    mock_update.effective_chat = None

    mock_context = AsyncMock(spec=CallbackContext)
    mock_bot = AsyncMock()
    mock_context.bot = mock_bot

    await get_hackernews(mock_update, mock_context)

    mock_bot.send_message.assert_not_called()
