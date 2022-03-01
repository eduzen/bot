from eduzen_bot.decorators import get_or_create_user
from eduzen_bot.models import User

from .factories import UserFactory


def test_create_user_all_good():
    before = User.select().count()
    telegram_user = UserFactory.create()
    get_or_create_user(telegram_user)
    after = User.select().count()
    assert before + 1 == after


def test_create_user_all_empty():
    before = User.select().count()
    telegram_user = UserFactory.create()
    user = get_or_create_user(telegram_user)
    after = User.select().count()
    assert user.id
    assert before + 1 == after


def test_create_user_mix():
    before = User.select().count()
    telegram_user = UserFactory.create()
    get_or_create_user(telegram_user)
    after = User.select().count()

    assert before + 1 == after


def test_create_users():
    before = User.select().count()
    telegram_user = UserFactory.create()
    get_or_create_user(telegram_user)
    get_or_create_user(telegram_user)
    get_or_create_user(telegram_user)
    get_or_create_user(telegram_user)
    after = User.select().count()

    assert before + 1 == after
