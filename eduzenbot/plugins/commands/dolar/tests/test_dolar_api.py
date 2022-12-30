import pytest

from eduzenbot.plugins.commands.dolar.api import (
    get_bluelytics,
    get_dolar_blue_geeklab,
    parse_bnc,
)


@pytest.fixture(autouse=True, scope="function")
def mock_cache(mocker):
    mocker.patch("eduzenbot.plugins.commands.dolar.api.cached")
    yield


@pytest.mark.vcr()
def test_dolar_get_dolar_geeklab():
    msg = get_dolar_blue_geeklab()
    assert "by http://ws.geeklab.com.ar" in msg


@pytest.mark.vcr()
def test_dolar_get_bluelytics():
    msg = get_bluelytics()
    assert "🏦 Oficial:" in msg


@pytest.mark.vcr()
def test_parse_bnc():
    msg = parse_bnc()
    assert "cotización cada 100 unidades" in msg


# # @pytest.mark.vcr()
# def test_get_dollar_all_good(mocker):
#     mocker.patch("eduzenbot.plugins.commands.dolar.api.cached")
#     msg = get_dollar()
#     assert "by https://openexchangerates.org" in msg
