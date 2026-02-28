from datetime import datetime

from eduzenbot.models import EventLog, Report, User


def test_user_todict():
    user = User.create(id=1, first_name="John", last_name="Doe", username="johndoe")
    d = user.todict()
    assert d["id"] == 1
    assert d["first_name"] == "John"
    assert d["last_name"] == "Doe"
    assert d["username"] == "johndoe"


def test_user_to_dict():
    user = User.create(id=2, first_name="Jane", last_name="Doe", username="janedoe")
    d = user.to_dict()
    assert d["id"] == 2
    assert d["username"] == "janedoe"


def test_user_str():
    user = User.create(id=3, first_name="Alice", last_name="Smith", username="alice")
    assert str(user) == "<alice: Alice Smith>"


def test_user_str_no_username():
    user = User.create(id=4, first_name="Bob", last_name="Brown")
    assert str(user) == "<: Bob Brown>"


def test_user_full_name_both():
    user = User.create(id=5, first_name="Alice", last_name="Smith")
    assert user.full_name == "Alice Smith"


def test_user_full_name_first_only():
    user = User.create(id=6, first_name="Alice")
    assert user.full_name == "Alice"


def test_user_full_name_none():
    user = User.create(id=7)
    assert user.full_name == ""


def test_user_to_str():
    user = User.create(id=8, first_name="Test", last_name="User", username="testuser", is_bot=False)
    result = user.to_str()
    assert "testuser" in result
    assert "Test User" in result
    assert "|" in result


def test_user_to_str_bot():
    user = User.create(id=9, first_name="Bot", username="botuser", is_bot=True)
    result = user.to_str()
    assert "bot!" in result


def test_eventlog_str():
    user = User.create(id=10, username="loguser")
    event = EventLog.create(user=user, command="/test")
    result = str(event)
    assert "<" in result
    assert "loguser" in result


def test_eventlog_telegram_property():
    user = User.create(id=11, username="teluser")
    event = EventLog.create(user=user, command="/hello", timestamp=datetime(2025, 1, 15, 10, 30))
    result = event.telegram
    assert "teluser" in result
    assert "/hello" in result
    assert "2025/01/15" in result


def test_report_str():
    report = Report.create(chat_id="12345", hour=10, min=30, show_weather=True, show_dollar=False, show_crypto=True)
    result = str(report)
    assert "12345" in result
    assert "10:30" in result
    assert "Weather: True" in result
    assert "Dollar: False" in result
    assert "Crypto: True" in result
