import os

import pytest

from eduzen_bot.telegram_bot import TelegramBot


def test_init_telegram_bot_missing_token():
    with pytest.raises(TypeError) as exc:
        TelegramBot()

    assert str(exc.value) == "__init__() missing 1 required positional argument: 'token'"


def test_init_telegram_bot_wrong_token():
    with pytest.raises(SystemExit) as exc:
        TelegramBot(token="someweirdtoken")

    assert str(exc.value) == "Invalid token"


@pytest.mark.vcr("telegram_bot_login.yaml")
def test_init_telegram_bot_good_token():
    token = os.getenv("TOKEN", "fruta")
    tb = TelegramBot(token=token)
    assert hasattr(tb, "updater")
