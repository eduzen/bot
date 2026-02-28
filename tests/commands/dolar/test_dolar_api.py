from unittest.mock import MagicMock

import httpx
import pytest

from eduzenbot.plugins.commands.dolar.api import (
    _extract,
    _process_bcn,
    _process_bluelytics,
    _process_dolarapi,
    _process_euro_dolarapi,
    get_banco_nacion,
    get_bluelytics,
    get_dolarapi,
    get_euro_dolarapi,
)

# ------------------------------
# Tests for `_extract` function
# ------------------------------


def test_extract_with_valid_data():
    """Should extract and format currency values correctly."""
    mock_data = MagicMock()
    mock_data.get_text.return_value = """
        Dolar Oficial 100,00
        Euro Oficial 120,00
        Real Oficial 20,00
        / Example Divider /
    """

    result = _extract(mock_data)

    assert result == [
        "🇺🇸 Dolar Oficial 100,00",  # Match original output with comma
        "🇪🇺 Euro Oficial 120,00",
        "🇧🇷 Real Oficial 20,00",
        "/ Example Divider /",
    ]


def test_extract_with_empty_data():
    """Should return an empty string if input is None."""
    result = _extract(None)
    assert result == ""


def test_extract_with_invalid_data():
    """Should gracefully handle non-numeric values."""
    mock_data = MagicMock()
    mock_data.get_text.return_value = "Dolar Oficial abc"

    result = _extract(mock_data)
    assert result == ["🇺🇸 Dolar Oficial abc"]


# ------------------------------
# Tests for `_process_bcn` function
# ------------------------------
def test_process_bcn_with_valid_html():
    """Should parse BNA HTML and return formatted exchange rates."""
    # Each value on its own row so get_text() produces newline-separated tokens
    html_data = """
    <table class="table cotizacion">
    <tr><td>Dolar U.S.A</td></tr>
    <tr><td>100,50</td></tr>
    <tr><td>105,75</td></tr>
    <tr><td>Euro</td></tr>
    <tr><td>120,00</td></tr>
    <tr><td>125,00</td></tr>
    <tr><td>Real (*)</td></tr>
    <tr><td>20,00</td></tr>
    <tr><td>25,00</td></tr>
    </table>
    """

    result = _process_bcn(html_data)

    assert "🇺🇸 Dolar" in result
    assert "100.50" in result
    assert "🇪🇺 Euro" in result
    assert "120.00" in result
    assert "🇧🇷 Real" in result
    assert "20.00" in result
    assert "(*) cotización cada 100 unidades." in result
    assert "👊 by bna.com.ar" in result


def test_process_bcn_with_invalid_html():
    """Should handle HTML without the expected table."""
    html_data = "<html><body><div>No data here</div></body></html>"

    result = _process_bcn(html_data)

    assert result == "Banco Nación cambió su HTML."


# ------------------------------
# Tests for `_process_bluelytics` function
# ------------------------------
def test_process_bluelytics_with_valid_data():
    """Should format Bluelytics API response correctly."""
    mock_data = {
        "oficial": {"value_buy": 100.0, "value_sell": 105.0},
        "blue": {"value_buy": 200.0, "value_sell": 210.0},
        "oficial_euro": {"value_buy": 120.0, "value_sell": 125.0},
        "blue_euro": {"value_buy": 220.0, "value_sell": 230.0},
    }

    result = _process_bluelytics(mock_data)

    # Values are formatted via fmt() as f"{float(x):,.2f}"
    expected_output = (
        "🏦 Oficial:\n"
        "💵 Dólar 100.00 - 105.00\n"
        "🇪🇺 Euro 120.00 - 125.00\n"
        "\n🌳 Blue:\n"
        "💵 Dólar 200.00 - 210.00\n"
        "🇪🇺 Euro 220.00 - 230.00\n"
        "📊 Brecha Dólar: 100.0%"
    )

    assert result == expected_output


def test_process_bluelytics_with_missing_keys():
    """Should handle missing keys gracefully by returning empty string."""
    incomplete_data = {
        "oficial": {"value_buy": 100.0},
        "blue": {"value_buy": 200.0},
    }

    result = _process_bluelytics(incomplete_data)
    assert result == ""


# ------------------------------
# Tests for `_process_dolarapi` function
# ------------------------------


