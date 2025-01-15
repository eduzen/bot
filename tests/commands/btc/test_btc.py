import calendar
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytz
from telegram import Chat, Update
from telegram import User as TelegramUser
from telegram.ext import CallbackContext

# Import your code. Adjust these paths as needed.
from eduzenbot.plugins.commands.btc.command import (
    btc,
    daily_report,
    get_crypto_report,
    melistock,
)

# If you have them in separate modules:


@pytest.mark.asyncio
async def test_btc_handler(mocker):
    """
    Test the btc command handler. We will mock `get_all` so we don't do real I/O.
    """
    # 1. Mock the context and the bot
    mock_context = AsyncMock(spec=CallbackContext)
    mock_bot = AsyncMock()
    mock_context.bot = mock_bot

    # 2. Mock the update with a user and a chat
    mock_user = TelegramUser(id=12345, first_name="TestUser", is_bot=False)
    mock_chat = Chat(id=999, type="private")
    mock_update = AsyncMock(spec=Update)
    mock_update.effective_user = mock_user
    mock_update.effective_chat = mock_chat

    # 3. Mock get_all to return a known string
    #    Patch the import path to wherever your get_all is actually used.
    mocker.patch("eduzenbot.plugins.commands.btc.command.get_all", return_value="BTC info")

    # 4. Call the handler
    await btc(mock_update, mock_context)

    # 5. Assertions
    mock_bot.send_chat_action.assert_called_once_with(chat_id=999, action="typing")
    mock_bot.send_message.assert_called_once_with(chat_id=999, text="BTC info")


@pytest.mark.asyncio
async def test_daily_report_handler(mocker):
    """
    Test the daily_report command handler. We'll mock out all the async calls in get_crypto_report
    so it returns a known string.
    """
    # 1. Mock the context and the bot
    mock_context = AsyncMock(spec=CallbackContext)
    mock_bot = AsyncMock()
    mock_context.bot = mock_bot

    # 2. Mock the update
    mock_user = TelegramUser(id=12345, first_name="TestUser", is_bot=False)
    mock_chat = AsyncMock(id=999, type="private")
    mock_update = AsyncMock(spec=Update)
    mock_update.effective_user = mock_user
    mock_update.effective_chat = mock_chat

    # 3. Patch get_crypto_report so we don't do real I/O
    fake_report_text = "Fake Daily Report"
    mocker.patch("eduzenbot.plugins.commands.btc.command.get_crypto_report", return_value=fake_report_text)

    # 4. Call daily_report
    await daily_report(mock_update, mock_context)

    # 5. Assertions
    mock_bot.send_chat_action.assert_called_once_with(chat_id=999, action="typing")
    mock_bot.send_message.assert_called_once_with(
        chat_id=999,
        text=fake_report_text,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )


@pytest.mark.asyncio
async def test_get_crypto_report(mocker):
    """
    Test the get_crypto_report function directly by mocking its dependencies.
    """
    # Mock get_all, get_bluelytics, get_klima, and fetch_hackernews_stories
    mocker.patch("eduzenbot.plugins.commands.btc.command.get_all", return_value="CRYPTO DATA")
    mocker.patch("eduzenbot.plugins.commands.btc.command.get_bluelytics", return_value="DOLLAR DATA")
    mocker.patch(
        "eduzenbot.plugins.commands.btc.command.get_klima",
        side_effect=[
            "Buenos Aires Weather",
            "Amsterdam Weather",
            "Dallas Weather",
        ],
    )
    mocker.patch("eduzenbot.plugins.commands.btc.command.fetch_hackernews_stories", return_value="HN STORIES")

    # Also control the current date/time so we can assert the formatting
    tz = pytz.timezone("America/Argentina/Buenos_Aires")
    fake_now = datetime(2025, 1, 10, 10, 30, tzinfo=tz)
    mocker.patch("eduzenbot.plugins.commands.btc.command.datetime")

    # Call the function
    text = await get_crypto_report()

    # Validate pieces are in the returned string
    # e.g., "CRYPTO DATA", "DOLLAR DATA", "Buenos Aires Weather", "HN STORIES", etc.
    assert "CRYPTO DATA" in text
    assert "DOLLAR DATA" in text
    assert "Buenos Aires Weather" in text
    assert "Amsterdam Weather" in text
    assert "Dallas Weather" in text
    assert "HN STORIES" in text

    # Confirm the date formatting is used
    assert "10 January del 2025" in text  # or check the actual localized string
    # Confirm day name
    weekday_str = calendar.day_name[fake_now.weekday()]  # e.g., "Friday"
    assert weekday_str in text


def test_melistock(mocker):
    """
    Test the melistock function by mocking yfinance Ticker.
    """
    # Patch yfinance.Ticker object
    fake_ticker = MagicMock()
    fake_ticker.info = {
        "shortName": "Fake Stock Inc.",
        "regularMarketPrice": 123.45,
        "market": "NYSE",
        "fiftyDayAverage": 120.0,
    }
    mocker.patch("eduzenbot.plugins.commands.btc.command.yfinance.Ticker", return_value=fake_ticker)

    text = melistock("FAKE")
    assert "Fake Stock Inc." in text
    assert "U$D 123.45" in text
    assert "NYSE" in text
    assert "55 days average price U$D 120.0" in text


def test_melistock_error(mocker):
    """
    Test melistock handles exceptions gracefully.
    """
    mocker.patch("eduzenbot.plugins.commands.btc.command.yfinance.Ticker", side_effect=Exception("Oops"))
    text = melistock("BADSTOCK")
    assert "No encontramos nada con 'BADSTOCK'" in text
