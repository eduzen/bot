import pytest

from eduzenbot.plugins.commands.dolar.api import get_bluelytics


@pytest.mark.vcr
def test_get_bluelytics_exception(mocker):
    mocker.patch("eduzenbot.plugins.commands.dolar.api.process_bluelytics", side_effect=Exception())

    msg = get_bluelytics()
    assert msg == "Bluelytics no responde 🤷‍♀️"


@pytest.mark.vcr
def test_get_bluelytics():
    msg = get_bluelytics()

    assert "🏦 Oficial:" in msg
