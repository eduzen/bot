import pytest

from eduzenbot.plugins.commands.dolar.api import (
    get_banco_nacion,
    get_bluelytics,
    get_dolar_blue_geeklab,
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
    msg = get_banco_nacion()
    assert "cotización cada 100 unidades" in msg