def test_process_dolarapi_with_valid_data():
    """Should format dolarapi.com API response correctly."""
    mock_data = [
        {
            "moneda": "USD",
            "casa": "oficial",
            "nombre": "Oficial",
            "compra": 1400,
            "venta": 1450,
            "fechaActualizacion": "2025-10-09T17:02:00.000Z",
        },
        {
            "moneda": "USD",
            "casa": "blue",
            "nombre": "Blue",
            "compra": 1455,
            "venta": 1475,
            "fechaActualizacion": "2025-10-10T21:02:00.000Z",
        },
        {
            "moneda": "USD",
            "casa": "bolsa",
            "nombre": "Bolsa",
            "compra": 1436.5,
            "venta": 1458,
            "fechaActualizacion": "2025-10-10T21:02:00.000Z",
        },
    ]

    result = _process_dolarapi(mock_data)

    # Updated to reflect new emojis and grouping with blank lines
    expected_output = (
        "💱 Cotizaciones del Dólar:\n"
        "🇺🇸 Oficial: $1,400.00 - $1,450.00\n"
        "\n"
        "🌳 Blue: $1,455.00 - $1,475.00\n"
        "💰 Bolsa: $1,436.50 - $1,458.00\n"
        "👊 by dolarapi.com"
    )

    assert result == expected_output


def test_process_dolarapi_with_empty_data():
    """Should handle empty data by returning empty string."""
    result = _process_dolarapi([])
    assert result == ""


def test_process_dolarapi_with_missing_fields():
    """Should skip items with missing compra or venta fields."""
    mock_data = [
        {
            "moneda": "USD",
            "casa": "oficial",
            "nombre": "Oficial",
            "compra": 1400,
            "venta": 1450,
        },
        {
            "moneda": "USD",
            "casa": "incomplete",
            "nombre": "Incomplete",
            "compra": None,
            "venta": 1500,
        },
    ]

    result = _process_dolarapi(mock_data)

    assert "Oficial" in result
    assert "Incomplete" not in result
    assert "1,400.00" in result


# ------------------------------
# Tests for `get_dolarapi` async function
# ------------------------------


@pytest.mark.asyncio
async def test_get_dolarapi_success(respx_mock):
    """Should fetch and return formatted dolarapi.com data."""
    import httpx

    mock_response = [
        {
            "moneda": "USD",
            "casa": "oficial",
            "nombre": "Oficial",
            "compra": 1400,
            "venta": 1450,
            "fechaActualizacion": "2025-10-09T17:02:00.000Z",
        }
    ]

    respx_mock.get("https://dolarapi.com/v1/dolares").mock(return_value=httpx.Response(200, json=mock_response))

    result = await get_dolarapi()

    assert "💱 Cotizaciones del Dólar:" in result
    assert "Oficial" in result
    assert "1,400.00" in result


@pytest.mark.asyncio
async def test_get_dolarapi_timeout(respx_mock):
    """Should handle timeout gracefully."""
    import httpx

    respx_mock.get("https://dolarapi.com/v1/dolares").mock(side_effect=httpx.TimeoutException("Timeout"))

    result = await get_dolarapi()

    assert "timeout" in result.lower()


@pytest.mark.asyncio
async def test_get_dolarapi_network_error(respx_mock):
    """Should handle network errors gracefully."""
    import httpx

    respx_mock.get("https://dolarapi.com/v1/dolares").mock(side_effect=httpx.RequestError("Network error"))

    result = await get_dolarapi()

    assert "network error" in result.lower()


# ------------------------------
# Tests for `_process_euro_dolarapi` function
# ------------------------------


def test_process_euro_dolarapi_with_valid_data():
    """Should format dolarapi.com Euro API response correctly."""
    # EUR API returns a single dict, not a list
    mock_data = {
        "moneda": "EUR",
        "casa": "oficial",
        "nombre": "Euro Oficial",
        "compra": 1500,
        "venta": 1600,
        "fechaActualizacion": "2025-10-09T17:02:00.000Z",
    }

    result = _process_euro_dolarapi(mock_data)

    expected_output = "💱 🇪🇺 Euro Oficial: $1,500.00 - $1,600.00\n👊 by dolarapi.com"

    assert result == expected_output


def test_process_euro_dolarapi_with_empty_data():
    """Should handle empty data by returning empty string."""
    result = _process_euro_dolarapi({})
    assert result == ""


def test_process_euro_dolarapi_with_missing_fields():
    """Should return empty string if compra or venta is missing."""
    mock_data = {
        "moneda": "EUR",
        "casa": "incomplete",
        "nombre": "Incomplete",
        "compra": None,
        "venta": 1700,
    }

    result = _process_euro_dolarapi(mock_data)

    assert result == ""


# ------------------------------
# Tests for `get_euro_dolarapi` async function
# ------------------------------


