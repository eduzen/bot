from dataclasses import asdict, dataclass

from eduzen_bot.decorators import get_or_create_user
from eduzen_bot.models import User

from .conftest import BaseTestCase

# use an in-memory SQLite for tests.


@dataclass
class TelegramUser:
    id: int
    first_name: str
    last_name: str
    username: str
    is_bot: bool = False
    language_code: str = "en"

    def to_dict(self):
        return asdict(self)


class UserTesCase(BaseTestCase):
    def test_create_user_all_good(
        self,
    ):
        before = User.select().count()
        telegram_user = TelegramUser(
            **{
                "id": 3,
                "first_name": self.faker.first_name(),
                "is_bot": False,
                "last_name": self.faker.last_name(),
                "username": self.faker.last_name_nonbinary(),
                "language_code": "en",
            }
        )
        get_or_create_user(telegram_user)
        after = User.select().count()

        assert before + 1 == after

    def test_create_user_all_empty(self):
        before = User.select().count()
        telegram_user = TelegramUser(
            **{
                "id": 365263,
                "first_name": "",
                "is_bot": False,
                "last_name": "",
                "username": "",
                "language_code": "en",
            }
        )
        user = get_or_create_user(telegram_user)
        after = User.select().count()
        assert user.id
        assert before + 1 == after

    def test_create_user_mix(self):
        before = User.select().count()
        telegram_user = TelegramUser(
            **{
                "id": 652653,
                "first_name": None,
                "is_bot": False,
                "last_name": None,
                "username": None,
                "language_code": "en",
            }
        )
        get_or_create_user(telegram_user)
        after = User.select().count()

        assert before + 1 == after

    def test_create_users(
        self,
    ):
        data = {
            "id": 365254,
            "first_name": self.faker.first_name(),
            "is_bot": False,
            "last_name": self.faker.last_name(),
            "username": self.faker.last_name_nonbinary(),
            "language_code": "en",
        }
        before = User.select().count()
        telegram_user = TelegramUser(**data)
        get_or_create_user(telegram_user)
        get_or_create_user(telegram_user)
        get_or_create_user(telegram_user)
        get_or_create_user(telegram_user)
        after = User.select().count()

        assert before + 1 == after
