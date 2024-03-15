from telegram.ext import CallbackContext, Updater

from eduzenbot.plugins.commands.dolar.command import get_dolar


def test_get_dolar(mocker):
    mocker_update = mocker.MagicMock(autospec=Updater)
    mocker_context = mocker.MagicMock(autospec=CallbackContext)

    mock_send_msg = mocker.patch("eduzenbot.plugins.commands.dolar.command.send_msg")
    mock_send_msg.return_value = "ok"
    mock_send_message = mocker.patch("telegram.Bot.send_message")
    mock_send_message.return_value = "ok"
    mock_send_chat_action = mocker.patch("telegram.Bot.send_chat_action")
    mock_send_chat_action.return_value = "ok"
    mock_get_banco_nacion = mocker.patch(
        "eduzenbot.plugins.commands.dolar.command.get_banco_nacion"
    )
    mock_get_banco_nacion.return_value = "ok"
    mock_get_bluelytics = mocker.patch(
        "eduzenbot.plugins.commands.dolar.command.get_bluelytics"
    )
    mock_get_bluelytics.return_value = "ok"
    mock_get_dolar_blue_geeklab = mocker.patch(
        "eduzenbot.plugins.commands.dolar.command.get_dolar_blue_geeklab"
    )
    mock_get_dolar_blue_geeklab.return_value = "ok"
    mock_create_user = mocker.patch(
        "eduzenbot.plugins.commands.dolar.command.create_user"
    )
    mock_create_user.return_value = "ok"

    get_dolar(mocker_update, mocker_context)

    mock_get_banco_nacion.assert_called_once()
    mock_get_bluelytics.assert_called_once()
    mock_get_dolar_blue_geeklab.assert_called_once()
