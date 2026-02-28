import httpx
import pytest
import respx

from eduzenbot.plugins.commands.weather.api import get_klima, get_sun_times, get_timezone


# -----------------------------------
# Pure function tests for get_timezone
# -----------------------------------


def test_get_timezone_known_city():
    result = get_timezone("amsterdam")
    assert "Amsterdam" in result


def test_get_timezone_city_with_spaces():
    result = get_timezone("new york")
    assert "New_York" in result


def test_get_timezone_city_with_comma():
    result = get_timezone("buenos aires,ar")
    assert "Buenos_Aires" in result


def test_get_timezone_dallas():
    result = get_timezone("dallas")
    assert result == "America/Chicago"


def test_get_timezone_unknown():
    result = get_timezone("xyznonexistentcity")
    assert result == "UTC"


# -----------------------------------
# Tests for get_sun_times
# -----------------------------------


def test_get_sun_times():
    data = {"sunrise": 1704067200, "sunset": 1704103200}  # 2024-01-01 ~UTC times
    sunrise, sunset = get_sun_times(data, "amsterdam")
    # Just verify HH:MM format
    assert ":" in sunrise
    assert ":" in sunset
    assert len(sunrise) == 5
    assert len(sunset) == 5


# -----------------------------------
# Async tests for get_klima
# -----------------------------------

WEATHER_JSON = {
    "name": "Amsterdam",
    "sys": {"sunrise": 1704067200, "sunset": 1704103200},
    "weather": [{"main": "Clear", "description": "clear sky"}],
    "main": {"temp": 5.0, "humidity": 80, "temp_max": 7.0, "temp_min": 3.0},
}


@pytest.mark.asyncio
async def test_get_klima_success(respx_mock, monkeypatch):
    monkeypatch.setattr("eduzenbot.plugins.commands.weather.api.ow_token", "fake_token")

    respx_mock.get("https://api.openweathermap.org/data/2.5/weather/").mock(
        return_value=httpx.Response(200, json=WEATHER_JSON)
    )

    result = await get_klima("Amsterdam,nl")
    assert "Amsterdam" in result
    assert "5.0" in result
    assert "80" in result
    assert "🌞" in result  # clear -> sun emoji


@pytest.mark.asyncio
async def test_get_klima_non_200(respx_mock, monkeypatch):
    monkeypatch.setattr("eduzenbot.plugins.commands.weather.api.ow_token", "fake_token")

    respx_mock.get("https://api.openweathermap.org/data/2.5/weather/").mock(
        return_value=httpx.Response(404, json={})
    )

    result = await get_klima("NonExistent")
    assert result == "No pudimos conseguir el clima"


@pytest.mark.asyncio
async def test_get_klima_unknown_emoji(respx_mock, monkeypatch):
    monkeypatch.setattr("eduzenbot.plugins.commands.weather.api.ow_token", "fake_token")

    weather_json = {
        **WEATHER_JSON,
        "weather": [{"main": "Squall", "description": "squalls"}],
    }

    respx_mock.get("https://api.openweathermap.org/data/2.5/weather/").mock(
        return_value=httpx.Response(200, json=weather_json)
    )

    result = await get_klima("Amsterdam,nl")
    # "squall" is not in WEATHER_EMOJIS, so falls back to the raw weather string
    assert "squall" in result.lower()
    assert "Squall" in result  # capitalized in output
