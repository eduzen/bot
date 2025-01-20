import calendar
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytz
from telegram import Chat, Update
from telegram import User as TelegramUser
from telegram.ext import CallbackContext

# Import your code. Adjust these paths as needed.
from eduzenbot.models import Report
from eduzenbot.plugins.commands.btc.command import (
    btc,
    get_crypto_report,
    melistock,
    show_daily_report,
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
    mock_chat = Chat(id="999", type="private")
    mock_update = AsyncMock(spec=Update)
    mock_update.effective_user = mock_user
    mock_update.effective_chat = mock_chat

    # 3. Mock get_all to return a known string
    #    Patch the import path to wherever your get_all is actually used.
    mocker.patch(
        "eduzenbot.plugins.commands.btc.command.get_all",
        new=AsyncMock(return_value="BTC info"),
    )

    # 4. Call the handler
    await btc(mock_update, mock_context)

    # 5. Assertions
    mock_bot.send_chat_action.assert_called_once_with(chat_id="999", action="typing")
    mock_bot.send_message.assert_called_once_with(chat_id="999", text="BTC info")


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
    mock_chat = AsyncMock(id="999", type="private")
    mock_update = AsyncMock(spec=Update)
    mock_update.effective_user = mock_user
    mock_update.effective_chat = mock_chat

    # 3. Patch get_crypto_report so we don't do real I/O
    fake_report_text = AsyncMock(return_value="Fake Daily Report")
    mocker.patch("eduzenbot.plugins.commands.btc.command.get_crypto_report", new=fake_report_text)

    # 4. Call daily_report
    await show_daily_report(mock_update, mock_context)

    # 5. Assertions
    mock_bot.send_chat_action.assert_called_once_with(chat_id="999", action="typing")
    mock_bot.send_message.assert_called_once_with(
        chat_id="999",
        text="Fake Daily Report",
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )


@pytest.mark.asyncio
async def test_get_crypto_report(mocker):
    """
    Test the get_crypto_report function directly by mocking its dependencies.
    """
    # Mock get_all, get_bluelytics, get_klima, and fetch_hackernews_stories
    crypto_mock = AsyncMock(return_value="CRYPTO DATA")
    dollar_mock = AsyncMock(return_value="DOLLAR DATA")
    mocker.patch("eduzenbot.plugins.commands.btc.command.get_all", new=crypto_mock)
    mocker.patch("eduzenbot.plugins.commands.btc.command.get_bluelytics", new=dollar_mock)
    mocker.patch(
        "eduzenbot.plugins.commands.btc.command.get_klima",
        new=AsyncMock(
            side_effect=[
                "Buenos Aires Weather",
                "Amsterdam Weather",
                "Dallas Weather",
            ]
        ),
    )
    hn_mock = AsyncMock(return_value="HN STORIES")
    mocker.patch("eduzenbot.plugins.commands.btc.command.fetch_hackernews_stories", new=hn_mock)

    tz = pytz.timezone("America/Argentina/Buenos_Aires")
    fake_now = datetime(2025, 1, 10, 10, 30, tzinfo=tz)

    mock_datetime = mocker.patch("eduzenbot.plugins.commands.btc.command.datetime")
    mock_datetime.now.return_value = fake_now

    text = await get_crypto_report(report=Report(chat_id=12345))

    assert "CRYPTO DATA" in text
    assert "DOLLAR DATA" in text
    assert "Buenos Aires Weather" in text
    assert "Amsterdam Weather" in text
    assert "Dallas Weather" in text
    assert "HN STORIES" in text

    assert "10 January del 2025" in text
    weekday_str = calendar.day_name[fake_now.weekday()]
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
