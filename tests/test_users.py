from unittest import TestCase

from eduzen_bot.decorators import get_or_create_user
from eduzen_bot.models import User

from .factories import UserFactory


class UserTesCase(TestCase):
    def test_create_user_all_good(self):
        before = User.select().count()
        telegram_user = UserFactory()
        get_or_create_user(telegram_user)
        after = User.select().count()
        assert before + 1 == after

    def test_create_user_all_empty(self):
        before = User.select().count()
        telegram_user = UserFactory()
        user = get_or_create_user(telegram_user)
        after = User.select().count()
        assert user.id
        assert before + 1 == after

    def test_create_user_mix(self):
        before = User.select().count()
        telegram_user = UserFactory()
        get_or_create_user(telegram_user)
        after = User.select().count()

        assert before + 1 == after

    def test_create_users(self):
        before = User.select().count()
        telegram_user = UserFactory()
        get_or_create_user(telegram_user)
        get_or_create_user(telegram_user)
        get_or_create_user(telegram_user)
        get_or_create_user(telegram_user)
        after = User.select().count()

        assert before + 1 == after
