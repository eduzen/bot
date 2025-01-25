from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from eduzenbot.plugins.commands.btc.api import (
    client,
    fetch_and_process,
    process_all,
    process_dogecoin,
    process_eth,
)


@pytest.mark.asyncio
@patch.object(client, "get")
async def test_fetch_and_process_success(mock_get):
    """Should call process_func and return its result when status_code=200."""
    # 1) Mock the response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    # 2) Define a simple process_func
    def mock_process_func(response: httpx.Response) -> str:
        return "processed data"

    result = await fetch_and_process("https://example.com", mock_process_func)
    assert result == "processed data"
    mock_get.assert_awaited_once_with("https://example.com")


@pytest.mark.asyncio
@patch.object(client, "get")
async def test_fetch_and_process_non_200(mock_get):
    """Should return fallback message if response is not 200."""
    mock_response = AsyncMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    # process_func that would raise if it got called
    mock_process_func = MagicMock(return_value="should not see this")

    result = await fetch_and_process("https://example.com", mock_process_func)
    assert result == "Perdón! No hay ninguna api disponible!"
    mock_process_func.assert_not_called()  # process_func not called on error


@pytest.mark.asyncio
@patch.object(client, "get")
async def test_fetch_and_process_http_error(mock_get):
    """Should return fallback message if an HTTPError is raised."""
    mock_get.side_effect = httpx.HTTPError("Connection failed")

    mock_process_func = MagicMock(return_value="not reachable")

    result = await fetch_and_process("https://example.com", mock_process_func)
    assert result == "Perdón! No hay ninguna api disponible!"
    mock_process_func.assert_not_called()


def test_process_eth_success():
    """Should parse USD/EUR data and return formatted ETH string."""
    response = MagicMock(spec=httpx.Response)
    response.json.return_value = {"USD": 2000.0, "EUR": 1900.0}

    result = process_eth(response)
    assert result == "⧫ 1 eth == USD 2000.0 💵 | EUR 1900.0 🇪🇺"


def test_process_eth_error():
    """Should return fallback text if JSON is invalid or missing keys."""
    response = MagicMock(spec=httpx.Response)
    # Force an exception in response.json()
    response.json.side_effect = ValueError("Invalid JSON")

    result = process_eth(response)
    assert result == "Perdón! No hay ninguna api disponible!"


def test_process_dogecoin_success():
    """Should parse dogecoin price and return the correct string."""
    response = MagicMock(spec=httpx.Response)
    response.json.return_value = {"data": {"prices": [{"price": "0.25"}]}}

    result = process_dogecoin(response)
    assert result == "🐶 1 dogecoin == USD 0.25 💵"


def test_process_dogecoin_error():
    """Should return fallback text if data is malformed."""
    response = MagicMock(spec=httpx.Response)
    response.json.side_effect = KeyError("missing 'prices'")

    result = process_dogecoin(response)
    assert result == "Perdón! No hay ninguna api disponible!"


def test_process_all_success():
    """Should parse multiple coin prices and return formatted multi-line string."""
    response = MagicMock(spec=httpx.Response)
    response.json.return_value = {
        "bitcoin": {"usd": 30000.0},
        "ethereum": {"usd": 2000.0},
        "solana": {"usd": 100.0},
        "cardano": {"usd": 0.5},
    }

    result = process_all(response)
    assert "₿ 1 btc == USD 30000.0" in result
    assert "⧫ 1 eth == USD 2000.0" in result
    assert "☀️ 1 sol == USD 100.0" in result
    assert "🧚‍♀️ 1 ada == USD 0.5" in result


def test_process_all_error():
    """Should return fallback text if JSON is invalid."""
    response = MagicMock(spec=httpx.Response)
    response.json.side_effect = KeyError("missing data")

    result = process_all(response)
    assert result == "Perdón! No hay ninguna api disponible!"
