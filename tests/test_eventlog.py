import unittest

from faker import Faker
from playhouse.sqlite_ext import SqliteExtDatabase

from eduzen_bot.models import EventLog, User
from eduzen_bot.plugins.commands.events.command import get_users_usage

MODELS = [User, EventLog]

# use an in-memory SQLite for tests.
tmp_db = SqliteExtDatabase(":memory:")


class UserTesCase(unittest.TestCase):
    def setUp(self):
        self.faker = Faker()
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        tmp_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        tmp_db.connect()
        tmp_db.create_tables(MODELS)
        self.user = User.create(
            **{
                "id": 3652654,
                "first_name": "Eduardo",
                "is_bot": False,
                "last_name": "Enriquez",
                "username": "eduzen",
                "language_code": "en",
            }
        )
        self.user_2 = User.create(
            **{
                "id": 3652655,
                "first_name": "Arturo",
                "is_bot": False,
                "last_name": "Enriquez",
                "username": "edu_zen",
                "language_code": "es",
            }
        )
        self.events = []
        for _ in range(5):
            self.events.append(EventLog.create(user=self.user, command="btc"))
            self.events.append(EventLog.create(user=self.user_2, command="btc"))

    def test_count_aggregation_of_usage(self):
        txt = get_users_usage()
        txt = txt.split("\n")
        assert len(txt) == 2
