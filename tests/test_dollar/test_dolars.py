import pytest

from eduzenbot.plugins.commands.dolar.api import _sessions_cache, get_bluelytics


@pytest.fixture(autouse=True, scope="function")
def clear_cache():
    _sessions_cache.clear()
    yield
    _sessions_cache.clear()


@pytest.mark.vcr
def test_get_bluelytics_exception(mocker):
    mocker.patch("eduzenbot.plugins.commands.dolar.api.process_bluelytics", side_effect=Exception())

    msg = get_bluelytics()
    assert msg == "Bluelytics no responde 🤷‍♀️"


@pytest.mark.vcr
def test_get_bluelytics():
    msg = get_bluelytics()

    assert "🏦 Oficial:" in msg