@pytest.mark.asyncio
async def test_get_euro_dolarapi_success(respx_mock):
    """Should fetch and return formatted dolarapi.com Euro data."""
    import httpx

    # EUR API returns a single dict, not a list
    mock_response = {
        "moneda": "EUR",
        "casa": "oficial",
        "nombre": "Euro",
        "compra": 1500,
        "venta": 1600,
        "fechaActualizacion": "2025-10-09T17:02:00.000Z",
    }

    respx_mock.get("https://dolarapi.com/v1/cotizaciones/eur").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    result = await get_euro_dolarapi()

    assert "💱" in result
    assert "Euro" in result
    assert "1,500.00" in result


@pytest.mark.asyncio
async def test_get_euro_dolarapi_timeout(respx_mock):
    """Should handle timeout gracefully."""
    import httpx

    respx_mock.get("https://dolarapi.com/v1/cotizaciones/eur").mock(side_effect=httpx.TimeoutException("Timeout"))

    result = await get_euro_dolarapi()

    assert "timeout" in result.lower()


@pytest.mark.asyncio
async def test_get_euro_dolarapi_network_error(respx_mock):
    """Should handle network errors gracefully."""
    import httpx

    respx_mock.get("https://dolarapi.com/v1/cotizaciones/eur").mock(side_effect=httpx.RequestError("Network error"))

    result = await get_euro_dolarapi()

    assert "network error" in result.lower()


# ------------------------------
# Tests for `get_banco_nacion` async function
# ------------------------------

BNC_HTML = """
<table class="table cotizacion">
<tr><td>Dolar U.S.A</td></tr>
<tr><td>100,50</td></tr>
<tr><td>105,75</td></tr>
<tr><td>Euro</td></tr>
<tr><td>120,00</td></tr>
<tr><td>125,00</td></tr>
<tr><td>Real (*)</td></tr>
<tr><td>20,00</td></tr>
<tr><td>25,00</td></tr>
</table>
"""


@pytest.mark.asyncio
async def test_get_banco_nacion_success(respx_mock):
    """Should fetch and return formatted BNA data."""
    respx_mock.get("https://www.bna.com.ar/Personas").mock(return_value=httpx.Response(200, text=BNC_HTML))

    result = await get_banco_nacion()
    assert "🇺🇸 Dolar" in result
    assert "bna.com.ar" in result


@pytest.mark.asyncio
async def test_get_banco_nacion_timeout(respx_mock):
    """Should handle timeout gracefully."""
    respx_mock.get("https://www.bna.com.ar/Personas").mock(side_effect=httpx.TimeoutException("Timeout"))

    result = await get_banco_nacion()
    assert "timeout" in result.lower()


@pytest.mark.asyncio
async def test_get_banco_nacion_network_error(respx_mock):
    """Should handle network errors gracefully."""
    respx_mock.get("https://www.bna.com.ar/Personas").mock(side_effect=httpx.RequestError("Network error"))

    result = await get_banco_nacion()
    assert "network error" in result.lower()


# ------------------------------
# Tests for `get_bluelytics` async function
# ------------------------------

BLUELYTICS_JSON = {
    "oficial": {"value_buy": 100.0, "value_sell": 105.0},
    "blue": {"value_buy": 200.0, "value_sell": 210.0},
    "oficial_euro": {"value_buy": 120.0, "value_sell": 125.0},
    "blue_euro": {"value_buy": 220.0, "value_sell": 230.0},
}


@pytest.mark.asyncio
async def test_get_bluelytics_success(respx_mock):
    """Should fetch and return formatted bluelytics data."""
    respx_mock.get("https://api.bluelytics.com.ar/v2/latest").mock(
        return_value=httpx.Response(200, json=BLUELYTICS_JSON)
    )

    result = await get_bluelytics()
    assert "Oficial" in result
    assert "Blue" in result


@pytest.mark.asyncio
async def test_get_bluelytics_timeout(respx_mock):
    """Should handle timeout gracefully."""
    respx_mock.get("https://api.bluelytics.com.ar/v2/latest").mock(side_effect=httpx.TimeoutException("Timeout"))

    result = await get_bluelytics()
    assert "timeout" in result.lower()


@pytest.mark.asyncio
async def test_get_bluelytics_network_error(respx_mock):
    """Should handle network errors gracefully."""
    respx_mock.get("https://api.bluelytics.com.ar/v2/latest").mock(side_effect=httpx.RequestError("Network error"))

    result = await get_bluelytics()
    assert "network error" in result.lower()
