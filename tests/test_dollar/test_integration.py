import pytest
from telegram.ext import CallbackContext, ExtBot, Updater

from eduzenbot.plugins.commands.dolar.command import get_dolar


@pytest.mark.vcr()
def test_dollar_command(mocker):
    mocked_createuser = mocker.patch("eduzenbot.plugins.commands.dolar.command.create_user")

    mocked_updater = mocker.MagicMock(autospec=Updater)

    mocked_context = mocker.MagicMock(autospec=CallbackContext)
    mocked_bot = mocker.MagicMock(autospec=ExtBot)
    mocked_context.bot.return_value = mocked_bot

    answer = get_dolar(mocked_updater, mocked_context)

    assert answer is None
    assert mocked_updater.bot.send_chat_action.call_count == 1
    assert mocked_createuser.called
