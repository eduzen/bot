import unittest
from dataclasses import asdict, dataclass

from playhouse.sqlite_ext import SqliteExtDatabase

from eduzen_bot.decorators import get_or_create_user
from eduzen_bot.models import User

MODELS = [User]

# use an in-memory SQLite for tests.
tmp_db = SqliteExtDatabase(":memory:")


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


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        tmp_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        tmp_db.connect()
        tmp_db.create_tables(MODELS)

    def tearDown(self):
        # Not strictly necessary since SQLite in-memory databases only live
        # for the duration of the connection, and in the next step we close
        # the connection...but a good practice all the same.
        tmp_db.drop_tables(MODELS)

        # Close connection to db.
        tmp_db.close()

        # If we wanted, we could re-bind the models to their original
        # database here. But for tests this is probably not necessary.

    def test_create_user_all_good(self):
        before = User.select().count()
        telegram_user = TelegramUser(
            **{
                "id": 3652654,
                "first_name": "Eduardo",
                "is_bot": False,
                "last_name": "Enriquez",
                "username": "eduzen",
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
                "id": 3652653,
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
                "id": 3652653,
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

    def test_create_users(self):
        data = {
            "id": 3652654,
            "first_name": "Eduardo",
            "is_bot": False,
            "last_name": "Enriquez",
            "username": "eduzen",
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
