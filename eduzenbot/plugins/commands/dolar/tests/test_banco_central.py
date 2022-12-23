import pytest

from eduzenbot.plugins.commands.dolar.api import parse_bnc


@pytest.mark.vcr
def test_parse_bnc():
    result = parse_bnc()
    assert len(result.split("\n")) == 6
