import pytest

from eduzenbot.plugins.commands.dolar.api import (
    get_bluelytics,
    get_dolar_blue,
    get_dollar,
    parse_bnc,
)


@pytest.fixture(autouse=True)
def clear_cache():
    yield
    parse_bnc.cache_clear()
    get_bluelytics.cache_clear()
    get_dollar.cache_clear()
    get_dolar_blue.cache_clear()
