import pytest

from eduzenbot.plugins.commands.btc.command import coingecko_all_crypto


@pytest.mark.vcr()
def test_coingecko_all_crypto():
    msg = coingecko_all_crypto()

    assert "btc" in msg
    assert "eth" in msg
    assert "doge" in msg
    assert "sol" in msg
    assert "ada" in msg
    assert "kava" in msg
    assert "shiba" in msg
    assert "mana" in msg
